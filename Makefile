envVar:
	mkdir ./dags ./logs ./plugins \
	&& echo "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

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