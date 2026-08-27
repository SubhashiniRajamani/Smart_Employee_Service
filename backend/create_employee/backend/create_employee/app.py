import json
import os
import uuid
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["EMPLOYEE_TABLE_NAME"])


def lambda_handler(event, context):
    try:
        body = event.get("body", event)

        if isinstance(body, str):
            body = json.loads(body)

        required_fields = [
            "first_name",
            "last_name",
            "email",
            "department",
            "role",
            "manager",
            "joining_date",
            "employment_type"
        ]

        missing_fields = [
            field for field in required_fields
            if not body.get(field)
        ]

        if missing_fields:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required fields",
                    "missing_fields": missing_fields
                })
            }

        employee_id = str(uuid.uuid4())

        item = {
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": "PROFILE",
            "employee_id": employee_id,
            "first_name": body["first_name"],
            "last_name": body["last_name"],
            "email": body["email"],
            "department": body["department"],
            "role": body["role"],
            "manager": body["manager"],
            "joining_date": body["joining_date"],
            "employment_type": body["employment_type"],
            "overall_status": "IN_PROGRESS",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK)"
        )

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Employee created successfully",
                "employee_id": employee_id
            })
        }

    except Exception as e:
        print(f"ERROR: {e}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error"
            })
        }
