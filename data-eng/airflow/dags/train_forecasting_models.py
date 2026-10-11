from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from _common import DEFAULT_ARGS


with DAG(
    dag_id="train_forecasting_models",
    description="Retrain the demand forecasting model and promote the champion",
    schedule="@weekly",
    start_date=datetime(2025, 3, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["ml", "forecast"],
) as dag:
    train = DockerOperator(
        task_id="train_demand",
        image="sme-intelligence-ml:latest",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="sme-intelligence_default",
        command=["python", "-m", "src.training.train_demand"],
        environment={
            "DATABASE_URL": "postgresql://sme:sme@postgres:5432/sme_oltp",
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
            "MLFLOW_DEMAND_MODEL_NAME": "demand_forecast_xgboost",
        },
    )