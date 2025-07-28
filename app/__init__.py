from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from .config import Config
import os
from flask_cors import CORS

bcrypt = Bcrypt()
mongo = PyMongo()

def create_app(config_class=Config):

    print("Creating app")
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

    from .routes.customer_routes import customer_bp
    from .routes.file_routes import file_bp
    from .routes.machine_routes import machine_bp

    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(file_bp, url_prefix='/api/files')
    app.register_blueprint(machine_bp, url_prefix='/api/machines')

    return app 