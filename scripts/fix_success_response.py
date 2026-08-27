from pathlib import Path

file_path = Path("backend/create_employee/app.py")

text = file_path.read_text()

old_block = '''return {
    "statusCode": 201,
    "body": json.dumps({
        "message": "Employee created and onboarding workflow started",
        "employee_id": employee_id,
        "email": body["email"]
    })
}
'''

new_block = '''        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "Employee created and onboarding workflow started",
                "employee_id": employee_id,
                "email": body["email"]
            })
        }
'''

if old_block in text:
    text = text.replace(old_block, new_block)
    file_path.write_text(text)
    print("Success response indentation fixed.")
else:
    print("Could not find the exact success response block.")
    print("Please check backend/create_employee/app.py manually.")
