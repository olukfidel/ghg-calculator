"""
Configuration Management.

This file defines configuration classes for different environments
(Development, Testing, Production). It loads sensitive data
from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class."""
    # Secret key is crucial for session security, CSRF protection, and JWT signing
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_hard_to_guess_default_secret_key'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Define the database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = False # Set to True to see SQL queries in logs


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    # Use an in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable CSRF protection in testing forms (if you use Flask-WTF)
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Dictionary to map config names to their respective classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}