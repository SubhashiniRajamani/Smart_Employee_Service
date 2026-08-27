from pathlib import Path

template_path = Path("infrastructure/main.yaml")

text = template_path.read_text()

# ---------------------------------------------------------
# STEP 1:
# Add STATE_MACHINE_ARN to CreateEmployee Lambda env vars
# ---------------------------------------------------------

old_env = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
          USER_POOL_ID: !Ref EmployeeUserPool
"""

new_env = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
          USER_POOL_ID: !Ref EmployeeUserPool
          STATE_MACHINE_ARN: !Ref EmployeeOnboardingStateMachine
"""

if "STATE_MACHINE_ARN:" not in text:
    if old_env in text:
        text = text.replace(old_env, new_env)
        print("Added STATE_MACHINE_ARN environment variable.")
    else:
        print("WARNING: Could not find expected Lambda environment section.")
else:
    print("STATE_MACHINE_ARN already exists.")


# ---------------------------------------------------------
# STEP 2:
# Add states:StartExecution permission
# ---------------------------------------------------------

old_policy = """              - Effect: Allow
                Action:
                  - cognito-idp:AdminCreateUser
                Resource: !GetAtt EmployeeUserPool.Arn
"""

new_policy = """              - Effect: Allow
                Action:
                  - cognito-idp:AdminCreateUser
                Resource: !GetAtt EmployeeUserPool.Arn

              - Effect: Allow
                Action:
                  - states:StartExecution
                Resource: !Ref EmployeeOnboardingStateMachine
"""

if "states:StartExecution" not in text:
    if old_policy in text:
        text = text.replace(old_policy, new_policy)
        print("Added states:StartExecution IAM permission.")
    else:
        print("WARNING: Could not find expected Cognito IAM policy section.")
else:
    print("states:StartExecution permission already exists.")


# ---------------------------------------------------------
# STEP 3:
# No extra resource is needed.
# This validates that the Step Functions resource exists.
# ---------------------------------------------------------

if "EmployeeOnboardingStateMachine:" in text:
    print("EmployeeOnboardingStateMachine resource found.")
else:
    print(
        "WARNING: EmployeeOnboardingStateMachine resource was not found. "
        "Add the Step Functions resource before deploying."
    )


template_path.write_text(text)

print("\nFinished updating infrastructure/main.yaml")
