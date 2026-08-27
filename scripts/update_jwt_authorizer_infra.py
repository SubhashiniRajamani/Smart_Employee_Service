from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

# Add JWT authorizer before Outputs
authorizer_block = r'''
  EmployeeJwtAuthorizer:
    Type: AWS::ApiGatewayV2::Authorizer
    Properties:
      ApiId: !Ref EmployeeHttpApi
      AuthorizerType: JWT
      IdentitySource:
        - "$request.header.Authorization"
      JwtConfiguration:
        Audience:
          - "25h8kd74jg20u2pfvvmoojj6os"
        Issuer: "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_b4Hhj4rL4"
      Name: smart-employee-jwt-authorizer
'''

if "EmployeeJwtAuthorizer:" not in text:
    pos = text.index("\nOutputs:")
    text = text[:pos] + "\n" + authorizer_block + "\n" + text[pos:]
    print("Added EmployeeJwtAuthorizer.")
else:
    print("EmployeeJwtAuthorizer already exists.")


# Protect GetProgressRoute
old_progress = '''  GetProgressRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "GET /employees/{employee_id}/progress"
      Target: !Sub integrations/${GetProgressIntegration}
'''

new_progress = '''  GetProgressRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "GET /employees/{employee_id}/progress"
      Target: !Sub integrations/${GetProgressIntegration}
      AuthorizationType: JWT
      AuthorizerId: !Ref EmployeeJwtAuthorizer
'''

if old_progress in text:
    text = text.replace(old_progress, new_progress, 1)
    print("Protected GetProgressRoute.")
elif "GetProgressRoute:" in text and "AuthorizationType: JWT" in text:
    print("GetProgressRoute may already be protected.")
else:
    print("WARNING: Could not automatically update GetProgressRoute.")


# Protect CompleteStageRoute
old_complete = '''  CompleteStageRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "POST /employees/{employee_id}/stages/{stage}/complete"
      Target: !Sub integrations/${CompleteStageIntegration}
'''

new_complete = '''  CompleteStageRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref EmployeeHttpApi
      RouteKey: "POST /employees/{employee_id}/stages/{stage}/complete"
      Target: !Sub integrations/${CompleteStageIntegration}
      AuthorizationType: JWT
      AuthorizerId: !Ref EmployeeJwtAuthorizer
'''

if old_complete in text:
    text = text.replace(old_complete, new_complete, 1)
    print("Protected CompleteStageRoute.")
elif "CompleteStageRoute:" in text and "AuthorizationType: JWT" in text:
    print("CompleteStageRoute may already be protected.")
else:
    print("WARNING: Could not automatically update CompleteStageRoute.")


path.write_text(text)

print("JWT infrastructure update finished.")
