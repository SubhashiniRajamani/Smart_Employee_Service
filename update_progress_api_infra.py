from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

# ---------------------------------------------------------
# 1. Add GetProgress Lambda role
# ---------------------------------------------------------

role_block = '''
  GetProgressLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-get-progress-role-${Environment}
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
        - PolicyName: GetProgressPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:GetItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn

              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"
'''

if "GetProgressLambdaRole:" not in text:
    marker = "  ValidateDocumentLambdaRole:"
    pos = text.find(marker)

    if pos == -1:
        raise SystemExit("ERROR: Could not find ValidateDocumentLambdaRole")

    text = text[:pos] + role_block + "\n" + text[pos:]
    print("Added GetProgressLambdaRole.")
else:
    print("GetProgressLambdaRole already exists.")


# ---------------------------------------------------------
# 2. Add GetProgress Lambda function
# ---------------------------------------------------------

function_block = '''
  GetProgressFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-get-progress-${Environment}
      Runtime: python3.12
      Handler: app.lambda_handler
      Role: !GetAtt GetProgressLambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "statusCode": 200,
                  "body": "Temporary GetProgress deployment"
              }
'''

if "GetProgressFunction:" not in text:
    marker = "  ValidateDocumentFunction:"
    pos = text.find(marker)

    if pos == -1:
        raise SystemExit("ERROR: Could not find ValidateDocumentFunction")

    text = text[:pos] + function_block + "\n" + text[pos:]
    print("Added GetProgressFunction.")
else:
    print("GetProgressFunction already exists.")


# ---------------------------------------------------------
# 3. Add API integration
# ---------------------------------------------------------

integration_block = '''
  GetProgressIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref EmployeeHttpApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !GetAtt GetProgressFunction.Arn
      PayloadFormatVersion: "2.0"
'''

if "GetProgressIntegration:" not in text:
    marker = "  "
    api_pos = text.find("Integration:", text.find("EmployeeHttpApi"))

    # insert before Outputs if no better marker
    outputs_pos = text.find("\nOutputs:")

    if outputs_pos == -1:
        raise SystemExit("ERROR: Could not find Outputs section")

    text = text[:outputs_pos] + "\n" + integration_block + text[outputs_pos:]
    print("Added GetProgressIntegration.")
else:
    print("GetProgressIntegration already exists.")


# ---------------------------------------------------------
# 4. Add API route
# ---------------------------------------------------------

route_block = '''
  GetProgressRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "GET /employees/{employee_id}/progress"
      Target: !Sub integrations/${GetProgressIntegration}
'''

if "GetProgressRoute:" not in text:
    outputs_pos = text.find("\nOutputs:")

    text = text[:outputs_pos] + "\n" + route_block + text[outputs_pos:]
    print("Added GetProgressRoute.")
else:
    print("GetProgressRoute already exists.")


# ---------------------------------------------------------
# 5. Add Lambda invoke permission for API Gateway
# ---------------------------------------------------------

permission_block = '''
  GetProgressApiPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref GetProgressFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${EmployeeHttpApi}/*
'''

if "GetProgressApiPermission:" not in text:
    outputs_pos = text.find("\nOutputs:")

    text = text[:outputs_pos] + "\n" + permission_block + text[outputs_pos:]
    print("Added GetProgressApiPermission.")
else:
    print("GetProgressApiPermission already exists.")


path.write_text(text)

print("\nInfrastructure updated successfully.")
