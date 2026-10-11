from datetime import datetime

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from _common import DEFAULT_ARGS


with DAG(
    dag_id="sme_pipeline",
    description="End-to-end: ingest -> transform -> warehouse -> train",
    schedule="@daily",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["pipeline"],
) as dag:
    ingest_sales = TriggerDagRunOperator(
        task_id="ingest_sales", trigger_dag_id="ingest_sales", wait_for_completion=True
    )
    ingest_inventory = TriggerDagRunOperator(
        task_id="ingest_inventory", trigger_dag_id="ingest_inventory", wait_for_completion=True
    )
    ingest_customers = TriggerDagRunOperator(
        task_id="ingest_customers", trigger_dag_id="ingest_customers", wait_for_completion=True
    )
    transform = TriggerDagRunOperator(
        task_id="transform_data", trigger_dag_id="transform_data", wait_for_completion=True
    )
    warehouse = TriggerDagRunOperator(
        task_id="build_warehouse", trigger_dag_id="build_warehouse", wait_for_completion=True
    )
    train = TriggerDagRunOperator(
        task_id="train_models", trigger_dag_id="train_forecasting_models", wait_for_completion=True
    )

    [ingest_sales, ingest_inventory, ingest_customers] >> transform >> warehouse >> train