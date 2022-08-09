import uuid
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

dag = DAG("API_Data_To_Cassandra",
    description="A simple DAG that help to process data from an api call and send it to Cassandra Database",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["ETL_jobs"])


def extract(**context):
    task_instance = context["ti"]

    params = dict()
    base_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=ETH&category=ethereum-ecosystem&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h"

    response_from_api = requests.get(base_url, params=params)
    json_data = json.loads(response_from_api.text)
    task_instance.xcom_push("json_data", json_data)


def transform(**context):
    task_instance = context["ti"]
    data_from_api = task_instance.xcom_pull(task_ids='extract', 
                                            key='json_data'
                                            )


    tmp_file = json.dumps(data_from_api)
    with open("/tmp/api_data.json", "w") as data_file:
        data_file.write(tmp_file)


def load(**context):
    task_instance = context["ti"]
    Eth_Eco_data = task_instance.xcom_pull(task_ids='extract', 
                                            key='json_data'
                                            )
    cluster = Cluster(['172.27.0.3'], port = 9042)
    session = cluster.connect('eth_eco')

    for i in range(0, len(Eth_Eco_data)):
        print("testing:" +str(Eth_Eco_data[i]["market_cap_rank"]) + "," +str(Eth_Eco_data[i]["price_change_percentage_24h"]) + " --- type: " + str(type(Eth_Eco_data[i]["market_cap_rank"])) + "," + str(type(Eth_Eco_data[i]["price_change_percentage_24h"])))
        session.execute(
        """
        INSERT INTO eth_eco.stats_table ("uuid", "id", "symbol", "name", "current_price", "market_cap", "market_cap_rank", "total_volume", "high_24h", "low_24h", "price_change_24h", "price_change_percentage_24h") 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
        (uuid1().hex, Eth_Eco_data[i]["id"], Eth_Eco_data[i]["symbol"],
            Eth_Eco_data[i]["name"], float(Eth_Eco_data[i]["current_price"]),
            float(Eth_Eco_data[i]["market_cap"]), int(Eth_Eco_data[i]["market_cap_rank"]),
            int(Eth_Eco_data[i]["total_volume"]), float(Eth_Eco_data[i]["high_24h"]),
            float(Eth_Eco_data[i]["low_24h"]), float(Eth_Eco_data[i]["market_cap_rank"]),
            float(Eth_Eco_data[i]["price_change_percentage_24h"])
            )
        )
        print("Done Sending : ->", Eth_Eco_data[i])
    
    cluster.shutdown()

extract = PythonOperator( 
    task_id="extract", 
    python_callable=extract, 
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