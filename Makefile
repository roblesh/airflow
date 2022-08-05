getDockerComposeFile:
	curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.3/docker-compose.yaml'

editFile: getDockerComposeFile
	sed -i '' "s/{_PIP_ADDITIONAL_REQUIREMENTS:-}/{_PIP_ADDITIONAL_REQUIREMENTS:- apache-airflow-providers-amazon}/g" ./docker-compose.yaml

createEnvVariables: editFile
	mkdir ./dags ./logs ./plugins \
	&& echo "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

build: createEnvVariables
	docker-compose up airflow-init

run: build
	docker-compose up

clean:
	docker-compose down --volumes --remove-clearorphans --rmi all \
	&& rm -f -r ./dags \
	&& rm -f -r ./logs \
	&& rm -f -r ./plugins \
	&& rm -f .env \
	&& rm -f docker-compose.yaml