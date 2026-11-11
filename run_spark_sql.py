from pathlib import Path
import csv

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

ROOT = Path(__file__).resolve().parent
GOLD = ROOT / "output" / "real" / "gold"
SQL_FILE = ROOT / "sql" / "agricultural_risk_analytics.sql"
OUT = ROOT / "output" / "sql_results"
OUT.mkdir(parents=True, exist_ok=True)

builder = (
    SparkSession.builder
    .appName("USDA_Agricultural_Risk_SQL")
    .master("local[*]")
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    )
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    )
)

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

try:
    gold = spark.read.format("delta").load(str(GOLD))
    gold.createOrReplaceTempView("corn_yield")

    print("Gold records:", gold.count())

    sql_text = SQL_FILE.read_text(encoding="utf-8")
    queries = [
        q.strip()
        for q in sql_text.split(";")
        if q.strip()
    ]

    names = [
        "top_10_yield_2025",
        "largest_yield_declines",
        "yield_volatility",
    ]

    for name, query in zip(names, queries):
        print(f"\n=== {name.upper()} ===")
        result = spark.sql(query)
        result.show(10, truncate=False)

        rows = result.collect()
        output_path = OUT / f"{name}.csv"

        with output_path.open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(result.columns)
            for row in rows:
                writer.writerow(list(row))

        print("Saved:", output_path)

    print("\nSpark SQL analysis completed.")

finally:
    spark.stop()
