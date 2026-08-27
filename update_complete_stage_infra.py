from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

if "\nOutputs:" not in text:
    raise SystemExit("ERROR: Outputs section not found")

block = r'''
  CompleteStageLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-complete-stage-role-${Environment}
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
        - PolicyName: CompleteStagePolicy
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

  CompleteStageFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-complete-stage-${Environment}
      Runtime: python3.12
      Handler: app.lambda_handler
      Role: !GetAtt CompleteStageLambdaRole.Arn
      Timeout: 10
      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "statusCode": 200,
                  "body": "Temporary CompleteStage deployment"
              }

  CompleteStageIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref EmployeeHttpApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !GetAtt CompleteStageFunction.Arn
      PayloadFormatVersion: "2.0"

  CompleteStageRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "POST /employees/{employee_id}/stages/{stage}/complete"
      Target: !Sub integrations/${CompleteStageIntegration}

  CompleteStageApiPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref CompleteStageFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${EmployeeHttpApi}/*
'''

if "CompleteStageFunction:" in text:
    print("CompleteStage resources already exist.")
else:
    pos = text.index("\nOutputs:")
    text = text[:pos] + "\n" + block + "\n" + text[pos:]
    path.write_text(text)
    print("Added CompleteStage API resources.")
