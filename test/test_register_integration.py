#!/usr/bin/env python3
"""
Integration test for the /register endpoint
Tests the actual registration flow with a running server
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_register_endpoint():
    """Test the register endpoint with various scenarios"""
    print("🧪 Testing Register Endpoint")
    print("=" * 50)
    
    # Test 1: Successful registration
    print("\n1. Testing successful registration...")
    customer_data = {
        "name": "Test User",
        "email": f"testuser_{int(time.time())}@example.com",  # Unique email
        "phone": "+1234567890",
        "address": "123 Test St, Test City, TS 12345",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/customers/register", json=customer_data)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"   ✅ Registration successful")
        print(f"   Customer ID: {result.get('customer_id')}")
        print(f"   Token: {result.get('token')[:50]}...")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"   ❌ Registration failed: {response.text}")
        return False
    
    # Test 2: Duplicate email registration
    print(f"\n2. Testing duplicate email registration...")
    response = requests.post(f"{BASE_URL}/api/customers/register", json=customer_data)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"   ✅ Duplicate email correctly rejected")
        print(f"   Error: {result.get('error')}")
    else:
        print(f"   ❌ Duplicate email not properly handled: {response.text}")
        return False
    
    # Test 3: Missing required fields
    print(f"\n3. Testing missing required fields...")
    incomplete_data = {
        "name": "Test User",
        "email": "test@example.com"
        # Missing phone, address, password
    }
    
    response = requests.post(f"{BASE_URL}/api/customers/register", json=incomplete_data)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"   ✅ Missing fields correctly rejected")
        print(f"   Error: {result.get('error')}")
    else:
        print(f"   ❌ Missing fields not properly handled: {response.text}")
        return False
    
    # Test 4: Empty required fields
    print(f"\n4. Testing empty required fields...")
    empty_data = {
        "name": "",
        "email": "test@example.com",
        "phone": "+1234567890",
        "address": "123 Test St",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/customers/register", json=empty_data)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"   ✅ Empty fields correctly rejected")
        print(f"   Error: {result.get('error')}")
    else:
        print(f"   ❌ Empty fields not properly handled: {response.text}")
        return False
    
    # Test 5: Invalid JSON
    print(f"\n5. Testing invalid JSON data...")
    response = requests.post(
        f"{BASE_URL}/api/customers/register", 
        data="invalid json data",
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 500:
        result = response.json()
        print(f"   ✅ Invalid JSON correctly rejected")
        print(f"   Error: {result.get('error')}")
    else:
        print(f"   ❌ Invalid JSON not properly handled: {response.text}")
        return False
    
    print(f"\n🎉 All register endpoint tests passed!")
    return True

def test_register_and_login_flow():
    """Test the complete flow: register -> login"""
    print("\n🔄 Testing Register -> Login Flow")
    print("=" * 50)
    
    # Register a new customer
    print("\n1. Registering new customer...")
    customer_data = {
        "name": "Flow Test User",
        "email": f"flowtest_{int(time.time())}@example.com",
        "phone": "+1234567890",
        "address": "456 Flow St, Flow City, FC 67890",
        "password": "flowpassword123"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/customers/register", json=customer_data)
    
    if register_response.status_code != 201:
        print(f"   ❌ Registration failed: {register_response.text}")
        return False
    
    register_result = register_response.json()
    customer_id = register_result.get('customer_id')
    print(f"   ✅ Registration successful, Customer ID: {customer_id}")
    
    # Login with the same credentials
    print(f"\n2. Logging in with registered credentials...")
    login_data = {
        "email": customer_data["email"],
        "password": customer_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/api/customers/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"   ✅ Login successful")
        print(f"   Customer ID: {login_result.get('customer_id')}")
        print(f"   Token: {login_result.get('token')[:50]}...")
        
        # Verify customer_id matches
        if login_result.get('customer_id') == customer_id:
            print(f"   ✅ Customer ID matches between register and login")
        else:
            print(f"   ❌ Customer ID mismatch")
            return False
    else:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    print(f"\n🎉 Register -> Login flow test passed!")
    return True

if __name__ == "__main__":
    try:
        # Test basic register endpoint functionality
        if test_register_endpoint():
            # Test complete flow
            test_register_and_login_flow()
        else:
            print("\n❌ Register endpoint tests failed!")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 