# Extract text from PDF stored in S3 and write the parsed text to S3 for downstream processing.
import io
import json
import logging
import os

import boto3
from pypdf import PdfReader

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    lambda_client = boto3.client("lambda")

    bucket_name = os.environ.get("nys-ads-raw-data")
    s3_key = os.environ.get("NYC_ads_list.pdf")
    output_prefix = os.environ.get("nys-ads-parsed")
    cleaner_lambda_name = os.environ.get("cleanNysData")

    output_S3_key = f"{output_prefix.rstrip('/')}/{os.path.basename(s3_key).rsplit('.', 1)[0]}.txt"

    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        pdf_bytes = response["Body"].read()
    except Exception:
        logger.exception("Failed to read PDF from S3: %s/%s", bucket_name, s3_key)
        raise

    reader = PdfReader(io.BytesIO(pdf_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text.strip())

    text = "\n\n".join(text_parts)
    if not text.strip():
        raise RuntimeError(f"No text extracted from PDF: {bucket_name}/{s3_key}")

    s3.put_object(
        Bucket=bucket_name,
        Key=output_S3_key,
        Body=text.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )

    logger.info("Uploaded extracted text to s3://%s/%s", bucket_name, output_S3_key)

    if cleaner_lambda_name:
        payload = {
            "bucket": bucket_name,
            "key": output_S3_key,
            "source_key": s3_key,
        }
        lambda_client.invoke(
            FunctionName=cleaner_lambda_name,
            InvocationType="Event",
            Payload=json.dumps(payload),
        )
        logger.info("Triggered cleaner Lambda: %s", cleaner_lambda_name)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": bucket_name,
            "source_key": s3_key,
            "output_S3_key": output_S3_key
        })
    }


# TODO: make sure file exports to s3://nys-ads-raw-data/parsed-text/
# TODO: find way to view and validate the extracted text
# TODO: lambda is failing in AWS due to lambda layer issue. Repackage the layer.zip file and re-upload to AWS.