# Extract text from PDF stored in S3 and write the parsed text to S3 for downstream processing.
from csv import reader
import io
import json
import logging
import os
import boto3
import sys
from pypdf import PdfReader

def lambda_handler(event, context):
    logging.basicConfig(level=logging.INFO, force=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.propagate = True

    s3_client = boto3.client('s3')

    source_file = os.environ.get('SOURCE_FILE', 'NYS_ads_list.pdf')
    source_bucket = os.environ.get('SOURCE_BUCKET', 'nys-ads-raw-data')
    target_file = os.environ.get('TARGET_FILE', 'raw_text.txt')
    target_bucket = os.environ.get('TARGET_BUCKET', 'nys-ads-raw-data')

    # Get the PDF stored in S3
    pdf_file = s3_client.get_object(Bucket=source_bucket, Key=source_file)['Body'].read()
    reader = PdfReader(io.BytesIO(pdf_file))
    number_of_pages = len(reader.pages)

    # Loop through each page and append extracted text to target file
    try:
        with open('/tmp/' + target_file, 'w') as f:
            for i in range(0, number_of_pages):
                logger.info("Extracting text from page #%s", i)
                page = reader.pages[i]
                text = page.extract_text()
                f.write(text)
                logger.info("Text extracted from page #%s", i)
        logger.info("Writing extracted text to S3")
        s3_client.upload_file('/tmp/' + target_file, target_bucket, target_file)
        logger.info("Text successfully written to S3")
    except:
        logger.error("Unexpected error: ", sys.exc_info()[0])
        logger.error("Page #%s: ", i)
    else:
        logger.info("All %s pages of text extracted from PDF successfully.", number_of_pages)
    
    return {
        'statusCode': 200,
        'body': json.dumps('parseNysPdfData has completed.')
    }


# TODO: lambda is failing on put object - doesn't like the target location reference
# TODO: make sure file exports to s3://nys-ads-raw-data/parsed-text/