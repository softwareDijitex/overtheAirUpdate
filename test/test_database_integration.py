#!/usr/bin/env python3
"""
Test script to verify database integration in FastAPI
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_database_connection():
    """Test database connection through FastAPI"""
    print("🗄️ Testing Database Integration")
    print("=" * 50)
    
    # Test database connection endpoint
    print("\n1. Testing database connection...")
    try:
        response = requests.get(f"{BASE_URL}/api/customers/test-db")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Database connection successful")
            print(f"   Customer count: {result.get('customer_count')}")
            print(f"   Database name: {result.get('database_name')}")
            return True
        else:
            result = response.json()
            print(f"   ❌ Database connection failed: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Database test request failed: {e}")
        return False

def test_customer_creation():
    """Test creating a customer through FastAPI"""
    print(f"\n2. Testing customer creation...")
    
    import time
    customer_data = {
        "name": "Test Customer",
        "email": f"test_customer_{int(time.time())}@example.com",
        "phone": "+1234567890",
        "address": "123 Test St, Test City, TC 12345",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/register",
            json=customer_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Customer creation successful")
            print(f"   Customer ID: {result.get('customer_id')}")
            return result.get('customer_id')
        else:
            result = response.json()
            print(f"   ❌ Customer creation failed: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Customer creation request failed: {e}")
        return None

def test_customer_login(customer_id):
    """Test logging in with the created customer"""
    print(f"\n3. Testing customer login...")
    
    login_data = {
        "email": f"test_customer_{int(time.time()-1)}@example.com",  # Use same timestamp
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Customer login successful")
            print(f"   Customer ID: {result.get('customer_id')}")
            print(f"   Token: {result.get('token')[:50]}...")
            return result.get('token')
        else:
            result = response.json()
            print(f"   ❌ Customer login failed: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Customer login request failed: {e}")
        return None

def test_customer_profile(token):
    """Test getting customer profile with token"""
    print(f"\n4. Testing customer profile...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/customers/profile",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Customer profile retrieved successfully")
            print(f"   Customer name: {result.get('name')}")
            print(f"   Customer email: {result.get('email')}")
            return True
        else:
            result = response.json()
            print(f"   ❌ Customer profile failed: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Customer profile request failed: {e}")
        return False

if __name__ == "__main__":
    import time
    
    try:
        # Test database connection
        if test_database_connection():
            # Test customer creation
            customer_id = test_customer_creation()
            
            if customer_id:
                # Test customer login
                token = test_customer_login(customer_id)
                
                if token:
                    # Test customer profile
                    test_customer_profile(token)
                    
        print(f"\n🎉 Database integration test completed!")
        
    except Exception as e:
        print(f"❌ Database integration test failed with error: {e}") 