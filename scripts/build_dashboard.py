"""Build an offline presentation dashboard from recorded test evidence."""
import argparse
import csv
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def timestamp(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def date_label(value):
    date = timestamp(value)
    return date.strftime("%d %b %Y, %H:%M %Z") if date else "No recorded run"


def link(root, path, label, css="button"):
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        return f'<span class="{css} disabled" aria-disabled="true">{escape(label)} (not generated)</span>'
    href = "../" + quote(target.relative_to(root.resolve()).as_posix(), safe="/")
    return f'<a class="{css}" href="{href}">{escape(label)}</a>'


def badge(outcome):
    text = {"passed": "Passed", "failed": "Failed", "error": "Error",
            "skipped": "Skipped", "not-run": "Not run"}[outcome]
    return f'<span class="badge {outcome}">{text}</span>'


def assignments(root):
    text = (root / "docs/TEAM_ASSIGNMENTS.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (\d+) \| ([1-5]) \| \x60([^\x60]+)\x60", text, re.M)
    owners = {node: int(owner) for _, owner, node in rows}
    if len(rows) != 25 or len(owners) != 25:
        raise ValueError("The team plan must assign all 25 original cases exactly once.")
    return owners


def case_outcomes(records):
    """A failing setup/teardown takes precedence over a passed call for the same test."""
    cases = {}
    rank = {"not-run": 0, "skipped": 1, "passed": 2, "failed": 3, "error": 4}
    for row in records:
        node = row["test"]
        outcome = row["outcome"]
        if outcome == "failed" and row["phase"] != "call":
            outcome = "error"
        if outcome not in rank:
            raise ValueError(f"Unrecognized result outcome: {outcome}")
        case = cases.setdefault(node, {"outcome": "not-run", "records": [], "requirements": set()})
        case["records"].append(row)
        case["requirements"].update(row.get("requirements", []))
        if rank[outcome] > rank[case["outcome"]]:
            case["outcome"] = outcome
    return cases


def build(root=ROOT, report_hint=None):
    root = root.resolve()
    owners = assignments(root)
    summary = read_json(root / "dashboard/recording/summary.json") or {}
    records = summary.get("results", [])
    if not isinstance(records, list):
        raise ValueError("Execution summary results must be a list.")
    cases = case_outcomes(records)
    if set(cases) != set(owners):
        raise ValueError("Recorded cases must match the 25 assigned tests.")
    counts = {key: sum(c["outcome"] == key for c in cases.values())
              for key in ("passed", "failed", "error", "skipped")}
    total = len(cases)
    passed, failed, errors = (counts[k] for k in ("passed", "failed", "error"))
    pass_rate = f"{passed / total:.0%}" if total else "-"
    started, finished = timestamp(summary.get("started_utc")), timestamp(summary.get("finished_utc"))
    duration = f"{(finished - started).total_seconds():.1f}s" if started and finished else "-"
    core_run = len(set(cases) & set(owners))
    extra_run = total - core_run
    scope = ("Original case-study suite" if set(cases) == set(owners)
             else "Selected test run" if total else "Ready for the first run")
    assessment = read_json(root / "performance/results/assessment.json") or {}
    metadata = read_json(root / "performance/results/run-metadata.json") or {}
    aggregate = {}
    csv_path = root / "performance/results/aggregate.csv"
    if csv_path.is_file():
        with csv_path.open(newline="", encoding="utf-8") as stream:
            aggregate = {row["label"]: row for row in csv.DictReader(stream)}
    qualified = (assessment.get("profile_qualified") is True
                 and assessment.get("measurement_verified") is True
                 and all(label in aggregate for label in ("Login page", "Products page", "TOTAL")))
    nfr_passes = sum(value == "PASS" for value in assessment.get("verdicts", {}).values()) if qualified else 0

    team = []
    areas = {
        1: ("Login", "FR-01 to FR-04"),
        2: ("Boundaries & access", "FR-05 limited; FR-10"),
        3: ("Products & cart", "FR-06 to FR-09"),
        4: ("Checkout flow", "FR-11/12/13/15/16"),
        5: ("Postal validation", "FR-14"),
    }
    for owner, (area, requirements) in areas.items():
        assigned = {node for node, member in owners.items() if member == owner}
        selected = assigned & set(cases)
        ok = sum(cases[node]["outcome"] == "passed" for node in selected)
        failed_cases = sum(cases[node]["outcome"] == "failed" for node in selected)
        error_cases = sum(cases[node]["outcome"] == "error" for node in selected)
        rest = len(selected) - ok - failed_cases - error_cases
        result = f"{ok} passed"
        if failed_cases:
            result += f" / {failed_cases} failed"
        if error_cases:
            result += f" / {error_cases} errors"
        if rest:
            result += f" / {rest} skipped"
        result = result if selected else "Not in this run"
        if selected and len(selected) < len(assigned):
            result += f" ({len(selected)} of {len(assigned)} ran)"
        team.append(f'<tr><th scope="row">Member {owner}</th><td>{area}<small>{requirements}</small></td>'
                    f'<td>{len(assigned)}</td><td>{result}</td></tr>')
    perf_result = f"{nfr_passes}/3 HTTP NFRs passed" if qualified else "No qualified performance result"
    team.append('<tr><th scope="row">Member 6</th><td>Performance & integration'
                '<small>NFR-01 to NFR-03; framework and evidence</small></td><td>Integration</td>'
                f'<td>{perf_result}<small>Separate recorded load run</small></td></tr>')

    rows = []
    for node, case in sorted(cases.items(), key=lambda pair: (pair[1]["outcome"] not in {"failed", "error"}, pair[0])):
        owner = f"Member {owners[node]}" if node in owners else "Extended"
        title = node.split("::")[-1].removeprefix("test_").replace("_", " ")
        requirements = ", ".join(sorted(case["requirements"])) or "Unmapped"
        evidence = []
        for record in case["records"]:
            if record.get("screenshot"):
                evidence.append(link(root, record["screenshot"], "Screenshot", "text-link"))
            if record.get("failure"):
                evidence.append('<details><summary>Failure details</summary><pre>'
                                + escape(record["failure"]) + '</pre></details>')
        rows.append(f'<tr data-outcome="{case["outcome"]}"><td><strong>{escape(title)}</strong>'
                    f'<small class="node">{escape(node)}</small></td><td>{escape(requirements)}</td>'
                    f'<td>{owner}</td><td>{badge(case["outcome"])}</td><td>{"".join(evidence) or "-"}</td></tr>')
    if not rows:
        rows.append('<tr class="empty"><td colspan="5">No executed results yet. Run START_DEMO.cmd to record the 25-case suite.</td></tr>')

    nfr_cards = []
    nfrs = [
        ("NFR-01", "Login document P95", "Login page", "p95_ms", "ms", "Under 3,000 ms"),
        ("NFR-02", "Products document P95", "Products page", "p95_ms", "ms", "Under 4,000 ms"),
        ("NFR-03", "Overall error rate", "TOTAL", "error_percent", "%", "Under 2%"),
    ]
    for req, label, sampler, key, unit, threshold in nfrs:
        measured = aggregate.get(sampler, {}).get(key)
        value = escape(str(measured)) + (" " if unit == "ms" else "") + unit if measured is not None else "-"
        verdict = assessment.get("verdicts", {}).get(req, "Not recorded") if qualified else "Not qualified"
        css = "passed" if verdict == "PASS" else "failed" if verdict == "FAIL" else "not-run"
        nfr_cards.append(f'<article class="nfr"><div class="nfr-label">{req} / {label}</div>'
                         f'<div class="nfr-value">{value}</div><div class="nfr-bottom">'
                         f'<span>{threshold}</span><span class="badge {css}">{escape(verdict)}</span></div></article>')

    proportions = [passed, failed, errors, counts["skipped"]]
    segments = "".join(f'<span class="{state}" style="width:{100*count/total:.4f}%"></span>'
                       for state, count in zip(("passed", "failed", "error", "skipped"), proportions) if count and total)
    runner_error = summary.get("exit_code", 0) not in (0, 1)
    state = ("Run interrupted or runner error" if runner_error
             else "No execution evidence" if not total else "Review errors" if errors
             else "Requirement failures recorded" if failed
             else "Completed with skipped tests" if counts["skipped"] else "Selected tests passed")
    state_css = ("error" if errors or runner_error else "failed" if failed
                 else "not-run" if not total or counts["skipped"] else "passed")
    elapsed = f"{duration} recorded window" if total else "No tests have been executed"
    marker = "25 core / " + str(core_run) + " recorded"
    if extra_run:
        marker += f" / {extra_run} extended recorded"
    snapshot = (f"{date_label(summary.get('started_utc'))} / {elapsed}. "
                f"Core coverage in this run: {core_run}/25. "
                + (f"{extra_run} extended cases also ran." if extra_run else "No extended cases in this run."))
    if not total and runner_error:
        snapshot = (f"{date_label(summary.get('started_utc'))}. The run ended without test results; "
                    "inspect the test console. Planned assignments are shown below.")
    elif not total:
        snapshot = "No execution results are available. The dashboard shows planned ownership until a run completes."
    values = {
        "%%SCOPE%%": escape(scope), "%%SNAPSHOT%%": escape(snapshot),
        "%%TOTAL%%": str(total) if total else "-", "%%PASSED%%": str(passed) if total else "-",
        "%%FAILED%%": str(failed + errors) if total else "-", "%%RATE%%": pass_rate,
        "%%STATE%%": f'<span class="badge {state_css}">{state}</span>',
        "%%SEGMENTS%%": segments, "%%TEAM%%": "".join(team), "%%CASES%%": "".join(rows),
        "%%RECORDED%%": str(total), "%%CORE%%": escape(marker),
        "%%LEGEND%%": f"{passed} passed / {failed} failed / {errors} errors / {counts['skipped']} skipped",
        "%%REPORT%%": link(root, "dashboard/recording/report.html", "Detailed test report"),
        "%%JMETER%%": link(root, "performance/html_report/index.html", "JMeter dashboard", "text-link"),
        "%%NFRS%%": "".join(nfr_cards),
        "%%PERF_DATE%%": escape(date_label(metadata.get("started_utc"))),
        "%%PERF_PROFILE%%": escape(f"{metadata.get('users', '-')} users / "
                                  f"{metadata.get('ramp_seconds', '-')}s ramp / "
                                  f"{metadata.get('duration_seconds', '-')}s duration"),
        "%%PERF_SAMPLES%%": f"{assessment.get('samples', 0):,}" if assessment else "-",
    }
    html = (root / "dashboard/template.html").read_text(encoding="utf-8")
    for token, value in values.items():
        html = html.replace(token, value)
    if re.search(r"%%[A-Z_]+%%", html):
        raise ValueError("Dashboard template has unresolved fields.")
    output = root / "reports/dashboard.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Dashboard: {output}\nRecorded tests: {total}; passed: {passed}; failed: {failed}; errors: {errors}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", help="Preferred HTML report; linked only when its XML matches this run.")
    args = parser.parse_args()
    build(report_hint=args.report)
