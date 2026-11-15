# Technical report — USDA Delta Lake Pipeline V3

**Environment:** Databricks Free Edition (interactive training lab)  
**Status:** Tested November 2026  
**Source disclosure:** Fictional 2026 corn-yield measurements were used solely to exercise incremental batch processing. The separate historical USDA NASS Quick Stats analysis in this repository must not be confused with these records.

## 1. Objective

Demonstrate reliability and observability patterns for an incremental Spark/Delta Lake pipeline. The work evolved from basic merges to a V3 wrapper that verifies registered batch identity and reconciles a completed batch before skipping repeated processing.

## 2. Architecture and controls

**Source contract:** a Spark DataFrame of `year`, `state` and `yield_bu_acre`, accompanied by a stable batch ID. Invalid/null/blank values, nonpositive or NaN yields and conflicting values for the same year-state key are rejected. Identical repeated source rows are counted as duplicate occurrences rather than silently lost.

**Accounting invariant:**

```text
incoming_rows = accepted_rows + quarantined_rows + duplicate_rows
```

**Fingerprint registry:** small training batches are normalized, sorted and hashed with SHA-256, preserving duplicate occurrences. A previously registered batch ID with changed source observations is rejected before any intended Delta writes. This implementation collects source rows in the driver and is unsuitable for large distributed loads without redesign.

**Delta target:** conditional MERGE keyed by `(year, state)`, with updates for changed yields and explicit insert-column mappings.

**Persistence:** quarantine history, duplicate accounting and completion audit are maintained separately with insert-once or verify-on-retry patterns. These writes do not form a single ACID transaction across tables.

**V3 controller:** for a completed audit (`SUCCESS` or `SUCCESS_WITH_QUARANTINE`), run completed-batch reconciliation and return `SKIPPED_COMPLETED`. With no completion audit, delegate to V2, which inspects for suspicious partial state and blocks unsafe replay with `INVESTIGATE_PARTIAL`.

## 3. Controlled interruption recovery

A Vermont test intentionally persisted two rejected Iowa records and omitted the accepted Vermont MERGE and completion audit. The recovery inspection found zero audit rows, two quarantine rows and zero matching accepted rows, returning `INVESTIGATE_PARTIAL`.

A separate read-only preflight verified registered source identity, duplicate accounting, quarantine contents using `exceptAll` both directions, absence of the accepted target key, and missing audit. An operator then performed only the missing accepted-record MERGE, verified target and quarantine counts, and inserted the missing completion audit. A subsequent V3 execution returned `SKIPPED_COMPLETED`.

This is a narrowly controlled, manual, **single-operator recovery demonstration**. It is not automatic recovery and does not prove exactly-once behavior under concurrency.

## 4. Monitored assets

| Asset | Description |
| --- | --- |
| `workspace.usda_training.delta_merge_lab` | Target keyed on state-year |
| `workspace.usda_training.delta_merge_quarantine_history` | Persisted rejection records |
| `workspace.usda_training.delta_merge_batch_audit` | Batch completion and totals |
| `workspace.usda_training.batch_source_fingerprints` | Registered source identity |
| `workspace.usda_training.batch_duplicate_accounting` | Source disposition totals |
| `workspace.usda_training.v_usda_pipeline_health` | Four health KPIs |
| `workspace.usda_training.v_usda_batch_status` | Batch-level audit and controls |
| `workspace.usda_training.v_usda_monitoring_coverage` | Registered-control coverage |

The published **USDA Pipeline V3 Monitoring** dashboard has a **Pipeline Overview** page with the target count, quarantine count, completed-batch count, duplicate target-key count and monitoring-control coverage, plus a detailed batch-status table.

## 5. Verified observations

As of the final lab verification: **260 target rows, 10 completed audits, 20 quarantined observations, zero duplicate target keys, and 30% of completed batches with both registration controls.** Four completed batches had fingerprints and three had duplicate accounting. Five fingerprint registry entries were observed overall, including one not counted in completed-batch fingerprint coverage.

Detailed evidence: [TEST_EVIDENCE.md](TEST_EVIDENCE.md).

## 6. Reproducibility

The Databricks implementation uses two notebooks in the same workspace folder: `USDA_Pipeline_Functions` and `USDA_Delta_Merge_Lab`. In the lab notebook, `%run ./USDA_Pipeline_Functions` restored all fourteen function definitions; the callability check reported no missing functions.

The cleaned functions notebook is now included under `notebooks/USDA_Pipeline_Functions.ipynb`; the full training lab archive has not yet been committed. Reproduction requires those exports, the Databricks table schemas, proper workspace permissions and deliberate initialization in a **fresh isolated schema**. **Do not rerun historical initialization, quarantine writes, or processing cells against the validated lab tables.**

## 7. Limitations and next steps

- No atomic commit across five separate Delta tables; interrupted writes need reconciliation.
- No tested concurrent ingestion or exactly-once guarantee.
- Current-target reconciliation can fail after later valid corrections to the same year-state keys; consider immutable per-batch snapshots or versioned comparisons.
- Fingerprint method uses driver-side collection; replace with scalable streaming/deterministic partition hashing for larger datasets.
- Older training batches predate fingerprint and duplicate-accounting controls. Missing registry entries should not be backfilled without evidence of the original source.
- Dashboard controls report registration presence, not independently audited compliance or security effectiveness.
- Expand automated tests for failed stages, repeated execution, concurrent attempts and data evolution before claiming production readiness.

## 8. Portfolio summary

Designed and tested a Databricks Delta Lake incremental batch-ingestion proof of concept using PySpark, SHA-256 source identity checks, duplicate-aware quarantine, conditional MERGE, batch auditing, controlled interrupted-run recovery, reusable notebook functions, Spark SQL monitoring views and a published dashboard. Results are lab observations from synthetic 2026 incremental data, not official USDA yield estimates or an independently reproduced production deployment.
