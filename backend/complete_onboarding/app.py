import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    employee_id = event["employee_id"]

    table.update_item(
        Key={
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": "PROFILE"
        },
        UpdateExpression=(
            "SET overall_status = :status, "
            "updated_at = :updated_at"
        ),
        ExpressionAttributeValues={
            ":status": "COMPLETE",
            ":updated_at": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )

    print(
        f"Onboarding completed for employee {employee_id}"
    )

    return {
        "employee_id": employee_id,
        "overall_status": "COMPLETE"
    }
