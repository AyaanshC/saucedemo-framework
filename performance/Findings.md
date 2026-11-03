# Performance findings

Historical run summary. Raw samples, logs, and the HTML dashboard are generated local artifacts
excluded from Git. Run `scripts/run_performance.py` after JMeter setup to generate current outputs
and replace this summary with the new measurements.

Measured run started (UTC): 2026-11-03T15:41:29.607003+00:00.
JMeter exit code: 0. Host: www.saucedemo.com.
Profile: 20 users, 60s ramp, 180s duration (ramp included).
Observed peak: 20 users; sample window: 179.02s; total samples: 7236.
Mandatory profile verified: True.

| Requirement | Threshold | Measured | Errors | Result |
|---|---|---|---|---|
| NFR-01 | Login P95 < 3000 ms | 55 ms | 0.0% | PASS |
| NFR-02 | Products P95 < 4000 ms | 60 ms | 100.0% | FAIL |
| NFR-03 | Overall errors < 2% | 49.9447% | included at left | FAIL |

HTTP response codes by sampler: `{"Login page": {"200": 3622}, "Products page": {"404": 3614}}`.

P95 uses nearest rank over all samples of each label, including errors. Error rate uses exact counts
before rounding. Samples with failed HTTP status or response assertions are errors. A sampler with
no successful responses cannot pass its latency requirement. A diagnostic profile cannot qualify
the mandatory NFRs. Aggregate CSV is derived from the raw JTL, not invented measurements.

## Interpretation

These are HTTP document response timings from this machine and network. SauceDemo is a client-side
application: fetching inventory.html does not log a user in, execute JavaScript, load all assets, or
measure rendered product readiness. The Products sampler measures the direct HTTP route response.
Every direct Products response was HTTP 404. The initial supplied run independently verified that this is a JavaScript SPA redirect document. JMeter does not execute that redirect; these samples remain errors. A fast 404 is not a successful Products page, so NFR-02 fails with no successful samples even when error-response P95 is below 4000ms. This is a route/measurement compatibility issue, not evidence of slow product rendering.
Use the Selenium suite to demonstrate authenticated workflows. This plan therefore demonstrates
basic HTTP page performance as requested, not authenticated browser transaction performance.
The 180-second scheduler duration includes the 60-second ramp; roughly 120 seconds remain at full
load. Requests already in flight may finish after the scheduler cutoff. Results are specific to this run.

Files: results/results.jtl, results/aggregate.csv, results/run-metadata.json, results/jmeter.log,
and html_report/index.html (the entire dashboard folder must stay together).
