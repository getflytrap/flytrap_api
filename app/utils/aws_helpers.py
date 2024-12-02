from flask import current_app, Response
import logging
import boto3
import botocore.exceptions

logger = logging.getLogger()


def create_aws_client(service: str, region: str) -> boto3.client:
    """Instantiates a boto3 client for a specific AWS service"""
    try:
        client = boto3.client(
            service,
            region_name=region,
            endpoint_url=f"https://{service}.{region}.amazonaws.com",
        )
        logger.debug(f"AWS client created for {service} in region {region}.")
        return client
    except botocore.exceptions.BotoCoreError as e:
        logger.error(f"Failed to create AWS client for {service}: {e}")
        raise RuntimeError(f"Error creating AWS client for {service}: {str(e)}")


def get_secret(secret_name: str, region: str) -> str:
    """Fetch a secret from AWS Secrets Manager."""
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region)

        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]
        logger.debug(f"Secret {secret_name} fetched successfully.")
        return secret
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to fetch secret {secret_name}: {e}")
        raise RuntimeError(f"Failed to fetch secret {secret_name}: {e}")


def associate_api_key_with_usage_plan(project_name: str, api_key: str) -> None:
    """Associates a project's API key with the AWS usage plan"""
    if current_app.config["ENVIRONMENT"] == "development":
        logger.info(
            f"[MOCK] Associating API key {api_key} with usage plan for project "
            f"{project_name}."
        )
        return

    try:
        client = create_aws_client("apigateway", current_app.config["AWS_REGION"])
        response = client.create_api_key(name=project_name, value=api_key, enabled=True)
        api_key_id = response["id"]

        client.create_usage_plan_key(
            usagePlanId=current_app.config["USAGE_PLAN_ID"],
            keyId=api_key_id,
            keyType="API_KEY",
        )

        logger.info(f"API key {api_key} associated with usage plan.")
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to associate API key with usage plan: {e}")
        raise RuntimeError(f"Error associating API key with usage plan: {str(e)}")


def delete_api_key_from_aws(api_key_value: str) -> None:
    """Remove API key resources from AWS when the corresponding project is deleted"""
    if current_app.config["ENVIRONMENT"] == "development":
        logger.info(f"[MOCK] Deleting API key {api_key_value}.")
        return

    try:
        client = create_aws_client("apigateway")
        response = client.get_api_keys(includeValues=True)
        all_keys = response.get("items", [])

        key_id = next(
            (item["id"] for item in all_keys if item["value"] == api_key_value), None
        )

        if not key_id:
            logger.warning(f"API key {api_key_value} not found for deletion.")
            return

        client.delete_api_key(apiKey=key_id)
        logger.info(f"API key {api_key_value} deleted successfully.")
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to delete API key from AWS: {e}")
        raise RuntimeError(f"Error deleting API key: {str(e)}")


def create_sns_topic(project_uuid: str) -> str:
    """Creates an SNS topic for a specific project if it doesn't exist."""
    if current_app.config["ENVIRONMENT"] == "development":
        logger.info(f"[MOCK] Creating sns topic arn for project {project_uuid}.")
        return (
            f"arn:aws:sns:mock-region:123456789012:project_{project_uuid}_notifications"
        )

    try:
        sns_client = create_aws_client("sns", current_app.config["AWS_REGION"])
        topic_name = f"project_{project_uuid}_notifications"
        response = sns_client.create_topic(Name=topic_name)
        sns_topic_arn = response.get("TopicArn")
        logger.info(f"SNS topic created for project {project_uuid}.")
        return sns_topic_arn
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to create SNS topic for project {project_uuid}: {e}")
        raise RuntimeError(
            f"Error creating SNS topic for project {project_uuid}: {str(e)}"
        )


def create_sns_subscription(project_uuid: str, user_uuid: str) -> Response:
    """Creates an SNS subscription for a user"""
    from app.models import fetch_user, get_topic_arn

    try:
        user_info = fetch_user(user_uuid)
        user_email = user_info.get("email")
        sns_topic_arn = get_topic_arn(project_uuid)

        if current_app.config["ENVIRONMENT"] == "development":
            logger.info(
                f"[MOCK] Subscribing {user_email} to {project_uuid} notifications."
            )
            return

        if not user_email or not sns_topic_arn:
            logger.error(
                (
                    f"Missing data for subscription: user_email={user_email}, "
                    f"sns_topic_arn={sns_topic_arn}."
                )
            )
            raise ValueError("User email or SNS topic ARN is missing.")

        client = create_aws_client("sns", current_app.config["AWS_REGION"])
        response = client.subscribe(
            TopicArn=sns_topic_arn, Protocol="email", Endpoint=user_email
        )
        subscription_arn = response.get("SubscriptionArn")

        logger.info(
            (
                f"Email {user_email} subscribed successfully to topic {sns_topic_arn}. "
                f"Subscription ARN: {subscription_arn}."
            )
        )
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to create SNS subscription: {e}")
        raise RuntimeError(f"Error creating SNS subscription: {str(e)}")


def remove_sns_subscription(project_uuid: str, user_uuid: str) -> Response:
    """Removes an SNS subscription for a user."""
    from app.models import fetch_user, get_topic_arn, get_subscription_arn_by_email

    try:
        user_info = fetch_user(user_uuid)
        user_email = user_info.get("email")
        sns_topic_arn = get_topic_arn(project_uuid)

        if current_app.config["ENVIRONMENT"] == "development":
            logger.info(
                f"[MOCK] Unsubscribing {user_email} from {project_uuid} notifications."
            )
            return

        if not user_email or not sns_topic_arn:
            logger.error(
                (
                    f"Missing data for unsubscription: user_email={user_email}, "
                    f"sns_topic_arn={sns_topic_arn}."
                )
            )
            raise ValueError("User email or SNS topic ARN is missing.")

        client = create_aws_client("sns", current_app.config["AWS_REGION"])

        # Retrieve the subscription ARN associated with the user's email
        subscription_arn = get_subscription_arn_by_email(
            client, sns_topic_arn, user_email
        )

        if not subscription_arn:
            logger.warning(
                f"No subscription found for {user_email} on topic {sns_topic_arn}."
            )
            return

        client.unsubscribe(SubscriptionArn=subscription_arn)
        logger.info(
            f"Email {user_email} unsubscribed successfully from topic {sns_topic_arn}."
        )
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to unsubscribe SNS subscription: {e}")
        raise RuntimeError(f"Error unsubscribing SNS subscription: {str(e)}")


def send_sns_notification(project_uuid: str) -> None:
    """Send an SNS notification to all subscribed users when an error occurs"""
    if current_app.config["ENVIRONMENT"] == "development":
        logger.info(f"[MOCK] Sending notification to {project_uuid}: New Issue Logged")
        return

    try:
        from app.models import get_topic_arn

        client = create_aws_client("sns", current_app.config["AWS_REGION"])
        sns_topic_arn = get_topic_arn(project_uuid)

        client.publish(
            TopicArn=sns_topic_arn,
            Message="New Issue Logged",
            Subject=f"Notification for Project {project_uuid}",
            MessageAttributes={
                "project_id": {"DataType": "String", "StringValue": project_uuid}
            },
        )
        logger.info(f"Notification sent for project {project_uuid}.")
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")
        raise RuntimeError(f"Error sending SNS notification: {str(e)}")


def delete_sns_topic_from_aws(project_uuid: str) -> None:
    """Delete SNS topic from SNS when the corresponding project is deleted"""
    if current_app.config["ENVIRONMENT"] == "development":
        logger.info(f"[MOCK] Deleting SNS topic for project {project_uuid}.")
        return

    try:
        from app.models import get_topic_arn

        topic_arn = get_topic_arn(project_uuid)
        if not topic_arn:
            logger.warning(
                f"No SNS topic ARN found for project {project_uuid}. Skipping deletion."
            )
            return

        client = create_aws_client("sns")
        client.deleteTopic(TopicArn=topic_arn)
        logger.info(f"SNS topic {topic_arn} deleted successfully.")
    except botocore.exceptions.ClientError as e:
        logger.error(f"Failed to delete SNS topic for project {project_uuid}: {e}")
        raise RuntimeError(
            f"Error deleting SNS topic for project {project_uuid}: {str(e)}"
        )


def get_subscription_arn_by_email(client, topic_arn: str, email: str) -> str:
    """Finds the subscription ARN for a given email."""
    try:
        paginator = client.get_paginator("list_subscriptions_by_topic")
        for page in paginator.paginate(TopicArn=topic_arn):
            for subscription in page.get("Subscriptions", []):
                if subscription.get("Endpoint") == email:
                    subscription_arn = subscription.get("SubscriptionArn")
                    logger.debug(
                        f"Found subscription ARN for email {email}: {subscription_arn}."
                    )
                    return subscription_arn
        logger.info(
            f"No subscription ARN found for email {email} on topic {topic_arn}."
        )
        return None
    except botocore.exceptions.ClientError as e:
        logger.error(f"Error retrieving subscriptions for topic {topic_arn}: {e}")
        raise RuntimeError(f"Error retrieving subscriptions: {str(e)}")
