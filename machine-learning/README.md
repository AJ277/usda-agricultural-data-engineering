# USDA Corn Yield Prediction — Databricks ML Portfolio

**Project type:** Independent educational portfolio project (not professional employment or a production forecasting service)  
**Tools:** Databricks, Apache Spark/PySpark, Delta Lake (upstream source table), Python, pandas, scikit-learn, MLflow, Matplotlib  
**Source:** Historical USDA NASS corn-yield observations, 2020–2025

## Objective

Explore whether historical annual corn yields can predict the following year's corn yield (bushels per acre) for 41 state-level series. Compare a simple previous-year baseline against Linear Regression, Random Forest Regression, and Gradient Boosting Regression using chronological validation. Demonstrate feature engineering, error analysis, and MLflow experiment tracking.

## Dataset and lineage

The notebook reads the existing Databricks Delta table:

```text
workspace.usda_training.silver_usda_corn
```

This table was prepared by the separate [USDA agricultural data-engineering project](../README.md). It is **not included** in this folder. To reproduce the notebook, first create/populate the upstream Silver table or adjust the input-table reference and ensure equivalent schema and observations are available.

Recorded dataset characteristics:

| Characteristic | Observed value |
|---|---:|
| Historical years | 2020–2025 |
| Observations | 246 |
| State-level series | 41 |
| Observations per year | 41 |
| Missing fields in checked columns | 0 |
| Duplicate `(year, state)` keys | 0 |
| Invalid/nonpositive yields | 0 |

The modeling notebook uses historical USDA observations only. **Synthetic 2026 yields from separate pipeline training exercises are excluded.** Annual unweighted state-level averages are **not** national production-weighted corn yield estimates.

## Methodology

1. **Inspect and validate data:** Check schema, year coverage, missing values, duplicate `(year, state)` combinations, and invalid yields.
2. **Engineer lag features:** Group by `state` and sort by `year`; use `lag()` to derive `previous_year_yield` and `two_years_ago_yield`. The `two_year_average` is the arithmetic mean of those two prior yields. Only past observations are used in features.
3. **Establish a baseline:** Predict the current yield using `previous_year_yield`.
4. **Fit models:** Linear Regression, Random Forest, Gradient Boosting; initial hyperparameters are fixed and used for educational model comparisons.
5. **Use chronological evaluation:** An initial exploratory evaluation trains on 2021–2024 and evaluates 2025 (41 observations). Later, walk-forward validation tests 2023 and 2024 using earlier years only. Two-feature comparisons restrict both feature variants to the *same* eligible training and test records, 2022 onward.
6. **Diagnose errors:** Examine actual vs predicted yields, residuals, highest-error states, feature correlations, and regression coefficients.
7. **Track experiments:** Log parameters, metrics, feature descriptions, and year-split tags in MLflow. Export a CSV summary report.

## Recorded results

### Initial one-feature evaluation (2025; exploratory)

| Approach | MAE (bu/acre) | RMSE (bu/acre) | R² |
|---|---:|---:|---:|
| Previous-year baseline | 17.78 | 22.96 | 0.3458 |
| Linear Regression | 16.06 | 19.97 | 0.5047 |
| Random Forest | **14.44** | **18.01** | **0.5973** |
| Gradient Boosting | 14.97 | 18.66 | 0.5677 |

Random Forest had the lowest error for this particular year, **not** the best demonstrated performance across validation years.

### Walk-forward development validation (2023 and 2024)

Using the one-feature dataset, the reported average MAEs were: Linear Regression **16.13**, baseline **16.20**, Random Forest **17.94**, Gradient Boosting **18.36** bu/acre. Random Forest beat the baseline in **0 of 2** validation years.

### Fair one-feature vs two-feature comparison (same eligible records)

| Model | One-feature average MAE | Two-feature average MAE |
|---|---:|---:|
| Linear Regression | 19.17 | **15.35** |
| Random Forest | 19.20 | 17.24 |
| Gradient Boosting | 19.85 | 17.69 |

Comparisons use validation years 2023 and 2024 with 2022 as the first eligible target year; training sizes were 41 and 82, respectively. Two-feature Linear Regression achieved the lowest development-validation average MAE, **15.35 bu/acre**, in this comparison.

### Two-feature Linear Regression diagnostics (2024 validation)

Trained on 2022–2023 (82 observations), validated on 2024 (41 observations):

| Measure | Value |
|---|---:|
| MAE | 16.68 bu/acre |
| RMSE | 20.96 bu/acre |
| R² | 0.6939 |
| Mean residual (actual − prediction) | −2.48 bu/acre |
| Largest absolute error | 49.57 bu/acre |
| Underpredictions / overpredictions | 23 / 18 |

### MLflow evidence

Five experiment runs were recorded in Databricks. Example run IDs:

- Gradient Boosting 2025: `f37e9fc5a47744a4919b66769c61006a`
- Two-feature Linear Regression 2024: `5dc3dd57d9a6424ab5547804ea617c66`

Run IDs are workspace-specific; the tracked experiment is not anonymously accessible by default.

## Files

```text
machine-learning/
├── README.md
├── notebooks/
│   └── USDA_Corn_Yield_ML.ipynb
├── reports/
│   └── usda_ml_evaluation_report.csv
└── figures/
    └── README.md
```

The report CSV is the **recorded summary** from the Databricks exercise, not an automatically recomputed verification artifact. Reexecute the notebook to produce actual outputs in an appropriate Databricks environment.

## Reproduction

1. Use a Databricks workspace with Python, PySpark, pandas, NumPy, Matplotlib, scikit-learn and MLflow available. The training environment reported Spark **4.2.0**, scikit-learn **1.7.2**, MLflow **3.12.0**; other compatible versions may work.
2. Ensure `workspace.usda_training.silver_usda_corn` is accessible. Required fields include `year`, `state` and numeric `yield_bu_acre`.
3. Import `notebooks/USDA_Corn_Yield_ML.ipynb` into Databricks.
4. Review all read/write paths before execution. The notebook writes the summary CSV to `/Workspace/Shared/usda_ml_evaluation_report.csv`; adjust this path if needed.
5. Run cells in order. Some cells repeat preparation steps from the original learning exercise; MLflow cells create new experiment runs each time executed.
6. Verify source row counts, chronological splits, model metrics and generated diagnostics. Avoid retraining/tuning models based on the already-observed 2025 evaluation.

## Limitations and responsible interpretation

- **No independent untouched final test.** The 2025 test was consulted while comparing algorithms and is now an exploratory holdout, not evidence of independent generalization.
- Only **two** development validation years (2023 and 2024); training observations across states are not statistically independent of common annual conditions.
- Only historical yields were used; no weather, soil, planting, or agronomic inputs. Results are insufficient for operational crop forecasts.
- Lagged values are available only after the prior year's observation is published. Do not interpret retrospective metrics as a real-time forecasting service.
- Two-year average overlaps strongly with the previous-year feature, so coefficients are not causal explanations.
- No claim of production deployment, robust forecast uncertainty, or tested performance for years after 2025.

## Next experiments

Add weather variables with valid observation timestamps, compare against seasonal historical-average baselines, investigate state effects, use expanded historical coverage for more rolling validation folds, and reserve a genuinely untouched future dataset for final evaluation.
