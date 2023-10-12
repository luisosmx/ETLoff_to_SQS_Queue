import boto3

# Configura el cliente de AWS SQS
sqs = boto3.client('sqs', region_name='us-east-1')

# Nombre de la cola SQS
cola_sqs_nombre = 'login-queue'

# Recupera los mensajes de la cola
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
    # Procesa cada mensaje JSON
    body = message['Body']
    # ... Realiza las operaciones necesarias con los datos JSON ...
    # Elimina el mensaje de la cola
    sqs.delete_message(
        QueueUrl=cola_sqs_nombre,
        ReceiptHandle=message['ReceiptHandle']
    )

