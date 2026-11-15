-- Databricks Spark SQL monitoring views for the USDA Delta Lake V3 lab.
-- Views read existing lab tables; no base-table DML is performed.
-- Replace workspace.usda_training when reproducing in an isolated schema.

CREATE OR REPLACE VIEW workspace.usda_training.v_usda_pipeline_health AS
SELECT
    (SELECT COUNT(*) FROM workspace.usda_training.delta_merge_lab) AS target_records,
    (SELECT COUNT(*) FROM workspace.usda_training.delta_merge_quarantine_history) AS quarantine_records,
    (SELECT COUNT(*) FROM workspace.usda_training.delta_merge_batch_audit
      WHERE status IN ('SUCCESS', 'SUCCESS_WITH_QUARANTINE')) AS completed_batches,
    (SELECT COUNT(*) FROM (
        SELECT year, state
        FROM workspace.usda_training.delta_merge_lab
        GROUP BY year, state
        HAVING COUNT(*) > 1
    )) AS duplicate_target_keys;

CREATE OR REPLACE VIEW workspace.usda_training.v_usda_batch_status AS
SELECT
    a.batch_id, a.processed_at, a.status,
    a.incoming_rows, a.accepted_rows, a.quarantined_rows,
    (f.batch_id IS NOT NULL) AS has_fingerprint,
    (d.batch_id IS NOT NULL) AS has_accounting,
    CASE
        WHEN f.batch_id IS NOT NULL AND d.batch_id IS NOT NULL
        THEN 'BOTH_CONTROLS_REGISTERED'
        ELSE 'MISSING_REGISTRATION'
    END AS monitoring_status
FROM workspace.usda_training.delta_merge_batch_audit a
LEFT JOIN (
    SELECT DISTINCT batch_id
    FROM workspace.usda_training.batch_source_fingerprints
) f ON a.batch_id = f.batch_id
LEFT JOIN (
    SELECT DISTINCT batch_id
    FROM workspace.usda_training.batch_duplicate_accounting
) d ON a.batch_id = d.batch_id;

CREATE OR REPLACE VIEW workspace.usda_training.v_usda_monitoring_coverage AS
SELECT
    COUNT(*) AS completed_batches,
    COUNT_IF(has_fingerprint = TRUE) AS batches_with_fingerprints,
    COUNT_IF(has_accounting = TRUE) AS batches_with_accounting,
    COUNT_IF(has_fingerprint = TRUE AND has_accounting = TRUE) AS batches_with_both_controls,
    ROUND(
        100.0 * COUNT_IF(has_fingerprint = TRUE AND has_accounting = TRUE)
        / NULLIF(COUNT(*), 0), 2
    ) AS full_coverage_pct
FROM workspace.usda_training.v_usda_batch_status
WHERE status IN ('SUCCESS', 'SUCCESS_WITH_QUARANTINE');
