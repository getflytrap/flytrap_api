import pytest
from moto import mock_apigateway, mock_sns
import boto3
from app import create_app
from flask import json


# This will mock both API Gateway and SNS
@pytest.fixture
def app():
    # Initialize the Flask app
    app = create_app()
    yield app


# Mocking API Gateway for our tests
@mock_apigateway
@mock_sns
def test_create_project(app):
    # Mocking API Gateway setup
    client = boto3.client('apigateway', region_name='us-east-1')
    client.create_rest_api(name='TestAPI', description='Test API')

    # Mocking SNS setup
    sns_client = boto3.client('sns', region_name='us-east-1')
    sns_topic = sns_client.create_topic(Name='TestTopic')

    # Now you can test your Flask route for creating a project
    with app.test_client() as client:
        data = {
            'name': 'Test Project',
            'platform': 'Test Platform'
        }

        # Make a POST request to your API to create a project
        response = client.post('/api/projects', data=json.dumps(data), content_type='application/json')

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'status' in response_data and response_data['status'] == 'success'
        assert 'data' in response_data
        assert 'uuid' in response_data['data']


# You can also mock other routes or test behaviors for different scenarios
@mock_apigateway
@mock_sns
def test_delete_project(app):
    # Mock the delete project logic as needed (API Gateway, SNS etc.)
    # For instance, test what happens when deleting a project
    with app.test_client() as client:
        response = client.delete('/api/projects/some-uuid')
        assert response.status_code == 204
