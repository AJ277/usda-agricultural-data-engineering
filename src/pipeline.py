"""USDA Quick Stats export -> Spark cleaning -> Delta bronze/silver/gold -> Spark SQL.

Source CSV must be downloaded from USDA Quick Stats by the user or use the
explicitly synthetic fixture shipped with this repository.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "year", "state_name", "commodity_desc", "statisticcat_desc", "unit_desc",
    "value", "agg_level_desc", "domain_desc", "freq_desc"
}


def spark_session() -> SparkSession:
    builder = (SparkSession.builder.master("local[2]")
        .appName("USDA-Agricultural-Data-Engineering")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))
    return configure_spark_with_delta_pip(builder).getOrCreate()


def clean_source(raw):
    """Normalize Quick Stats columns and keep state-level annual total crop metrics."""
    df = raw.toDF(*[x.lower().strip() for x in raw.columns])
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing USDA Quick Stats columns: {sorted(missing)}")
    for field in ["state_name", "commodity_desc", "statisticcat_desc", "unit_desc",
                  "agg_level_desc", "domain_desc", "freq_desc"]:
        df = df.withColumn(field, F.upper(F.trim(F.col(field))))
    df = df.filter(
        F.col("commodity_desc").isin("CORN", "SOYBEANS", "WHEAT") &
        (F.col("agg_level_desc") == "STATE") &
        (F.col("freq_desc") == "ANNUAL") &
        (F.col("domain_desc") == "TOTAL") &
        F.col("statisticcat_desc").isin("PRODUCTION", "YIELD")
    )
    # USDA suppression markers such as (D), (Z), and (NA) are not numeric.
    # try_cast returns NULL rather than raising CAST_INVALID_INPUT in Spark 4.
    df = (df.withColumn("year", F.expr("try_cast(year AS INT)"))
          .withColumn("value_numeric", F.expr(
              "try_cast(regexp_replace(trim(value), ',', '') AS DOUBLE)")))
    df = df.filter(F.col("year").between(1900, 2100) & F.col("value_numeric").isNotNull())
    # Duplicate records can occur in USDA exports due to practice/class or other dimensions.
    # Keep exact duplicates only; retain multidimensional source columns for traceability.
    key_fields = ["year", "state_name", "commodity_desc", "statisticcat_desc", "unit_desc", "value_numeric"]
    df = df.dropDuplicates(key_fields)
    return df.select(*key_fields)


def run(source: Path, destination: Path, export_csv: bool = True) -> dict:
    if not source.is_file():
        raise FileNotFoundError(f"Source CSV does not exist: {source}")
    spark = spark_session()
    try:
        # Spark reads CSV as strings so suppressed values remain visible in bronze.
        bronze = spark.read.option("header", True).option("multiLine", True).option("quote", '"').csv(str(source))
        (bronze.write.format("delta").mode("overwrite")
         .option("overwriteSchema", "true").save(str(destination / "bronze")))
        silver = clean_source(bronze)
        if silver.limit(1).count() == 0:
            raise ValueError("No eligible records after filtering; check USDA export query/columns")
        (silver.write.format("delta").mode("overwrite")
         .option("overwriteSchema", "true").save(str(destination / "silver")))
        spark.read.format("delta").load(str(destination / "silver")).createOrReplaceTempView("crop_metrics")
        # Retain statistic and unit in aggregation to avoid mixing incompatible measurements.
        gold = spark.sql("""
        SELECT year, state_name, commodity_desc, statisticcat_desc, unit_desc,
               ROUND(AVG(value_numeric), 3) AS reported_value,
               COUNT(*) AS source_rows
        FROM crop_metrics
        GROUP BY year, state_name, commodity_desc, statisticcat_desc, unit_desc
        """)
        (gold.write.format("delta").mode("overwrite")
         .option("overwriteSchema", "true").save(str(destination / "gold")))
        gold.createOrReplaceTempView("gold_metrics")
        trend = spark.sql("""
        SELECT year, state_name, commodity_desc, statisticcat_desc, unit_desc,
               reported_value,
               LAG(reported_value) OVER (
                 PARTITION BY state_name, commodity_desc, statisticcat_desc, unit_desc ORDER BY year
               ) AS previous_reported_value,
               LAG(year) OVER (
                 PARTITION BY state_name, commodity_desc, statisticcat_desc, unit_desc ORDER BY year
               ) AS previous_year
        FROM gold_metrics
        """).withColumn("yoy_pct", F.when(
             F.col("previous_year") == F.col("year") - 1,
             F.when(F.col("previous_reported_value") != 0,
                    100 * (F.col("reported_value") / F.col("previous_reported_value") - 1))
        ))
        destination.mkdir(parents=True, exist_ok=True)
        if export_csv:
            # Small aggregated result intended for visual inspection, not Spark-scale data.
            trend.orderBy("state_name", "commodity_desc", "statisticcat_desc", "year").coalesce(1).write.mode("overwrite").option("header", True).csv(str(destination / "trend_csv"))
        n_bronze, n_silver, n_gold = bronze.count(), silver.count(), gold.count()
        print(f"Bronze rows: {n_bronze} | filtered silver rows: {n_silver} | gold groups: {n_gold}")
        print(f"Delta tables: {destination.resolve()}")
        return {"bronze_rows": n_bronze, "silver_rows": n_silver, "gold_groups": n_gold}
    finally:
        spark.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["demo", "real"], default="demo")
    parser.add_argument("--csv", default=None, help="USDA Quick Stats CSV path (required for --source real)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    if args.source == "real" and not args.csv:
        parser.error("--source real requires --csv PATH")
    source = Path(args.csv) if args.csv else ROOT / "data" / "sample" / "usda_quickstats_SYNTHETIC.csv"
    output = Path(args.out) if args.out else ROOT / "output" / args.source
    print("DATA MODE:", "SYNTHETIC DEMONSTRATION" if args.source == "demo" else "USDA CSV PROVIDED BY USER")
    run(source, output)


if __name__ == "__main__":
    main()
