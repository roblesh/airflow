from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.apache.cassandra.hooks.cassandra import CassandraHook
from cassandra.cluster import Cluster
from uuid import uuid1
import json
import requests
import pprint

cassandra_hook = CassandraHook("cassandra_default")
pp = pprint.PrettyPrinter(indent=4)

dag = DAG("CSV_To_Cassandra",
    description="A simple DAG that help to process data from a local folder and send it to Cassandra Database",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["ETL_jobs"])

def get_rest_api_data(**context):
    task_instance = context["ti"]

    params = dict()
    base_url = "http://api.mediastack.com/v1/news"
    params["access_key"] = "YOUR_API_KEY"
    params['sources'] = "cnn,bbc" 

    response_from_api = requests.get(base_url, params=params)
    json_data = json.loads(response_from_api.text)
    task_instance.xcom_push("json_data", json_data)


def extract(**context):
    task_instance = context["ti"]

    params = dict()
    base_url = "http://api.mediastack.com/v1/news"
    params["access_key"] = "YOUR_API_KEY"
    params['sources'] = "cnn,bbc" 

    response_from_api = requests.get(base_url, params=params)
    json_data = json.loads(response_from_api.text)
    task_instance.xcom_push("json_data", json_data)


def transform(**context):
    task_instance = context["ti"]
    data_from_api = task_instance.xcom_pull(task_ids='get_rest_api_data', 
                                            key='json_data'
                                            )
    data_to_write = json.dumps(data_from_api)
    with open("/tmp/api_data.json", "w") as data_file:
        data_file.write(data_to_write)


def load(**context):
    task_instance = context["ti"]
    Live_News_data = task_instance.xcom_pull(task_ids='get_rest_api_data', 
                                            key='json_data'
                                            )
    cluster = Cluster(['127.0.0.1'], port = 9042)
    session = cluster.connect('news')

    for i in range(0, len(Live_News_data['data'])):
        session.execute(
        """
        INSERT INTO news.news_table (uuiid, author, title, description, url, source, image, category, language, country, published_at)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s )
        """,(uuid1(), Live_News_data['data'][i]["author"], Live_News_data['data'][i]["title"], 
        Live_News_data['data'][i]["description"], Live_News_data['data'][i]["url"], 
        Live_News_data['data'][i]["source"], Live_News_data['data'][i]["image"],
        Live_News_data['data'][i]["category"], Live_News_data['data'][i]["language"], 
        Live_News_data['data'][i]["country"], Live_News_data['data'][i]["published_at"],
        )
        )
        print("Done Sending : ->",Live_News_data['data'][i])

extract = PythonOperator( 
    task_id="extract", 
    python_callable=get_rest_api_data, 
    dag=dag
    )

transform = PythonOperator(
    task_id='transform',
    python_callable=transform,
    op_kwargs={
        'filename': "/tmp/api_data.json",
        'key': 'api_data.json',
        'bucket_name': 'anantworkflowresult',
    }, 
    dag=dag,)

load = PythonOperator(
    task_id="load",
    python_callable=load,
    dag=dag,
)


extract >> transform >> load