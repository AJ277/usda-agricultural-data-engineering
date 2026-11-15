# USDA Delta Lake Pipeline V3 — Databricks portfolio extension

**Status:** Demonstrated in Databricks Free Edition, November 2026  
**Stack:** Python · PySpark · Delta Lake · Spark SQL · Databricks Lakeview dashboard  
**Data provenance:** **The incremental 2026 state-yield observations are synthetic training data, not official USDA measurements.** This extension is separate from the repository's historical USDA NASS Quick Stats workflow.

## Overview

An incremental batch-processing training lab built on Delta Lake to demonstrate source-integrity verification, duplicate-aware quality rules, conditional MERGE processing, rejected-record quarantine, completion auditing, verified reruns and controlled investigation/recovery of partial processing.

The original repository's **historical USDA agricultural analysis** remains documented in [the root README](../README.md). Do not combine its historical observations with synthetic 2026 training values or treat the V3 test table as an official USDA series.

## Demonstrated system

```text
Incoming PySpark batch (fictional 2026 yields)
    |
    v
Registered SHA-256 source fingerprint / batch ID
    |
    v
Duplicate-aware validation (incoming = accepted + quarantined + duplicates)
    |
    +--> Rejected observations --> Delta quarantine history
    +--> Duplicate occurrence accounting
    |
    v
Audit and existing-write inspection
    |
    +--> Completed --> full reconciliation --> SKIPPED_COMPLETED
    +--> Partial --> INVESTIGATE_PARTIAL / manual controlled recovery
    +--> New --> conditional Delta MERGE --> completion audit
    |
    v
SQL monitoring views --> Published Databricks dashboard
```

### Point-in-time demonstrated results

| Measure | Observed |
| --- | ---: |
| Target records | 260 |
| Completed batch audit records | 10 |
| Quarantined records | 20 |
| Duplicate state-year target keys | 0 |
| Completed batches with fingerprint registration | 4 of 10 |
| Completed batches with duplicate accounting | 3 of 10 |
| Completed batches with both | 3 of 10 (30%) |
| Reusable Python functions loaded via `%run` | 14 |

Counts were observed during the interactive training lab and are **not** performance benchmarks, data quality scores or guaranteed live values.

### Representative test evidence

- **Montana:** six source rows reconciled as two accepted, two quarantined and two repeated source occurrences; completed-batch V3 retry returned `SKIPPED_COMPLETED`.
- **Dakotas:** five source rows reconciled as two accepted, two quarantined and one duplicate; two new state-year keys inserted; target grew from 257 to 259. A completed retry preserved existing table counts.
- **Changed-source protection:** a modified South Dakota yield under an already registered batch ID triggered `BATCH SOURCE MISMATCH`; the original stored value was preserved.
- **Vermont:** an intentionally interrupted run wrote two quarantine rows but no Vermont target observation or audit. Inspection returned `INVESTIGATE_PARTIAL`. Following source, quarantine, accounting and target reconciliation, the accepted row was merged, completion audited and a V3 retry returned `SKIPPED_COMPLETED`. Target grew from 259 to 260.

See [technical report](docs/TECHNICAL_REPORT.md) and [test evidence](docs/TEST_EVIDENCE.md).

## Data assets

All Delta tables and views are in `workspace.usda_training`:

| Table / view | Role |
| --- | --- |
| `delta_merge_lab` | Delta target keyed on `(year, state)` |
| `delta_merge_quarantine_history` | Rejection history with batch IDs and rejection reasons |
| `delta_merge_batch_audit` | Batch completion audit |
| `batch_source_fingerprints` | Registered small-batch source hashes |
| `batch_duplicate_accounting` | Incoming/accepted/quarantined/duplicate reconciliation |
| `v_usda_pipeline_health` | Health KPIs |
| `v_usda_batch_status` | Batch audit and registration flags |
| `v_usda_monitoring_coverage` | Registration-coverage totals and percentage |

## Databricks notebooks and dashboard

The functioning notebooks were developed in the Databricks workspace:

- `USDA_Pipeline_Functions`: fourteen reusable function definitions.
- `USDA_Delta_Merge_Lab`: interactive tests, recovery demonstrations and SQL monitoring views.
- Published dashboard: **USDA Pipeline V3 Monitoring**, page **Pipeline Overview**, with five KPI counters and a batch processing/status table.

**Actual notebook exports and redacted dashboard images are not included in this documentation-only GitHub change.** Follow [export and reproduction guidance](docs/EXPORT_GUIDE.md) to add genuine exports. This repository does **not** claim the Databricks V3 implementation has been independently reproduced from the GitHub files.

## Limitations

This is a sequential training proof of concept, not a production-safe distributed orchestration service. Writes span multiple Delta tables and are not atomic as a group. Concurrent workers, state changes following a completed audit, and the small-batch `collect()`-based fingerprint method require stronger safeguards. Completed-batch reconciliation compares accepted rows against the current target, so a later legitimate correction can invalidate historical checks. Historical batches predate new registration controls; missing registration is not proof of processing failure.

## Navigation

- [Technical report](docs/TECHNICAL_REPORT.md)
- [Verified test evidence](docs/TEST_EVIDENCE.md)
- [Notebook export and portfolio checklist](docs/EXPORT_GUIDE.md)
- [Monitoring view SQL](sql/monitoring_views.sql)
