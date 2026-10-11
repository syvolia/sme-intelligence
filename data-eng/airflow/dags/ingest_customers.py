from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from _common import DEFAULT_ARGS


def _check_customers() -> None:
    hook = PostgresHook(postgres_conn_id="sme_oltp")
    row = hook.get_first(
        """
        SELECT
          (SELECT count(*) FROM public.customers),
          (SELECT count(*) FROM public.suppliers),
          (SELECT count(*) FROM public.products)
        """
    )
    print(f"Ingest master: customers={row[0]} suppliers={row[1]} products={row[2]}")


with DAG(
    dag_id="ingest_customers",
    description="Land customer, supplier, product master data",
    schedule="@daily",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["ingest", "master"],
) as dag:
    PythonOperator(task_id="check_master", python_callable=_check_customers)