# Export, redact and reproduce — Databricks V3 portfolio checklist

## What is already documented

- V3 architecture, processing stages and known limitations.
- Interactive validation and recovery evidence.
- Published dashboard design and a point-in-time metric snapshot.
- SQL definitions for the three monitoring views.

## What still must be exported from your Databricks workspace

1. **`USDA_Pipeline_Functions`**: a cleaned 15-definition notebook (14 required functions plus the `validate_usda_batch` helper) has now been committed to `notebooks/USDA_Pipeline_Functions.ipynb`. Original Databricks notebook was supplied and inspected; validation of runtime behavior remains in the user's Databricks environment.
2. **`USDA_Delta_Merge_Lab`**: export as **Databricks notebook source (.py)** or **.ipynb**. Review cells to separate reproducible setup and read-only checks from historical data-modifying training exercises.
3. **Dashboard evidence**: capture a screenshot of the published **USDA Pipeline V3 Monitoring → Pipeline Overview** page with all five KPI counters and the batch table visible. Redact workspace identities, URLs, user initials, email addresses, workspace IDs and any secrets.
4. **Optional detailed test output**: capture sanitized screenshots of `SKIPPED_COMPLETED`, `BATCH SOURCE MISMATCH`, `INVESTIGATE_PARTIAL` and successful controlled recovery.
5. **Schema / test setup**: export CREATE TABLE definitions and initialization instructions for a **fresh isolated demo schema**. Existing lab tables should not be overwritten.

## Suggested GitHub paths

```text
databricks-v3/
  README.md
  docs/
    TECHNICAL_REPORT.md
    TEST_EVIDENCE.md
    EXPORT_GUIDE.md
  sql/
    monitoring_views.sql
  notebooks/                  # add exported notebooks after manual review
    USDA_Pipeline_Functions.py
    USDA_Delta_Merge_Lab.py
  figures/                    # add sanitized screenshot(s)
    dashboard_overview.png
```

The cleaned `notebooks/USDA_Pipeline_Functions.ipynb` is committed. The `notebooks/USDA_Delta_Merge_Lab.py` and `figures/dashboard_overview.png` paths remain planned additions. A non-executable archival lab export was prepared separately for owner review before public upload.

## Reproduction considerations

- Use a Databricks workspace with Spark, Delta Lake and appropriate Unity Catalog permissions; Free Edition behavior and permissions can differ from paid workspaces.
- The live lab used catalog `workspace` and schema `usda_training`; replace these identifiers if testing elsewhere.
- Execute the reusable definitions with `%run ./USDA_Pipeline_Functions` when both notebooks are in the same workspace folder.
- First construct new tables **in an isolated schema** and use **new, unique training batch IDs**; never replay initialization or deliberately partial test writes on the demonstrated tables.
- Restore source-to-target contract, quarantine schema, audit schema, fingerprint registry and duplicate-accounting schema consistently.
- Test new ingestion, completed replay, source mutation rejection and intentional interruption in a controlled environment.
- Check counts after each test; never assume this snapshot's 260 rows will remain the live target total.

## Sharing precautions

- The GitHub repository is public. Do not commit workspace access tokens, service credentials, private storage paths, emails or screenshots showing account details.
- USDA historical records and synthetic 2026 training observations must remain clearly labeled and separate.
- The currently published dashboard may require Databricks authentication and data permissions; do not claim it is publicly viewable from a GitHub link without testing that specific access.
