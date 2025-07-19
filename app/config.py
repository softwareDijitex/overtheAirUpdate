import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_and_secure_key_please_change_this'
    MONGO_URI = os.environ.get('MONGO_URI')
    DB_NAME = os.environ.get('DB_NAME')
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME')
    MAX_FILE_SIZE = (int(os.environ.get('MAX_FILE_SIZE_MB', 2))) * 1024 * 1024
    
    # Debug: Print environment variables
    print(f"MONGO_URI: {MONGO_URI}")
    print(f"DB_NAME: {DB_NAME}")
    print(f"AZURE_STORAGE_CONNECTION_STRING: {AZURE_STORAGE_CONNECTION_STRING[:50]}..." if AZURE_STORAGE_CONNECTION_STRING else "Not set")
    print(f"AZURE_STORAGE_CONTAINER_NAME: {AZURE_STORAGE_CONTAINER_NAME}")
