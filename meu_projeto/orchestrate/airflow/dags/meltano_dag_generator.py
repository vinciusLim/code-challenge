from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import os


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("meltano_jobs", default_args=default_args, schedule_interval="@daily")

tap_csv_to_target_csv = BashOperator(
    task_id='tap_csv_to_target_csv',
    bash_command='cd /home/vinicius/code-challenge/meu_projeto && meltano run tap-csv-to-target-csv',
    env={
        "PATH": os.getenv("PATH"),
        "MELTANO_PROJECT_ROOT": "/home/vinicius/code-challenge/meu_projeto",
    },
    dag=dag,
)

tap_postgres_to_target_csv = BashOperator(
    task_id='tap_postgres_to_target_csv',
    bash_command='cd /home/vinicius/code-challenge/meu_projeto && meltano run tap-postgres-to-target-csv',
    env={
        "PATH": os.getenv("PATH"),
        "MELTANO_PROJECT_ROOT": "/home/vinicius/code-challenge/meu_projeto",
    },
    dag=dag,
)

tap_csv_to_target_postgres = BashOperator(
    task_id='tap_csv_to_target_postgres',
    bash_command='cd /home/vinicius/code-challenge/meu_projeto && meltano run tap_csv_to_target_postgres',
    env={
        "PATH": os.getenv("PATH"),
        "MELTANO_PROJECT_ROOT": "/home/vinicius/code-challenge/meu_projeto",
    },
    dag=dag,
)

[tap_csv_to_target_csv, tap_postgres_to_target_csv]>> tap_csv_to_target_postgres
