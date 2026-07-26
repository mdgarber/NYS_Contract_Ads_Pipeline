import json
import boto3
import requests

def lambda_handler(event, context):
     # Variables
    web_url = 'https://www.nyscr.ny.gov/Ads/GenerateSearchPdf'
    bucket_name = 'nys-ads-raw-data'
    s3_key = 'NYC_ads_list.pdf'

    # 1. Initialize the S3 Client
    # automatically pick up  AWS credentials (IAM role, env vars, or ~/.aws/credentials)
    s3_client = boto3.client('s3')

    # 2. Open the connection to the web file with streaming enabled
    with requests.get(web_url, stream=True) as response:
        response.raise_for_status()
        
        # 3. Use 'raw' to get the raw socket response stream
        # upload_fileobj expects a file-like object; response.raw acts exactly like one
        s3_client.upload_fileobj(
            Fileobj=response.raw, 
            Bucket=bucket_name, 
            Key=s3_key
        )
            
        print(f"Successfully streamed {web_url} directly into s3://{bucket_name}/{s3_key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Lambda is OK!')
    }
