import boto3
import os
from app.config import ENVIRONMENT, AWS_REGION

def create_aws_client():
    if ENVIRONMENT == "production":
        return boto3.client("apigateway", region_name=AWS_REGION)
    return None


def associate_api_key_with_usage_plan(client, project_name, api_key, usage_plan_id):
    # Create the API key in AWS
    response = client.create_api_key(name=project_name, value=api_key, enabled=True)
    api_key_id = response["id"]

    # Associate API key with the usage plan
    client.create_usage_plan_key(
        usagePlanId=usage_plan_id, keyId=api_key_id, keyType="API_KEY"
    )

def create_sns_topic(project_uuid):
    """Creates an SNS topic for a specific project if it doesn't exist."""
    sns_client = boto3.client('sns', region_name=AWS_REGION)
    topic_name = f"project_{project_uuid}_notifications"
    
    # Create a new SNS topic (or retrieve ARN if it already exists)
    response = sns_client.create_topic(Name=topic_name)
    sns_topic_arn = response['TopicArn']
    return sns_topic_arn

def create_sns_subscription(project_uuid, user_uuid):
    from app.models import get_user_info
    user_email = get_user_info(user_uuid)['email']
    sns_client = boto3.client('sns')
    sns_topic_arn = f"project_{project_uuid}_notifications"

    try:
        sns_client.subscribe(
            TopicArn = sns_topic_arn,
            Protocol = 'email',
            Endpoint = user_email
        )

        return {
            'statusCode': 200,
            'body': f'Email {user_email} subscribed successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error subscribing email: {str(e)}'
        }

def send_sns_notification(project_uuid):
    sns_client = boto3.client("sns", region_name=os.getenv("AWS_REGION"))
    sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
    
    try:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message="An error occurred",
            Subject=f"Notification for Project {project_uuid}",
            MessageAttributes={
                'project_id': {
                    'DataType': 'String',
                    'StringValue': project_uuid
                }
            }
        )
        print(f"Sent notification to developers assigned to project {project_uuid}")
    except Exception as e:
        print(f"Error sending notification to  developers assigned to project {project_uuid}: {str(e)}")