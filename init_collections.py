#!/usr/bin/env python3
"""
Initialize MongoDB collections for the Customer Management System
This script ensures all required collections exist before the application starts.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def init_collections():
    """Initialize MongoDB collections"""
    try:
        # Get MongoDB URI
        mongo_uri = os.environ.get('MONGO_URI')
        if not mongo_uri:
            print("❌ MONGO_URI not found in environment variables")
            return False
        
        print(f"🔗 Connecting to MongoDB...")
        client = MongoClient(mongo_uri)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db_name = os.environ.get('DB_NAME', 'customer_management')
        db = client[db_name]
        
        # Initialize collections
        collections_to_create = ['customers', 'files']
        
        for collection_name in collections_to_create:
            try:
                # Create collection if it doesn't exist
                if collection_name not in db.list_collection_names():
                    db.create_collection(collection_name)
                    print(f"✅ Created collection: {collection_name}")
                else:
                    print(f"ℹ️  Collection already exists: {collection_name}")
                
                # Create indexes for better performance
                if collection_name == 'customers':
                    db.customers.create_index("email", unique=True)
                    db.customers.create_index("customer_id", unique=True)
                    print(f"✅ Created indexes for {collection_name}")
                
                elif collection_name == 'files':
                    db.files.create_index([("customer_id", 1), ("filename", 1), ("version", 1)], unique=True)
                    db.files.create_index("customer_id")
                    print(f"✅ Created indexes for {collection_name}")
                
            except Exception as e:
                print(f"⚠️  Warning creating collection {collection_name}: {e}")
        
        print("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__app__":
    init_collections() 