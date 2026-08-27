from pathlib import Path

file_path = Path("backend/validate_document/app.py")

text = file_path.read_text()

# ---------------------------------------------------------
# 1. Add SNS client
# ---------------------------------------------------------

old_clients = '''s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
'''

new_clients = '''s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
'''

if 'sns = boto3.client("sns")' not in text:
    text = text.replace(old_clients, new_clients)
    print("Added SNS client.")
else:
    print("SNS client already exists.")


# ---------------------------------------------------------
# 2. Add SNS topic environment variable
# ---------------------------------------------------------

old_env = '''TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]

table = dynamodb.Table(TABLE_NAME)
'''

new_env = '''TABLE_NAME = os.environ["EMPLOYEE_TABLE_NAME"]
HR_NOTIFICATION_TOPIC_ARN = os.environ["HR_NOTIFICATION_TOPIC_ARN"]

table = dynamodb.Table(TABLE_NAME)
'''

if "HR_NOTIFICATION_TOPIC_ARN" not in text:
    text = text.replace(old_env, new_env)
    print("Added HR_NOTIFICATION_TOPIC_ARN.")
else:
    print("HR_NOTIFICATION_TOPIC_ARN already exists.")


# ---------------------------------------------------------
# 3. Add required document list
# ---------------------------------------------------------

allowed_block = '''ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}
'''

required_block = '''ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}

REQUIRED_DOCUMENTS = {
    "ID_PROOF",
    "DEGREE_CERTIFICATE",
    "OFFER_LETTER"
}
'''

if "REQUIRED_DOCUMENTS" not in text:
    text = text.replace(allowed_block, required_block)
    print("Added REQUIRED_DOCUMENTS.")
else:
    print("REQUIRED_DOCUMENTS already exists.")


# ---------------------------------------------------------
# 4. Add completion + SNS logic after table.put_item(Item=item)
# ---------------------------------------------------------

marker = '''        table.put_item(Item=item)
'''

logic = '''        table.put_item(Item=item)

        if status == "VERIFIED":

            response = table.query(
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={
                    ":pk": f"EMPLOYEE#{employee_id}"
                }
            )

            verified_documents = {
                db_item["document_type"]
                for db_item in response["Items"]
                if db_item.get("SK", "").startswith("DOCUMENT#")
                and db_item.get("status") == "VERIFIED"
            }

            print(f"Verified documents: {verified_documents}")

            if REQUIRED_DOCUMENTS.issubset(verified_documents):

                table.put_item(
                    Item={
                        "PK": f"EMPLOYEE#{employee_id}",
                        "SK": "STAGE#DOCUMENTS",
                        "stage": "DOCUMENTS",
                        "status": "COMPLETE",
                        "updated_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }
                )

                sns.publish(
                    TopicArn=HR_NOTIFICATION_TOPIC_ARN,
                    Subject="Employee documents verified",
                    Message=(
                        f"All required onboarding documents for employee "
                        f"{employee_id} have been received and verified."
                    )
                )

                print("HR SNS notification sent.")
'''

if "HR SNS notification sent." not in text:
    if marker in text:
        text = text.replace(marker, logic, 1)
        print("Added document completion + SNS logic.")
    else:
        print("ERROR: Could not find table.put_item(Item=item)")
        raise SystemExit(1)
else:
    print("Completion logic already exists.")


file_path.write_text(text)

print("\nUpdated backend/validate_document/app.py successfully.")
