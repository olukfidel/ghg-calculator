"""
Application Factory.

This file contains the `create_app` factory function which initializes
and configures the Flask application, extensions, and blueprints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import config
import os

# Initialize extensions
# These are initialized here but configured inside the factory
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()


def create_app(config_name='default'):
    """
    Application factory function.
    
    Args:
        config_name (str): The name of the configuration to use
                           (e.g., 'development', 'production').
                           
    Returns:
        Flask: The configured Flask application instance.
    """
    
    app = Flask(__name__)
    
    # Load configuration from the config object
    app.config.from_object(config[config_name])
    
    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    # Enable CORS for all routes, allowing credentials
    cors.init_app(app, supports_credentials=True)

    # --- Register Blueprints ---
    # Blueprints help organize routes
    
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # --- Register CLI Commands ---
    # This adds commands like `flask seed_db`
    
    from .seed import seed_db_command
    app.cli.add_command(seed_db_command, "seed_db")

    return app