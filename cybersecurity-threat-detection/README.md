# Project 4 — Cybersecurity Threat Detection with Spark MLlib

An **educational, synthetic-data** classification project created in **Databricks Free Edition**. It demonstrates Spark data preparation, derived security features, model training and evaluation, MLflow experiment tracking, feature-level model interpretation, and technical reporting. This is **not** a production security detector or an FCA operational system.

## Project contents

| File | Purpose |
| --- | --- |
| `Cybersecurity_Threat_Detection_ML_Portfolio.ipynb` | Organized notebook: data generation, feature engineering, training, evaluation, MLflow, explanations, final QA |
| `MODEL_EVALUATION_REPORT.md` | Recorded model results, experiment IDs, dataset description, and limitations |
| `random_forest_feature_importance.csv` | Eight mean-decrease-in-impurity feature importance scores |
| `logistic_regression_coefficients.csv` | Eight coefficients for standardized features |

## Architecture

```text
Seeded synthetic network-event generator (5,000 labeled rows)
           ↓
Unity Catalog volume CSV → PySpark schema and quality validation
           ↓
EDA and feature engineering (8 numeric model inputs)
           ↓
Seeded 80/20 random train/test split (4,042 / 958)
           ↓
Logistic Regression (scaled) + Random Forest (unscaled)
           ↓
Security-class precision, recall, F1, confusion matrices
           ↓
MLflow metrics/parameters + feature importance and coefficient CSVs
           ↓
Markdown technical report + 12 final QA checks
```

## Observed results (original Databricks session)

| Metric | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Test accuracy | 99.90% | 100.00% |
| Suspicious-class precision | 100.00% | 100.00% |
| Suspicious-class recall | 99.28% | 100.00% |
| Suspicious-class F1 | 99.64% | 100.00% |
| True positives | 137 | 138 |
| True negatives | 820 | 820 |
| False positives | 0 | 0 |
| False negatives | 1 | 0 |

In the original session, 4,223 records had a normal label and 777 had a suspicious label. Both MLflow runs completed (`FINISHED`), the feature importance values summed to 1.0, two explanation CSVs were exported, and **12 final QA assertions passed**. The published notebook has been reorganized but **has not been reexecuted** following that correction.

### Main feature-importance finding

Random Forest assigned 0.4430 importance to `failed_login_attempts` and 0.3439 to `failed_login_rate` (together ~78.70% of impurity-based importance). These inputs are correlated; importance is not a causal effect or proof that the attributes alone identify threats. The Logistic Regression coefficients reflect conditional associations in standardized inputs.

## How to run in Databricks

1. Import `Cybersecurity_Threat_Detection_ML_Portfolio.ipynb` into a Databricks Python notebook.
2. Ensure you have an accessible Unity Catalog volume, or update the `project_base` and `data_path` cells to use your own volume. The verified notebook used `/Volumes/workspace/usda_training/raw_files/cyber_threat_detection/`.
3. Run the cells **in order**. The generator uses Python `random.seed(42)` and writes `data/network_events.csv` only when the file does not already exist. Inspect/remove an incompatible existing file *deliberately*, rather than silently overwriting it.
4. Review the validation checks, MLflow experiment, feature importances, and generated report in `reports/` and `output/`. Running the MLflow logging section again creates additional runs.
5. The exact split sizes and scores recorded here are from the original verified session. If a split differs in another environment, inspect the results; the original QA assertions include fixed expected counts.

## Limitations and next steps

- **Labels drive feature generation:** The synthetic suspicious class uses disjoint destination-port choices and failed-login ranges. Extremely high accuracy is expected and does not establish real-world threat detection.
- **Simple random holdout:** No time-separated validation, external dataset, noise stress test, cross-dataset evaluation, or drift analysis was performed.
- **No deployment:** The project does not ingest production security logs, raise operational alerts, or perform automated incident response. No serialized models were registered or deployed.
- **Feature correlations:** `total_bytes`, `send_receive_ratio`, and `failed_login_rate` are derived from the original features; importance and regression coefficient magnitude can shift under collinearity.
- **Reproducibility scope:** This publication preserves educational code and observed results, not a fully automated cross-environment production test suite.

## Provenance

The notebook is a publication-ready organization of the user's exported notebook. The exported code omitted the CSV-to-`security_df` load cell and placed feature validation before feature engineering; those structural issues were corrected using the pipeline's previously executed steps. The original verified report and CSV exports are included unchanged.