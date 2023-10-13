import boto3
import time
import json


# Create an SQS client using the localstack endpoint
sqs = boto3.client('sqs', endpoint_url='http://localhost:4566')

# Specify the URL of the queue you want to receive messages from
queue_url = 'http://localhost:4566/000000000000/login-queue'

# Number of messages to receive at a time
max_messages = 1
user_login = []
state = True

while True:
    # Receive messages from the queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=max_messages,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    # Check if there are messages in the response
    if 'Messages' in response:
        for message in response['Messages']:
            # Process the message
            #print(f"Received message: {message['Body']}")
            user_login.append(message['Body'])

            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            
    else:
        break
        #print("No messages in the queue. Waiting for messages...")
        #time.sleep(2)
masked_data = []

for item in user_login:
    item_dict = json.loads(item)

    item_dict['device_id'] = '*** Masked ***'
    item_dict['ip'] = '*** Masked ***'

    masked_item = json.dumps(item_dict)

    masked_data.append(masked_item)


print(masked_data)

