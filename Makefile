getDockerComposeFile:
	curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.3/docker-compose.yaml'

startDatabase: getDockerComposeFile
	docker-compose up airflow-init

run: startDatabase
	docker-compose up

clean:
	docker-compose down --volumes --remove-orphans \
	&& rm -d ./dags \
	&& rm -d ./logs \
	&& rm -d ./plugins