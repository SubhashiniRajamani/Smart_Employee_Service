import json
import os
import uuid

import boto3
from botocore.config import Config


AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
BUCKET_NAME = os.environ["DOCUMENT_BUCKET_NAME"]

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(
        signature_version="s3v4",
        s3={
            "addressing_style": "virtual"
        }
    )
)

ALLOWED_DOCUMENT_TYPES = {
    "ID_PROOF",
    "DEGREE_CERTIFICATE",
    "OFFER_LETTER"
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}


def lambda_handler(event, context):
    try:
        body = event.get("body", event)

        if isinstance(body, str):
            body = json.loads(body)

        employee_id = body.get("employee_id")
        document_type = body.get("document_type")
        content_type = body.get("content_type")

        if not employee_id or not document_type or not content_type:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "employee_id, document_type and content_type are required"
                })
            }

        if document_type not in ALLOWED_DOCUMENT_TYPES:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid document_type"
                })
            }

        if content_type not in ALLOWED_CONTENT_TYPES:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid content_type"
                })
            }

        extension_map = {
            "application/pdf": "pdf",
            "image/jpeg": "jpg",
            "image/png": "png"
        }

        extension = extension_map[content_type]

        object_key = (
            f"employees/{employee_id}/documents/"
            f"{document_type}/{uuid.uuid4()}.{extension}"
        )

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=900
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "upload_url": upload_url,
                "object_key": object_key,
                "expires_in": 900
            })
        }

    except Exception as error:
        print(f"ERROR: {error}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Could not generate upload URL"
            })
        }
