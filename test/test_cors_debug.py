#!/usr/bin/env python3
"""
CORS debugging script to identify CORS issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_cors_preflight():
    """Test CORS preflight requests"""
    print("🔍 Testing CORS Preflight Requests")
    print("=" * 50)
    
    # Test 1: OPTIONS request to login endpoint
    print("\n1. Testing OPTIONS request to login endpoint...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/customers/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for header, value in response.headers.items():
            if header.lower().startswith('access-control'):
                print(f"     {header}: {value}")
        
        if response.status_code == 200:
            print("   ✅ OPTIONS request successful")
        else:
            print("   ❌ OPTIONS request failed")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ OPTIONS request failed: {e}")
    
    # Test 2: Test CORS debug endpoint
    print(f"\n2. Testing CORS debug endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/test-cors",
            headers={"Origin": "http://localhost:3000"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ CORS debug endpoint working")
        else:
            print("   ❌ CORS debug endpoint failed")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS debug request failed: {e}")

def test_login_with_cors():
    """Test login endpoint with CORS headers"""
    print(f"\n3. Testing login endpoint with CORS headers...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customers/login",
            json=login_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for header, value in response.headers.items():
            if header.lower().startswith('access-control'):
                print(f"     {header}: {value}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful: {result}")
        elif response.status_code == 401:
            result = response.json()
            print(f"   ✅ Login correctly rejected: {result}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Login request failed: {e}")

def test_server_info():
    """Test server information"""
    print(f"\n4. Testing server information...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health endpoint status: {response.status_code}")
        
        # Test OpenAPI docs
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   OpenAPI docs status: {response.status_code}")
        
        # Test OpenAPI spec
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"   OpenAPI spec status: {response.status_code}")
        
        if response.status_code == 200:
            spec = response.json()
            print(f"   API title: {spec.get('info', {}).get('title', 'Unknown')}")
            print(f"   API version: {spec.get('info', {}).get('version', 'Unknown')}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server info request failed: {e}")

def test_frontend_origin():
    """Test what origin the frontend is actually using"""
    print(f"\n5. Testing frontend origin detection...")
    
    # Common frontend origins
    origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    for origin in origins:
        try:
            response = requests.get(
                f"{BASE_URL}/api/test-cors",
                headers={"Origin": origin}
            )
            
            if response.status_code == 200:
                print(f"   ✅ Origin {origin} is working")
            else:
                print(f"   ❌ Origin {origin} failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Origin {origin} failed: {e}")

if __name__ == "__main__":
    try:
        test_cors_preflight()
        test_login_with_cors()
        test_server_info()
        test_frontend_origin()
    except Exception as e:
        print(f"❌ CORS debug failed with error: {e}") 