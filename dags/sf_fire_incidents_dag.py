from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
sys.path.append('/opt/airflow/scripts')
from extract_sf_fire_data import main as extract_main

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'sf_fire_incidents_pipeline',
    default_args=default_args,
    description='SF Fire Incidents ELT Pipeline',
    schedule_interval='@daily',  # Run daily
    catchup=False,
    tags=['sf', 'fire', 'incidents', 'etl'],
)

# Task 1: Extract and load raw data
extract_load_task = PythonOperator(
    task_id='extract_and_load_raw_data',
    python_callable=extract_main,
    dag=dag,
)

# Task 2: Run DBT models
dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir ./',
    dag=dag,
)

# Task 3: Run DBT tests
dbt_test_task = BashOperator(
    task_id='run_dbt_tests',
    bash_command='cd /opt/airflow/dbt_project && dbt test --profiles-dir ./',
    dag=dag,
)

# Task 4: Generate documentation
dbt_docs_task = BashOperator(
    task_id='generate_dbt_docs',
    bash_command='cd /opt/airflow/dbt_project && dbt docs generate --profiles-dir ./',
    dag=dag,
)

# Set task dependencies
extract_load_task >> dbt_run_task >> dbt_test_task >> dbt_docs_task