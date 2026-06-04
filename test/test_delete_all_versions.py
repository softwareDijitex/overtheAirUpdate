#!/usr/bin/env python3
"""
Tests for the delete-all-versions feature (feature/delete-entire-file).

Covers:
  1. Customer can delete all versions of their own file
  2. Customer cannot delete another customer's file (403)
  3. Deleting a filename that doesn't exist returns an error
  4. Admin can delete any customer's file
  5. Unauthenticated request is rejected

Run with: python test/test_delete_all_versions.py
Backend must be running at http://localhost:8000
"""

import requests
import time
import os

BASE_URL = "http://localhost:8000"

# Unique emails per run so tests don't collide with previous runs
_ts = int(time.time())
_machine_counter = 0
CUSTOMER_A_EMAIL = f"delete_test_a_{_ts}@example.com"
CUSTOMER_B_EMAIL = f"delete_test_b_{_ts}@example.com"
PASSWORD = "password123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_and_login(email):
    """Register a new customer and return their token + customer_id."""
    requests.post(f"{BASE_URL}/api/customers/register", json={
        "email": email, "password": PASSWORD,
        "name": "Test User", "phone": "0000000000", "address": "Test St"
    })
    resp = requests.post(f"{BASE_URL}/api/customers/login",
                         json={"email": email, "password": PASSWORD})
    data = resp.json()
    return data["token"], data["customer_id"]


def _admin_token():
    resp = requests.post(f"{BASE_URL}/api/customers/admin/login",
                         json={"email": "admin@example.com", "password": "admin123"})
    return resp.json()["token"]


def _create_machine(token, customer_id):
    global _machine_counter
    _machine_counter += 1
    resp = requests.post(
        f"{BASE_URL}/api/machines/customer/{customer_id}",
        json={
            "name": "Test Machine",
            "mac_address": f"AA:BB:CC:{_ts % 99:02X}:{_machine_counter:02X}:FF",
            "description": "test",
            "customer_id": customer_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json()["id"]


def _upload_file(token, customer_id, machine_id, filename, version):
    """Upload a small text file."""
    tmp = f"/tmp/{filename}"
    with open(tmp, "w") as f:
        f.write(f"test content v{version}")
    with open(tmp, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/api/files/customer/{customer_id}/machine/{machine_id}/upload",
            files={"file": (filename, f, "text/plain")},
            data={"version": version},
            headers={"Authorization": f"Bearer {token}"}
        )
    os.remove(tmp)
    return resp


def _versions_of(token, customer_id, machine_id, filename):
    """Return all stored versions of a filename using the dedicated versions endpoint."""
    resp = requests.get(
        f"{BASE_URL}/api/files/versions/{customer_id}/{machine_id}/{filename}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json().get("versions", [])


def ok(msg):   print(f"  PASS  {msg}")
def fail(msg): print(f"  FAIL  {msg}")


# ---------------------------------------------------------------------------
# Setup — runs once, creates throwaway data for all tests
# ---------------------------------------------------------------------------

print("\nSetting up test data...")
token_a, cid_a = _register_and_login(CUSTOMER_A_EMAIL)
token_b, cid_b = _register_and_login(CUSTOMER_B_EMAIL)
admin_tok       = _admin_token()
mid_a           = _create_machine(token_a, cid_a)

# Upload two versions of the same filename so we can confirm both get deleted
_upload_file(token_a, cid_a, mid_a, "firmware.bin", "1.0")
_upload_file(token_a, cid_a, mid_a, "firmware.bin", "1.1")
print("  Setup complete\n")


# ---------------------------------------------------------------------------
# Test 1 — customer deletes all versions of their own file (happy path)
# ---------------------------------------------------------------------------
print("Test 1: Customer deletes all versions of their own file")

before = _versions_of(token_a, cid_a, mid_a, "firmware.bin")
if len(before) < 2:
    fail(f"Expected 2 versions before delete, got {len(before)} — check upload step")
else:
    resp = requests.delete(
        f"{BASE_URL}/api/files/delete/{cid_a}/{mid_a}/firmware.bin",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    after = _versions_of(token_a, cid_a, mid_a, "firmware.bin")
    if resp.status_code == 200 and len(after) == 0:
        ok(f"Deleted {len(before)} versions, 0 remain (status {resp.status_code})")
    else:
        fail(f"status={resp.status_code}, versions remaining={len(after)}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 2 — customer cannot delete another customer's file (expects 403)
# ---------------------------------------------------------------------------
print("\nTest 2: Customer cannot delete another customer's file")

# Give customer A a fresh machine + file for this test
mid_a2 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid_a2, "other.bin", "1.0")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid_a2}/other.bin",
    headers={"Authorization": f"Bearer {token_b}"}  # Customer B's token — should be blocked
)
if resp.status_code == 403:
    ok(f"Got 403 as expected")
else:
    fail(f"Expected 403, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 3 — deleting a filename that does not exist returns an error
# ---------------------------------------------------------------------------
print("\nTest 3: Deleting a non-existent filename returns an error")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid_a}/does_not_exist.bin",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code >= 400:
    ok(f"Got error status {resp.status_code} as expected")
else:
    fail(f"Expected an error status, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 4 — admin can delete any customer's file
# ---------------------------------------------------------------------------
print("\nTest 4: Admin can delete any customer's file")

mid_admin_test = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid_admin_test, "admin_target.bin", "1.0")

resp = requests.delete(
    f"{BASE_URL}/api/files/admin/delete/{cid_a}/{mid_admin_test}/admin_target.bin",
    headers={"Authorization": f"Bearer {admin_tok}"}
)
after = _versions_of(token_a, cid_a, mid_admin_test, "admin_target.bin")
if resp.status_code == 200 and len(after) == 0:
    ok(f"Admin deleted file successfully (status {resp.status_code})")
else:
    fail(f"status={resp.status_code}, versions remaining={len(after)}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 5 — unauthenticated request is rejected
# ---------------------------------------------------------------------------
print("\nTest 5: Unauthenticated request is rejected")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid_a}/firmware.bin"
    # no Authorization header
)
if resp.status_code in (401, 403):
    ok(f"Got {resp.status_code} as expected")
else:
    fail(f"Expected 401 or 403, got {resp.status_code}: {resp.text}")


print("\nDone.")
