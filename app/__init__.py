from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from .config import Config
import os
from flask_cors import CORS

bcrypt = Bcrypt()
mongo = PyMongo()

def create_app(config_class=Config):
    """Create Flask app for compatibility with existing models"""
    print("Creating Flask app for compatibility")
    app = Flask(__name__, 
                static_folder='../frontend/build',
                static_url_path='')
    app.config.from_object(config_class)
    
    # Explicitly set MongoDB URI for Flask-PyMongo
    app.config['MONGO_URI'] = config_class.MONGO_URI

    # Enable CORS for all routes
    CORS(app)

    bcrypt.init_app(app)
    mongo.init_app(app)

    return app

def init_fastapi_components():
    """Initialize Flask components for FastAPI compatibility"""
    print("Initializing FastAPI components")
    
    # Create a minimal Flask app to initialize components
    temp_app = Flask(__name__)
    temp_app.config.from_object(Config)
    temp_app.config['MONGO_URI'] = Config.MONGO_URI
    
    # Initialize components
    bcrypt.init_app(temp_app)
    mongo.init_app(temp_app)
    
    print("FastAPI components initialized successfully")
    return bcrypt, mongo 