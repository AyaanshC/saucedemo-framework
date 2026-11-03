# Case study analysis and test design

## What the assignment asks for

This is a framework demonstration, not a single end-to-end script. The deliverable must separate
page actions from assertions, handle asynchronous UI state, use external test data for at least two
tests, select smoke versus regression runs, capture failures, log execution, and produce reports.
The minimum functional set is FR-01, FR-02, FR-07, FR-12, FR-14 and FR-16 plus two additional
requirements including a negative/boundary case. This implementation covers all 16 FRs in 25 cases.

## Equivalence partitioning (EP)

| Input | Partition | Representative | Expected |
|---|---|---|---|
| Login credentials | Known valid account | standard_user / secret_sauce | Products |
| Password | Nonempty invalid | wrong_password | Error, stays on Login |
| Username | Empty | empty string | Username required |
| Password | Empty | empty string | Password required |
| First name | Empty vs nonempty | empty / Demo | Error vs proceed if other fields valid |
| Last name | Empty vs nonempty | empty / Tester | Error vs proceed if other fields valid |
| Postal | Valid numeric | 12345, 123456 | Overview |
| Postal | Too short numeric | 1234 | Error under FR-14 |
| Postal | Alphabetic | ABCDE | Error under FR-14 |
| Postal | Mixed | 12A45 | Error under FR-14 |
| Postal | Empty | empty string | Required-field error |

Login rejection is driven by `testdata/login_cases.json`; postal acceptance/rejection by
`testdata/postal_cases.json`. These are two separate data-driven test families.

## Boundary value analysis (BVA)

- **FR-05:** 29, 30 and 31 characters around the stated 30-character boundary. All synthetic usernames
  are unregistered and expected to be rejected. A rejection above 30 satisfies the observable negative
  outcome, but the generic credentials error cannot distinguish length validation from authentication.
  A valid 30-character account or an isolated validator would be needed to prove the exact length rule.
- **FR-14:** 4, 5 and 6 digits implement exactly the requested boundary values: invalid, valid, valid.
  The brief does not specify whether 7 digits are valid, so no unsupported 6-digit maximum is invented.
  Alphabetic and mixed values cover the invalid non-numeric partition.
- **FR-08:** badge transitions 2 -> 1 -> 0 verify decrement and the absent zero badge.

## Traceability

Paths below are relative to `tests/`. Every test also carries a machine-readable requirement marker.

| Requirement | Automated test(s) | Expected observation |
|---|---|---|
| FR-01 | test_login.py::test_successful_login | Products title and inventory URL |
| FR-02 | test_login.py::test_rejected_login[invalid-password] | Credentials error; Login remains |
| FR-03 | test_login.py::test_rejected_login[blank-username], [both-blank] | Username required |
| FR-04 | test_login.py::test_rejected_login[blank-password] | Password required |
| FR-05 | test_login.py::test_username_length_boundary (29/30/31) | Login rejects synthetic unknown usernames; limitation above |
| FR-06 | test_inventory_cart.py::test_product_catalog | At least six named, priced, addable products |
| FR-07 | test_inventory_cart.py::test_add_to_cart | Badge 0 -> 1 -> 2; Remove buttons |
| FR-08 | test_inventory_cart.py::test_remove_from_cart | Badge 2 -> 1 -> 0; Add to cart buttons |
| FR-09 | test_inventory_cart.py::test_cart_details_match_products | Two product names and prices match |
| FR-10 | test_inventory_cart.py::test_protected_page_after_logout (two URLs) | Redirect to Login |
| FR-11 | test_checkout.py::test_checkout_navigation | Checkout: Your Information |
| FR-12 | test_checkout.py::test_mandatory_information[missing-first-name] | First Name required; same page |
| FR-13 | test_checkout.py::test_mandatory_information[missing-last-name] | Last Name required; same page |
| FR-14 | test_checkout.py::test_postal_code_contract (five data rows), test_mandatory_information[missing-postal] | BVA/EP acceptance and rejection |
| FR-15 | test_checkout.py::test_checkout_overview | Valid data opens Overview |
| FR-16 | test_checkout.py::test_finish_order | Completion URL and thank-you message |

## Engineering decisions

- A new browser per case isolates cookies, storage and cart state.
- One WebDriver Manager resolution per session avoids repeated driver downloads.
- Page objects own selectors/actions; tests own business assertions.
- Explicit waits observe the required page or state rather than guessing elapsed time.
- A postal outcome wait recognizes either a banner or Overview, so incorrect acceptance fails
  immediately with a descriptive assertion instead of a misleading timeout.
- A pytest hook saves original PNG evidence and embeds it into the self-contained HTML report.
- Execution logs record START, STEP and STATUS without writing entered field values.
- Explicit waits check readiness. Optional headed-demo pauses let viewers follow actions and inspect
  the final screen; normal runs have no presentation delay. No retry-to-green strategy or
  expected-failure markers conceal defects.

## Performance design

The default JMX runs 20 threads, a 60-second ramp and a 180-second scheduler window including ramp.
Each loop makes Login and Products HTML GETs, with 250-500ms think time before each request.
HTTP status and application root assertions avoid counting obvious error pages as successful samples.
No browser asset rendering or authenticated transaction is claimed. The runner records actual data,
qualifies the requested profile and computes strict NFR threshold verdicts in Findings.md.

## Scope limits

Coverage means an automated observable check exists; it is not a claim that the site implements every
business rule correctly. FR-05 has an observability limitation. FR-14 may expose an AUT/specification
disagreement. Resolve such disagreements with the requirement owner rather than changing expected
results to match whatever the application currently does.
