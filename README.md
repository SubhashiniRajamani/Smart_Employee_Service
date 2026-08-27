# Smart Employee Onboarding and Identity Service

A fully AWS-native, serverless employee onboarding platform that automates the employee journey from profile creation to Day 1 readiness.

The system creates a canonical employee record, provisions user identity, collects and validates onboarding documents, orchestrates multi-stage onboarding using AWS Step Functions, sends notifications, and provides employee and HR-facing web portals with real-time onboarding progress.

---

## Project Overview

The goal of this project is to automate the employee onboarding lifecycle using managed AWS services.

The onboarding flow covers:

- Employee profile creation
- Cognito user provisioning
- Document collection
- Document validation
- IT provisioning
- Policy sign-off
- Manager introduction
- HR notifications
- Onboarding progress tracking
- Secure authenticated API access
- Employee and HR dashboards

The project is designed as a serverless AWS architecture using Infrastructure as Code.

---

## Solution Architecture

![AWS Solution Architecture](docs/architecture_diagram_aws.png)

The application uses:

- Amazon CloudFront for HTTPS delivery
- Amazon S3 for frontend hosting
- Amazon Cognito for authentication
- Amazon API Gateway for backend APIs
- API Gateway JWT Authorizer for route protection
- AWS Lambda for backend logic
- Amazon DynamoDB for employee, stage, and document metadata
- AWS Step Functions for onboarding orchestration
- Amazon S3 for onboarding documents
- Amazon SNS for HR notifications
- AWS CloudFormation for Infrastructure as Code
- Amazon CloudWatch for logs and monitoring

### High-Level Flow

```text
Employee / HR
      |
      v
Amazon CloudFront
      |
      v
Amazon S3 Frontend
      |
      +--------------------+
      |                    |
      v                    v
Amazon Cognito       Amazon API Gateway
                           |
                           v
                     AWS Lambda
                           |
                 +---------+---------+
                 |                   |
                 v                   v
          Amazon DynamoDB      AWS Step Functions
                                     |
                         +-----------+-----------+
                         |           |           |
                         v           v           v
                    Documents   IT Provisioning  Policy Sign-off
                         |                       |
                         v                       v
                    Amazon S3              Manager Intro
                         |
                         v
                Validation Lambda
                         |
                  +------+------+
                  |             |
                  v             v
              DynamoDB       Amazon SNS
```

---

## AWS Services Used

- AWS Lambda
- Amazon DynamoDB
- Amazon Cognito
- Amazon API Gateway
- AWS Step Functions
- Amazon S3
- Amazon CloudFront
- Amazon SNS
- Amazon CloudWatch
- AWS CloudFormation

---

## Key Features

### Employee Record and Identity

- Creates a new employee profile using AWS Lambda
- Generates a UUID-based employee identifier
- Stores structured employee information in DynamoDB
- Provisions a Cognito user account
- Supports authenticated employee login

Employee attributes include department, role, manager, joining date, employment type, email, and overall onboarding status.

---

## Onboarding Workflow

AWS Step Functions orchestrates the employee onboarding workflow.

```text
Document Collection
        ↓
IT Provisioning
        ↓
Policy Sign-off
        ↓
Manager Intro
        ↓
Complete
```

Each stage invokes Lambda functions, reads and updates state in DynamoDB, checks completion, enters reminder logic when incomplete, and advances when complete.

For demonstration purposes, the deployed workflow uses a shortened wait interval. The production configuration uses:

```text
86400 seconds = 24 hours
```

---

## Document Collection

The employee uploads:

- ID proof
- Degree certificate
- Signed offer letter

The document workflow includes:

- Presigned S3 upload URLs
- Server-side encryption
- File validation using Lambda
- Document verification status stored in DynamoDB
- Detection of missing required documents
- SNS notification to HR after all required documents are verified

---

## Authentication and API Security

Authentication is handled using Amazon Cognito.

Protected routes use an Amazon API Gateway JWT Authorizer.

Authenticated requests send:

```text
Authorization: Bearer <access_token>
```

Requests without a valid token are rejected with:

```text
HTTP 401 Unauthorized
```

Protected routes include:

```text
GET /employees/{employee_id}/progress
POST /employees/{employee_id}/stages/{stage}/complete
```

---

## DynamoDB Design

The project uses a DynamoDB single-table design.

### Employee Profile

```text
PK = EMPLOYEE#<employee_id>
SK = PROFILE
```

### Onboarding Stages

```text
PK = EMPLOYEE#<employee_id>
SK = STAGE#DOCUMENTS
SK = STAGE#IT_PROVISIONING
SK = STAGE#POLICY_SIGNOFF
SK = STAGE#MANAGER_INTRO
```

### Documents

```text
PK = EMPLOYEE#<employee_id>
SK = DOCUMENT#ID_PROOF
SK = DOCUMENT#DEGREE_CERTIFICATE
SK = DOCUMENT#OFFER_LETTER
```

This allows all data related to one employee to be retrieved efficiently using a single partition key.

---

## Logical Data Model

![DynamoDB ER Diagram](docs/er_diagram.png)

```text
EMPLOYEE
--------
employee_id
name
email
department
role
manager
joining_date
employment_type
overall_status
created_at
updated_at

EMPLOYEE_STAGE
--------------
employee_id
stage
status
updated_at

DOCUMENT
--------
employee_id
document_type
status
s3_key
uploaded_at
verified_at
```

Relationships:

```text
EMPLOYEE 1 ----- N EMPLOYEE_STAGE
EMPLOYEE 1 ----- N DOCUMENT
```

---

## Frontend

### New Hire Portal

Displays:

- Authentication and login
- Employee onboarding progress
- Current stage status
- Progress percentage
- Document status
- Overall onboarding completion status

### HR Admin Dashboard

Displays:

- Employee details
- Onboarding pipeline
- Stage status
- Progress bar
- Stage completion controls

Statuses include Pending, In Progress, and Complete.

---

## Progress API

Example:

```text
GET /employees/{employee_id}/progress
```

The response includes employee profile, document status, onboarding stages, overall status, and progress percentage.

Example completed workflow:

```text
DOCUMENTS          COMPLETE
IT_PROVISIONING    COMPLETE
POLICY_SIGNOFF     COMPLETE
MANAGER_INTRO      COMPLETE

Progress: 100%
Overall Status: COMPLETE
```

---

## Project Structure

```text
Smart_Employee_Service/
├── backend/
│   ├── create_employee/
│   ├── onboarding_stage/
│   ├── generate_upload_url/
│   ├── validate_document/
│   ├── get_progress/
│   ├── check_stage_status/
│   ├── send_reminder/
│   ├── complete_onboarding/
│   └── complete_stage/
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── hr.html
│   └── hr.js
├── infrastructure/
│   ├── main.yaml
│   └── iam/
├── scripts/
├── step-functions/
│   ├── onboarding-workflow.json
│   └── onboarding-workflow-production.json
├── docs/
│   ├── architecture_diagram_aws.png
│   ├── er_diagram.png
│   ├── project_report.pdf
│   ├── cost_estimate.md
│   └── screenshots/
├── .gitignore
└── README.md
```

---

## Infrastructure as Code

AWS CloudFormation is used to define and deploy the project infrastructure.

```bash
aws cloudformation deploy \
  --template-file infrastructure/main.yaml \
  --stack-name smart-employee-onboarding-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-south-1
```

---

## Example User Journey

1. HR submits a new employee onboarding form
2. Lambda generates an employee UUID
3. Employee profile is stored in DynamoDB
4. Cognito user identity is provisioned
5. Step Functions onboarding execution starts
6. Employee signs into the onboarding portal
7. Employee uploads required documents
8. Documents are stored in S3
9. Lambda validates the documents
10. DynamoDB document records are updated
11. HR receives an SNS notification
12. Document Collection becomes complete
13. IT Provisioning begins
14. HR completes IT Provisioning
15. Policy Sign-off begins
16. HR completes Policy Sign-off
17. Manager Intro begins
18. HR completes Manager Intro
19. Step Functions execution succeeds
20. Employee profile is marked COMPLETE
21. Portal displays 100% onboarding progress

---

## Security

Implemented controls include:

- Cognito-based authentication
- API Gateway JWT Authorizer
- Protected backend APIs
- S3 server-side encryption
- S3 public access blocking for employee documents
- Presigned S3 upload URLs
- IAM execution roles
- HTTPS delivery through CloudFront
- Infrastructure managed through CloudFormation

---

## Cost Estimate

For approximately 50 employee onboarding events per month, expected AWS operating cost is low because the architecture primarily uses serverless and pay-per-use services.

Main cost components:

- AWS Lambda invocations
- DynamoDB reads and writes
- API Gateway requests
- Step Functions state transitions
- S3 storage
- CloudFront traffic
- Cognito users
- SNS notifications
- CloudWatch logs

Estimated light demo-scale cost:

```text
Approximately $1 - $5 USD per month
```

Actual cost varies based on document size, API traffic, data transfer, log retention, notification volume, and AWS Free Tier eligibility.

---

## Demo

The project demo demonstrates:

- Employee authentication
- Cognito identity creation
- DynamoDB employee record
- Step Functions onboarding workflow
- Document storage
- Document validation
- HR notification
- HR dashboard
- Employee progress
- API authentication
- Infrastructure as Code
- Cost estimate

---

## Current Limitations and Future Improvements

- Dedicated HR and New Hire Cognito groups
- Fine-grained role-based authorization
- Ensure employees can access only their own records
- Fully migrate onboarding reminder delivery to Amazon SES
- Automated SES login invitations
- Dynamic employee selection on the HR dashboard
- Remove remaining hard-coded demo identifiers
- CI/CD using AWS CodePipeline and CodeBuild
- Private frontend S3 origin using CloudFront Origin Access Control
- CloudWatch alarms and dashboards
- Idempotent SNS notification logic
- Stage sequencing enforcement
- Automated integration and end-to-end testing

---

## What I Learned

This project provided hands-on experience with:

- Serverless AWS architecture
- Event-driven workflows
- AWS Step Functions orchestration
- AWS Lambda backend development
- DynamoDB single-table design
- Cognito authentication
- JWT-based API protection
- S3 presigned uploads
- Event-driven S3 processing
- CloudFront delivery
- SNS notifications
- CloudFormation Infrastructure as Code
- IAM permissions and troubleshooting
- Debugging distributed AWS applications

---

## Interview Talking Points

This project demonstrates practical experience with:

- Serverless architecture
- Identity and authentication
- Workflow orchestration
- Event-driven architecture
- NoSQL data modeling
- Secure API design
- Infrastructure as Code
- Cloud storage
- AWS IAM
- Frontend-to-backend integration
- Production versus demo configuration management

---

## References

- AWS Lambda Documentation
- Amazon DynamoDB Documentation
- Amazon Cognito Documentation
- Amazon API Gateway Documentation
- AWS Step Functions Documentation
- Amazon S3 Documentation
- Amazon CloudFront Documentation
- Amazon SNS Documentation
- AWS CloudFormation Documentation
- Amazon CloudWatch Documentation

---

## Author

**Subhashini**

AWS Cloud / DevOps Portfolio Project

---

## Project Status

```text
Core onboarding workflow: Complete
Document workflow: Complete
Employee portal: Complete
HR dashboard: Complete
Cognito authentication: Complete
JWT-protected API: Complete
Step Functions workflow: Complete
CloudFormation deployment: Complete
Submission documentation: Complete
Production hardening: Ongoing
```

