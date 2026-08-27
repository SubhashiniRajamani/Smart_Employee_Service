from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

if "\nOutputs:" not in text:
    raise SystemExit("ERROR: Could not find Outputs: in infrastructure/main.yaml")


resources = r'''
  CheckStageStatusLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-check-stage-status-role-${Environment}
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - sts:AssumeRole
      Policies:
        - PolicyName: CheckStageStatusPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn

              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"

  CheckStageStatusFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-check-stage-status-${Environment}
      Runtime: python3.12
      Handler: app.lambda_handler
      Role: !GetAtt CheckStageStatusLambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "employee_id": event.get("employee_id"),
                  "stage": event.get("stage"),
                  "status": "TEMPORARY"
              }

  SendReminderLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-send-reminder-role-${Environment}
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - sts:AssumeRole
      Policies:
        - PolicyName: SendReminderPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sns:Publish
                Resource: !Ref HRNotificationTopic

              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"

  SendReminderFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-send-reminder-${Environment}
      Runtime: python3.12
      Handler: app.lambda_handler
      Role: !GetAtt SendReminderLambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          HR_NOTIFICATION_TOPIC_ARN: !Ref HRNotificationTopic
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "employee_id": event.get("employee_id"),
                  "stage": event.get("stage"),
                  "reminder_sent": False
              }
'''


required_ids = [
    "CheckStageStatusLambdaRole:",
    "CheckStageStatusFunction:",
    "SendReminderLambdaRole:",
    "SendReminderFunction:",
]

existing = [resource for resource in required_ids if resource in text]

if existing:
    print("Some workflow helper resources already exist:")
    for resource in existing:
        print(" -", resource)
    print("No duplicate resources were added.")
else:
    outputs_position = text.index("\nOutputs:")
    text = (
        text[:outputs_position]
        + "\n"
        + resources
        + "\n"
        + text[outputs_position:]
    )

    path.write_text(text)
    print("Added workflow helper Lambda resources successfully.")
