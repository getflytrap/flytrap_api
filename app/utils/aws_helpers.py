import boto3
import os
from app.config import ENVIRONMENT, AWS_REGION
from flask import current_app


def create_aws_client(service):
    if ENVIRONMENT == "production":
        return boto3.client(
            service, 
            region_name=AWS_REGION, 
            endpoint_url=f"https://{service}.{AWS_REGION}.amazonaws.com"
        )
    return None


def associate_api_key_with_usage_plan(project_name, api_key, usage_plan_id):
    # Create the API key in AWS
    api_gateway_client = create_aws_client('apigateway')
    response = api_gateway_client.create_api_key(name=project_name, value=api_key, enabled=True)
    api_key_id = response["id"]

    # Associate API key with the usage plan
    api_gateway_client.create_usage_plan_key(
        usagePlanId=usage_plan_id, keyId=api_key_id, keyType="API_KEY"
    )

def create_sns_topic(project_uuid):
    """Creates an SNS topic for a specific project if it doesn't exist."""
    sns_client = create_aws_client('sns')
    topic_name = f"project_{project_uuid}_notifications"
    
    # Create a new SNS topic (or retrieve ARN if it already exists)
    response = sns_client.create_topic(Name=topic_name)
    sns_topic_arn = response.get('TopicArn')
    return sns_topic_arn

def create_sns_subscription(project_uuid, user_uuid):
    from app.models import get_user_info, get_topic_arn, save_sns_subscription_arn_to_db

    user_info = get_user_info(user_uuid)
    user_email = user_info.get('email')
    sns_topic_arn = get_topic_arn(project_uuid)
    current_app.logger.info(f"user_email: {user_email}, sns_topic_arn: {sns_topic_arn}")
    sns_client = create_aws_client('sns')

    try:
        subscription_arn = sns_client.subscribe(
            TopicArn=sns_topic_arn,
            Protocol='email',
            Endpoint=user_email
        )

        # To-do: implement functionality to asynchronously receive subscription arn and save to db
        #save_sns_subscription_arn_to_db(user_uuid, project_uuid, subscription_arn)

        return {
            'statusCode': 200,
            'body': f'Email {user_email} subscribed successfully.'
        }
    except Exception as e:
        current_app.logger.debug(f"Error in SNS Subscription: {e}")
        raise e

def send_sns_notification(project_uuid):
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

def delete_api_key_from_aws(api_key_value):
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

# To-do: finish implementing logic to properly set sns_subscription_arns

# def delete_sns_subscriptions_from_aws(table, uuid):
#     from app.models import get_all_sns_subscription_arns_for_user, get_all_sns_subscription_arns_for_project

#     try:
#         if table == 'projects':
#             arns = get_all_sns_subscription_arns_for_project(uuid)
#         elif table == 'users':
#             arns = get_all_sns_subscription_arns_for_user(uuid)
        
#         sns_client = create_aws_client('sns')

#         for arn in arns:
#             if arn is not None:
#                 sns_client.unsubscribe(SubscriptionArn=arn)
    
#     except Exception as e:
#         current_app.logger.debug(f"Error deleting sns subscription from AWS: {str(e)}")
