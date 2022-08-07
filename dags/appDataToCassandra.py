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
    data_to_write = json.dumps(data_from_api)
    with open("/tmp/api_data.json", "w") as data_file:
        data_file.write(data_to_write)


def load(**context):
    task_instance = context["ti"]
    Eth_Eco_data = task_instance.xcom_pull(task_ids='extract', 
                                            key='json_data'
                                            )
    cluster = Cluster(['172.27.0.3'], port = 9042)
    session = cluster.connect('eth_eco')

    for i in range(0, len(Eth_Eco_data['data'])):
        session.execute(
        """
        INSERT INTO eth_eco.eco_table (uuid, id, symbol, name, image, current_price, market_cap, market_cap_rank, fully_diluted_valuation, total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h, circulating_supply, total_supply, max_supply, ath, ath_change_percentage, ath_date, atl, atl_change_percentage, atl_date, roi, last_updated, price_change_percentage_1h_in_currency)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s )
        """,(uuid1(), Eth_Eco_data['data'][i]["id"], Eth_Eco_data['data'][i]["symbol"], 
        Eth_Eco_data['data'][i]["name"], Eth_Eco_data['data'][i]["image"], 
        Eth_Eco_data['data'][i]["current_price"], Eth_Eco_data['data'][i]["market_cap"],
        Eth_Eco_data['data'][i]["market_cap_rank"], Eth_Eco_data['data'][i]["fully_diluted_valuation"], 
        Eth_Eco_data['data'][i]["total_volume"], Eth_Eco_data['data'][i]["high_24h"],
        Eth_Eco_data['data'][i]["low_24h"], Eth_Eco_data['data'][i]["price_change_24h"],
        Eth_Eco_data['data'][i]["price_change_percentage_24h"], Eth_Eco_data['data'][i]["market_cap_change_24h"], 
        Eth_Eco_data['data'][i]["market_cap_change_percentage_24h"], Eth_Eco_data['data'][i]["circulating_supply"],
        Eth_Eco_data['data'][i]["total_supply"], Eth_Eco_data['data'][i]["max_supply"],
        Eth_Eco_data['data'][i]["ath"], Eth_Eco_data['data'][i]["ath_change_percentage"], 
        Eth_Eco_data['data'][i]["ath_date"], Eth_Eco_data['data'][i]["atl"],
        Eth_Eco_data['data'][i]["atl_change_percentage"], Eth_Eco_data['data'][i]["atl_date"],
        Eth_Eco_data['data'][i]["roi"], Eth_Eco_data['data'][i]["last_updated"], 
        Eth_Eco_data['data'][i]["price_change_percentage_1h_in_currency"],
        )
        )
        print("Done Sending : ->", Eth_Eco_data['data'][i])

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