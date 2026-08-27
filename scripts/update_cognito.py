from pathlib import Path

template_path = Path("infrastructure/main.yaml")

text = template_path.read_text()

# 1. Add USER_POOL_ID environment variable
text = text.replace(
"""      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
""",
"""      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
          USER_POOL_ID: !Ref EmployeeUserPool
"""
)

# 2. Add Cognito IAM permission after DynamoDB PutItem permission
text = text.replace(
"""              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn
""",
"""              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !GetAtt EmployeeOnboardingTable.Arn

              - Effect: Allow
                Action:
                  - cognito-idp:AdminCreateUser
                Resource: !GetAtt EmployeeUserPool.Arn
"""
)

# 3. Add Cognito resources before CreateEmployeeFunction
cognito_resources = """
  EmployeeUserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub smart-employee-user-pool-${Environment}

      UsernameAttributes:
        - email

      AutoVerifiedAttributes:
        - email

      AdminCreateUserConfig:
        AllowAdminCreateUserOnly: true

      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireUppercase: true
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: true


  EmployeeUserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: !Sub smart-employee-client-${Environment}
      UserPoolId: !Ref EmployeeUserPool
      GenerateSecret: false

      ExplicitAuthFlows:
        - ALLOW_USER_PASSWORD_AUTH
        - ALLOW_REFRESH_TOKEN_AUTH


"""

marker = "  CreateEmployeeFunction:\n"

if "EmployeeUserPool:" not in text:
    text = text.replace(marker, cognito_resources + marker)

# 4. Add Cognito outputs
cognito_outputs = """

  EmployeeUserPoolId:
    Description: Cognito User Pool ID
    Value: !Ref EmployeeUserPool

  EmployeeUserPoolClientId:
    Description: Cognito App Client ID
    Value: !Ref EmployeeUserPoolClient
"""

if "EmployeeUserPoolId:" not in text:
    text = text.rstrip() + cognito_outputs + "\n"

template_path.write_text(text)

print("Updated infrastructure/main.yaml successfully.")
