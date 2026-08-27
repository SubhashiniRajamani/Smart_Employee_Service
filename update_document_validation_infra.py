from pathlib import Path

template_path = Path("infrastructure/main.yaml")

text = template_path.read_text()

resources = """

  ValidateDocumentLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-validate-document-role-${Environment}

      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - sts:AssumeRole

      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

      Policies:
        - PolicyName: ValidateDocumentPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:

              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub ${EmployeeDocumentsBucket.Arn}/*

              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn


  ValidateDocumentFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-validate-document-${Environment}

      Runtime: python3.12
      Handler: app.lambda_handler

      Role: !GetAtt ValidateDocumentLambdaRole.Arn

      Timeout: 15
      MemorySize: 128

      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable

      Code:
        ZipFile: |
          def lambda_handler(event, context):
              print("Temporary validation Lambda")
              return {
                  "statusCode": 200
              }

      Tags:
        - Key: Project
          Value: SmartEmployeeOnboarding
        - Key: Environment
          Value: !Ref Environment


  ValidateDocumentS3Permission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ValidateDocumentFunction
      Action: lambda:InvokeFunction
      Principal: s3.amazonaws.com
      SourceArn: !GetAtt EmployeeDocumentsBucket.Arn

"""

if "ValidateDocumentFunction:" not in text:

    marker = "\nOutputs:\n"

    if marker not in text:
        raise SystemExit("Could not find Outputs section")

    text = text.replace(
        marker,
        resources + marker,
        1
    )

    print("Added validation Lambda resources.")

else:
    print("Validation Lambda resources already exist.")

output = """

  ValidateDocumentFunctionName:
    Description: Validate Document Lambda
    Value: !Ref ValidateDocumentFunction
"""

if "ValidateDocumentFunctionName:" not in text:
    text = text.rstrip() + output + "\n"

template_path.write_text(text)

print("Infrastructure update complete.")
