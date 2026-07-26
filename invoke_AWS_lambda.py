import boto3
import json

client = boto3.client("lambda")

response = client.invoke(
    FunctionName="YOUR_LAMBDA_NAME",    #THIS GUY RIGHT HERE
    InvocationType="RequestResponse",
    Payload=json.dumps({})
)

print(response["Payload"].read().decode("utf-8"))