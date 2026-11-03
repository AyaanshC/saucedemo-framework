"""Build a portable submission ZIP containing source, reports and all JMeter evidence."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ['README.md', 'DEMO_GUIDE.md', 'VERIFICATION.md', 'SUBMISSION.md',
                'START_DEMO.cmd', 'conftest.py', 'pytest.ini', 'requirements.txt',
                'requirements-lock.txt', '.gitignore', '.gitattributes']
TREES = ['pages', 'tests', 'testdata', 'scripts', 'docs', 'performance']
REPORTS = ['smoke.html', 'smoke-junit.xml', 'functional.html', 'junit.xml',
           'case-study.html', 'case-study-junit.xml', 'classification-check.html', 'classification-check.xml',
           'expanded-initial.html', 'expanded-initial.xml', 'dynamic-check.html', 'dynamic-check.xml',
           'expanded-combined.xml', 'expanded-summary.json', 'expanded-demo-check.html', 'expanded-demo-check.xml',
           'coverage-map.json',
           'submission-dashboard-preview.png', 'dashboard-validation.json',
           'slider-demo-check.html', 'slider-demo-check.xml']
REQUIRED = SOURCE_FILES + [
    'docs/CASE_STUDY_COMPLIANCE.md', 'performance/jmx/saucedemo_weekend_lab.jmx',
    'performance/results/results.jtl', 'performance/results/aggregate.csv',
    'performance/results/run-metadata.json', 'performance/results/route-evidence.json',
    'performance/results/assessment.json', 'performance/html_report/index.html',
    'performance/Findings.md', 'reports/case-study.html', 'reports/case-study-junit.xml',
    'reports/expanded-summary.json', 'reports/logs/case-study.log',
    'reports/coverage-map.json',
]


def build():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file() or (ROOT / name).stat().st_size == 0]
    if missing:
        raise SystemExit('Required submission evidence missing: ' + ', '.join(missing))
    assessment = json.loads((ROOT / 'performance/results/assessment.json').read_text())
    if not assessment['profile_qualified']:
        raise SystemExit('Mandatory performance profile is not qualified; include a real 20-user/60s/180s run.')
    files = {ROOT / name for name in SOURCE_FILES}
    for name in TREES + ['reports/logs', 'reports/screenshots']:
        files.update(path for path in (ROOT / name).rglob('*') if path.is_file()
                     and '__pycache__' not in path.parts and path.suffix not in {'.pyc', '.pyo'}
                     and not path.name.startswith('.env') and not path.is_symlink())
    files.update(ROOT / 'reports' / name for name in REPORTS if (ROOT / 'reports' / name).is_file())
    # Use an explicit allowlist. Never include .git, environments, drivers, tools, or local .env files.
    for path in files:
        path.resolve().relative_to(ROOT)
    manifest = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(files)}
    output = ROOT / 'dist/saucedemo-case-study-submission.zip'
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(files):
            archive.write(path, arcname='saucedemo-framework/' + path.relative_to(ROOT).as_posix())
        archive.writestr('saucedemo-framework/SUBMISSION_MANIFEST.json', json.dumps({
            'sha256': manifest, 'note': 'Hashes cover all packaged source/evidence files; excludes this manifest.'}, indent=2))
    with zipfile.ZipFile(temporary) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise SystemExit('ZIP integrity check failed: ' + corrupt)
        for name in REQUIRED:
            assert 'saucedemo-framework/' + name in archive.namelist(), name
    temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.zip.sha256').write_text(f'{digest}  {output.name}\n', encoding='ascii')
    print(f'Created {output}\nFiles: {len(files) + 1}\nBytes: {output.stat().st_size}')
    print('Performance verdicts:', assessment['verdicts'])
    return output


if __name__ == '__main__':
    build()
