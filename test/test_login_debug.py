#!/usr/bin/env python3
"""
Debug script to test the login endpoint and identify issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_endpoint():
    """Test the login endpoint with various scenarios"""
    print("🔍 Debugging Login Endpoint")
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
        print("   Make sure the Flask server is running on localhost:8000")
        return False
    
    # Test 2: Test login endpoint directly
    print(f"\n2. Testing login endpoint...")
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
            print(f"   Error: {result.get('error')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 3: Test with missing fields
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
        
        if response.status_code == 400:
            result = response.json()
            print(f"   ✅ Missing fields correctly rejected")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 4: Test with invalid JSON
    print(f"\n4. Testing login with invalid JSON...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/login", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 500:
            result = response.json()
            print(f"   ✅ Invalid JSON correctly rejected")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    print(f"\n🎉 Login endpoint debug completed!")
    return True

def test_cors_headers():
    """Test CORS headers"""
    print(f"\n🌐 Testing CORS headers...")
    
    try:
        response = requests.options(f"{BASE_URL}/api/customers/login")
        print(f"   OPTIONS request status: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
        
        # Check for CORS headers
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods', 
            'Access-Control-Allow-Headers'
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"   ✅ {header}: {response.headers[header]}")
            else:
                print(f"   ❌ {header} missing")
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS test failed: {e}")

if __name__ == "__main__":
    try:
        test_login_endpoint()
        test_cors_headers()
    except Exception as e:
        print(f"❌ Debug failed with error: {e}") 