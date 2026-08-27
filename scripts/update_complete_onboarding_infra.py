from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

if "\nOutputs:" not in text:
    raise SystemExit("ERROR: Could not find Outputs section.")

block = r'''
  CompleteOnboardingLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-complete-onboarding-role-${Environment}
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
        - PolicyName: CompleteOnboardingPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:UpdateItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn

              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"

  CompleteOnboardingFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-complete-onboarding-${Environment}
      Runtime: python3.12
      Handler: app.lambda_handler
      Role: !GetAtt CompleteOnboardingLambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "employee_id": event.get("employee_id"),
                  "overall_status": "TEMPORARY"
              }
'''

if "CompleteOnboardingFunction:" in text:
    print("CompleteOnboardingFunction already exists.")
else:
    pos = text.index("\nOutputs:")
    text = text[:pos] + "\n" + block + "\n" + text[pos:]
    path.write_text(text)
    print("Added CompleteOnboarding Lambda resources.")
