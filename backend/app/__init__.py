# __init__.py
from flask import Flask
from flask_cors import CORS
from .transaction import start_transaction_processor  # Import your transaction logic

def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes and origins
    CORS(app)
    
    # Start Kafka consumer in a background thread
    start_transaction_processor()

    # Register blueprints
    from .routes import api
    app.register_blueprint(api)

    return app
