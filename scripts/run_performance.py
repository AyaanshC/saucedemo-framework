"""Execute genuine JMeter samples, generate its dashboard, then assess the NFRs."""
import argparse
import csv
import json
import math
import os
import re
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from verify_routes import verify_routes, BASE_URL, PRODUCTS_DOCUMENT

ROOT = Path(__file__).resolve().parents[1]
PERF = ROOT / 'performance'


def resolve_java(supplied):
    """Prefer the requested executable/PATH; find common Windows installs without changing PATH."""
    found = shutil.which(supplied)
    candidates = [Path(found)] if found else [Path(supplied)]
    if supplied == 'java':
        if os.getenv('JAVA_HOME'):
            candidates.append(Path(os.environ['JAVA_HOME']) / 'bin/java.exe')
        program_files = Path(os.getenv('ProgramFiles', r'C:\Program Files'))
        for folder in ['Eclipse Adoptium', 'Java']:
            base = program_files / folder
            candidates.extend(sorted(base.glob('*8*/bin/java.exe')))
            candidates.extend(sorted(base.glob('*/bin/java.exe')))
    for candidate in dict.fromkeys(candidates):
        if not candidate.is_file():
            continue
        result = subprocess.run([str(candidate), '-version'], capture_output=True, text=True, timeout=10)
        version_text = (result.stderr or result.stdout).strip()
        match = re.search(r'version "(?:1\.)?(\d+)', version_text)
        if result.returncode == 0 and match and int(match.group(1)) >= 8:
            return str(candidate.resolve()), version_text.splitlines()[0]
    raise ValueError('Java 8+ not found. Install Java or pass --java C:\\path\\to\\java.exe.')


def percentile(values, p):
    """Nearest-rank percentile; report the method explicitly."""
    return sorted(values)[max(0, math.ceil(len(values) * p) - 1)]


def analyze():
    metadata = json.loads((PERF / 'results/run-metadata.json').read_text())
    with (PERF / 'results/results.jtl').open(newline='', encoding='utf-8-sig') as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError('No JMeter samples: NFRs cannot be assessed.')
    required = {'Login page', 'Products page'}
    labels = {r['label'] for r in rows}
    if not required <= labels:
        raise ValueError(f'Missing required samplers: {required - labels}')
    start = min(int(r['timeStamp']) for r in rows)
    end = max(int(r['timeStamp']) + int(r['elapsed']) for r in rows)
    elapsed = (end - start) / 1000
    peak = max(int(r['allThreads']) for r in rows)
    profile_ok = (metadata['users'], metadata['ramp_seconds'], metadata['duration_seconds']) == (20, 60, 180)
    profile_ok = profile_ok and peak == 20 and elapsed >= 170 and metadata['jmeter_exit_code'] == 0
    observed_urls = {label: sorted({r.get('URL', 'not recorded') for r in rows if r['label'] == label})
                     for label in required}
    measurement_ok = (metadata.get('measurement_kind') == 'spa_bootstrap_http'
                      and metadata.get('route_preflight_verified') is True
                      and observed_urls['Login page'] == [BASE_URL + '/']
                      and observed_urls['Products page'] == [BASE_URL + PRODUCTS_DOCUMENT])
    profile_ok = profile_ok and measurement_ok
    aggregates = []
    for label in ['Login page', 'Products page', 'TOTAL']:
        group = rows if label == 'TOTAL' else [r for r in rows if r['label'] == label]
        times = [int(r['elapsed']) for r in group]
        errors = sum(r['success'].lower() != 'true' for r in group)
        aggregates.append(dict(label=label, samples=len(group), average_ms=round(statistics.mean(times), 2),
                               min_ms=min(times), max_ms=max(times), p95_ms=percentile(times, .95),
                               error_percent=round(100 * errors / len(group), 4),
                               throughput_per_second=round(len(group) / elapsed, 3)))
    with (PERF / 'results/aggregate.csv').open('w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=list(aggregates[0]))
        writer.writeheader()
        writer.writerows(aggregates)
    checks = [aggregates[0]['p95_ms'] < 3000 and aggregates[0]['error_percent'] < 100,
              aggregates[1]['p95_ms'] < 4000 and aggregates[1]['error_percent'] < 100,
              sum(r['success'].lower() != 'true' for r in rows) / len(rows) < .02]
    status = lambda passed: ('PASS' if passed else 'FAIL') if profile_ok else 'NOT QUALIFIED'
    codes = {}
    for label in ('Login page', 'Products page'):
        codes[label] = {}
        for row in rows:
            if row['label'] == label:
                code = row['responseCode']
                codes[label][code] = codes[label].get(code, 0) + 1
    route_note = (
        'Before this run, real Chrome authenticated as standard_user and verified that navigating to '
        '/inventory.html loads the HTTP 200 document /?/inventory.html, then displays Products with '
        'six items at /inventory.html. JMeter requests that verified SPA bootstrap document directly '
        'and still requires HTTP 200 plus the React root marker. The original direct-route 404 run '
        'and diagnostic JMX are preserved separately. NFR-02 here means Products bootstrap-document '
        'HTTP response time; it is not authenticated rendered-product readiness or end-to-end '
        'navigation including the initial 404 hop. Do not present it as a browser-rendering verdict.'
        if measurement_ok else
        'This run lacks the verified SPA bootstrap measurement metadata. Mandatory NFR verdicts '
        'are NOT QUALIFIED. Legacy direct-route HTTP 404 responses do not establish Products performance.'
    )
    assessment = {'profile_qualified': profile_ok, 'measurement_verified': measurement_ok,
                  'measurement': metadata.get('measurement_kind', 'legacy_direct_route_http'),
                  'peak_users': peak, 'sample_window_seconds': round(elapsed, 2), 'samples': len(rows),
                  'overall_error_percent': round(100 * sum(r['success'].lower() != 'true' for r in rows) / len(rows), 4),
                  'verdicts': {f'NFR-0{i}': status(passed) for i, passed in enumerate(checks, 1)},
                  'http_response_codes': codes, 'observed_request_urls': observed_urls}
    (PERF / 'results/assessment.json').write_text(json.dumps(assessment, indent=2), encoding='utf-8')
    text = f'''# Performance findings

Measured run started (UTC): {metadata['started_utc']}.
JMeter exit code: {metadata['jmeter_exit_code']}. Host: www.saucedemo.com.
Profile: {metadata['users']} users, {metadata['ramp_seconds']}s ramp, {metadata['duration_seconds']}s duration (ramp included).
Observed peak: {peak} users; sample window: {elapsed:.2f}s; total samples: {len(rows)}.
Mandatory profile verified: {profile_ok}.
Measurement: {metadata.get('measurement_kind', 'legacy_direct_route_http')}.
Login document: {metadata.get('login_document_url', 'not recorded')}.
Products document: {metadata.get('products_document_url', 'not recorded')}.

| Requirement | Threshold | Measured | Errors | Result |
|---|---|---|---|---|
| NFR-01 | Login P95 < 3000 ms | {aggregates[0]['p95_ms']} ms | {aggregates[0]['error_percent']}% | {status(checks[0])} |
| NFR-02 | Products P95 < 4000 ms | {aggregates[1]['p95_ms']} ms | {aggregates[1]['error_percent']}% | {status(checks[1])} |
| NFR-03 | Overall errors < 2% | {aggregates[2]['error_percent']}% | included at left | {status(checks[2])} |

HTTP response codes by sampler: `{json.dumps(codes, sort_keys=True)}`.
Observed request URLs from the JTL: `{json.dumps(observed_urls, sort_keys=True)}`.

P95 uses nearest rank over all samples of each label, including errors. Error rate uses exact counts
before rounding. Samples with failed HTTP status or response assertions are errors. A sampler with
no successful responses cannot pass its latency requirement. A diagnostic profile cannot qualify
the mandatory NFRs. Aggregate CSV is derived from the raw JTL, not invented measurements.

## Interpretation

These are HTTP document response timings from this machine and network. JMeter does not log a user
in, execute JavaScript, load browser assets, or measure rendered product readiness.
{route_note}
Use the Selenium suite to demonstrate authenticated workflows. This plan therefore demonstrates
basic HTTP page performance as requested, not authenticated browser transaction performance.
The {metadata['duration_seconds']}-second scheduler duration includes the {metadata['ramp_seconds']}-second ramp; roughly {max(0, metadata['duration_seconds'] - metadata['ramp_seconds'])} seconds remain at full
load. Requests already in flight may finish after the scheduler cutoff. Results are specific to this run.

Files: results/results.jtl, results/aggregate.csv, results/run-metadata.json, results/route-evidence.json,
results/assessment.json, results/jmeter.log,
and html_report/index.html (the entire dashboard folder must stay together).
'''
    (PERF / 'Findings.md').write_text(text, encoding='utf-8')
    print(text)
    return 0 if profile_ok and all(checks) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jmeter-home', default=os.getenv('JMETER_HOME', str(ROOT / 'tools/apache-jmeter-5.6.3')))
    parser.add_argument('--java', default='java')
    parser.add_argument('--driver-path', default=os.getenv('CHROMEDRIVER_PATH'))
    parser.add_argument('--users', type=int, default=20)
    parser.add_argument('--ramp', type=int, default=60)
    parser.add_argument('--duration', type=int, default=180)
    parser.add_argument('--analyze-only', action='store_true')
    args = parser.parse_args()
    if args.analyze_only:
        return analyze()
    if min(args.users, args.duration) < 1 or args.ramp < 0:
        parser.error('Users/duration must be positive and ramp non-negative.')
    home = Path(args.jmeter_home).resolve()
    jar = home / 'bin/ApacheJMeter.jar'
    if not jar.is_file():
        parser.error('JMeter not found. Run scripts/setup.ps1 -WithJMeter or supply --jmeter-home.')
    try:
        java, java_version = resolve_java(args.java)
    except ValueError as error:
        parser.error(str(error))
    print('Verifying the actual Products SPA document in Chrome before issuing load...', flush=True)
    route_evidence = verify_routes(args.driver_path)
    if not route_evidence['verified']:
        parser.error('Products route verification failed; refusing to measure an unverified substitute URL.')
    # Preserve prior evidence. Every move stays under this framework's performance folder.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    archive = PERF / 'history' / stamp
    for name in ('Findings.md', 'route-evidence.json'):
        if (PERF / name).is_file():
            archive.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PERF / name, archive / name)
    for name in ('results', 'html_report'):
        source = (PERF / name).resolve()
        if source.exists() and any(source.iterdir()):
            destination = (PERF / 'history' / stamp / name).resolve()
            source.relative_to(PERF.resolve())
            destination.relative_to(PERF.resolve())
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
    (PERF / 'results').mkdir(parents=True, exist_ok=True)
    metadata = dict(started_utc=datetime.now(timezone.utc).isoformat(), users=args.users,
                    ramp_seconds=args.ramp, duration_seconds=args.duration, jmeter_version='5.6.3',
                    measurement_kind='spa_bootstrap_http', route_preflight_verified=True,
                    java_executable=java, java_version=java_version,
                    login_document_url=BASE_URL + '/', products_document_url=BASE_URL + PRODUCTS_DOCUMENT)
    (PERF / 'route-evidence.json').write_text(json.dumps(route_evidence, indent=2), encoding='utf-8')
    (PERF / 'results/route-evidence.json').write_text(json.dumps(route_evidence, indent=2), encoding='utf-8')
    command = [java, '-Xms256m', '-Xmx1g', '-jar', str(jar), '-d', str(home), '-n',
               '-t', str(PERF / 'jmx/saucedemo_weekend_lab.jmx'),
               '-l', str(PERF / 'results/results.jtl'), '-j', str(PERF / 'results/jmeter.log'),
               '-e', '-o', str(PERF / 'html_report'),
               '-Jjmeter.save.saveservice.url=true',
               f'-Jusers={args.users}', f'-Jramp={args.ramp}', f'-Jduration={args.duration}']
    print('Running:', subprocess.list2cmdline(command), flush=True)
    metadata['jmeter_exit_code'] = subprocess.run(command, cwd=ROOT).returncode
    (PERF / 'results/run-metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    if not (PERF / 'results/results.jtl').exists():
        print('JMeter produced no JTL. Inspect performance/results/jmeter.log.', file=sys.stderr)
        return 2
    return analyze()


if __name__ == '__main__':
    sys.exit(main())
