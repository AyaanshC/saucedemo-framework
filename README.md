# SauceDemo Automation Framework

A Python test automation framework using Selenium 4, pytest, and the Page Object Model for
[SauceDemo](https://www.saucedemo.com/), built for **Automation Framework Case Study v1.0**.
It contains **157 independent functional cases**: the original **25 cases mapped to FR-01 through
FR-16** and **132 extended app checks**. The visible demo keeps its focused **12-test smoke suite**.
An Apache JMeter HTTP performance plan is also included.

## Assignment scope and case counts

The PDF specifies requirements, not a fixed number of test cases. Its minimum is FR-01, FR-02,
FR-07, FR-12, FR-14, FR-16 plus at least two additional requirements including negative/boundary
coverage. The original 25 cases already exceed that minimum; the other 132 are optional extensions.
Use `-m case_study` to run the original 25-case submission suite with `standard_user` as the valid
shopping account. The 157-case default includes the extended checks. FR-05 has a documented
observability limitation and carries `coverage_limited`; it is not needed to meet the minimum.

See [SUBMISSION.md](SUBMISSION.md) for the hand-in package and
[docs/CASE_STUDY_COMPLIANCE.md](docs/CASE_STUDY_COMPLIANCE.md) for requirement-by-requirement status.

## Features

- Login and advertised account authentication, recovery after errors, keyboard submission, and protected routes.
- All six products, names/prices/descriptions/images, title/image/detail links, and four sorting modes.
- Empty and multi-item carts, removal from inventory/details/cart, quantities, refresh persistence, and reset.
- Checkout validation/recovery, cancellation, line items, subtotal/tax/total, repeat orders, and PDF download integrity.
- Shared menus, footer link destinations, logout, lazy loading, spinner results, and slider controls/auto-advance.
- JSON-driven negative login cases and postal-code equivalence and boundary partitions.
- Reusable page objects, explicit waits, and a fresh Chrome session for every test.
- Self-contained HTML reports, embedded failure screenshots, JUnit XML, logs, and JSON summaries.
- Windows setup and demonstration scripts, plus JMeter execution and NFR assessment.

## Prerequisites

- Python 3.11+ and Google Chrome.
- Internet access for dependency/driver downloads and tests against the live application.
- Windows PowerShell for the supplied setup and demo scripts.
- Java 8+ and Apache JMeter 5.6.3 for the performance suite, which is mandatory for the assignment.

The tests use SauceDemo's publicly documented demo credentials, `standard_user` / `secret_sauce`.

## Get the source

```powershell
git clone https://github.com/AyaanshC/saucedemo-framework.git
cd saucedemo-framework
```

The current expansion and submission corrections are local and have not been committed or pushed.
Use the evidence-inclusive submission ZIP for this exact version; the existing GitHub branch is older.

Generated reports, virtual environments, downloaded drivers, and local tool installations are
excluded from Git. Run the suites below to generate reports on your machine. Historical run
summaries are recorded in [VERIFICATION.md](VERIFICATION.md), [docs/DEFECTS.md](docs/DEFECTS.md),
and [performance/Findings.md](performance/Findings.md); their referenced raw artifacts are local
outputs and are not bundled in Git. The submission ZIP built below includes the required evidence.

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

# Complete suite / all regression tests (157 cases)
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m regression

# Only the 132 added app checks
.\.venv\Scripts\python.exe -m pytest -m extended

# Original 25-case submission suite / proposed additional acceptance rules
.\.venv\Scripts\python.exe -m pytest -m case_study
.\.venv\Scripts\python.exe -m pytest -m proposed_contract

# Broad regression without the three proposed acceptance-rule checks
.\.venv\Scripts\python.exe -m pytest -m "not proposed_contract"

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
that a dedicated length validator exists. The performance plan measures HTTP document responses;
its verified Products SPA bootstrap scope is described below. The original case-study PDF is not included.

The original results above apply to the original 25-case suite. See
[docs/TEST_CASES.md](docs/TEST_CASES.md) for the expanded coverage inventory and
[docs/EXPANDED_VERIFICATION.md](docs/EXPANDED_VERIFICATION.md) for its executed results.

Extended checks use `APP-*` traceability labels rather than inventing case-study requirement IDs.
The catalog in `testdata/products.json`, 8% tax, payment/shipping labels, and external link targets
are reviewable regression baselines observed on 3 November 2026. They are not additional claims
about the original brief. Three `proposed_contract` cases ask whether an empty cart should be blocked
from checkout and whether whitespace-only first/last names should be rejected. These proposed rules
need product-owner agreement; they remain visible in the default run. The whitespace-only postal
case is explicitly FR-14 because a postal code containing only spaces is not numeric.

The PDF case checks that a completed order downloads a nonempty, complete PDF. It does not parse the
receipt's contents. Footer and About URLs are checked without testing third-party websites. Alternate
demo personas are checked for authentication only; the full shopping journey uses `standard_user`.
Dynamic lazy loading intentionally repeats product/size variants, so tests check incremental growth
and retained rows rather than assuming unique names or a finite catalog.

This provides broad functional regression coverage, not exhaustive proof across every input,
browser, screen size, accessibility requirement, backend security condition, or performance profile.

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

The runner checks PATH, JAVA_HOME and common Windows Java installation folders. To select an
installation explicitly, add `--java "C:\path\to\java.exe"`.
Use `--driver-path C:\tools\chromedriver.exe` when a managed driver is required. The runner first
verifies the Products route in a single real Chrome session, closes Chrome, then starts JMeter.

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
| Browser route proof / machine-readable verdicts | `performance/results/route-evidence.json`, `performance/results/assessment.json` |

Existing performance results and dashboard are moved together to `performance/history/<UTC timestamp>/`
before a new run. Threshold violations return exit code 1. A short diagnostic run can be requested with
`--users 1 --ramp 1 --duration 10`, but is explicitly marked **NOT QUALIFIED** for the mandatory NFRs.
`--analyze-only` re-evaluates an existing JTL and its metadata without issuing network requests.

### What the performance measurements mean

JMeter requests `/` for Login and `/?/inventory.html` for the Products SPA bootstrap document,
requiring **HTTP 200 plus the React root marker** for both. Real Chrome authenticates with the
prescribed standard account and verifies that navigating to either `/inventory.html` or its
bootstrap URL loads the HTTP 200 document `/?/inventory.html`, then shows Products with six items
at `/inventory.html`. The route proof and the JTL's actual request URLs are retained with each run.

This corrects the original direct-HTTP 404 measurement. The original results, findings, dashboard,
and `saucedemo_direct_route_diagnostic.jmx` remain available for comparison. HTTP 404 responses are
never relabelled as successful. The measured NFR-02 scope is **Products bootstrap-document HTTP
response time**. It excludes the initial JavaScript redirect hop, authentication, assets and
rendering, so it must not be presented as end-to-end browser readiness. This is the assignment's
basic HTTP page-response interpretation; an evaluator requesting rendered readiness needs a
separate browser-performance measurement, not these HTTP results.

NFRs: Login P95 < 3000ms, Products P95 < 4000ms, overall error rate < 2%.
The CSV assessment uses nearest-rank P95; JMeter's dashboard may use a slightly different percentile
estimator. Run settings and actual observed concurrency are checked before assigning mandatory verdicts.

## Build the evidence-inclusive submission

After functional and performance execution:

```powershell
.\.venv\Scripts\python.exe .\scripts\package_submission.py
```

This creates `dist/saucedemo-case-study-submission.zip` with source, documentation, HTML reports,
screenshots/logs, raw JTL, aggregate CSV, findings, and the entire JMeter dashboard. It includes a
SHA-256 file manifest and validates ZIP integrity. It excludes Git metadata, virtual environments,
driver caches, downloaded tools and local environment files. Git ignore rules do not remove
evidence from this explicit submission package.

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
