from flask import current_app, Response
import boto3
import botocore.exceptions

def create_aws_client(service: str, region: str) -> boto3.client:
    """Instantiates a boto3 client for a specific AWS service"""
    try:
        return boto3.client(
            service,
            region_name=region,
            endpoint_url=f"https://{service}.{region}.amazonaws.com"
        )
    except botocore.exceptions.BotoCoreError as e:
        current_app.logger.error(f"Failed to create AWS client for {service}: {e}")
        raise RuntimeError(f"Error creating AWS client for {service}: {str(e)}")


def get_secret(secret_name: str, region: str) -> str:
    """Fetch a secret from AWS Secrets Manager."""
    try:
        client = create_aws_client('secretsmanager', region)
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Failed to fetch secret {secret_name}: {e}")


def associate_api_key_with_usage_plan(project_name: str, api_key: str) -> None:
    """Associates a project's API key with the AWS usage plan"""
    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Associating API key {api_key} with usage plan for project {project_name}.")
        return

    try:
        client = create_aws_client('apigateway', current_app.config['AWS_REGION'])
        response = client.create_api_key(name=project_name, value=api_key, enabled=True)
        api_key_id = response["id"]

        client.create_usage_plan_key(
            usagePlanId=current_app.config["USAGE_PLAN_ID"], keyId=api_key_id, keyType="API_KEY"
        )
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to associate API key with usage plan: {e}")
        raise RuntimeError(f"Error associating API key with usage plan: {str(e)}")


def delete_api_key_from_aws(api_key_value: str) -> None:
    """Remove API key resources from AWS when the corresponding project is deleted"""
    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Deleting API key {api_key_value}.")
        return

    try:
        client = create_aws_client('apigateway')
        response = client.get_api_keys(includeValues=True)
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
        client.delete_api_key(apiKey=key_id)
        return True
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to delete API key from AWS: {e}")
        raise RuntimeError(f"Error deleting API key: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error deleting API key: {str(e)}")
        raise e


def create_sns_topic(project_uuid: str) -> str:
    """Creates an SNS topic for a specific project if it doesn't exist."""
    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Creating sns topic arn for project {project_uuid}.")
        return f"arn:aws:sns:mock-region:123456789012:project_{project_uuid}_notifications"
    
    try:
        sns_client = create_aws_client('sns', current_app.config['AWS_REGION'])
        topic_name = f"project_{project_uuid}_notifications"

        response = sns_client.create_topic(Name=topic_name)
        sns_topic_arn = response.get('TopicArn')
        return sns_topic_arn
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to create SNS topic for project {project_uuid}: {e}")
        raise RuntimeError(f"Error creating SNS topic for project {project_uuid}: {str(e)}")


def create_sns_subscription(project_uuid: str, user_uuid: str) -> Response:
    """Creates an SNS subscription for a user to receive notifications when errors occur"""
    from app.models import (
        get_user_info, 
        get_topic_arn
    )

    user_info = get_user_info(user_uuid)
    user_email = user_info.get('email')
    sns_topic_arn = get_topic_arn(project_uuid)

    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Subscribing {user_email} to {project_uuid} notifications.")
        return

    try:
        client = create_aws_client('sns', current_app.config['AWS_REGION'])

        client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol='email',
            Endpoint=user_email
        )

        current_app.logger.info(f"Email {user_email} subscribed successfully to topic {sns_topic_arn}.")
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to create SNS subscription: {e}")
        raise RuntimeError(f"Error creating SNS subscription: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error in SNS subscription: {str(e)}")
        raise e


def unsubscribe_sns_subscription(project_uuid: str, user_uuid: str) -> Response:
    """Removes an SNS subscription for a user."""
    from app.models import (
        get_user_info,
        get_topic_arn,
        get_subscription_arn_by_email
    )

    user_info = get_user_info(user_uuid)
    user_email = user_info.get('email')
    sns_topic_arn = get_topic_arn(project_uuid)

    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Unsubscribing {user_email} from {project_uuid} notifications.")
        return

    try:
        client = create_aws_client('sns', current_app.config['AWS_REGION'])

        # Retrieve the subscription ARN associated with the user's email
        subscription_arn = get_subscription_arn_by_email(client, sns_topic_arn, user_email)

        if subscription_arn is None:
            current_app.logger.warning(f"No subscription found for {user_email} on topic {sns_topic_arn}.")
            return

        client.unsubscribe(SubscriptionArn=subscription_arn)
        current_app.logger.info(f"Email {user_email} unsubscribed successfully from topic {sns_topic_arn}.")
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to unsubscribe SNS subscription: {e}")
        raise RuntimeError(f"Error unsubscribing SNS subscription: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error in SNS unsubscription: {str(e)}")
        raise e


def send_sns_notification(project_uuid: str) -> None:
    """Send an SNS notification to all subscribed users when an error occurs"""
    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Sending notification to {project_uuid}: New Issue Logged")
        return

    try:
        from app.models import get_topic_arn

        client = create_aws_client('sns', current_app.config['AWS_REGION'])
        sns_topic_arn = get_topic_arn(project_uuid)
        
        client.publish(
            TopicArn=sns_topic_arn,
            Message="New Issue Logged",
            Subject=f"Notification for Project {project_uuid}",
            MessageAttributes={
                'project_id': {
                    'DataType': 'String',
                    'StringValue': project_uuid
                }
            }
        )
        current_app.logger.info(f"Sent notification to developers assigned to project {project_uuid}")
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to send SNS notification: {e}")
        raise RuntimeError(f"Error sending SNS notification: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error sending SNS notification: {str(e)}")
        raise e


def delete_sns_topic_from_aws(project_uuid: str) -> None:
    """Delete SNS topic from SNS when the corresponding project is deleted"""
    if current_app.config["ENVIRONMENT"] == "development":
        current_app.logger.info(f"[MOCK] Deleting SNS topic for project {project_uuid}.")
        return

    try:
        from app.models import get_topic_arn

        topic_arn = get_topic_arn(project_uuid)
        client = create_aws_client('sns')
        client.deleteTopic(TopicArn=topic_arn)
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Failed to delete SNS topic for project {project_uuid}: {e}")
        raise RuntimeError(f"Error deleting SNS topic for project {project_uuid}: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Unexpected error deleting SNS topic: {str(e)}")
        raise e
    
def get_subscription_arn_by_email(client, topic_arn: str, email: str) -> str:
    """Finds the subscription ARN for a given email."""
    try:
        paginator = client.get_paginator('list_subscriptions_by_topic')
        for page in paginator.paginate(TopicArn=topic_arn):
            for subscription in page.get('Subscriptions', []):
                if subscription.get('Endpoint') == email:
                    return subscription.get('SubscriptionArn')
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Error retrieving subscriptions for topic {topic_arn}: {e}")
        raise RuntimeError(f"Error retrieving subscriptions: {str(e)}")

    return None
