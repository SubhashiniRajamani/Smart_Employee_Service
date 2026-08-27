from pathlib import Path

file_path = Path("backend/create_employee/app.py")

text = file_path.read_text()

start_marker = """        table.put_item(
            Item=employee,
            ConditionExpression="attribute_not_exists(PK)"
        )
"""

end_marker = """    except cognito.exceptions.UsernameExistsException:
"""

replacement = """        table.put_item(
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

        print(
            f"STEP_FUNCTION_EXECUTION: "
            f"{sfn_response['executionArn']}"
        )

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Employee created and onboarding workflow started",
                "employee_id": employee_id,
                "email": body["email"],
                "execution_arn": sfn_response["executionArn"]
            })
        }

"""

if start_marker not in text:
    print("ERROR: Could not find table.put_item block.")
    raise SystemExit(1)

if end_marker not in text:
    print("ERROR: Could not find Cognito exception block.")
    raise SystemExit(1)

start_index = text.index(start_marker)
end_index = text.index(end_marker)

text = text[:start_index] + replacement + text[end_index:]

file_path.write_text(text)

print("Updated backend/create_employee/app.py successfully.")
