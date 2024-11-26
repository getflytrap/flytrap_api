from flask import current_app, Response
import boto3
import botocore.exceptions


def create_aws_client(service: str, region: str) -> boto3.client:
    """Instantiates a boto3 client for a specific AWS service"""
    return boto3.client(
        service, 
        region_name=region, 
        endpoint_url=f"https://{service}.{region}.amazonaws.com"
    )


def get_secret(secret_name: str, region: str) -> str:
    """Fetch a secret from AWS Secrets Manager."""
    client = create_aws_client('secretsmanager', region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Failed to fetch secret {secret_name}: {e}")


def associate_api_key_with_usage_plan(project_name: str, api_key: str, usage_plan_id: str) -> None:
    """Associates a project's API key with the AWS usage plan"""

    client = create_aws_client('apigateway')
    response = client.create_api_key(name=project_name, value=api_key, enabled=True)
    api_key_id = response["id"]

    # Associate API key with the usage plan
    client.create_usage_plan_key(
        usagePlanId=usage_plan_id, keyId=api_key_id, keyType="API_KEY"
    )


def delete_api_key_from_aws(api_key_value: str) -> None:
    """Remove API key resources from AWS when the corresponding project is deleted"""

    try:
        api_gateway_client = create_aws_client('apigateway')
        
        response = api_gateway_client.get_api_keys(includeValues=True)
        current_app.logger.info(f"api keys response: {response}")
        all_keys = response.get('items')
        if all_keys:
            current_app.logger.info('all keys exists')
            current_app.logger.info(f"all keys print: {all_keys}")
            key_id = [item['id'] for item in all_keys if item['value'] == api_key_value][0]
        else:
            current_app.logger.info("get item didn't work")
            key_id = [item['id'] for item in response if item['value'] == api_key_value][0]

        current_app.logger.info(f"key_id print here: {key_id}")
        api_gateway_client.delete_api_key(apiKey=key_id)
        return True
    except Exception as e:
        current_app.logger.debug(f"Error deleting API key from AWS: {str(e)}")


def create_sns_topic(project_uuid: str) -> str:
    """Creates an SNS topic for a specific project if it doesn't exist."""

    sns_client = create_aws_client('sns')
    topic_name = f"project_{project_uuid}_notifications"
    
    # Create a new SNS topic (or retrieve ARN if it already exists)
    response = sns_client.create_topic(Name=topic_name)
    sns_topic_arn = response.get('TopicArn')
    return sns_topic_arn


def create_sns_subscription(project_uuid: str, user_uuid: str) -> Response:
    """Creates an SNS subscription for a user to receive notifications when errors occur"""

    from app.models import (
        get_user_info, 
        get_topic_arn
    )

    user_info = get_user_info(user_uuid)
    user_email = user_info.get('email')
    sns_topic_arn = get_topic_arn(project_uuid)
    current_app.logger.info(f"user_email: {user_email}, sns_topic_arn: {sns_topic_arn}")
    sns_client = create_aws_client('sns')

    try:
        sns_client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol='email',
            Endpoint=user_email
        )

        return {
            'statusCode': 200,
            'body': f'Email {user_email} subscribed successfully.'
        }
    except Exception as e:
        current_app.logger.debug(f"Error in SNS Subscription: {e}")
        raise e


def send_sns_notification(project_uuid: str) -> None:
    """Send an SNS notification to all subscribed users when an error occurs"""

    from app.models import get_topic_arn

    sns_client = create_aws_client('sns')
    sns_topic_arn = get_topic_arn(project_uuid)
    current_app.logger.info(f"sending sns notification to: {sns_topic_arn}")
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
        current_app.logger.info(f"Sent notification to developers assigned to project {project_uuid}")
    except Exception as e:
        current_app.logger.debug(f"Error sending notification to  developers assigned to project {project_uuid}: {str(e)}")


def delete_sns_topic_from_aws(project_uuid: str) -> None:
    """Delete SNS topic from SNS when the corresponding project is deleted"""

    from app.models import get_topic_arn
    try:
        topic_arn = get_topic_arn(project_uuid)
        client = create_aws_client('sns')
        client.deleteTopic(TopicArn=topic_arn)
    except Exception as e:
        current_app.logger.debug(f"Error deleting SNS topic from AWS: {str(e)}")
