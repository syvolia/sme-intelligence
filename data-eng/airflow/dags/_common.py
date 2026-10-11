from datetime import timedelta
from airflow import DAG

DEFAULT_ARGS = {
    "owner": "sme-data-eng",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "depends_on_past": False,
}

def make_dag(dag_id: str, schedule: str, description: str, tags: list[str]) -> DAG:
    return DAG(
        dag_id=dag_id,
        description=description,
        schedule=schedule,
        start_date=None,   # replace with real date at deploy time
        catchup=False,
        default_args=DEFAULT_ARGS,
        tags=tags,
        max_active_runs=1,
    )