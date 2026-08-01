# Extract text from PDF stored in S3 and write the parsed text to S3 for downstream processing.
import io
import json
import logging
import os

import boto3

try:
    from pypdf import PdfReader
except ImportError as exc:
    logging.basicConfig(level=logging.INFO, force=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.error("pypdf import failed. Ensure the Lambda layer is built for the correct Python runtime and attached to the function.")
    raise ImportError("pypdf is not available in the Lambda runtime") from exc

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.propagate = True


def lambda_handler(event, context):
    logger.info("Starting PDF parsing.")
    s3 = boto3.client("s3")
    lambda_client = boto3.client("lambda")

    bucket_name = os.environ.get("nys-ads-raw-data") or "nys-ads-raw-data"
    logger.info("Bucket name: %s assigned", bucket_name)

    s3_key = os.environ.get("NYS_ads_list.pdf") or "NYS_ads_list.pdf"
    logger.info("S3 key: %s assigned", s3_key)

    output_prefix = os.environ.get("OUTPUT_PREFIX") or os.environ.get("nys-ads-parsed") or "nys-ads-parsed"
    logger.info("Output prefix: %s assigned", output_prefix)
    #cleaner_lambda_name = os.environ.get("CLEANER_LAMBDA_NAME") or os.environ.get("cleanNysData")

    output_prefix = output_prefix.rstrip("/")
    logger.info("Output prefix after stripping trailing slash: %s", output_prefix)

    output_S3_key = f"{output_prefix}/{os.path.basename(s3_key).rsplit('.', 1)[0]}.txt"

    logger.info("Output S3 key: %s", output_S3_key)
    logger.info("Starting to read PDF from S3: %s/%s", bucket_name, s3_key)
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

#    logger.error("PDF parsing - end of process. Now to return the response to the caller....")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": bucket_name,
            "source_key": s3_key,
            "output_S3_key": output_S3_key
        })
    }

# TODO: lambda is timing out in AWS. continue debugging
# TODO: make sure file exports to s3://nys-ads-raw-data/parsed-text/
# TODO: find way to view and validate the extracted text