# Verified discrepancies - 3 November 2026

Verified against the live SauceDemo application with Chrome 156 and the supplied standard account.
These findings describe the AUT versus the case-study contract. The framework records them honestly.
Referenced screenshots and reports are generated local artifacts excluded from Git. Rerun the
reproduction steps or suites to capture current evidence.

## BUG-01: four-digit postal code accepted

- Requirement: FR-14 says four digits are invalid.
- Steps: log in; add Sauce Labs Backpack; open Cart; Checkout; enter first name Demo, last name Tester,
  postal code `1234`; click Continue.
- Expected: error banner; remain on Checkout: Your Information.
- Actual: Checkout: Overview opens.
- Impact: checkout permits a postal length disallowed by the stated requirement.
- Evidence: `reports/screenshots/tests_test_checkout_py__test_postal_code_contract_four-digits-invalid__call.png`
  and the corresponding failing assertion in `reports/functional.html`.

## BUG-02: alphabetic postal code accepted

- Requirement: FR-14 requires a numeric postal code.
- Steps: same as BUG-01 with postal `ABCDE`.
- Expected: error; remain on information page.
- Actual: Overview opens.
- Evidence: `reports/screenshots/tests_test_checkout_py__test_postal_code_contract_alphabetic-invalid__call.png`.

## BUG-03: mixed postal code accepted

- Requirement: FR-14 requires a numeric postal code.
- Steps: same as BUG-01 with postal `12A45`.
- Expected: error; remain on information page.
- Actual: Overview opens.
- Evidence: `reports/screenshots/tests_test_checkout_py__test_postal_code_contract_mixed-invalid__call.png`.

Empty postal values are rejected, and five/six digits reach Overview, as the passing cases show.
The failure screenshots capture the resulting Overview. The HTML assertion records the actual input;
Overview itself does not display the entered postal value.

## PERF-01: direct Products HTTP route returns a JavaScript redirect with 404

- Request: GET https://www.saucedemo.com/inventory.html using JMeter, not an authenticated browser.
- Expected for the plan's successful page response: HTTP 200 plus the application root marker.
- Actual: 3,614 requests returned HTTP 404. Direct inspection returned a document titled
  `Single Page Apps for GitHub Pages`, containing a JavaScript redirect.
- Login URL: all 3,622 requests returned HTTP 200.
- Consequence: overall error rate 49.9447%; NFR-03 fails. Products error-response P95 is 60ms,
  but there are no successful Products responses, so it cannot be accepted as passing NFR-02.
- Evidence: `performance/results/results.jtl`, `performance/results/aggregate.csv`, dashboard and Findings.md.
- Interpretation: HTTP tooling does not execute this client-side redirect. Chrome's SPA navigation
  can still work, as the functional results demonstrate. This does not establish slow rendering.
- Follow-up: agree with the evaluator whether to measure the SPA bootstrap URL/redirect chain or use
  browser performance instrumentation for authenticated rendered Products readiness. Any such change
  must state the revised measurement definition. The supplied direct-route results remain preserved.

## Coverage limitation: FR-05

Synthetic usernames of 29, 30 and 31 characters all produce a generic credentials error. This checks
the specified rejection above 30 but does not prove that length itself is being validated. A genuine
boundary proof requires an appropriate valid account or isolated validator. Do not present this
negative-only evidence as proof of a 30-character acceptance limit.
