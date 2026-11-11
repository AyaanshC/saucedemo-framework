# Presenting the working demo

Allow extra presentation time for the pauses between actions, plus first-time downloads. Generate reports before presenting a Git clone;
the repository excludes generated HTML, screenshots, logs, raw results, and dashboards.
Internet, Chrome and Python are required for a fresh functional run; Java and JMeter for performance.

## 1. Explain the problem (one minute)

"This framework verifies SauceDemo login, product/cart behavior and checkout against FR-01 to FR-16.
The original 25 cases are supplemented by 132 app checks for product details, sorting, cart and
checkout behavior, navigation, dynamic catalogs, and PDF downloading. The default demo runs the
original 25 cases; the optional smoke subset has 12. The six-person assignments are in
`docs/TEAM_ASSIGNMENTS.md`.
It also runs the required basic HTTP performance test. Assertions follow the written requirements,
so a report can expose a product defect even when the framework itself is working."

Show `docs/TEST_DESIGN.md`: highlight the postal-code EP/BVA table and the traceability matrix.

## 2. Show the framework (one minute)

Open `pages/checkout_page.py`, `tests/test_checkout.py` and `testdata/postal_cases.json`.

"Page objects hold reusable UI actions and locators. Tests hold the expected behavior. JSON holds
the input partitions, so adding another data row creates another case without copying the test.
Explicit waits synchronize with page state. Every case starts with a clean browser."

## 3. Run the visible case-study demo

Double-click `START_DEMO.cmd`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\demo.ps1
```

All 25 original cases run. For the shorter 12-case subset, add `-Suite smoke`.
Chrome opens repeatedly because each test is independent. Explain the console's test names and step
logs while login, validation, cart and checkout flows run. The dashboard opens at the end.
The default demo pauses 2 seconds after each navigation, click, and field entry, and 3 seconds on
each final screen before closing that test's browser. To give yourself more explanation time, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\demo.ps1 -StepDelay 3 -EndPause 5
```

Use `-StepDelay 0 -EndPause 0` for a full-speed visible demo. Direct pytest runs remain full speed
unless `--headed --slow-mo 2 --end-pause 3` is supplied; headless runs ignore the presentation pauses.
Highlight the passing order flow, invalid-password rejection, and required first-name validation.

## 4. Demonstrate finding a real requirement mismatch (one minute)

After running the default demo, open `reports/case-study.html`, filter to failed tests and expand a postal-code failure.
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

- **Why a failing full suite?** It records written-contract discrepancies and separately tagged proposed acceptance gaps.
- **Why is smoke green?** It selects core flows and supported input cases; regression adds invalid
  boundary partitions. Smoke alone is not the full FR-14 acceptance decision.
- **Where is data-driven execution?** Login negatives and postal partitions are JSON-parametrized.
- **Where are failure evidence and logs?** `reports/screenshots/`, embedded HTML images and `reports/logs/`.
- **How do you prove the 30-character username limit?** We test 29/30/31 rejection, but unknown accounts
  cannot prove a dedicated length validator. That is explicitly documented as a coverage limitation.
- **Can another machine reproduce it?** Clone or extract, run setup, then use the commands in README.md.

For presentation, keep README.md, the reports and this guide open before starting.
Use OPEN_DASHBOARD.cmd to rebuild and open the latest recorded snapshot without rerunning tests.
Use its **Failed / errors** filter to inspect failures, or **Detailed test report** for full output.
Point out that the default demo runs exactly 25 cases; the additional 132 are optional.
The dashboard dates functional and performance evidence separately.

## 7. Demonstrate the expanded coverage

Use `docs/TEST_CASES.md` to explain the added checks and their limits. To run one area visibly:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_products.py -m extended --headed --slow-mo 2 --end-pause 3
.\.venv\Scripts\python.exe -m pytest tests/test_dynamic_catalog.py -m extended --headed --slow-mo 2 --end-pause 3
```

For the full expanded headless run use `-m extended`. The three `proposed_contract` cases are proposed
acceptance rules beyond the original brief. Whitespace postal rejection is FR-14. For the original
25-case assignment run use `-m case_study`; the PDF does not require all 157 cases.
