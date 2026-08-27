# Smart Employee Onboarding and Identity Service

A fully AWS-native, serverless employee onboarding platform that automates the journey from employee creation to Day 1 readiness.

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

The application uses the following architecture:

- Amazon CloudFront delivers the frontend over HTTPS
- Amazon S3 hosts the frontend application
- Amazon Cognito manages employee authentication
- Amazon API Gateway exposes backend APIs
- API Gateway JWT Authorizer protects authenticated routes
- AWS Lambda contains the backend business logic
- Amazon DynamoDB stores employee profiles, stages, and document metadata
- AWS Step Functions orchestrates the onboarding lifecycle
- Amazon S3 stores onboarding documents
- Amazon SNS sends HR notifications
- AWS CloudFormation manages infrastructure deployment
- Amazon CloudWatch provides logs and operational visibility

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
