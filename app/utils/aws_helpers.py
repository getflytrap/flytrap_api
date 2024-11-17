import boto3
from app.config import ENVIRONMENT, AWS_REGION


def create_aws_api_gateway_client():
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

def delete_api_key(client, api_key):
    try:
        # delete_api_key returns None if successful
        client.delete_api_key(apiKey=api_key)
        return "", 204
    except Exception as e:
        raise e

