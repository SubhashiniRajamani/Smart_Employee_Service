import json
import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["EMPLOYEE_TABLE_NAME"])


def lambda_handler(event, context):

    employee_id = event["employee_id"]
    stage = event["stage"]

    print(f"Processing stage {stage} for employee {employee_id}")

    table.put_item(
        Item={
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": f"STAGE#{stage}",
            "stage": stage,
            "status": "IN_PROGRESS",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    )

    return {
        "employee_id": employee_id,
        "stage": stage,
        "stage_status": "IN_PROGRESS"
    }
