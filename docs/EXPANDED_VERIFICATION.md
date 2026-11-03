# Expanded suite verification — 3 November 2026

Evidence links download the recorded files from the v1.0.0 release. For offline viewing, extract
the complete submission ZIP and open the corresponding files under `reports/` or
`performance/results/`; keep the dashboard folder intact.

Executed against the live SauceDemo app in Chrome. These are actual results, not example data.

## Result

**157 unique cases: 150 passed, 7 failed, 0 errors, 0 skipped.** The suite increased from 25 to 157 cases (132 additions). The 12-case smoke selection is unchanged; those cases passed within the main run.

| Coverage | Cases | Passed | Failed |
|---|---:|---:|---:|
| Original case-study suite | 25 | 22 | 3 |
| Extended app suite | 132 | 128 | 4 |
| Total | 157 | 150 | 7 |

## Execution batches and evidence

Coverage was executed in two headless batches while the dynamic-catalog cases were being added. The combined JUnit and JSON outputs preserve the source of each result; they do not represent a single simultaneous 157-case run. Every case used a fresh browser session.

| Batch | Cases | Passed | Failed | Elapsed seconds | Report |
|---|---:|---:|---:|---:|---|
| expanded-initial | 139 | 132 | 7 | 882.52 | [HTML](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/expanded-initial.html), [JUnit](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/expanded-initial.xml) |
| dynamic-check | 18 | 18 | 0 | 148.87 | [HTML](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/dynamic-check.html), [JUnit](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/dynamic-check.xml) |

- [Combined JUnit](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/expanded-combined.xml)
- [Combined per-case JSON summary](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/expanded-summary.json)
- Separate logs: `reports/logs/expanded-initial.log`, `reports/logs/dynamic-check.log`.
- Failure screenshots: `reports/screenshots/`, also embedded in the main HTML report.

Generated artifacts are local and excluded from Git. The Markdown inventory and this summary remain readable without those artifacts.

## Interpretation of the seven failures

| Cases | Expected | Observed | Status |
|---|---|---|---|
| Postal `1234`, `ABCDE`, `12A45` (3 cases) | Error and remain on information page | Overview opens | Original FR-14 contract discrepancies |
| Empty cart (1 case) | Prevent entry to checkout | Information page opens | Proposed acceptance rule, not an original FR |
| Whitespace-only first name, last name (2 cases) | Reject the required-field value | Overview opens | Proposed acceptance rules, not original FRs |
| Whitespace-only postal code (1 case) | Reject non-numeric postal input | Overview opens | FR-14; classification corrected after reviewing the PDF |

The three proposed rules carry the `proposed_contract` marker and require product-owner agreement before being classified as confirmed defects. Whitespace postal rejection now carries FR-14. This classification correction does not change the recorded 150/7 outcomes or the total case count. None are skipped, retried, or marked xfail. See [DEFECTS.md](DEFECTS.md) for reproduction steps.

## Additional validation

- Four sorting cases passed in visible Chrome with `--slow-mo 2 --end-pause 1` ([headed report](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/expanded-demo-check.html)). That report also contains an initial carousel-test timing failure.
- The initial headed carousel failure came from separate DOM reads straddling automatic rotation. The test was corrected to capture product content and active-dot metadata in one browser snapshot.
- Both final slider-control and automatic-advance checks then passed in visible Chrome at the slower pace ([corrected slider report](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/slider-demo-check.html), [JUnit](https://github.com/AyaanshC/saucedemo-framework/releases/download/v1.0.0/slider-demo-check.xml)).
- The final sorting assertions were exercised in the headed run; the corrected slider implementation was exercised in the final focused run. Focused rechecks are not added again to the 157 unique-case total.
- All Python sources parse; pytest collects 157 cases and the unchanged 12-case smoke subset; Git whitespace checks pass.
- No package additions were required. Downloaded PDFs use per-test temporary directories. Receipt testing checks PDF download integrity, not parsed receipt contents.
- JMeter was not rerun as part of this functional coverage expansion.

## Scope and repository state

The expanded inventory is in [TEST_CASES.md](TEST_CASES.md). Catalog data, 8% tax, payment/shipping labels and link destinations are observed regression baselines. Cross-browser/device coverage, accessibility audits, backend/security assessments, parsed PDF receipt content, and full journeys for deliberately buggy alternate personas remain outside this suite.

This document records executed testing, independently of Git publication. Use the submission ZIP
and its file manifest to identify the exact packaged source and evidence.
