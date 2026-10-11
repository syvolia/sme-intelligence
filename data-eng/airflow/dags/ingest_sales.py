from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from _common import DEFAULT_ARGS


def _check_source() -> None:
    """
    In a real deployment this would pull from a POS/ERP system.
    Here we verify the OLTP source has fresh rows and log the count.
    """
    hook = PostgresHook(postgres_conn_id="sme_oltp")
    row = hook.get_first(
        "SELECT count(*), max(sale_date)::date FROM public.sales"
    )
    print(f"Ingest sales: {row[0]} rows, latest {row[1]}")


with DAG(
    dag_id="ingest_sales",
    description="Land sales transactions from the source system",
    schedule="@hourly",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["ingest", "sales"],
) as dag:
    PythonOperator(
        task_id="check_source",
        python_callable=_check_source,
    )