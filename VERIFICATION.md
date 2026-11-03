# Actual verification - 3 November 2026

These are executed results from the live application, not example or fabricated report data.
This document records the historical run. Generated reports, screenshots, logs, JTL files, and
dashboards are excluded from Git; the evidence paths below are local outputs. A fresh clone must
run the suites to produce its own evidence, which may differ from these recorded results.
These functional counts refer to the original 25-case suite. See
[the expanded verification](docs/EXPANDED_VERIFICATION.md) for the later 157-case coverage.
The latest assignment-focused rerun and corrected Products-document JMeter measurement are recorded
in [CASE_STUDY_COMPLIANCE.md](docs/CASE_STUDY_COMPLIANCE.md); the old direct-route results below remain historical evidence.

| Check | Result |
|---|---|
| Smoke suite | 12 passed, 13 deselected; 131.48 seconds |
| Full suite | 22 passed, 3 failed, 0 errors; 231.99 seconds |
| Requirements represented | FR-01 through FR-16 |
| Failed assertions | FR-14: `1234`, `ABCDE`, `12A45` reached Overview |
| Failure screenshots | All three saved as PNG and embedded in HTML |
| JMeter execution | Completed successfully as a tool; NFR assessment returns failure |
| Load | 20 users, 60s ramp, 180s scheduler duration including ramp |
| Observed peak / samples | 20 users / 7,236 samples |
| Login HTTP responses | 3,622 HTTP 200; P95 55ms; NFR-01 PASS |
| Products HTTP responses | 3,614 HTTP 404; error-response P95 60ms; NFR-02 FAIL |
| Overall error rate | 49.9447%; NFR-03 FAIL |
| HTML report verification | Smoke, full suite and JMeter dashboard rendered in Chrome; no console errors |
| Static verification | Python files and PowerShell scripts parsed; JMX XML parsed |
| Dependency setup | scripts/setup.ps1 completed successfully into local .venv |
| Ready-environment visible demo | Order completion passed with headed Chrome / Python 3.13; 20.67 seconds |

Functional execution environment: Windows 11, Python 3.12.6, Chrome/ChromeDriver 156.0.8078.80,
Selenium 4.52.0, PyTest 9.2.0, pytest-html 4.2.0, WebDriver Manager 4.1.2.
Performance: Apache JMeter 5.6.3, Temurin OpenJDK 8u392. The JMeter archive was verified against
Apache's SHA-512 checksum before extraction. The demo launcher's local environment was created by
the installed Python launcher (Python 3.13); portable ZIP setup resolves the user's Python 3.11+.

Full suite ran approximately 21:11-21:15 IST. JMeter ran approximately 21:11-21:14 IST.
JSON metadata stores precise UTC timestamps. These measurements are specific to this machine,
network and application version. Later live results may differ.

The full suite's exit code 1 is expected for these three observed contract discrepancies. JMeter's
process exited 0 because it executed the plan; the Python runner exits 1 because NFRs failed.
Tool completion and requirement acceptance are separate outcomes.

See docs/DEFECTS.md for reproduction steps and performance/Findings.md for interpretation.
The Products HTTP failure measures the direct route and client-side redirect incompatibility;
it is not proof of slow browser rendering. FR-05 has a documented boundary observability limitation.

The portable ZIP intentionally excludes machine-specific virtual environments, driver caches and
tool installations. The source folder on this machine has its local .venv ready. The ZIP's setup
script reconstructs the environment and can download verified JMeter when -WithJMeter is requested.
