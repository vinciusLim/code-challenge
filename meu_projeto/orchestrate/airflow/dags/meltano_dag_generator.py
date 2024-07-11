from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

def tap_csv_to_target_csv_job():
    print("Executing tap-csv-to-target-csv job")

def tap_postgres_to_target_csv_job():
    print("Executing tap-postgres-to-target-csv job")

def tap_csv_to_target_postgres_job():
    print("Executing tap-csv-to-target-postgres job")

with DAG(
    'meltano_jobs_dag',
    default_args={'owner': 'airflow'},
    description='Run Meltano jobs in sequence',
    schedule_interval='@Daily',  
    start_date=datetime(2024, 7, 11),
    catchup=False,
) as dag:


    tap_csv_to_target_csv_task = PythonOperator(
        task_id='tap_csv_to_target_csv',
        python_callable=tap_csv_to_target_csv_job,
    )

    tap_postgres_to_target_csv_task = PythonOperator(
        task_id='tap_postgres_to_target_csv',
        python_callable=tap_postgres_to_target_csv_job,
    )

    tap_csv_to_target_postgres_task = PythonOperator(
        task_id='tap_csv_to_target_postgres',
        python_callable=tap_csv_to_target_postgres_job,
    )

[tap_csv_to_target_csv_task, tap_postgres_to_target_csv_task] >> tap_csv_to_target_postgres_task
