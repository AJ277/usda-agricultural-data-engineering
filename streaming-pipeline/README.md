# Agricultural Transaction Streaming Pipeline (Project 3)

An educational, synthetic-data demonstration of incremental file ingestion, data-quality validation, Delta Lake MERGE operations, checkpoint recovery, and batch reconciliation in Databricks.

**Data provenance:** All transaction examples are fabricated for learning purposes. No Farm Credit Administration (FCA) records, customer accounts, or real lending transactions were used.

## Architecture

```text
Synthetic CSV batch_001 … batch_004
                |
                v
Spark Structured Streaming (availableNow trigger)
  + checkpoint: checkpoints/bronze_v1
                |
                v
Bronze Delta table (all ingested source records)
                |
                v
Field validation: ID / date / amount / category / state
           /                         \
          v                           v
Silver Delta table          Quarantine Delta table
(accepted records)          (failed records + reasons)
           \                         /
            v                       v
       SQL monitoring view: batch-by-batch reconciliation
```

## Environment

- Databricks Free Edition, serverless environment; Apache Spark 4.2.0 as reported during the demonstration
- Python / PySpark, Spark Structured Streaming, Delta Lake, Spark SQL, Unity Catalog
- Demonstration catalog/schema: `workspace.usda_training`
- Input volume: `/Volumes/workspace/usda_training/raw_files/agri_streaming_project/`
- Bronze: `workspace.usda_training.agri_streaming_bronze`
- Silver: `workspace.usda_training.agri_streaming_silver`
- Quarantine: `workspace.usda_training.agri_streaming_quarantine`
- Monitoring view: `workspace.usda_training.agri_streaming_batch_audit`

## Observed results

| Batch | Bronze | Silver | Quarantine |
|---|---:|---:|---:|
| batch_001.csv | 5 | 5 | 0 |
| batch_002.csv | 5 | 5 | 0 |
| batch_003.csv | 5 | 1 | 4 |
| batch_004.csv | 3 | 3 | 0 |
| **Total** | **18** | **14** | **4** |

The SQL monitoring view reported **0 unaccounted records**. The notebook's final run recorded **7 passing quality checks**, including nonempty transaction IDs, distinct accepted IDs, quarantine explanations, and reconciliation. An exact replay of the Silver and Quarantine MERGE statements left the 15/11/4 intermediate dataset unchanged, with zero duplicate accepted IDs. After a Python restart, batch_004 added three new Bronze records using the original checkpoint; a subsequent MERGE increased Silver from 11 to 14.

The test's successful completion was verified in the exported notebook; the GitHub-facing notebook copy intentionally clears execution output and error traces.

## Run notes — read before executing

This notebook is an **archival, stage-by-stage learning record**, not a fully automated installation script. It expects an existing Databricks workspace, catalog/schema, and volume with appropriate permissions. Cells include intermediate assertions for 5, 10, 15, and 18 Bronze records; therefore **do not use 'Run all' against an already-populated project**.

**Important:** The initial `batch_001.csv` creation cell overwrites the file if rerun. Do not overwrite a file already tracked by the Structured Streaming checkpoint. To reproduce from scratch, provision an isolated new schema/volume and an empty project directory/checkpoint path, then execute the stages in order, correcting stage-specific paths if you use a different environment. Never delete the working checkpoint or tables simply to make a rerun pass. The `%restart_python` step intentionally clears Python state.

### Data quality checks

- A transaction requires a nonempty ID.
- Date must be parseable as a calendar date.
- Amount must be present, finite for the tested input, and greater than zero; the implemented checks reject null, NaN, and nonpositive values.
- Loan category and state must be in the demonstration's explicitly allowed values.
- Invalid rows are retained in Bronze and routed to Quarantine with an explanation.
- Silver MERGE uses `transaction_id` as its match key. Quarantine MERGE matches source filename plus original field values with null-safe comparisons.

## Scope and limitations

- Batch-level examples, not a continuous production stream or measured throughput benchmark.
- The ingestion checkpoint tracks processed input files; it is not a universal deduplication mechanism for arbitrary row-level changes.
- Repeated identical invalid rows from the same source file are not uniquely distinguishable by the demonstrated quarantine MERGE condition. A production design should assign a stable source-record ID, e.g., source file plus row position or source-issued transaction event ID.
- Silver reconciliation by counts cannot independently prove record-level lineage. Further work could add immutable row IDs, schema evolution rules, durable audit/event records, failure alerting, and data-quality unit tests.
- The monitoring SQL view is computed from live Delta tables; it does not separately persist a time-stamped audit history.
- The demonstration source files and Unity Catalog objects are not embedded in the notebook; this repository describes the test rather than claiming turnkey deployment.

## Suggested repository layout

```text
streaming-pipeline/
  README.md
  Agricultural_Streaming_Pipeline_Portfolio.ipynb
```

## Portfolio summary

Built and tested an educational incremental data pipeline using PySpark Structured Streaming and Delta Lake on Databricks. Demonstrated checkpoint-based recovery after a Python-session restart, staged Bronze/Silver/Quarantine data-quality processing, retry-safe MERGE behavior on test data, and a persistent SQL batch reconciliation view across 18 synthetic transactions.