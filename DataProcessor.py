import pandas as pd
import boto3
import json
from sqlalchemy import create_engine

class DataProcessor:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name='us-east-1', endpoint_url='http://localhost:4566')
        self.queue_url = 'http://localhost:4566/000000000000/login-queue'
        self.max_messages = 1
        self.user_login = []

    def receive_data_from_queue(self):
        """Receive data from an SQS queue and mask sensitive information."""

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
                    self.user_login.append(message['Body'])

                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
            else:
                break

    def mask_sensitive_data(self):
        """Mask sensitive information in the received data."""
        
        print("Masking sensitive data...")

        masked_data = []

        for item in self.user_login:
            item_dict = json.loads(item)
            item_dict['device_id'] = '*** Masked ***'
            item_dict['ip'] = '*** Masked ***'
            masked_data.append(item_dict)

        return masked_data

    def process_and_store_data(self):
        """Process and store the data in a PostgreSQL database."""
        
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
    data_processor = DataProcessor()
    data_processor.receive_data_from_queue()
    data_processor.process_and_store_data()


awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue