"""
Integration Tests for the API Endpoints.

This file tests the API endpoints using a test client.
"""

import pytest
import json
from app import create_app, db
from app.models import User

@pytest.fixture(scope='module')
def test_client():
    """
    Pytest fixture to set up a test client for the application.
    Uses the 'testing' configuration.
    """
    app = create_app('testing')
    
    with app.test_client() as testing_client:
        with app.app_context():
            # Create all database tables
            db.create_all()
            yield testing_client  # this is where the testing happens!
            # Drop all tables after tests
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope='module')
def new_user():
    """Fixture to create a new user for testing auth."""
    user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "company_name": "Test Co"
    }
    return user


def test_register_user(test_client, new_user):
    """
    Test user registration.
    """
    response = test_client.post(
        '/auth/register',
        data=json.dumps(new_user),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'auth_token' in data
    assert data['user']['username'] == 'testuser'

def test_login_user(test_client, new_user):
    """
    Test user login.
    """
    # First, register the user (even if previous test did, this is isolated)
    test_client.post(
        '/auth/register',
        data=json.dumps(new_user),
        content_type='application/json'
    )
    
    # Now, test login
    response = test_client.post(
        '/auth/login',
        data=json.dumps({
            "email": new_user['email'],
            "password": new_user['password']
        }),
        content_type='application/json'
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'auth_token' in data
    assert data['user']['email'] == new_user['email']

def test_access_protected_route_without_token(test_client):
    """
    Test that accessing a protected route without a token fails.
    """
    response = test_client.get('/api/factors')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Token is missing.'

def test_access_protected_route_with_token(test_client, new_user):
    """
    Test that a protected route can be accessed with a valid token.
    """
    # 1. Register and Login to get a token
    test_client.post(
        '/auth/register',
        data=json.dumps(new_user),
        content_type='application/json'
    )
    login_response = test_client.post(
        '/auth/login',
        data=json.dumps({
            "email": new_user['email'],
            "password": new_user['password']
        }),
        content_type='application/json'
    )
    token = json.loads(login_response.data)['auth_token']

    # 2. Access the protected route with the token
    response = test_client.get(
        '/api/factors',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    
    assert response.status_code == 200
    # The response should be a list (even if empty, from seeding)
    assert isinstance(json.loads(response.data), list)