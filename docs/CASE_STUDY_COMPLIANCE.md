# Case-study compliance and submission scope

Evidence links download the recorded files from the v1.0.0 release. For offline viewing, extract
the complete submission ZIP and open the corresponding files under `reports/` or
`performance/results/`; keep the dashboard folder intact.

This maps the supplied Automation Framework Case Study v1.0 (five-page PDF) to the local code and
evidence. It distinguishes implemented automation, observed app discrepancies, and limitations.

| PDF section | Requirement | Implementation / evidence | Status |
|---|---|---|---|
| 1 | SauceDemo and prescribed valid account | `login`, `inventory`, and `checkout` fixtures; `standard_user` / `secret_sauce` | Implemented for case-study suite |
| 2 | Equivalence partitioning and boundary analysis | `docs/TEST_DESIGN.md`, login JSON, postal JSON, 29/30/31 username values | Implemented; FR-05 limitation below |
| 3 | Windows, Chrome, Python 3.11+, specified free tools | `requirements.txt`, setup scripts, Chrome fixtures, JMeter 5.6.3 | Implemented |
| 3 | Sleeps only with explicit justification | Comments at both presentation sleeps; delays default to zero in direct pytest, ignored headless | Implemented |
| 4–5 | FR-01, FR-02, FR-07, FR-12, FR-14, FR-16 | Original tests selected by `case_study`; requirement markers and traceability table | Automated; FR-14 app discrepancies remain visible |
| 5 | At least two additional FRs including negative/boundary coverage | FR-03/04 negative login, FR-08/09 cart, FR-10 logout access, FR-11/13/15 checkout, plus limited FR-05 | Exceeds minimum |
| 6.1 | 20 users, 60s ramp, 180s duration | Parameterized JMX; runner checks actual peak, sample window, metadata and exit status | See latest verified results below |
| 6.2 | NFR-01/02/03 thresholds | Nearest-rank P95, exact error counts, machine-readable `assessment.json`, Findings | See latest measured verdicts below |
| 6.3 | Named JMX, JTL, CSV and complete HTML dashboard | `performance/jmx/saucedemo_weekend_lab.jmx`, `results/`, `html_report/` | Included in submission ZIP |
| 6.3 | NFR findings | `performance/Findings.md`, source metadata and route proof | Included in submission ZIP |
| 7.1 | POM, explicit waits, two data-driven test families | `pages/`, WebDriverWait, `testdata/login_cases.json`, `postal_cases.json` | Implemented |
| 7.1 | Smoke/regression selection | `pytest.ini`; default case-study 25, optional smoke 12, explicit regression 157 | Implemented |
| 7.1 | Failure PNGs, file logs, HTML reports | `conftest.py`, `reports/screenshots/`, `reports/logs/`, self-contained HTML | Executed evidence included |
| 7.1 | Reproducible README smoke/full instructions | `README.md`, `SUBMISSION.md`, setup/demo/package scripts | Implemented; portable ZIP checked |
| 8 | Framework demonstration | `START_DEMO.cmd`, `scripts/demo.ps1`, `DEMO_GUIDE.md`, recorded headed checks | Ready for the student's presentation |

## Case counts and account scope

The PDF defines a minimum of **eight distinct FRs**, not eight cases or 157 cases. The original
25 cases represent FR-01–FR-16 and include the mandatory six plus multiple additional FRs. The
132 optional extended cases bring the total to 157. The default run and launcher select the original
25. Use `-m regression` for all 157. The [six-person plan](TEAM_ASSIGNMENTS.md) assigns all original
cases plus required framework, performance, evidence and demo work. For the original scope,
use `-m case_study`; alternate valid personas and proposed acceptance rules remain in `extended`.

## Explicit FR-05 limitation

The three `coverage_limited` cases use unregistered usernames of 29, 30 and 31 characters and
observe rejection. They cannot distinguish length validation from unknown-account rejection.
No valid 30-character account or isolated validator is provided by the brief. Do not claim that
the dedicated length validator is proved. Mandatory coverage does not rely on FR-05; multiple
other additional FRs satisfy section 5. This is an external testability limit, not a fabricated pass.

## Products performance definition

The direct HTTP route `/inventory.html` returns a JavaScript SPA redirect document with HTTP 404.
Real Chrome using the prescribed account verifies that the actual HTTP 200 navigation document
is `/?/inventory.html`, and that it displays Products with six items at `/inventory.html`.
The current JMeter plan samples this verified document and requires HTTP 200 plus the app root.
The runner verifies the route before load and checks the actual URLs saved in the JTL.

NFR-02 is assessed as **Products SPA bootstrap-document HTTP response time**, consistent with the
brief's basic page-response interpretation. It is not a rendered-product readiness measurement,
does not include the initial 404 hop, and does not authenticate JMeter HTTP requests. If the
evaluator specifically requires browser-rendered readiness, that is a separate measurement and
these document timings must not be represented as such. Original 404 results are retained in history.

## Current failure classification

The 157-case evidence records 150 passes and 7 failures: four FR-14 variants (four digits,
alphabetic, mixed, whitespace-only postal input), plus three proposed rules (empty cart and
whitespace-only first/last names). The whitespace-postal marker was corrected after reviewing
the PDF; behavior and case count did not change. The original 25-case run contains only the first
three FR-14 discrepancies. See `DEFECTS.md` for reproduction and `EXPANDED_VERIFICATION.md` for history.

## Latest verification

Actual executed results from this local session:

| Check | Result | Evidence |
|---|---|---|
| Original assignment suite | 25 executed; 22 passed, 3 FR-14 assertion failures; 0 errors | [HTML](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/case-study.html), [JUnit](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/case-study-junit.xml) |
| Whitespace classification recheck | 3 reproduced failures; postal is FR-14, first/last are proposed | [HTML](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/classification-check.html), [coverage map](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/coverage-map.json) |
| Scope counts | 157 total = 25 original + 132 extended; smoke 12, proposed 3, limited 3 | [Actual collection](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/coverage-map.json) |
| JMeter mandatory profile | 20 users; 60s ramp; 180s duration; observed peak 20; 6715 samples; 179.51s sample window | [Metadata](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/run-metadata.json), [raw JTL](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/results.jtl) |
| NFR-01 | PASS: Login document P95 228 ms < 3000 ms | [Findings](../performance/Findings.md) |
| NFR-02 | PASS: verified Products bootstrap-document P95 223 ms < 4000 ms | [Route proof](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/route-evidence.json), [Findings](../performance/Findings.md) |
| NFR-03 | PASS: 0.9978% overall errors < 2% | [Assessment](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/assessment.json) |
| Diagnostic qualification control | 1-user/10s run correctly NOT QUALIFIED; its evidence is preserved in history | `performance/history/` |
| Measurement guard controls | Temporary copies with missing route proof or Products replaced by Login are rejected as NOT QUALIFIED | Analyzer control checks; production results unchanged |
| Default Java discovery | Finds installed Temurin Java 8 without modifying PATH | `resolve_java` helper verified |
| Dashboard visual check | Both sampler rows render; zero severe browser-console errors | [Preview](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/submission-dashboard-preview.png), [validation](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/dashboard-validation.json) |
| Source checks | Python parses; PowerShell setup parses; Git whitespace check passes | Source validation |

The mandatory run retained all **67 connection-reset errors** (62 SSL exceptions and 5 socket
exceptions) in the raw JTL and error-rate calculation. There were no HTTP 404 samples in the new
load run. Errors were not removed or retried to produce a passing rate. The measured error rate
is below the specified 2% threshold. P95 uses nearest rank; the dashboard's percentile estimator
has slightly different displayed decimals.

The core functional failures remain active because the application accepts postal inputs that
contradict FR-14. The framework and submission do not claim the external application is defect-free.
Latest extended-suite history is recorded separately in `EXPANDED_VERIFICATION.md`.

The package script validates required evidence, ZIP integrity and source/evidence hashes. An
extracted-copy collection check verifies portability of the test layout. Local tools/environments
are excluded and must be reconstructed using setup on the recipient's machine. Packaging and
verification do not invoke Git publication; the manifest identifies the exact working files included.
The actual class/demo presentation remains the student's step.
