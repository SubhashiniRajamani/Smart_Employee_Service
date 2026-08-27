from pathlib import Path

path = Path("backend/get_progress/app.py")

new_code = '''import os
import json
import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

ALL_STAGES = [
    "DOCUMENTS",
    "IT_PROVISIONING",
    "POLICY_SIGNOFF",
    "MANAGER_INTRO"
]


def lambda_handler(event, context):

    employee_id = event["pathParameters"]["employee_id"]

    response = table.query(
        KeyConditionExpression="PK = :pk",
        ExpressionAttributeValues={
            ":pk": f"EMPLOYEE#{employee_id}"
        }
    )

    items = response.get("Items", [])

    profile = None
    documents = []
    stage_map = {}

    for item in items:

        sk = item.get("SK", "")

        if sk == "PROFILE":
            profile = item

        elif sk.startswith("DOCUMENT#"):
            documents.append({
                "document_type": item.get("document_type"),
                "status": item.get("status")
            })

        elif sk.startswith("STAGE#"):
            stage_name = item.get("stage")

            if stage_name:
                stage_map[stage_name] = item.get(
                    "status",
                    "NOT_STARTED"
                )

    stages = []
    completed_stages = 0

    for stage_name in ALL_STAGES:

        status = stage_map.get(
            stage_name,
            "NOT_STARTED"
        )

        if status == "COMPLETE":
            completed_stages += 1

        stages.append({
            "stage": stage_name,
            "status": status
        })

    progress_percentage = int(
        (completed_stages / len(ALL_STAGES)) * 100
    )

    overall_status = (
        "COMPLETE"
        if completed_stages == len(ALL_STAGES)
        else "IN_PROGRESS"
    )

    result = {
        "employee_id": employee_id,
        "overall_status": overall_status,
        "progress_percentage": progress_percentage,
        "profile": profile,
        "documents": documents,
        "stages": stages
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(
            result,
            default=str
        )
    }
'''

path.write_text(new_code)

print("Updated backend/get_progress/app.py successfully.")
