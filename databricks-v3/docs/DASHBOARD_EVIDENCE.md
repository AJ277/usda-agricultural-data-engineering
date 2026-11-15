# Dashboard evidence and interpretation

The owner supplied screenshots from **two distinct published Databricks dashboards**.

## A. USDA Pipeline V3 Monitoring

The V3 incremental Delta Lake batch-monitoring dashboard displays:

| Metric | Screenshot value |
| --- | ---: |
| Target state-year records | 260 |
| Quarantined observations | 20 |
| Completed batch audit records | 10 |
| Duplicate target state-year keys | 0 |
| Completed batches with both registrations | 30% |

It also contains a batch-level table with incoming and quarantined totals, registration flags and processing status. Some historical entries lack registry records because those controls were introduced later.

## B. USDA Pipeline Monitoring Dashboard

This is a **separate pipeline execution-monitoring dashboard**, not a different page of the V3 batch-monitoring dashboard. The screenshots show:

- **Latest recorded status:** `SUCCESS`, completed **2026-11-13 08:01 PM** as displayed in the dashboard. This is a recorded audit status, not necessarily the authoritative Databricks Jobs run status.
- **Historical execution status chart:** `FAILED` = 11 and `SUCCESS` = 10 audit entries. The historical failures are **not** evidence that the latest pipeline run failed.
- **Failure category chart:** `VALIDATION_TEST` = 8, `TRAINING_TEST` = 2, `OPERATIONAL_FAILURE` = 1.
- **Execution-duration chart:** includes a long roughly 126.75-second entry and several shorter entries near 1–2 seconds. The screenshot alone does not establish standardized end-to-end benchmark timing.
- **Recent failures:** an audit log includes source-validation examples such as `Expected 250 records; found 252`, plus other training-stage errors. Do not conflate these simulations with a production outage.

**Audit interpretation:** The dashboard itself explicitly warns that its historical records include intentional validation and failure simulations, that manually timed/partial executions are included, and that displayed latest audit status should not be interpreted as authoritative Databricks job status. Keep this caveat with all screenshots and metrics.

## Screenshot handoff

Four cropped and reviewed screenshots were prepared separately from the owner's supplied images for public-facing portfolio use:

- `figures/usda_v3_monitoring_dashboard.png`
- `figures/usda_pipeline_latest_status.png` — run identifier redacted
- `figures/usda_pipeline_audit_charts.png`
- `figures/usda_pipeline_failure_categories.png` — recent-failures table excluded to avoid run identifiers

**These image binaries are not yet committed on the GitHub branch.** Add only after final visual review. Do not link them as if they are present until uploaded.

Screenshot snapshots describe historical training results and do not imply continuous monitoring or public dashboard accessibility.
