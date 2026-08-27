import os
import boto3

sns = boto3.client("sns")

HR_NOTIFICATION_TOPIC_ARN = os.environ["HR_NOTIFICATION_TOPIC_ARN"]


def lambda_handler(event, context):

    employee_id = event["employee_id"]
    stage = event["stage"]

    message = (
        f"Reminder: onboarding stage {stage} "
        f"is still incomplete for employee {employee_id}."
    )

    sns.publish(
        TopicArn=HR_NOTIFICATION_TOPIC_ARN,
        Subject="Employee Onboarding Reminder",
        Message=message
    )

    print(message)

    return {
        "employee_id": employee_id,
        "stage": stage,
        "reminder_sent": True
    }
