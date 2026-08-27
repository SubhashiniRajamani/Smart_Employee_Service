from pathlib import Path

template_path = Path("infrastructure/main.yaml")

text = template_path.read_text()

# ---------------------------------------------------------
# Add SNS topic resource
# ---------------------------------------------------------

sns_resource = """

  HRNotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub smart-hr-onboarding-${Environment}

"""

if "HRNotificationTopic:" not in text:
    marker = "\nOutputs:\n"

    if marker not in text:
        raise SystemExit("ERROR: Could not find Outputs section.")

    text = text.replace(
        marker,
        sns_resource + marker,
        1
    )

    print("Added HRNotificationTopic.")
else:
    print("HRNotificationTopic already exists.")


# ---------------------------------------------------------
# Add SNS output
# ---------------------------------------------------------

sns_output = """

  HRNotificationTopicArn:
    Description: HR onboarding SNS topic ARN
    Value: !Ref HRNotificationTopic
"""

if "HRNotificationTopicArn:" not in text:
    text = text.rstrip() + sns_output + "\n"
    print("Added HRNotificationTopicArn output.")
else:
    print("HRNotificationTopicArn output already exists.")


# ---------------------------------------------------------
# Add SNS environment variable to ValidateDocumentFunction
# ---------------------------------------------------------

old_env = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
"""

new_env = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
          HR_NOTIFICATION_TOPIC_ARN: !Ref HRNotificationTopic
"""

if "HR_NOTIFICATION_TOPIC_ARN:" not in text:
    if old_env in text:
        text = text.replace(old_env, new_env, 1)
        print("Added HR_NOTIFICATION_TOPIC_ARN environment variable.")
    else:
        print("WARNING: Could not find validation Lambda environment block.")
else:
    print("HR_NOTIFICATION_TOPIC_ARN already exists.")


# ---------------------------------------------------------
# Add SNS + DynamoDB Query permissions
# ---------------------------------------------------------

old_policy = """              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn
"""

new_policy = """              - Effect: Allow
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

if "sns:Publish" not in text:
    if old_policy in text:
        text = text.replace(old_policy, new_policy, 1)
        print("Added DynamoDB Query/Update and SNS Publish permissions.")
    else:
        print("WARNING: Could not find validation DynamoDB policy block.")
else:
    print("SNS permission already exists.")


template_path.write_text(text)

print("Finished updating infrastructure/main.yaml")
