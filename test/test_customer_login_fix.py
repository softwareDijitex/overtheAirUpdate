#!/usr/bin/env python3
"""
Test script to verify customer login fix
Tests: Login response format and customer_id extraction
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_customer_login_fix():
    print("🧪 Testing Customer Login Fix")
    print("=" * 50)
    
    # Step 1: Customer login
    print("\n1. Customer Login...")
    login_data = {
        "email": "customer1@inoweave.com",
        "password": "customer1"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/customers/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    login_result = login_response.json()
    print(f"✅ Login successful")
    print(f"   Customer ID: {login_result.get('customer_id')}")
    print(f"   Token: {login_result.get('token')[:50]}...")
    
    # Step 2: Test machine fetching with correct customer_id
    print(f"\n2. Testing machine fetch with customer_id...")
    headers = {"Authorization": f"Bearer {login_result['token']}"}
    
    machines_response = requests.get(
        f"{BASE_URL}/api/machines/customer/{login_result['customer_id']}", 
        headers=headers
    )
    
    if machines_response.status_code != 200:
        print(f"❌ Machine fetch failed: {machines_response.status_code}")
        return False
    
    machines_data = machines_response.json()
    machines = machines_data.get('machines', [])
    print(f"✅ Machine fetch successful")
    print(f"   Found {len(machines)} machines")
    
    for machine in machines:
        print(f"   - {machine['name']} (ID: {machine['id']})")
    
    print("\n🎉 All tests passed! Customer login fix is working correctly.")
    return True

if __name__ == "__main__":
    test_customer_login_fix() 