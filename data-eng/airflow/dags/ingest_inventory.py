from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from _common import DEFAULT_ARGS


def _check_source() -> None:
    hook = PostgresHook(postgres_conn_id="sme_oltp")
    row = hook.get_first(
        "SELECT count(*), max(movement_date)::date FROM public.inventory_movements"
    )
    print(f"Ingest inventory: {row[0]} rows, latest {row[1]}")


with DAG(
    dag_id="ingest_inventory",
    description="Land inventory movements from the source system",
    schedule="@daily",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["ingest", "inventory"],
) as dag:
    PythonOperator(task_id="check_source", python_callable=_check_source)