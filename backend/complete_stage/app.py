import os
import json
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

ALLOWED_STAGES = {
    "IT_PROVISIONING",
    "POLICY_SIGNOFF",
    "MANAGER_INTRO"
}


def lambda_handler(event, context):

    employee_id = event["pathParameters"]["employee_id"]
    stage = event["pathParameters"]["stage"]

    if stage not in ALLOWED_STAGES:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Invalid stage"
            })
        }

    table.update_item(
        Key={
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": f"STAGE#{stage}"
        },
        UpdateExpression=(
            "SET #status = :status, "
            "updated_at = :updated_at, "
            "stage = :stage"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "COMPLETE",
            ":updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            ":stage": stage
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "employee_id": employee_id,
            "stage": stage,
            "status": "COMPLETE"
        })
    }
