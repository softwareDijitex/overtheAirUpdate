#!/usr/bin/env python3
"""
Tests for machine update and delete operations.

Covers:
  1. Customer can update their own machine name/description
  2. Duplicate MAC address on update returns 400 with a 'detail' field
  3. Customer can delete their own machine
  4. Deleted machine is no longer fetchable (404)
  5. Customer cannot update another customer's machine (403)
  6. Customer cannot delete another customer's machine (403)
  7. Unauthenticated requests are rejected

Run with: python test/test_machine_crud.py
Backend must be running at http://localhost:8000
"""

import requests
import time

BASE_URL = "http://localhost:8000"

_ts = int(time.time())
_machine_counter = 0
CUSTOMER_A_EMAIL = f"machine_crud_a_{_ts}@example.com"
CUSTOMER_B_EMAIL = f"machine_crud_b_{_ts}@example.com"
PASSWORD = "password123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_and_login(email):
    requests.post(f"{BASE_URL}/api/customers/register", json={
        "email": email, "password": PASSWORD,
        "name": "Test User", "phone": "0000000000", "address": "Test St"
    })
    resp = requests.post(f"{BASE_URL}/api/customers/login",
                         json={"email": email, "password": PASSWORD})
    data = resp.json()
    return data["token"], data["customer_id"]


def _create_machine(token, customer_id, name="Test Machine"):
    global _machine_counter
    _machine_counter += 1
    resp = requests.post(
        f"{BASE_URL}/api/machines/customer/{customer_id}",
        json={
            "name": name,
            "mac_address": f"AA:BB:CC:{_ts % 99:02X}:{_machine_counter:02X}:FF",
            "description": "test",
            "customer_id": customer_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json()["id"], resp.json().get("mac_address")


def _fetch_machine(token, customer_id, machine_id):
    return requests.get(
        f"{BASE_URL}/api/machines/customer/{customer_id}/{machine_id}",
        headers={"Authorization": f"Bearer {token}"}
    )


def ok(msg):   print(f"  PASS  {msg}")
def fail(msg): print(f"  FAIL  {msg}")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

print("\nSetting up test data...")
token_a, cid_a = _register_and_login(CUSTOMER_A_EMAIL)
token_b, cid_b = _register_and_login(CUSTOMER_B_EMAIL)
print("  Setup complete\n")


# ---------------------------------------------------------------------------
# Test 1 — customer updates their own machine
# ---------------------------------------------------------------------------
print("Test 1: Customer can update their own machine")

mid, _ = _create_machine(token_a, cid_a, name="Original Name")
resp = requests.put(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid}",
    json={"name": "Updated Name"},
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 200 and resp.json().get("name") == "Updated Name":
    ok("Name updated successfully")
else:
    fail(f"status={resp.status_code}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 2 — duplicate MAC address returns 400 with 'detail' field
# (verifies the fix from feature/fix-admin-create-machine)
# ---------------------------------------------------------------------------
print("\nTest 2: Duplicate MAC address on update returns 400 with 'detail' field")

mid1, mac1 = _create_machine(token_a, cid_a, name="Machine 1")
mid2, _    = _create_machine(token_a, cid_a, name="Machine 2")

resp = requests.put(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid2}",
    json={"mac_address": mac1},
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 400 and "detail" in resp.json():
    ok(f"Got 400 with 'detail' field: {resp.json()['detail']}")
else:
    fail(f"status={resp.status_code}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 3 — customer deletes their own machine
# ---------------------------------------------------------------------------
print("\nTest 3: Customer can delete their own machine")

mid_to_delete, _ = _create_machine(token_a, cid_a, name="To Be Deleted")
resp = requests.delete(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid_to_delete}",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 200:
    ok("Delete returned 200")
else:
    fail(f"status={resp.status_code}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 4 — deleted machine is no longer fetchable
# ---------------------------------------------------------------------------
print("\nTest 4: Deleted machine returns 404 when fetched")

fetch_resp = _fetch_machine(token_a, cid_a, mid_to_delete)
if fetch_resp.status_code == 404:
    ok("Got 404 as expected")
else:
    fail(f"Expected 404, got {fetch_resp.status_code}: {fetch_resp.text}")


# ---------------------------------------------------------------------------
# Test 5 — customer cannot update another customer's machine (403)
# ---------------------------------------------------------------------------
print("\nTest 5: Customer cannot update another customer's machine")

mid_a, _ = _create_machine(token_a, cid_a)
resp = requests.put(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid_a}",
    json={"name": "Hacked Name"},
    headers={"Authorization": f"Bearer {token_b}"}
)
if resp.status_code == 403:
    ok("Got 403 as expected")
else:
    fail(f"Expected 403, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 6 — customer cannot delete another customer's machine (403)
# ---------------------------------------------------------------------------
print("\nTest 6: Customer cannot delete another customer's machine")

resp = requests.delete(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid_a}",
    headers={"Authorization": f"Bearer {token_b}"}
)
if resp.status_code == 403:
    ok("Got 403 as expected")
else:
    fail(f"Expected 403, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 7 — unauthenticated requests are rejected
# ---------------------------------------------------------------------------
print("\nTest 7: Unauthenticated requests are rejected")

mid_unauth, _ = _create_machine(token_a, cid_a)
update_resp = requests.put(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid_unauth}",
    json={"name": "No Auth"}
)
delete_resp = requests.delete(
    f"{BASE_URL}/api/machines/customer/{cid_a}/{mid_unauth}"
)
if update_resp.status_code in (401, 403) and delete_resp.status_code in (401, 403):
    ok(f"Update={update_resp.status_code}, Delete={delete_resp.status_code}")
else:
    fail(f"Update={update_resp.status_code}, Delete={delete_resp.status_code}")


print("\nDone.")
