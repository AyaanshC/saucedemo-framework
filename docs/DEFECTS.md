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

## PERF-01: historical direct Products HTTP route returns a JavaScript redirect with 404

- Request: GET https://www.saucedemo.com/inventory.html using JMeter, not an authenticated browser.
- Expected for the plan's successful page response: HTTP 200 plus the application root marker.
- Actual: 3,614 requests returned HTTP 404. Direct inspection returned a document titled
  `Single Page Apps for GitHub Pages`, containing a JavaScript redirect.
- Login URL: all 3,622 requests returned HTTP 200.
- Consequence: overall error rate 49.9447%; NFR-03 fails. Products error-response P95 is 60ms,
  but there are no successful Products responses, so it cannot be accepted as passing NFR-02.
- Evidence: the original run's `results/results.jtl`, `results/aggregate.csv`, dashboard and Findings.md,
  preserved together under `performance/history/` when the corrected plan is executed.
- Interpretation: HTTP tooling does not execute this client-side redirect. Chrome's SPA navigation
  can still work, as the functional results demonstrate. This does not establish slow rendering.
- Resolution for basic HTTP testing: real Chrome authenticated with the prescribed account proves
  that the actual HTTP 200 navigation document is `/?/inventory.html`; Products then appears at
  `/inventory.html` with six items. The current JMeter plan measures that verified bootstrap document,
  still strictly asserting HTTP 200 and the app root. Route proof and actual sampled URLs are saved.
  NFR-02 now means Products bootstrap-document response time, excluding the initial redirect hop,
  authentication and rendering. This does not establish authenticated rendered readiness.
  The old direct-route JMX remains as `performance/jmx/saucedemo_direct_route_diagnostic.jmx`.

## Coverage limitation: FR-05

Synthetic usernames of 29, 30 and 31 characters all produce a generic credentials error. This checks
the specified rejection above 30 but does not prove that length itself is being validated. A genuine
boundary proof requires an appropriate valid account or isolated validator. Do not present this
negative-only evidence as proof of a 30-character acceptance limit.

## BUG-04: whitespace-only postal code accepted (FR-14)

- Requirement: FR-14 says Postal Code must be numeric. Three spaces are non-numeric.
- Steps: log in with the standard account; add a product; go to Checkout; enter `Demo`, `Tester`,
  and a postal code of three spaces; click Continue.
- Expected: error and remain on Checkout: Your Information.
- Actual: Overview opens.
- Automated case: `test_whitespace_only_required_field_is_rejected[postalCode]` carries FR-14.
- Evidence: `reports/screenshots/tests_test_checkout_extended_py__test_whitespace_only_required_field_is_rejected_postalCode__call.png`.
- Classification correction: this case was initially grouped with proposed contracts; reviewing the
  numeric-only wording in the supplied PDF establishes direct FR-14 support.

## Proposed acceptance gaps found by the extended suite

The following observations were reproduced on 3 November 2026. The expected behavior is a proposed
acceptance rule beyond the original brief, not an additional FR requirement. These three cases carry
the `proposed_contract` marker and are included in the default run so the decision remains visible.

### APP-CHECKOUT-EMPTY: checkout can start with an empty cart

- Steps: log in as `standard_user`; open Cart without adding products; click Checkout.
- Proposed expectation: prevent checkout and remain on Cart (a disabled button or validation may implement this).
- Actual: the browser opens Checkout: Your Information.
- Automated case: `test_empty_cart_cannot_start_checkout` in `tests/test_checkout_extended.py`.
- Evidence: `reports/screenshots/tests_test_checkout_extended_py__test_empty_cart_cannot_start_checkout_call.png`.
- Scope: this case establishes that empty checkout can start; it does not claim to have completed an empty order.

### APP-CHECKOUT-WHITESPACE: first/last names accept whitespace-only values

- Steps: log in; add a product; open Checkout. Set exactly one of first name or last name
  to three spaces, keeping the other fields valid (`Demo`, `Tester`, `12345`); click Continue.
- Proposed expectation: reject the whitespace-only required field and stay on the information page.
- Actual: both variants reach Checkout: Overview.
- Automated cases: `test_whitespace_only_required_field_is_rejected[firstName]` and `[lastName]`.
- Evidence: corresponding `tests_test_checkout_extended_py__test_whitespace_only_required_field_is_rejected_*__call.png`
  files under `reports/screenshots/` and the expanded HTML report.

Agree these rules with the requirement owner before classifying them as confirmed product defects.
The four FR-14 postal-code discrepancies remain separately documented above.
