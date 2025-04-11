from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from refresh_script import leagues_data_ingestion

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    'refresh_data',
    default_args=default_args,
    start_date= datetime(2024, 4, 9),
    description='A simple DAG to refresh data',
    schedule_interval='0 */6 * * *', #None, #   #'@daily',
    catchup=False
)

# refresh standings
# refresh_task =  BashOperator(
#     task_id='refresh_data_script',
#     bash_command='python3 /opt/airflow/dags/refresh_script.py',
#     dag=dag,
# )

refresh_task = PythonOperator(
    task_id='refresh_data_function',
    python_callable=leagues_data_ingestion,
    dag=dag,
)