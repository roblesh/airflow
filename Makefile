envVar:
	mkdir ./dags ./logs ./plugins \
	&& echo "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

cassandraDb:
	docker-compose -f ./cassandra/docker-compose.yaml up -d

airflow:
	curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.3/docker-compose.yaml' \
	&& sed -i '' "s/{_PIP_ADDITIONAL_REQUIREMENTS:-}/{_PIP_ADDITIONAL_REQUIREMENTS:- pandas apache-airflow-providers-amazon apache-airflow-providers-apache-cassandra}/g" ./docker-compose.yaml

build:
	docker-compose up airflow-init

run: build
	docker-compose up \
	&& docker network connect airflow_default cassandra_cassandra_1

clean:
	docker-compose down --volumes --remove-clearorphans --rmi all \
	&& rm -f -r ./dags \
	&& rm -f -r ./logs \
	&& rm -f -r ./plugins \
	&& rm -f .env \
	&& rm -f docker-compose.yaml