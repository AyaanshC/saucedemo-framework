# Performance findings

Measured run started (UTC): 2026-11-03T18:15:29.075723+00:00.
JMeter exit code: 0. Host: www.saucedemo.com.
Profile: 20 users, 60s ramp, 180s duration (ramp included).
Observed peak: 20 users; sample window: 179.51s; total samples: 6715.
Mandatory profile verified: True.
Measurement: spa_bootstrap_http.
Login document: https://www.saucedemo.com/.
Products document: https://www.saucedemo.com/?/inventory.html.

| Requirement | Threshold | Measured | Errors | Result |
|---|---|---|---|---|
| NFR-01 | Login P95 < 3000 ms | 228 ms | 0.8029% | PASS |
| NFR-02 | Products P95 < 4000 ms | 223 ms | 1.1933% | PASS |
| NFR-03 | Overall errors < 2% | 0.9978% | included at left | PASS |

HTTP response codes by sampler: `{"Login page": {"200": 3336, "Non HTTP response code: java.net.SocketException": 2, "Non HTTP response code: javax.net.ssl.SSLException": 25}, "Products page": {"200": 3312, "Non HTTP response code: java.net.SocketException": 3, "Non HTTP response code: javax.net.ssl.SSLException": 37}}`.
Observed request URLs from the JTL: `{"Login page": ["https://www.saucedemo.com/"], "Products page": ["https://www.saucedemo.com/?/inventory.html"]}`.

P95 uses nearest rank over all samples of each label, including errors. Error rate uses exact counts
before rounding. Samples with failed HTTP status or response assertions are errors. A sampler with
no successful responses cannot pass its latency requirement. A diagnostic profile cannot qualify
the mandatory NFRs. Aggregate CSV is derived from the raw JTL, not invented measurements.

## Interpretation

These are HTTP document response timings from this machine and network. JMeter does not log a user
in, execute JavaScript, load browser assets, or measure rendered product readiness.
Before this run, real Chrome authenticated as standard_user and verified that navigating to /inventory.html loads the HTTP 200 document /?/inventory.html, then displays Products with six items at /inventory.html. JMeter requests that verified SPA bootstrap document directly and still requires HTTP 200 plus the React root marker. The original direct-route 404 run and diagnostic JMX are preserved separately. NFR-02 here means Products bootstrap-document HTTP response time; it is not authenticated rendered-product readiness or end-to-end navigation including the initial 404 hop. Do not present it as a browser-rendering verdict.
Use the Selenium suite to demonstrate authenticated workflows. This plan therefore demonstrates
basic HTTP page performance as requested, not authenticated browser transaction performance.
The 180-second scheduler duration includes the 60-second ramp; roughly 120 seconds remain at full
load. Requests already in flight may finish after the scheduler cutoff. Results are specific to this run.

Files: results/results.jtl, results/aggregate.csv, results/run-metadata.json, results/route-evidence.json,
results/assessment.json, results/jmeter.log,
and html_report/index.html (the entire dashboard folder must stay together).
