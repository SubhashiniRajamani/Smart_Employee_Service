from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

start = text.find("  ValidateDocumentFunction:")
if start == -1:
    raise SystemExit("ERROR: ValidateDocumentFunction not found")

end = text.find("\n  ", start + 3)

# Find the next CloudFormation resource after ValidateDocumentFunction
while end != -1:
    candidate = text[end + 1:]
    first_line = candidate.splitlines()[0]

    if first_line.startswith("  ") and not first_line.startswith("    "):
        break

    end = text.find("\n  ", end + 3)

if end == -1:
    end = text.find("\nOutputs:", start)

section = text[start:end]

old = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
"""

new = """      Environment:
        Variables:
          EMPLOYEE_TABLE_NAME: !Ref EmployeeOnboardingTable
          HR_NOTIFICATION_TOPIC_ARN: !Ref HRNotificationTopic
"""

if "HR_NOTIFICATION_TOPIC_ARN:" in section:
    print("HR_NOTIFICATION_TOPIC_ARN already exists in ValidateDocumentFunction.")
else:
    if old not in section:
        raise SystemExit(
            "ERROR: Could not find ValidateDocumentFunction environment block"
        )

    section = section.replace(old, new, 1)
    text = text[:start] + section + text[end:]
    path.write_text(text)

    print("Added HR_NOTIFICATION_TOPIC_ARN to ValidateDocumentFunction.")
