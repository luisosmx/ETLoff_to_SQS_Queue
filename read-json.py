import pandas as pd
import boto3
import json
import psycopg2
from sqlalchemy import create_engine

# Create an SQS client using the localstack endpoint
sqs = boto3.client('sqs', endpoint_url='http://localhost:4566')

# Specify the URL of the queue you want to receive messages from
queue_url = 'http://localhost:4566/000000000000/login-queue'

# Number of messages to receive at a time
max_messages = 1
user_login = []

while True:
    # Receive messages from the queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=max_messages,
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    if 'Messages' in response:
        for message in response['Messages']:
            user_login.append(message['Body'])

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
    else:
        break

masked_data = []

for item in user_login:
    item_dict = json.loads(item)
    item_dict['device_id'] = '*** Masked ***'
    item_dict['ip'] = '*** Masked ***'
    masked_data.append(item_dict)

df = pd.DataFrame(masked_data)


db_config = {
    "host": "localhost",  # Cambia esto al host de tu servidor PostgreSQL
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')

# Guardar el DataFrame en la tabla "user_logins"
df.to_sql("user_logins", engine, if_exists="replace", index=False)

# Cerrar la conexión
engine.dispose()


