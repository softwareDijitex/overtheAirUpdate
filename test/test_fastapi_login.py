#!/usr/bin/env python3
"""
Test script for FastAPI login endpoint
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_fastapi_login():
    """Test the FastAPI login endpoint"""
    print("🧪 Testing FastAPI Login Endpoint")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health check status: {response.status_code}")
        if response.status_code == 204:
            print("   ✅ Server is running")
        else:
            print("   ❌ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server")
        print("   Make sure the FastAPI server is running on localhost:8000")
        return False
    
    # Test 2: Test login endpoint with valid data
    print(f"\n2. Testing login endpoint with valid data...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/login", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful")
            print(f"   Response: {json.dumps(result, indent=2)}")
        elif response.status_code == 401:
            result = response.json()
            print(f"   ✅ Login correctly rejected (expected for invalid credentials)")
            print(f"   Error: {result.get('detail') or result.get('error')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 3: Test login endpoint with missing fields
    print(f"\n3. Testing login with missing fields...")
    incomplete_data = {
        "email": "test@example.com"
        # Missing password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/login", 
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 422:  # FastAPI validation error
            result = response.json()
            print(f"   ✅ Missing fields correctly rejected")
            print(f"   Validation Error: {result}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 4: Test API documentation
    print(f"\n4. Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   OpenAPI docs status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API documentation available at /docs")
        else:
            print("   ❌ API documentation not available")
            
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"   OpenAPI spec status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ OpenAPI specification available")
        else:
            print("   ❌ OpenAPI specification not available")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Documentation test failed: {e}")
    
    print(f"\n🎉 FastAPI login endpoint test completed!")
    return True

def test_register_endpoint():
    """Test the FastAPI register endpoint"""
    print(f"\n📝 Testing FastAPI Register Endpoint")
    print("=" * 50)
    
    # Test registration with unique email
    print(f"\n1. Testing registration...")
    register_data = {
        "name": "FastAPI Test User",
        "email": f"fastapi_test_{int(time.time())}@example.com",
        "phone": "+1234567890",
        "address": "123 FastAPI St, Test City, TC 12345",
        "password": "fastapipassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/register", 
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Registration successful")
            print(f"   Customer ID: {result.get('customer_id')}")
            print(f"   Token: {result.get('token')[:50]}...")
            return result.get('customer_id'), result.get('token')
        else:
            result = response.json()
            print(f"   ❌ Registration failed: {result}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return None, None

def test_login_with_registered_user():
    """Test login with a newly registered user"""
    print(f"\n🔄 Testing Login with Registered User")
    print("=" * 50)
    
    # First register a user
    customer_id, token = test_register_endpoint()
    
    if not customer_id:
        print("   ❌ Cannot test login - registration failed")
        return False
    
    # Then try to login with the same credentials
    print(f"\n2. Testing login with registered credentials...")
    login_data = {
        "email": f"fastapi_test_{int(time.time()-1)}@example.com",  # Use same timestamp
        "password": "fastapipassword123"
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
            print(f"   ✅ Login successful")
            print(f"   Customer ID: {result.get('customer_id')}")
            print(f"   Token: {result.get('token')[:50]}...")
            
            # Verify customer_id matches
            if result.get('customer_id') == customer_id:
                print(f"   ✅ Customer ID matches between register and login")
                return True
            else:
                print(f"   ❌ Customer ID mismatch")
                return False
        else:
            result = response.json()
            print(f"   ❌ Login failed: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    try:
        # Test basic login functionality
        if test_fastapi_login():
            # Test complete register -> login flow
            test_login_with_registered_user()
        else:
            print("\n❌ FastAPI login tests failed!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 