#!/usr/bin/env python3
"""
Test script for Admin Dashboard functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_dashboard():
    print("🧪 Testing Admin Dashboard Functionality")
    print("=" * 50)
    
    # Step 1: Admin Login
    print("\n1. Admin Login...")
    admin_login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/customers/admin/login", json=admin_login_data)
    
    if login_response.status_code == 200:
        admin_token = login_response.json().get('token')
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 2: Get All Customers
    print("\n2. Fetching all customers...")
    customers_response = requests.get(f"{BASE_URL}/api/customers/", headers=headers)
    
    if customers_response.status_code == 200:
        customers = customers_response.json()
        print(f"✅ Found {len(customers)} customers")
        if customers:
            customer_id = customers[0].get('customer_id')
            print(f"   Using customer: {customer_id}")
        else:
            print("❌ No customers found")
            return
    else:
        print(f"❌ Failed to fetch customers: {customers_response.status_code}")
        print(customers_response.text)
        return
    
    # Step 3: Get Customer Machines
    print(f"\n3. Fetching machines for customer {customer_id}...")
    machines_response = requests.get(f"{BASE_URL}/api/machines/admin/customer/{customer_id}", headers=headers)
    
    if machines_response.status_code == 200:
        machines_data = machines_response.json()
        machines = machines_data.get('machines', [])
        print(f"✅ Found {len(machines)} machines")
        if machines:
            machine_id = machines[0].get('id')
            print(f"   Using machine: {machine_id}")
        else:
            print("❌ No machines found for this customer")
            return
    else:
        print(f"❌ Failed to fetch machines: {machines_response.status_code}")
        print(machines_response.text)
        return
    
    # Step 4: Get Machine Files
    print(f"\n4. Fetching files for machine {machine_id}...")
    files_response = requests.get(f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}", headers=headers)
    
    if files_response.status_code == 200:
        files_data = files_response.json()
        files = files_data.get('files', [])
        print(f"✅ Found {len(files)} files")
        for file in files:
            print(f"   - {file.get('filename')} (v{file.get('version')})")
    else:
        print(f"❌ Failed to fetch files: {files_response.status_code}")
        print(files_response.text)
    
    print("\n🎉 Admin Dashboard Test Completed!")

if __name__ == "__main__":
    test_admin_dashboard() 