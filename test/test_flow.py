#!/usr/bin/env python3
"""
Automated Test Script for On The Fly Update System
Tests: Customer Registration -> Login -> Machine Creation -> File Upload
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_PASSWORD = "password123"
TEST_NAME = "Test User"
TEST_PHONE = "1234567890"
TEST_ADDRESS = "123 Test Street"

def print_step(step_num, description):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_response(response, step_name):
    """Print formatted response"""
    print(f"\n{step_name} Response:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def create_test_file():
    """Create a test file for upload"""
    test_content = f"""This is a test file created at {datetime.now()}
Customer: {TEST_NAME}
Email: {TEST_EMAIL}
This file is used for testing the file upload functionality.
"""
    filename = "test_file.txt"
    with open(filename, 'w') as f:
        f.write(test_content)
    return filename

def main():
    print("🚀 Starting Automated Test Flow for On The Fly Update System")
    print(f"Test Email: {TEST_EMAIL}")
    
    # Step 1: Register new customer
    print_step(1, "Registering New Customer")
    
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME,
        "phone": TEST_PHONE,
        "address": TEST_ADDRESS
    }
    
    register_response = requests.post(
        f"{BASE_URL}/api/customers/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(register_response, "Customer Registration")
    
    if register_response.status_code not in [200, 201, 400]:  # 400 means user already exists
        print("❌ Customer registration failed!")
        return
    
    # Step 2: Login as customer
    print_step(2, "Logging in as Customer")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/customers/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(login_response, "Customer Login")
    
    if login_response.status_code != 200:
        print("❌ Customer login failed!")
        return
    
    # Extract token and customer ID
    login_data = login_response.json()
    token = login_data.get('token')
    customer_id = login_data.get('customer_id')  # Changed from customer.id to customer_id
    
    if not token or not customer_id:
        print("❌ Failed to extract token or customer ID!")
        return
    
    print(f"✅ Token: {token[:20]}...")
    print(f"✅ Customer ID: {customer_id}")
    
    # Step 3: Create new machine
    print_step(3, "Creating New Machine")
    
    machine_data = {
        "name": "Test Machine 1",
        "description": "Test machine for automated testing",
        "location": "Test Lab",
        "mac_address": f"AA:BB:CC:DD:EE:{int(time.time()) % 100:02X}"
    }
    
    machine_response = requests.post(
        f"{BASE_URL}/api/machines/customer/{customer_id}",
        json=machine_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print_response(machine_response, "Machine Creation")
    
    if machine_response.status_code not in [200, 201]:
        print("❌ Machine creation failed!")
        print(f"Error details: {machine_response.text}")
        return
    
    machine_data = machine_response.json()
    machine_id = machine_data.get('machine_id')  # Changed from id to machine_id
    
    if not machine_id:
        print("❌ Failed to extract machine ID!")
        return
    
    print(f"✅ Machine ID: {machine_id}")
    
    # Step 4: Upload file to machine
    print_step(4, "Uploading File to Machine")
    
    # Create test file
    test_filename = create_test_file()
    
    upload_data = {
        'file': (test_filename, open(test_filename, 'rb'), 'text/plain'),
        'filename': test_filename,
        'version': '1.0'
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}/upload",
        files=upload_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print_response(upload_response, "File Upload")
    
    if upload_response.status_code not in [200, 201]:
        print("❌ File upload failed!")
        return
    
    # Clean up test file
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    # Step 5: Verify the flow by listing files
    print_step(5, "Verifying Upload - Listing Files")
    
    list_response = requests.get(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print_response(list_response, "File Listing")
    
    if list_response.status_code == 200:
        response_data = list_response.json()
        files = response_data.get('files', [])
        print(f"✅ Found {len(files)} files for the machine")
        for file in files:
            print(f"   - {file.get('filename', 'Unknown')} (v{file.get('version', 'Unknown')})")
    
    print(f"\n{'='*60}")
    print("🎉 AUTOMATED TEST FLOW COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"✅ Customer: {TEST_EMAIL}")
    print(f"✅ Machine: {machine_id}")
    print(f"✅ File uploaded successfully")
    print(f"\nYou can now test the frontend with these credentials!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 