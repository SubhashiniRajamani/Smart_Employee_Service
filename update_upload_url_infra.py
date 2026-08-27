from pathlib import Path

template_path = Path("infrastructure/main.yaml")

text = template_path.read_text()

# =========================================================
# STEP 3 - IAM ROLE FOR GENERATE UPLOAD URL LAMBDA
# =========================================================

iam_block = """
  GenerateUploadUrlLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub smart-upload-url-role-${Environment}

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
        - PolicyName: GeneratePresignedUploadPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:PutObject
                Resource: !Sub ${EmployeeDocumentsBucket.Arn}/*


"""

# =========================================================
# STEP 4 - GENERATE UPLOAD URL LAMBDA
# =========================================================

lambda_block = """
  GenerateUploadUrlFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub smart-generate-upload-url-${Environment}

      Runtime: python3.12
      Handler: app.lambda_handler

      Role: !GetAtt GenerateUploadUrlLambdaRole.Arn

      Timeout: 10
      MemorySize: 128

      Environment:
        Variables:
          DOCUMENT_BUCKET_NAME: !Ref EmployeeDocumentsBucket

      Code:
        ZipFile: |
          def lambda_handler(event, context):
              return {
                  "statusCode": 200,
                  "body": "Temporary deployment"
              }

      Tags:
        - Key: Project
          Value: SmartEmployeeOnboarding
        - Key: Environment
          Value: !Ref Environment


"""

# =========================================================
# STEP 5 - API GATEWAY ROUTE + INTEGRATION + PERMISSION
# =========================================================

api_block = """
  UploadUrlIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref EmployeeHttpApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !GetAtt GenerateUploadUrlFunction.Arn
      PayloadFormatVersion: "2.0"


  UploadUrlRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "POST /upload-url"
      Target: !Sub integrations/${UploadUrlIntegration}


  UploadUrlLambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref GenerateUploadUrlFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:${AWS::Partition}:execute-api:${AWS::Region}:${AWS::AccountId}:${EmployeeHttpApi}/*


"""

# =========================================================
# INSERT RESOURCES BEFORE OUTPUTS
# =========================================================

resources_to_add = ""

if "GenerateUploadUrlLambdaRole:" not in text:
    resources_to_add += iam_block
    print("Adding GenerateUploadUrlLambdaRole...")
else:
    print("GenerateUploadUrlLambdaRole already exists.")

if "GenerateUploadUrlFunction:" not in text:
    resources_to_add += lambda_block
    print("Adding GenerateUploadUrlFunction...")
else:
    print("GenerateUploadUrlFunction already exists.")

if "UploadUrlIntegration:" not in text:
    resources_to_add += api_block
    print("Adding API Gateway upload-url resources...")
else:
    print("Upload URL API resources already exist.")

if resources_to_add:
    outputs_marker = "\nOutputs:\n"

    if outputs_marker not in text:
        print("ERROR: Could not find Outputs: section.")
        raise SystemExit(1)

    text = text.replace(
        outputs_marker,
        "\n" + resources_to_add + outputs_marker,
        1
    )

# =========================================================
# ADD OUTPUT FOR LAMBDA FUNCTION
# =========================================================

output_block = """
  GenerateUploadUrlFunctionName:
    Description: Upload URL Lambda function name
    Value: !Ref GenerateUploadUrlFunction

"""

if "GenerateUploadUrlFunctionName:" not in text:
    text = text.rstrip() + "\n\n" + output_block
    print("Adding GenerateUploadUrlFunctionName output...")
else:
    print("GenerateUploadUrlFunctionName output already exists.")

template_path.write_text(text)

print()
print("Finished updating infrastructure/main.yaml")
