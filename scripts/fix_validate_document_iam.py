from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

role_start = text.find("  ValidateDocumentLambdaRole:")

if role_start == -1:
    raise SystemExit("ERROR: ValidateDocumentLambdaRole not found")

role_end = text.find("\n  ValidateDocumentFunction:", role_start)

if role_end == -1:
    raise SystemExit("ERROR: Could not find end of ValidateDocumentLambdaRole")

role_section = text[role_start:role_end]

old_block = """              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn
"""

new_block = """              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:Query
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn

              - Effect: Allow
                Action:
                  - sns:Publish
                Resource: !Ref HRNotificationTopic
"""

if "dynamodb:Query" in role_section and "sns:Publish" in role_section:
    print("ValidateDocument IAM permissions already look correct.")
else:
    if old_block not in role_section:
        raise SystemExit(
            "ERROR: Could not find DynamoDB PutItem policy inside "
            "ValidateDocumentLambdaRole"
        )

    role_section = role_section.replace(
        old_block,
        new_block,
        1
    )

    text = text[:role_start] + role_section + text[role_end:]

    path.write_text(text)

    print("Added DynamoDB Query/Update and SNS Publish permissions.")
