import json
import os
import uuid
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
cognito = boto3.client("cognito-idp")
stepfunctions = boto3.client("stepfunctions")

TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
USER_POOL_ID = os.environ["USER_POOL_ID"]
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

table = dynamodb.Table(TABLE_NAME)


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

        # Create the Cognito login first
        cognito_response = cognito.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=body["email"],
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": body["email"]
                },
                {
                    "Name": "email_verified",
                    "Value": "true"
                }
            ],
            DesiredDeliveryMediums=["EMAIL"]
        )

        cognito_username = cognito_response["User"]["Username"]

        employee = {
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
            "cognito_username": cognito_username,
            "overall_status": "IN_PROGRESS",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        table.put_item(
            Item=employee,
            ConditionExpression="attribute_not_exists(PK)"
        )

        print(f"Starting Step Functions for employee: {employee_id}")
        print(f"State machine ARN: {STATE_MACHINE_ARN}")

        sfn_response = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({
                "employee_id": employee_id,
                "email": body["email"]
            })
        )

        print(f"STEP_FUNCTION_EXECUTION: {sfn_response['executionArn']}")

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Employee created and onboarding workflow started",
                "employee_id": employee_id,
                "email": body["email"],
                "execution_arn": sfn_response["executionArn"]
            })
        }

    except cognito.exceptions.UsernameExistsException:
        return {
            "statusCode": 409,
            "body": json.dumps({
                "message": "A Cognito user with this email already exists"
            })
        }

    except Exception as error:
        print(f"ERROR: {str(error)}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(error)
            })
        }
