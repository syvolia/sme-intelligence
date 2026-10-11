"""
Spark cleaning job.

Reads OLTP tables from `public.*`, applies light cleaning, writes to
`curated.*`. Downstream, dbt staging reads from `curated.*` (via the
`source_schema` dbt var) instead of `public.*`.

Local (inside the spark container):
    /opt/spark/bin/spark-submit \
      --master 'local[*]' \
      --jars /opt/spark/jars/postgresql-42.7.3.jar \
      /opt/spark/work-dir/jobs/clean_all.py

CI (GitHub Actions):
    spark-submit \
      --master 'local[2]' \
      --driver-memory 2g \
      --jars /tmp/postgresql.jar \
      data-eng/spark/jobs/clean_all.py
"""
import os
import re

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DecimalType,
    IntegerType,
    TimestampType,
)


# ---------------------------------------------------------------------------
# Env var normalization — defends against secrets pasted with extra bits
# ---------------------------------------------------------------------------
def _clean_host(raw: str) -> str:
    """
    Accept any of:
      ep-xxx.neon.tech
      ep-xxx.neon.tech/neondb
      postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
    and return just the hostname.
    """
    s = raw.strip()

    # Strip any scheme prefix
    s = re.sub(r"^(jdbc:)?postgres(ql)?://", "", s)

    # Strip user:pass@ prefix if present
    if "@" in s:
        s = s.split("@", 1)[1]

    # Drop everything after the first slash (path, params, etc.)
    s = s.split("/", 1)[0]

    # Drop any trailing colon+port the user might have added
    s = s.split(":", 1)[0] if ":" in s else s

    return s.strip()


def _clean_db(raw: str) -> str:
    """Return just the database name — no slashes, no params."""
    s = raw.strip()
    s = s.split("?", 1)[0]          # drop query params
    s = s.split("/", 1)[0] if s.startswith("/") else s
    return s.strip()


def _clean_port(raw: str) -> str:
    """Return just the digits of the port, defaulting to 5432."""
    s = raw.strip()
    m = re.search(r"\d+", s)
    return m.group(0) if m else "5432"


# ---------------------------------------------------------------------------
# Connection configuration
# ---------------------------------------------------------------------------
POSTGRES_HOST = _clean_host(os.environ.get("POSTGRES_HOST", "postgres"))
POSTGRES_PORT = _clean_port(os.environ.get("POSTGRES_PORT_INTERNAL", "5432"))
POSTGRES_DB = _clean_db(os.environ.get("POSTGRES_DB", "sme_oltp"))
POSTGRES_USER = os.environ.get("POSTGRES_USER", "sme").strip()
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "sme").strip()

# Optional — set to "require" for Neon / hosted Postgres. Empty means no
# sslmode parameter is appended (local Docker Postgres).
POSTGRES_SSLMODE = os.environ.get("POSTGRES_SSLMODE", "").strip()

_ssl_suffix = f"?sslmode={POSTGRES_SSLMODE}" if POSTGRES_SSLMODE else ""
JDBC = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}{_ssl_suffix}"

PROPS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "driver": "org.postgresql.Driver",
}


# Print a sanitized summary of what we're connecting to (never log the
# password). Helps debug CI failures without leaking secrets.
def _mask(s: str) -> str:
    if not s:
        return "<empty>"
    if len(s) <= 4:
        return "*" * len(s)
    return s[0] + "*" * (len(s) - 2) + s[-1]


print("→ Spark job starting")
print(f"  host:     {POSTGRES_HOST}")
print(f"  port:     {POSTGRES_PORT}")
print(f"  database: {POSTGRES_DB}")
print(f"  user:     {POSTGRES_USER}")
print(f"  password: {_mask(POSTGRES_PASSWORD)}")
print(f"  sslmode:  {POSTGRES_SSLMODE or '(disabled)'}")
print(f"  JDBC URL: {JDBC}")


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
def read(spark: SparkSession, table: str):
    return spark.read.jdbc(JDBC, f"public.{table}", properties=PROPS)


def write(df, table: str):
    (
        df.write.mode("overwrite")
        .option("truncate", "true")
        .jdbc(JDBC, f"curated.{table}", properties=PROPS)
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
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