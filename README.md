# Airflow

I created this repo in order to give examples on how to locally spin up an instance of Airflow on MacOS and utilize several key functionalities.

In order to ramp up your Airflow environment for local learning and development, get started with the following instructions:

1. Install [Docker Community Edition (CE)](https://docs.docker.com/engine/installation/) on your workstation. You may need to configure your Docker instance to use 4.00 GB of memory for all containers to run properly.

2. Install [Docker Compose v1.29.1](https://docs.docker.com/compose/install/) or newer on your workstation.

3. Install [Python3](https://www.python.org/downloads/macos/) on your machine.

4. Create the folder where your code will be cloned to by using a shell/terminal/IDE to run: ```mkdir airflow-local```

5. Create a python virtual environment for your airflow packages to not interfere with any other python development you may have. Inside of your new airflow-local folder, run: ```python3 -m venv .venv```, and ```source .venv/bin/activate```.

6. Then, ```pip install --upgrade pip``` and ```pip install apache-airflow```.

7. Now you're ready to get the fun stuff going! Clone this repo into your airflow-local folder and inside of the terminal, run: ```make run```. You will begin to see a bunch of wizardry happen that gets your airflow server up and running, all inside of a Docker container!

8. Open a browser and enter: ```http://localhost:8080/``` for the url, and enter airflow for username and password. Voila!
