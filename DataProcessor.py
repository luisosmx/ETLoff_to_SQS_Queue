import pandas as pd
import boto3
import json
from sqlalchemy import create_engine
from cryptography.fernet import Fernet

class DataProcessor:
    def __init__(self, encryption_key):
        self.sqs = boto3.client('sqs', region_name='us-east-1', endpoint_url='http://localhost:4566')
        self.queue_url = 'http://localhost:4566/000000000000/login-queue'
        self.max_messages = 1
        self.user_login = []
        self.fernet = Fernet(encryption_key)

    def receive_data_from_queue(self):
        print("Receiving data from SQS queue...")
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=self.max_messages,
                MessageAttributeNames=['All'],
                VisibilityTimeout=0,
                WaitTimeSeconds=0
            )

            if 'Messages' in response:
                for message in response['Messages']:
                    print(f"Received message: {message['Body']}")

                    self.user_login.append(message['Body'])

                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
            else:
                break


    def mask_sensitive_data(self):
        print("Encrypting sensitive data...")
        masked_data = []
        fernet = Fernet(encryption_key)
        for item in self.user_login:
            item_dict = json.loads(item)

            if 'device_id' in item_dict and 'ip' in item_dict:
                item_dict['device_id'] = fernet.encrypt(item_dict['device_id'].encode()).decode()
                item_dict['ip'] = fernet.encrypt(item_dict['ip'].encode()).decode()
                masked_data.append(item_dict)
            else:
                print("Error: There is no data")

        return masked_data  

    def process_and_store_data(self):
        print("Processing and storing data in PostgreSQL...")
        data_to_store = self.mask_sensitive_data()
        df = pd.DataFrame(data_to_store)

        db_config = {
            "host": "localhost",
            "database": "postgres",
            "user": "postgres",
            "password": "postgres"
        }

        engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')

        df.to_sql("user_logins", engine, if_exists="replace", index=False)

        engine.dispose()
        print("Data processing and storage complete!")

if __name__ == "__main__":
    encryption_key = Fernet.generate_key()
    encryption_key_str = encryption_key.decode()

    data_processor = DataProcessor(encryption_key_str)
    data_processor.receive_data_from_queue()
    data_processor.process_and_store_data()
