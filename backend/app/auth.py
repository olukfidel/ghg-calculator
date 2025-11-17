"""
Authentication Handling (JWT).

This file contains helper functions for creating and decoding JSON Web Tokens (JWT)
and a decorator (`@token_required`) to protect API endpoints.
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, Blueprint
from .models import User

# Create a Blueprint for auth routes
auth = Blueprint('auth', __name__)

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :param user_id: integer
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1, seconds=0),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token: string
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def token_required(f):
    """
    Decorator for protecting routes with JWT.
    
    It expects the token in the 'Authorization' header as 'Bearer <token>'.
    It decodes the token, finds the user, and passes the user object
    to the decorated function as the first argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check for 'Authorization' header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Split 'Bearer <token>'
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Bearer token malformed.'}), 401

        if not token:
            return jsonify({'message': 'Token is missing.'}), 401

        # Decode the token
        user_id = decode_auth_token(token)
        
        # Handle decoding errors
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401
        
        # Fetch the user from the database
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'message': 'User not found.'}), 401

        # Pass the user object to the route
        return f(current_user, *args, **kwargs)

    return decorated


# --- Authentication Routes ---

from . import db, bcrypt
from .models import User

@auth.route('/register', methods=['POST'])
def register():
    """
    User Registration Endpoint.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required.'}), 400

    # Check if user already exists
    user = User.query.filter_by(email=data.get('email')).first()
    if user:
        return jsonify({'message': 'Email already registered.'}), 409
        
    user = User.query.filter_by(username=data.get('username')).first()
    if user:
        return jsonify({'message': 'Username already taken.'}), 409

    try:
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            company_name=data.get('company_name')
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token for the new user
        auth_token = encode_auth_token(new_user.id)
        
        return jsonify({
            'message': 'User registered successfully.',
            'auth_token': auth_token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500


@auth.route('/login', methods=['POST'])
def login():
    """
    User Login Endpoint.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required.'}), 400

    try:
        user = User.query.filter_by(email=data.get('email')).first()

        # Check if user exists and password is correct
        if user and user.check_password(data.get('password')):
            auth_token = encode_auth_token(user.id)
            return jsonify({
                'message': 'Login successful.',
                'auth_token': auth_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 401
            
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500