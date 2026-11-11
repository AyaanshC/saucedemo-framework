# Case-study scope and six-person work plan

## Selected scope

Keep the **25 original functional cases** as the main assignment suite. Both plain `pytest`
and `START_DEMO.cmd` now select these cases. The launcher shows Chrome with 2-second action
pauses and a 3-second pause before closing each test's browser.

The brief's section 5 requires FR-01, FR-02, FR-07, FR-12, FR-14 and FR-16, plus at least two
additional FRs including negative/boundary coverage. It does not prescribe 25 tests. This plan
retains the original 25 to cover the listed FR areas without adding the optional app features.
Parameterized data rows count as separate cases. FR-05 remains a limited observation, as below.

The 132 extended checks remain available with `-m extended`, and all 157 with `-m regression`.
Sorting, alternate-account login, dynamic catalogs, receipt downloads and proposed acceptance
rules are optional extension work. They are outside this team's main assignment scope.

## Ownership

Replace Member 1 through Member 6 with the actual team names. This is a proposed allocation of
review, maintenance, evidence and presentation work; it is not a claim about who authored the
existing code. Five people own the 25 functional cases. The sixth owns mandatory JMeter work
and framework integration, which has substantial work beyond functional test counts.

| Member | Area | Unique functional cases | Requirements | Main deliverables |
|---|---|---:|---|---|
| 1 | Login success and input partitions | 5 | FR-01 to FR-04 | Login tests, login JSON, EP table and login evidence |
| 2 | Username boundaries and logout protection | 5 | FR-05, FR-10 | Boundary/security checks, BVA explanation and FR-05 limitation |
| 3 | Products and cart | 4 | FR-06 to FR-09 | Inventory/cart checks, page actions and matching product evidence |
| 4 | Checkout navigation, names and completion | 5 | FR-11 to FR-13, FR-15, FR-16 | Checkout flow, required-name validation, overview and success evidence |
| 5 | Postal-code acceptance and rejection | 6 | FR-14 | Postal JSON, EP/BVA table, invalid-input failures and defect reproduction |
| 6 | Performance, reporting and integration | 0 additional | NFR-01 to NFR-03; engineering requirements | JMeter execution, POM/wait review, screenshots/logs/HTML, README, package and final demo coordination |
| **Total** | | **25** | **All original FR areas represented** | **Plus required performance and framework work** |

## Exact functional cases

Each row below belongs to one member only. Paths are relative to the repository root.

| # | Member | Pytest node ID | Expected result |
|---:|---:|---|---|
| 1 | 1 | `tests/test_login.py::test_successful_login` | Standard account opens Products |
| 2 | 1 | `tests/test_login.py::test_rejected_login[invalid-password]` | Error; remains on Login |
| 3 | 1 | `tests/test_login.py::test_rejected_login[blank-username]` | Username-required error |
| 4 | 1 | `tests/test_login.py::test_rejected_login[blank-password]` | Password-required error |
| 5 | 1 | `tests/test_login.py::test_rejected_login[both-blank]` | Username-required error |
| 6 | 2 | `tests/test_login.py::test_username_length_boundary[below-30]` | Unknown 29-character username rejected; limited observation |
| 7 | 2 | `tests/test_login.py::test_username_length_boundary[at-30]` | Unknown 30-character username rejected; limited observation |
| 8 | 2 | `tests/test_login.py::test_username_length_boundary[above-30]` | Unknown 31-character username rejected; limited observation |
| 9 | 2 | `tests/test_inventory_cart.py::test_protected_page_after_logout[/inventory.html]` | Redirects to Login |
| 10 | 2 | `tests/test_inventory_cart.py::test_protected_page_after_logout[/cart.html]` | Redirects to Login |
| 11 | 3 | `tests/test_inventory_cart.py::test_product_catalog` | At least six named, priced, addable products |
| 12 | 3 | `tests/test_inventory_cart.py::test_add_to_cart` | Badge increments; buttons become Remove |
| 13 | 3 | `tests/test_inventory_cart.py::test_remove_from_cart` | Badge decrements; buttons become Add to cart |
| 14 | 3 | `tests/test_inventory_cart.py::test_cart_details_match_products` | Cart names/prices match inventory |
| 15 | 4 | `tests/test_checkout.py::test_checkout_navigation` | Checkout information page opens |
| 16 | 4 | `tests/test_checkout.py::test_mandatory_information[missing-first-name]` | First-name error; stays on information page |
| 17 | 4 | `tests/test_checkout.py::test_mandatory_information[missing-last-name]` | Last-name error; stays on information page |
| 18 | 4 | `tests/test_checkout.py::test_checkout_overview` | Valid information opens Overview |
| 19 | 4 | `tests/test_checkout.py::test_finish_order` | Finish shows order-success message |
| 20 | 5 | `tests/test_checkout.py::test_mandatory_information[missing-postal]` | Postal-required error; stays on information page |
| 21 | 5 | `tests/test_checkout.py::test_postal_code_contract[four-digits-invalid]` | Reject 1234 |
| 22 | 5 | `tests/test_checkout.py::test_postal_code_contract[five-digits-valid]` | Accept 12345; opens Overview |
| 23 | 5 | `tests/test_checkout.py::test_postal_code_contract[six-digits-valid]` | Accept 123456; opens Overview |
| 24 | 5 | `tests/test_checkout.py::test_postal_code_contract[alphabetic-invalid]` | Reject ABCDE |
| 25 | 5 | `tests/test_checkout.py::test_postal_code_contract[mixed-invalid]` | Reject 12A45 |

FR-05's synthetic accounts are all unknown, so rejection cannot establish an isolated username
length validator. Keep the `coverage_limited` tag and explain this when presenting. Other additional
FRs meet the brief's minimum independently of FR-05.

The previous 25-case execution recorded 22 passes and three FR-14 failures: the site accepted
1234, ABCDE and 12A45. These assertions stay active. Do not mark them as expected failures or
change the expected outcomes to make the report green. A new live run may differ.

## Individual run commands

Run setup once from the repository root. Each member's command saves separate HTML, XML and logs.
Add `--headed --slow-mo 2 --end-pause 3` to a pytest command for a paced visible demonstration.
The default `case_study` marker also applies to the commands below.

Member 1 (5 cases):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_login.py -k "not username_length_boundary" --html=reports/member-1.html --junitxml=reports/member-1.xml -o log_file=reports/logs/member-1.log
```

Member 2 (5 cases):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_login.py::test_username_length_boundary tests/test_inventory_cart.py::test_protected_page_after_logout --html=reports/member-2.html --junitxml=reports/member-2.xml -o log_file=reports/logs/member-2.log
```

Member 3 (4 cases):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_inventory_cart.py -k "not protected_page_after_logout" --html=reports/member-3.html --junitxml=reports/member-3.xml -o log_file=reports/logs/member-3.log
```

Member 4 (5 cases):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_checkout.py -k "checkout_navigation or missing-first-name or missing-last-name or checkout_overview or finish_order" --html=reports/member-4.html --junitxml=reports/member-4.xml -o log_file=reports/logs/member-4.log
```

Member 5 (6 cases):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_checkout.py -k postal --html=reports/member-5.html --junitxml=reports/member-5.xml -o log_file=reports/logs/member-5.log
```

Member 6 (performance and final integrated evidence):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -WithJMeter
.\.venv\Scripts\python.exe -m pytest -m case_study --html=reports/case-study.html --junitxml=reports/case-study-junit.xml -o log_file=reports/logs/case-study.log
.\.venv\Scripts\python.exe scripts\collect_coverage.py
.\.venv\Scripts\python.exe scripts\run_performance.py
.\.venv\Scripts\python.exe scripts\package_submission.py
```

The integration run repeats the same 25 cases for a combined report; it does not add new cases.
Review the pytest results even when the exit code is 1: retained application defects must be
explained with evidence. Check each tool's output and required artifacts before packaging.

Member 6 must use 20 users, a 60-second ramp and a 180-second duration; compare Login P95 < 3s,
Products P95 < 4s and overall errors < 2%. Retain the named JMX, raw JTL, aggregate CSV, full HTML
dashboard and `performance/Findings.md`. Explain that the current Products measurement is the
verified HTTP bootstrap document, not browser rendering or an authenticated JMeter transaction.

## Integration and presentation

- Members 1-5 explain their requirement IDs, expected results, EP/BVA choices and evidence.
- Coordinate function-level changes where members share a module: Members 1/2 share login,
  2/3 share inventory/cart, and 4/5 share checkout. Coordinate shared page-object edits with Member 6.
- Member 6 reviews POM separation and explicit waits, both JSON-driven families, smoke/regression
  selection, failure screenshots, test/step/status logs and HTML reports. Every owner reviews their
  own assertions and leaves unexpected failures visible.
- Use `START_DEMO.cmd` for the full 25-case presentation. The shorter smoke demo is explicitly
  selected with `scripts/demo.ps1 -Suite smoke`; all 157 use `-Suite full`.
- Package source and required evidence after integration. Optional expanded history may remain
  in the package; it is not part of the 25 assigned functional cases.

## Verification of this allocation

The five individual commands were collected and matched to the case table: **5 + 5 + 4 + 5 + 6 = 25**,
with no omitted or duplicated cases. Default selection collects 25; smoke selects 12; extended
selects 132; full regression selects 157. The launcher's three suite selections and default
presentation arguments were also checked.

A fresh default headless run executed **25 cases: 22 passed, 3 failed, 0 errors**, with 132 optional
cases deselected, in 174.82 seconds. Only the three existing FR-14 postal-code discrepancies failed;
all three have failure screenshots. All FR-01 through FR-16 markers are represented, subject to
the FR-05 observation limit above. This was a functional rerun; performance was not rerun for
the selection/ownership changes.

Local evidence (also included in the rebuilt submission ZIP):

- `reports/team-scope-verification.json`: scope counts and exact assignment matching.
- `reports/team-core-check.html` and `reports/team-core-check.xml`: fresh functional results.
- `reports/logs/team-core-check.log` and `reports/screenshots/`: execution and failure evidence.

These new artifacts are local outputs; the earlier GitHub release does not include this update.
