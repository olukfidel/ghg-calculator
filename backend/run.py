"""
Application Entry Point.

This file serves as the main entry point for the Flask application.
It creates the app instance using the factory pattern and runs it.
It also registers the database migration commands.
"""

import os
from app import create_app, db
from flask_migrate import Migrate

# Create the application instance using the factory
# Use 'default' config unless FLASK_CONFIG is set in the environment
config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)

# Initialize Flask-Migrate
# This connects the app and the SQLAlchemy db instance for migrations
migrate = Migrate(app, db)

if __name__ == '__main__':
    # Run the application
    # The host '0.0.0.0' makes it accessible externally (e.g., from Docker)
    app.run(host='0.0.0.0')