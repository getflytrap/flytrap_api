import boto3

def setup_mock_sns_topic(project_uuid, region="us-east-1"):
    sns_client = boto3.client("sns", region_name=region)
    topic_name = f"project_{project_uuid}_notifications"
    topic_response = sns_client.create_topic(Name=topic_name)
    return topic_response["TopicArn"]