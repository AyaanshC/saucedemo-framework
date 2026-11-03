# Presenting the working demo

Allow about 8-10 minutes plus first-time downloads. Generate reports before presenting a Git clone;
the repository excludes generated HTML, screenshots, logs, raw results, and dashboards.
Internet, Chrome and Python are required for a fresh functional run; Java and JMeter for performance.

## 1. Explain the problem (one minute)

"This framework verifies SauceDemo login, product/cart behavior and checkout against FR-01 to FR-16.
It also runs the required basic HTTP performance test. Assertions follow the written requirements,
so a report can expose a product defect even when the framework itself is working."

Show `docs/TEST_DESIGN.md`: highlight the postal-code EP/BVA table and the traceability matrix.

## 2. Show the framework (one minute)

Open `pages/checkout_page.py`, `tests/test_checkout.py` and `testdata/postal_cases.json`.

"Page objects hold reusable UI actions and locators. Tests hold the expected behavior. JSON holds
the input partitions, so adding another data row creates another case without copying the test.
Explicit waits synchronize with page state. Every case starts with a clean browser."

## 3. Run the visible smoke demo (roughly two minutes)

Double-click `START_DEMO.cmd`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\demo.ps1
```

Chrome opens repeatedly because each test is independent. Explain the console's test names and step
logs while login, validation, cart and checkout flows run. The report opens at the end.
Highlight the passing order flow, invalid-password rejection, and required first-name validation.

## 4. Demonstrate finding a real requirement mismatch (one minute)

After running the full suite, open `reports/functional.html`, filter to failed tests and expand a postal-code failure.
Show the embedded screenshot and assertion with expected `error` versus actual `overview`.
Show the original image under `reports/screenshots/` and read `docs/DEFECTS.md`.

For a fresh focused run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_checkout.py -k postal_code_contract --headed
```

"The brief says four digits and non-numeric postal codes must be rejected. A transition to Overview
is evidence of an application/requirement mismatch. We keep that assertion failing and preserve
the evidence rather than changing the expected behavior."

If the AUT is fixed later, those cases should pass. Describe the current live result honestly.

## 5. Explain performance (one minute to inspect, three minutes to rerun)

Open `performance/Findings.md`, `performance/results/aggregate.csv`, and
`performance/html_report/index.html`. Show P95, errors, observed peak users and actual run profile.
Open the JMX in JMeter if you want to show the 20-user/60-second/180-second settings visually.

For a fresh run after JMeter setup:

```powershell
.\.venv\Scripts\python.exe scripts\run_performance.py
```

"This measures HTTP document response times. SauceDemo renders its UI in JavaScript, so these
requests do not measure browser rendering or authenticated checkout. The findings state that scope
explicitly. The Selenium tests provide the authenticated functional evidence."

## 6. Answer likely review questions

- **Why a failing full suite?** It tests the written contract and records application discrepancies.
- **Why is smoke green?** It selects core flows and supported input cases; regression adds invalid
  boundary partitions. Smoke alone is not the full FR-14 acceptance decision.
- **Where is data-driven execution?** Login negatives and postal partitions are JSON-parametrized.
- **Where are failure evidence and logs?** `reports/screenshots/`, embedded HTML images and `reports/logs/`.
- **How do you prove the 30-character username limit?** We test 29/30/31 rejection, but unknown accounts
  cannot prove a dedicated length validator. That is explicitly documented as a coverage limitation.
- **Can another machine reproduce it?** Clone or extract, run setup, then use the commands in README.md.

For presentation, keep README.md, the reports and this guide open before starting.
