# USDA Agricultural Data Engineering — Technical Report (Template)

**Status:** Starter scaffold, not a completed real-USDA analysis.

## Objective
Build a reproducible crop production and yield pipeline from USDA NASS Quick Stats data using PySpark, Delta Lake and Spark SQL.

## Methods
Describe download date, export filters, years, states, crops, field dictionary, bronze/silver/gold stages, suppression handling, deduplication strategy, and tests.

## Quality checks
Record source/silver/gold counts, rejected/suppressed rows, crop/unit consistency, duplicates by dimension and year continuity.

## Findings
Insert validated yield and production summaries by crop/state/year, with chart(s) and source citations. Do not interpret synthetic results as actual crop trends.

## Limitations and improvements
Discuss Quick Stats sampling, withheld values, reporting revisions, record dimensions, local Spark scalability, and plans for a cloud/Databricks run.

## Reproducibility
Provide Python, Java, Spark and Delta version details, exact commands, dataset file name and hash, and automated test logs.
