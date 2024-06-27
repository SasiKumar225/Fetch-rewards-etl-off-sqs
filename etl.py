import boto3
import hashlib
import json
import psycopg2
from botocore.config import Config

# Configuration
SQS_QUEUE_URL = 'http://fetch-localstack-1:4566/000000000000/login-queue'  # Use service name from Docker Compose
DB_HOST = 'localhost'  # Use 'localhost' when connecting from host to container
DB_PORT = 5433  # Host port specified in docker-compose.yml
DB_NAME = 'fetch_DB'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
AWS_ENDPOINT_URL = 'http://fetch-localstack-1:4566'  # Use service name and port from Docker Compose

# Attempt to connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        connect_timeout=5  # Add a timeout for connection attempt
    )
    print("Successfully connected to PostgreSQL!")
except psycopg2.OperationalError as e:
    print(f"Unable to connect to PostgreSQL: {e}")
    exit(1)

cur = conn.cursor()

# Connect to SQS
session = boto3.Session()
sqs = session.client('sqs', endpoint_url=AWS_ENDPOINT_URL, config=Config(region_name='us-east-1'))

def mask_pii(value):
    return hashlib.sha256(value.encode()).hexdigest()

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def process_message(message):
    data = json.loads(message['Body'])
    data = flatten_json(data)

    user_id = data.get('user_id')
    device_type = data.get('device_type')
    masked_ip = mask_pii(data.get('ip'))
    masked_device_id = mask_pii(data.get('device_id'))
    locale = data.get('locale')
    app_version = data.get('app_version')
    create_date = data.get('create_date')

    cur.execute("""
        INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date))
    conn.commit()

def main():
    while True:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )

        messages = response.get('Messages', [])
        if not messages:
            break

        for message in messages:
            process_message(message)
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )

if __name__ == '__main__':
    main()
