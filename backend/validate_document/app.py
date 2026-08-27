import os
import urllib.parse
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
HR_NOTIFICATION_TOPIC_ARN = os.environ["HR_NOTIFICATION_TOPIC_ARN"]

table = dynamodb.Table(TABLE_NAME)

MAX_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}

REQUIRED_DOCUMENTS = {
    "ID_PROOF",
    "DEGREE_CERTIFICATE",
    "OFFER_LETTER"
}


def lambda_handler(event, context):

    print("Received S3 event:", event)

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]

        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Bucket: {bucket}")
        print(f"Key: {key}")

        parts = key.split("/")

        # Expected:
        # employees/<employee_id>/documents/<document_type>/<file>

        if len(parts) < 5:
            print("Invalid document key structure")
            continue

        employee_id = parts[1]
        document_type = parts[3]

        metadata = s3.head_object(
            Bucket=bucket,
            Key=key
        )

        file_size = metadata["ContentLength"]
        content_type = metadata.get(
            "ContentType",
            "application/octet-stream"
        )

        status = "VERIFIED"
        rejection_reason = None

        if file_size > MAX_SIZE:
            status = "REJECTED"
            rejection_reason = "FILE_TOO_LARGE"

        elif content_type not in ALLOWED_CONTENT_TYPES:
            status = "REJECTED"
            rejection_reason = "INVALID_FILE_TYPE"

        item = {
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": f"DOCUMENT#{document_type}",
            "document_type": document_type,
            "s3_bucket": bucket,
            "s3_key": key,
            "file_size": file_size,
            "content_type": content_type,
            "status": status,
            "uploaded_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        if rejection_reason:
            item["rejection_reason"] = rejection_reason

        table.put_item(Item=item)

        if status == "VERIFIED":

            response = table.query(
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={
                    ":pk": f"EMPLOYEE#{employee_id}"
                }
            )

            verified_documents = {
                db_item["document_type"]
                for db_item in response["Items"]
                if db_item.get("SK", "").startswith("DOCUMENT#")
                and db_item.get("status") == "VERIFIED"
            }

            print(f"Verified documents: {verified_documents}")

            if REQUIRED_DOCUMENTS.issubset(verified_documents):

                table.put_item(
                    Item={
                        "PK": f"EMPLOYEE#{employee_id}",
                        "SK": "STAGE#DOCUMENTS",
                        "stage": "DOCUMENTS",
                        "status": "COMPLETE",
                        "updated_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }
                )

                sns.publish(
                    TopicArn=HR_NOTIFICATION_TOPIC_ARN,
                    Subject="Employee documents verified",
                    Message=(
                        f"All required onboarding documents for employee "
                        f"{employee_id} have been received and verified."
                    )
                )

                print("HR SNS notification sent.")

        print(
            f"Document {document_type} "
            f"for {employee_id} => {status}"
        )

    return {
        "statusCode": 200
    }
