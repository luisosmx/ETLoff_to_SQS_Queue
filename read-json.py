import pandas as pd
import boto3
import json
from sqlalchemy import create_engine
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()

sqs = boto3.client('sqs', endpoint_url='http://localhost:4566')

queue_url = 'http://localhost:4566/000000000000/login-queue'

max_messages = 1
user_login = []

while True:
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
fernet = Fernet(encryption_key)
for item in user_login:
    item_dict = json.loads(item)

    print(f'Existing data:'{item_dict})

    if 'device_id' in item_dict and 'ip' in item_dict:
        item_dict['device_id'] = fernet.encrypt(item_dict['device_id'].encode()).decode()
        item_dict['ip'] = fernet.encrypt(item_dict['ip'].encode()).decode()
        masked_data.append(item_dict)
    else:
        print("Error: There is no data")

df = pd.DataFrame(masked_data)


db_config = {
    "host": "localhost",  
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')

df.to_sql("user_logins", engine, if_exists="replace", index=False)

engine.dispose()


