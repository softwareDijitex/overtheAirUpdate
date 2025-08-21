from .config import Config
import os
from pymongo import MongoClient
import bcrypt

def get_mongo_client():
    """Get MongoDB client for FastAPI"""
    client = MongoClient(
        Config.MONGO_URI,
        ssl=True,
        tlsAllowInvalidCertificates=True,  # ❌ Insecure: for local testing only
        serverSelectionTimeoutMS=20000
    )
    return client

def get_database():
    """Get MongoDB database for FastAPI"""
    client = get_mongo_client()
    return client[Config.DB_NAME] if Config.DB_NAME else None

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Check password against hash using bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def init_fastapi_components():
    """Initialize FastAPI components - now just returns the database"""
    print("Initializing FastAPI components")
    
    # Test database connection
    try:
        db = get_database()
        if db is not None:
            # Test the connection
            db.command('ping')
            print("FastAPI components initialized successfully")
            return db
        else:
            print("Warning: Database not configured")
            return None
    except Exception as e:
        print(f"Error initializing database: {e}")
        return None 