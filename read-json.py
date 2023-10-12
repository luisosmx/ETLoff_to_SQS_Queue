import boto3

sqs = boto3.client('sqs', region_name='us-east-1', aws_access_key_id='fake-key', aws_secret_access_key='fake-secret')

cola_sqs_nombre = 'login-queue'

response = sqs.receive_message(
    QueueUrl=cola_sqs_nombre,
    AttributeNames=[
        'All'
    ],
    MaxNumberOfMessages=10,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)

messages = response.get('Messages', [])

for message in messages:
    body = message['Body']
    sqs.delete_message(
        QueueUrl=cola_sqs_nombre,
        ReceiptHandle=message['ReceiptHandle']
    )

