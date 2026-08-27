import os
import boto3

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    employee_id = event["employee_id"]
    stage = event["stage"]

    response = table.get_item(
        Key={
            "PK": f"EMPLOYEE#{employee_id}",
            "SK": f"STAGE#{stage}"
        }
    )

    item = response.get("Item")

    if not item:
        status = "NOT_STARTED"
    else:
        status = item.get("status", "NOT_STARTED")

    return {
        "employee_id": employee_id,
        "stage": stage,
        "status": status
    }
