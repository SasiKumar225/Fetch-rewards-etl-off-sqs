**Pre-requisite**
- Docker
- Docker Compose
- AWS CLI Local (awscli-local)
- psql (PostgreSQL command-line interface)
- Python 3.x

**SET UP INSTRUCTIONS**
- **CLONE THE REPOSITORY**
```
sh

https://github.com/SasiKumar225/Fetch-rewards-etl-off-sqs.git
```
Clones the repo containing the project files and scripts

- **Enter the repo**
```sh
Cd Fetch-rewards-etl-off-sqs
```
Navigate into the cloned repo directory

- **Check Installation**
```sh
make check-python              # Test if Python3 is available
make check-docker              # Test if Docker is available
make check-docker-compose      # Test if Docker-Compose is available
```
Verify the required tools are installed and accessible

- **Download the docker images localstack and postgres required for the application**
```sh
docker pull fetchdocker/data-takehome-postgres
docker pull fetchdocker/data-takehome-localstack
```
Pull the necessary Docker images from docker hub repo

- **Start docker container**
```sh
Docker – compose up -d
```
Start the containers defined in 'docker-compose.yaml'

- **Create the Queue**
```sh
awslocal sqs create-queue --queue-name login-queue
```

- **List the queue to verify**
```sh
awslocal sqs list-queues
```

- **Read a message from the queue using awslocal**
```sh
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
```
Uses 'awslocal' to receive messages from the local AWS queue

- **connect to the postgress database and verify table is created**
```sh
psql -d fetch_DB -U postgres -p 5433 -h localhost -W
```
Connects to the Postgres sql database as the user 'postgres' on port 5433, It ask password 

- **List Tables**
  ```sh
  \dt
  ```
This command displays list of all tables in the current database




- **Run the python script**
```sh
python etl_script.py
```
Run the python code to execute etl operation.





- **Notes**
- Ensure Docker and Docker Compose are installed and running before starting.

- Modify port numbers (-p) or other configurations in commands as per your setup.

- For AWS CLI commands (awslocal), ensure the local AWS services are properly configured and running.
