from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from _common import DEFAULT_ARGS


with DAG(
    dag_id="build_warehouse",
    description="dbt run + dbt test -> analytics.*",
    schedule="@daily",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["warehouse", "dbt"],
) as dag:
    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="sme-intelligence-dbt:latest",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="sme-intelligence_default",
        command=[
            "bash", "-c",
            "cd /dbt && dbt deps && "
            "dbt run --vars '{source_schema: curated}' --profiles-dir /dbt && "
            "dbt test --profiles-dir /dbt",
        ],
    )