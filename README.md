# SauceDemo Automation Framework

A Python test automation framework using Selenium 4, pytest, and the Page Object Model for
[SauceDemo](https://www.saucedemo.com/), built for **Automation Framework Case Study v1.0**.
It contains **25 independent functional tests mapped to FR-01 through FR-16**, including a
12-test smoke suite, plus an Apache JMeter HTTP performance plan.

## Features

- Login, product catalog, cart, logout protection, and checkout coverage.
- JSON-driven negative login cases and postal-code equivalence and boundary partitions.
- Reusable page objects, explicit waits, and a fresh Chrome session for every test.
- Self-contained HTML reports, embedded failure screenshots, JUnit XML, logs, and JSON summaries.
- Windows setup and demonstration scripts, plus JMeter execution and NFR assessment.

## Prerequisites

- Python 3.11+ and Google Chrome.
- Internet access for dependency/driver downloads and tests against the live application.
- Windows PowerShell for the supplied setup and demo scripts.
- Java 8+ and Apache JMeter 5.6.3 for the optional performance suite.

The tests use SauceDemo's publicly documented demo credentials, `standard_user` / `secret_sauce`.

## Get the source

```powershell
git clone https://github.com/AyaanshC/saucedemo-framework.git
cd saucedemo-framework
```

Generated reports, virtual environments, downloaded drivers, and local tool installations are
excluded from Git. Run the suites below to generate reports on your machine. Historical run
summaries are recorded in [VERIFICATION.md](VERIFICATION.md), [docs/DEFECTS.md](docs/DEFECTS.md),
and [performance/Findings.md](performance/Findings.md); their referenced raw artifacts are local
outputs and are not bundled in this repository.

## Quickest demo on Windows

1. Clone this repository or extract its ZIP to a writable folder.
2. Have Python 3.11+ and Google Chrome installed, with internet access.
3. Double-click **START_DEMO.cmd**. It sets up a local `.venv` on first use, shows Chrome running
   the 12 smoke tests at a presentation pace, and opens the HTML report when finished. It pauses
   **2 seconds after each navigation, click, and field entry**, and keeps each test's final screen
   visible for **3 seconds** before closing Chrome. The console remains open.

The smoke subset includes positive and negative flows. The full suite additionally tests invalid
postal codes against the case study's expected behavior. Application defects must appear as failures.
Read **DEMO_GUIDE.md** for the presentation walkthrough and **docs/TEST_DESIGN.md** for the detailed analysis.

## Manual setup

Run this command in PowerShell from the framework folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

No activation is required; every command calls the virtual environment directly.
`requirements.txt` pins the four primary tools. `requirements-lock.txt` records every package version
used for the recorded verification run on Windows/Python 3.12. Use it for a matching environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

ChromeDriver is downloaded once by WebDriver Manager to the local `.wdm` cache and reused.
If downloads are blocked, provide a ChromeDriver matching your installed Chrome:

```powershell
.\.venv\Scripts\python.exe -m pytest --driver-path C:\tools\chromedriver.exe
```

## Functional execution

```powershell
# Visible Chrome, smoke suite, report opens automatically
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1

# Slower presentation, with more time to explain each step
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1 -StepDelay 3 -EndPause 5

# Visible demo at full speed
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1 -StepDelay 0 -EndPause 0

# Headless smoke suite
.\.venv\Scripts\python.exe -m pytest -m smoke --html=reports/smoke.html --junitxml=reports/smoke-junit.xml

# Complete suite / all regression tests (same 25 tests)
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m regression

# Full visible demo, report opens automatically
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1 -Suite full

# Isolate the case-study postal-code contract
.\.venv\Scripts\python.exe -m pytest tests/test_checkout.py -k postal_code_contract --headed

# Present a single order flow slowly
.\.venv\Scripts\python.exe -m pytest tests/test_checkout.py::test_finish_order --headed --slow-mo 2 --end-pause 3
```

Default is headless unless `--headed` is provided. Each test gets a fresh Chrome session so tests
do not depend on execution order. Synchronization uses explicit waits. The optional presentation
pauses help viewers follow actions; they do not replace readiness checks. Direct pytest runs have
no presentation delay by default, and headless execution ignores presentation pauses. Delay values
must be finite, non-negative seconds. Slower presentation runs take longer to complete.
Exit code 0 means the selected tests passed; 1 means assertions failed; setup errors appear as errors.
The expected live-site contract discrepancies are documented in **docs/DEFECTS.md** after verification.

## Reports and evidence

| Path | Purpose |
|---|---|
| `reports/smoke.html` | Generated self-contained smoke report |
| `reports/functional.html` | Full-suite report with embedded failure screenshots |
| `reports/screenshots/*.png` | Original failure evidence |
| `reports/logs/execution.log` | Latest execution: test name, step, status |
| `reports/junit.xml` | Machine-readable full-suite results |
| `reports/run-summary.json` | Latest outcomes, requirement IDs, durations and evidence paths |
| `VERIFICATION.md` | Recorded historical run summary and environment |

Open HTML files in Chrome. Reports are regenerated on each run; copy them first if you want to
preserve your own run. Failed tests are never automatically retried, skipped, or marked xfail.

## Recorded results and known limitations

The recorded run on **3 November 2026** produced **12 smoke passes** and **22 passes / 3 failures**
in the full suite. The three failures check the case-study FR-14 contract: postal codes `1234`,
`ABCDE`, and `12A45` were accepted by the application instead of rejected. These assertions remain
active. See [the defect notes](docs/DEFECTS.md) for reproduction steps; later live results may differ.

The FR-05 username-length tests use unknown accounts, so generic login rejection alone cannot prove
that a dedicated length validator exists. The performance plan measures direct HTTP responses;
its Products-route limitation is described below. The original case-study PDF is not included.

## Performance: JMeter 5.6.3

Install Java 8+ on PATH and install JMeter locally using the SHA-512-verified setup:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithJMeter
.\.venv\Scripts\python.exe .\scripts\run_performance.py
```

Or use an existing installation:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_performance.py --jmeter-home C:\tools\apache-jmeter-5.6.3
```

The default profile is **20 users, 60-second ramp, 180-second duration including ramp**, with
250-500ms random think time before each request. The script uses JMeter CLI, not its GUI.
It creates the actual JTL, aggregate CSV, full JMeter dashboard, and a threshold assessment:

| Artifact | Location |
|---|---|
| Test plan | `performance/jmx/saucedemo_weekend_lab.jmx` |
| Raw samples | `performance/results/results.jtl` |
| Aggregate export | `performance/results/aggregate.csv` |
| Dashboard | `performance/html_report/index.html` |
| NFR verdicts | `performance/Findings.md` |
| Run parameters / JMeter log | `performance/results/` |

Existing performance results and dashboard are moved together to `performance/history/<UTC timestamp>/`
before a new run. Threshold violations return exit code 1. A short diagnostic run can be requested with
`--users 1 --ramp 1 --duration 10`, but is explicitly marked **NOT QUALIFIED** for the mandatory NFRs.
`--analyze-only` re-evaluates an existing JTL and its metadata without issuing network requests.

### What the performance measurements mean

JMeter requests `/` and `/inventory.html` and checks HTTP 200 plus the React root marker. SauceDemo
renders in JavaScript; in the recorded run its inventory URL returned HTTP 404 containing a JavaScript
SPA redirect. JMeter does not execute that JavaScript or authenticate through the UI. Thus this plan
measures the Products URL's direct HTTP response, which currently fails its success assertion.
It does not measure authenticated rendered-product readiness. This limitation is included
in the findings; authenticated business flows are verified by Selenium.

NFRs: Login P95 < 3000ms, Products P95 < 4000ms, overall error rate < 2%.
The CSV assessment uses nearest-rank P95; JMeter's dashboard may use a slightly different percentile
estimator. Run settings and actual observed concurrency are checked before assigning mandatory verdicts.

## Framework structure

```text
pages/                 Page locators, explicit waits and reusable actions
tests/                 Assertions, smoke/regression markers, requirement IDs
testdata/              JSON-driven login and postal-code partitions
conftest.py            Chrome fixtures, evidence capture, execution logging
scripts/               Setup, visible demo launcher, JMeter runner/analysis
docs/                  Test design, requirement traceability, verified defects
reports/               Generated functional results and screenshots (ignored by Git)
performance/           JMX, NFR findings, and generated performance outputs
```

## Troubleshooting

- **Python missing:** install Python 3.11+ and enable PATH; then rerun setup.
- **PowerShell policy:** the commands above use a process-scoped bypass; system policy is not changed.
- **Driver or package download fails:** check internet/proxy settings. Use `--driver-path` for a managed driver.
  Keep certificate verification enabled.
- **Chrome changes version:** WebDriver Manager resolves a compatible driver on the next run.
- **Java missing:** `java -version` must succeed, or supply `--java C:\path\to\java.exe`.
- **Postal-code failures:** inspect `docs/DEFECTS.md` and screenshots; these are contract checks against
  the specified requirements, not a reason to weaken the assertions.

## References

- Source brief: Automation Framework Case Study v1.0, supplied PDF, sections 1-8.
- Selenium documentation: https://www.selenium.dev/documentation/webdriver/
- JMeter CLI and dashboard: https://jmeter.apache.org/usermanual/get-started.html
- Target application: https://www.saucedemo.com/
