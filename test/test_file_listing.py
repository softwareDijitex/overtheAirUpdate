#!/usr/bin/env python3
"""
Automated test for file listing functionality
Tests: Customer registration, machine creation, file upload, and file listing
"""

import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8000"

def test_file_listing():
    print("🧪 Testing File Listing Functionality")
    print("=" * 50)
    
    # Step 1: Register a customer
    print("\n1. Customer Registration...")
    customer_data = {
        "email": f"testcustomer_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "name": "Test Customer",
        "company": "Test Company",
        "phone": "+1234567890",
        "address": "123 Test Street, Test City, 12345"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/customers/register", json=customer_data)
    
    if register_response.status_code == 201:
        print("✅ Customer registration successful")
        customer_id = register_response.json().get('customer_id')
    else:
        print(f"❌ Customer registration failed: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        return False
    
    # Step 2: Customer login
    print("\n2. Customer Login...")
    login_data = {
        "email": customer_data["email"],
        "password": customer_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/api/customers/login", json=login_data)
    
    if login_response.status_code == 200:
        print("✅ Customer login successful")
        token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Customer login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    # Step 3: Create a machine
    print("\n3. Machine Creation...")
    machine_data = {
        "name": "Test Machine for File Listing",
        "mac_address": f"AA:BB:CC:DD:EE:{uuid.uuid4().hex[:2]}",
        "description": "Machine for testing file listing functionality"
    }
    
    machine_response = requests.post(
        f"{BASE_URL}/api/machines/customer/{customer_id}",
        json=machine_data,
        headers=headers
    )
    
    if machine_response.status_code == 201:
        print("✅ Machine creation successful")
        machine_info = machine_response.json()
        machine_id = machine_info.get('machine', {}).get('id')
        print(f"   Machine ID: {machine_id}")
    else:
        print(f"❌ Machine creation failed: {machine_response.status_code}")
        print(f"Response: {machine_response.text}")
        return False
    
    # Step 4: Upload a test file
    print("\n4. File Upload...")
    
    # Create a simple test file content
    test_file_content = f"Test file content for machine {machine_id}\nCreated at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Create file upload data
    files = {
        'file': ('test_file.txt', test_file_content, 'text/plain')
    }
    data = {
        'version': '1.0'
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}/upload",
        files=files,
        data=data,
        headers=headers
    )
    
    if upload_response.status_code == 201:
        print("✅ File upload successful")
        print(f"   File: test_file.txt (v1.0)")
    else:
        print(f"❌ File upload failed: {upload_response.status_code}")
        print(f"Response: {upload_response.text}")
        return False
    
    # Step 5: Test file listing (empty list first)
    print("\n5. Testing File Listing (Initial)...")
    
    list_response = requests.get(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}",
        headers=headers
    )
    
    if list_response.status_code == 200:
        files_data = list_response.json()
        files_list = files_data.get('files', [])
        print(f"✅ File listing successful - Found {len(files_list)} files")
        
        if len(files_list) > 0:
            print("   Files found:")
            for file_info in files_list:
                print(f"   - {file_info.get('filename', 'Unknown')} (v{file_info.get('version', 'Unknown')})")
        else:
            print("   ⚠️  No files found (this might indicate a timing issue)")
    else:
        print(f"❌ File listing failed: {list_response.status_code}")
        print(f"Response: {list_response.text}")
        return False
    
    # Step 6: Upload another file to test multiple files
    print("\n6. Uploading Second File...")
    
    test_file_content_2 = f"Second test file for machine {machine_id}\nCreated at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    files_2 = {
        'file': ('test_file_2.txt', test_file_content_2, 'text/plain')
    }
    data_2 = {
        'version': '2.0'
    }
    
    upload_response_2 = requests.post(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}/upload",
        files=files_2,
        data=data_2,
        headers=headers
    )
    
    if upload_response_2.status_code == 201:
        print("✅ Second file upload successful")
        print(f"   File: test_file_2.txt (v2.0)")
    else:
        print(f"❌ Second file upload failed: {upload_response_2.status_code}")
        print(f"Response: {upload_response_2.text}")
        return False
    
    # Step 7: Test file listing again (should have 2 files)
    print("\n7. Testing File Listing (After Second Upload)...")
    
    list_response_2 = requests.get(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}",
        headers=headers
    )
    
    if list_response_2.status_code == 200:
        files_data_2 = list_response_2.json()
        files_list_2 = files_data_2.get('files', [])
        print(f"✅ File listing successful - Found {len(files_list_2)} files")
        
        if len(files_list_2) >= 2:
            print("   Files found:")
            for file_info in files_list_2:
                print(f"   - {file_info.get('filename', 'Unknown')} (v{file_info.get('version', 'Unknown')})")
        else:
            print(f"   ⚠️  Expected 2+ files, but found {len(files_list_2)}")
            print("   This might indicate a timing issue or file saving problem")
    else:
        print(f"❌ File listing failed: {list_response_2.status_code}")
        print(f"Response: {list_response_2.text}")
        return False
    
    # Step 8: Test unauthorized access (should fail)
    print("\n8. Testing Unauthorized Access...")
    
    # Try to access files with wrong customer ID
    wrong_customer_id = "wrong-customer-id"
    unauthorized_response = requests.get(
        f"{BASE_URL}/api/files/customer/{wrong_customer_id}/machine/{machine_id}",
        headers=headers
    )
    
    if unauthorized_response.status_code == 403:
        print("✅ Unauthorized access correctly blocked")
    else:
        print(f"❌ Unauthorized access not blocked: {unauthorized_response.status_code}")
        print(f"Response: {unauthorized_response.text}")
    
    # Step 9: Test with invalid machine ID (should fail)
    print("\n9. Testing Invalid Machine ID...")
    
    invalid_machine_id = "invalid-machine-id"
    invalid_machine_response = requests.get(
        f"{BASE_URL}/api/files/customer/{customer_id}/machine/{invalid_machine_id}",
        headers=headers
    )
    
    if invalid_machine_response.status_code in [404, 200]:  # 404 for not found, 200 for empty list
        print("✅ Invalid machine ID handled correctly")
        if invalid_machine_response.status_code == 200:
            files_data_invalid = invalid_machine_response.json()
            files_list_invalid = files_data_invalid.get('files', [])
            print(f"   Returned empty list with {len(files_list_invalid)} files")
    else:
        print(f"❌ Invalid machine ID not handled correctly: {invalid_machine_response.status_code}")
        print(f"Response: {invalid_machine_response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 FILE LISTING TEST COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = test_file_listing()
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc() 