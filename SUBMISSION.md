# Case-study submission

## Which tests are required?

There are **157 total cases**, not 157 extra cases. The original **25 case-study cases** implement
the stated FR scope; **132 additional cases** explore more app behavior. Section 5 specifies six
mandatory FRs plus at least two more requirements, including negative/boundary coverage. It does
not mandate a particular test count or all alternate account personas.

For assignment-focused execution:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithJMeter
.\.venv\Scripts\python.exe -m pytest -m case_study --html=reports/case-study.html --junitxml=reports/case-study-junit.xml -o log_file=reports/logs/case-study.log
.\.venv\Scripts\python.exe .\scripts\run_performance.py
.\.venv\Scripts\python.exe .\scripts\package_submission.py
```

Have Chrome, Python 3.11+, and Java 8+ installed. If Java is not on PATH, pass its full executable
path to the performance runner using `--java`. Internet is required. Extract the submission ZIP
to a writable folder before running setup. Environments, drivers and tools are rebuilt locally.

For the visible demo, double-click `START_DEMO.cmd`. It runs the 12 core smoke cases with 2-second
action pauses and a 3-second final-screen pause. This intentional presentation pacing is explicitly
justified in code; explicit waits still perform synchronization.

## Evidence to present

- `reports/case-study.html`: original 25-case submission execution and embedded failure screenshots.
- `reports/smoke.html`: recorded smoke evidence; the demo regenerates it.
- `reports/expanded-initial.html` and `reports/dynamic-check.html`: optional extended coverage.
- `reports/slider-demo-check.html`: corrected headed slider checks; the earlier timing-test report
  is retained as development history and is explained in `docs/EXPANDED_VERIFICATION.md`.
- `performance/results/results.jtl`, `aggregate.csv`, `run-metadata.json`, `assessment.json`:
  genuine latest JMeter samples, aggregate export, profile and NFR assessment.
- `performance/results/route-evidence.json`: HTTP routes plus real Chrome proof of the Products document.
- `performance/html_report/index.html`: JMeter dashboard; keep its complete folder intact.
- `performance/Findings.md`: current measured NFR verdicts and exact measurement definition.
- `performance/history/`: preserved earlier direct-route 404 evidence and diagnostic runs.
- `docs/CASE_STUDY_COMPLIANCE.md`, `TEST_DESIGN.md`, `DEFECTS.md`, `TEST_CASES.md`: compliance,
  EP/BVA design, traceability, reproduced discrepancies and complete case inventory.

## Important interpretation

Functional assertion failures expose behavior that disagrees with the brief; they do not mean the
framework should change expected outcomes to match the app. FR-14 postal cases remain active.
The extended suite additionally checks whitespace postal input under FR-14. Empty-cart checkout
and whitespace-only first/last names are three separately tagged proposed contracts.

FR-05 uses unknown synthetic usernames of 29, 30 and 31 characters. Their rejection checks the
observable negative result, but cannot prove an isolated 30-character validator. The cases carry
`coverage_limited`; this limitation is explicit and FR-05 is not needed for the minimum scope.

The JMeter Products sampler measures the verified SPA bootstrap HTTP document `/?/inventory.html`.
Real Chrome proves that this document displays Products at `/inventory.html` after standard-user
authentication. It does not measure JavaScript rendering, the original 404 redirect hop, or an
authenticated HTTP transaction. Interpret its NFR-02 verdict as document-response performance.
The original direct-route results are preserved, and HTTP 404 is never reclassified as HTTP 200.

## Submission ZIP

`scripts/package_submission.py` creates `dist/saucedemo-case-study-submission.zip`, including source
and all required evidence even though Git ignores generated results. The archive contains a
SHA-256 manifest and is checked for ZIP corruption and required files. No `.git`, `.venv`, driver
cache, downloaded tools, or local `.env` files are included. A source-only GitHub link does not
replace the evidence-inclusive ZIP.

Latest result details and any remaining external limitations are in
`docs/CASE_STUDY_COMPLIANCE.md`. Give the actual demo using the launcher and explain the findings.
