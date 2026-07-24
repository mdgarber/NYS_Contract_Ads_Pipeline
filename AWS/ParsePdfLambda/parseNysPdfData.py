# Extract text from PDF stored in S3
import io
import boto3
from pypdf import PdfReader

def lambda_handler(event, context):
    s3 = boto3.client("s3")

    bucket_name = 'nys-ads-raw-data'
    s3_key = 'NYC_ads_list.pdf'

    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    pdf_bytes = response["Body"].read()

    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"

    return {
        "statusCode": 200,
        "body": text
    }

print(lambda_handler({}, None))