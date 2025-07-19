#!/usr/bin/env python3
"""
Simple test to isolate machine creation issue
"""

import requests
import json

# Test data
BASE_URL = "http://localhost:8000"
CUSTOMER_ID = "888c53bc-6695-4dc4-904e-01d2c777be64"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6Ijg4OGM1M2JjLTY2OTUtNGRjNC05MDRlLTAxZDJjNzc3YmU2NCIsImVtYWlsIjoidGVzdHVzZXJfMTc1MDUzNjI1MEBleGFtcGxlLmNvbSIsImlzX2FkbWluIjpmYWxzZSwiZXhwIjoxNzUwNjIyNjU2LCJpYXQiOjE3NTA1MzYyNTZ9.S3GP2h4xRAHRZDd91lLfDskrGsZznpi9lEb_A_OnDhY"

def test_machine_creation():
    print("Testing machine creation...")

    # Test data
    machine_data = {
        "name": "Simple Test Machine",
        "description": "Simple test",
        "location": "Test Lab",
        "mac_address": "AA:BB:CC:DD:EE:99"
    }

    # Make request
    response = requests.post(
        f"{BASE_URL}/api/machines/customer/{CUSTOMER_ID}",
        json=machine_data,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200 or response.status_code == 201:
        print("✅ Machine creation successful!")
    else:
        print("❌ Machine creation failed!")

if __name__ == "__main__":
    test_machine_creation() 