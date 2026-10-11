"""
Spark cleaning job.

Reads OLTP tables from `public.*`, applies light cleaning, writes to
`curated.*`. Downstream, dbt staging reads from `curated.*` (via the
`source_schema` dbt var) instead of `public.*`.

    spark-submit \
      --jars /opt/spark/jars/postgresql-42.7.3.jar \
      /opt/spark/work-dir/jobs/clean_all.py
"""
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DecimalType,
    IntegerType,
    StringType,
    TimestampType,
)

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT_INTERNAL", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "sme_oltp")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "sme")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "sme")
POSTGRES_SSLMODE = os.environ.get("POSTGRES_SSLMODE", "").strip()

_ssl_suffix = f"?sslmode={POSTGRES_SSLMODE}" if POSTGRES_SSLMODE else ""
JDBC = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}{_ssl_suffix}"


def read(spark, table: str):
    return spark.read.jdbc(JDBC, f"public.{table}", properties=PROPS)


def write(df, table: str):
    (
        df.write.mode("overwrite")
        .option("truncate", "true")
        .jdbc(JDBC, f"curated.{table}", properties=PROPS)
    )


def main() -> None:
    spark = (
        SparkSession.builder.appName("sme-clean-all")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    lineage = F.current_timestamp().alias("_cleaned_at")

    # ---- sales ----------------------------------------------------------
    sales = (
        read(spark, "sales")
        .dropDuplicates(["id"])
        .withColumn("status", F.lower(F.col("status")))
        .filter(F.col("status").isin("paid", "pending", "cancelled"))
        .withColumn("currency", F.upper(F.col("currency")))
        .withColumn("sale_date", F.col("sale_date").cast(TimestampType()))
        .withColumn("total_amount", F.col("total_amount").cast(DecimalType(14, 2)))
        .withColumn("discount", F.col("discount").cast(DecimalType(14, 2)))
        .withColumn("_cleaned_at", lineage)
    )
    write(sales, "sales")

    # ---- sale_items -----------------------------------------------------
    items = (
        read(spark, "sale_items")
        .dropDuplicates(["id"])
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .filter(F.col("quantity") > 0)
        .withColumn("unit_price", F.col("unit_price").cast(DecimalType(14, 2)))
        .withColumn("unit_cost", F.col("unit_cost").cast(DecimalType(14, 2)))
        .withColumn("_cleaned_at", lineage)
    )
    write(items, "sale_items")

    # ---- inventory_movements --------------------------------------------
    moves = (
        read(spark, "inventory_movements")
        .dropDuplicates(["id"])
        .withColumn("movement_type", F.lower(F.col("movement_type")))
        .filter(F.col("movement_type").isin("in", "out", "adjust"))
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .withColumn("movement_date", F.col("movement_date").cast(TimestampType()))
        .withColumn("_cleaned_at", lineage)
    )
    write(moves, "inventory_movements")

    # ---- customers, suppliers, products, branches, businesses -----------
    for tbl, pk in [
        ("customers", "id"),
        ("suppliers", "id"),
        ("products", "id"),
        ("branches", "id"),
        ("businesses", "id"),
    ]:
        df = read(spark, tbl).dropDuplicates([pk]).withColumn("_cleaned_at", lineage)
        write(df, tbl)

    # ---- payments -------------------------------------------------------
    payments = (
        read(spark, "payments")
        .dropDuplicates(["id"])
        .withColumn("direction", F.lower(F.col("direction")))
        .filter(F.col("direction").isin("in", "out"))
        .withColumn("amount", F.col("amount").cast(DecimalType(14, 2)))
        .withColumn("currency", F.upper(F.col("currency")))
        .withColumn("payment_date", F.col("payment_date").cast(TimestampType()))
        .withColumn("_cleaned_at", lineage)
    )
    write(payments, "payments")

    # ---- purchase_orders ------------------------------------------------
    pos = (
        read(spark, "purchase_orders")
        .dropDuplicates(["id"])
        .withColumn("status", F.lower(F.col("status")))
        .filter(F.col("status").isin("open", "received", "cancelled"))
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .withColumn("unit_cost", F.col("unit_cost").cast(DecimalType(14, 2)))
        .withColumn("order_date", F.col("order_date").cast(TimestampType()))
        .withColumn("expected_date", F.col("expected_date").cast(TimestampType()))
        .withColumn("received_date", F.col("received_date").cast(TimestampType()))
        .withColumn("_cleaned_at", lineage)
    )
    write(pos, "purchase_orders")

    spark.stop()
    print("✅ Spark cleaning complete. curated.* populated.")


if __name__ == "__main__":
    main()