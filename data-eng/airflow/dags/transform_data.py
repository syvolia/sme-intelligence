from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from _common import DEFAULT_ARGS


with DAG(
    dag_id="transform_data",
    description="Run Spark cleaning: public.* -> curated.*",
    schedule="@daily",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["transform", "spark"],
    template_searchpath=["/opt/airflow/dags"],
) as dag:
    spark_clean = DockerOperator(
        task_id="spark_clean_all",
        image="sme-intelligence-spark:latest",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="sme-intelligence_default",
        command=[
            "/opt/spark/bin/spark-submit",
            "--master", "local[*]",
            "--jars", "/opt/spark/jars/postgresql-42.7.3.jar",
            "/opt/spark/work-dir/jobs/clean_all.py",
        ],
        environment={
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT_INTERNAL": "5432",
            "POSTGRES_DB": "{{ conn.sme_oltp.schema }}",
            "POSTGRES_USER": "{{ conn.sme_oltp.login }}",
            "POSTGRES_PASSWORD": "{{ conn.sme_oltp.password }}",
        },
    )