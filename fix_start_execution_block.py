from pathlib import Path

file_path = Path("backend/create_employee/app.py")

text = file_path.read_text()

start = text.find("        table.put_item(")
end = text.find("    except cognito.exceptions.UsernameExistsException:")

if start == -1:
    print("ERROR: Could not find table.put_item(")
    raise SystemExit(1)

if end == -1:
    print("ERROR: Could not find Cognito exception block")
    raise SystemExit(1)

replacement = '''        table.put_item(
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

'''

text = text[:start] + replacement + text[end:]

file_path.write_text(text)

print("Updated backend/create_employee/app.py successfully.")
