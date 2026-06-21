#!/usr/bin/env python3
"""
Tests for single-version file delete and file download.

Covers:
  Single version delete:
    1. Customer deletes one version — other versions remain
    2. Deleting a version that doesn't exist returns an error
    3. Customer cannot delete another customer's file version (403)
    4. Admin can delete any version
    5. Unauthenticated request is rejected

  File download:
    6. Customer can download their own file
    7. Downloaded content matches what was uploaded
    8. Customer cannot download another customer's file (403)
    9. Downloading a non-existent version returns 404
   10. Unauthenticated request is rejected

Run with: python test/test_file_operations.py
Backend must be running at http://localhost:8000
"""

import requests
import time
import os

BASE_URL = "http://localhost:8000"

_ts = int(time.time())
_machine_counter = 0
CUSTOMER_A_EMAIL = f"file_ops_a_{_ts}@example.com"
CUSTOMER_B_EMAIL = f"file_ops_b_{_ts}@example.com"
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
            "mac_address": f"BB:CC:DD:{_ts % 99:02X}:{_machine_counter:02X}:FF",
            "description": "test",
            "customer_id": customer_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json()["id"]


def _upload_file(token, customer_id, machine_id, filename, version, content=None):
    tmp = f"/tmp/{filename}"
    file_content = content or f"test content v{version}"
    with open(tmp, "w") as f:
        f.write(file_content)
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
    resp = requests.get(
        f"{BASE_URL}/api/files/versions/{customer_id}/{machine_id}/{filename}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return resp.json().get("versions", [])


def ok(msg):   print(f"  PASS  {msg}")
def fail(msg): print(f"  FAIL  {msg}")


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

print("\nSetting up test data...")
token_a, cid_a = _register_and_login(CUSTOMER_A_EMAIL)
token_b, cid_b = _register_and_login(CUSTOMER_B_EMAIL)
admin_tok       = _admin_token()
print("  Setup complete\n")


# ===========================================================================
# Single version delete
# ===========================================================================

# ---------------------------------------------------------------------------
# Test 1 — delete one version, other version remains
# ---------------------------------------------------------------------------
print("Test 1: Deleting one version leaves the other intact")

mid1 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid1, "app.bin", "1.0")
_upload_file(token_a, cid_a, mid1, "app.bin", "1.1")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid1}/app.bin/1.0",
    headers={"Authorization": f"Bearer {token_a}"}
)
remaining = _versions_of(token_a, cid_a, mid1, "app.bin")
if resp.status_code == 200 and len(remaining) == 1 and remaining[0]["version"] == "1.1":
    ok("v1.0 deleted, v1.1 still present")
else:
    fail(f"status={resp.status_code}, remaining={remaining}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 2 — deleting a version that doesn't exist returns an error
# ---------------------------------------------------------------------------
print("\nTest 2: Deleting a non-existent version returns an error")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid1}/app.bin/9.9",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code >= 400:
    ok(f"Got error status {resp.status_code} as expected")
else:
    fail(f"Expected an error, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 3 — customer cannot delete another customer's file version (403)
# ---------------------------------------------------------------------------
print("\nTest 3: Customer cannot delete another customer's file version")

mid3 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid3, "secure.bin", "1.0")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid3}/secure.bin/1.0",
    headers={"Authorization": f"Bearer {token_b}"}
)
if resp.status_code == 403:
    ok("Got 403 as expected")
else:
    fail(f"Expected 403, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 4 — admin can delete any version
# ---------------------------------------------------------------------------
print("\nTest 4: Admin can delete any customer's file version")

mid4 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid4, "admin_target.bin", "1.0")

resp = requests.delete(
    f"{BASE_URL}/api/files/admin/delete/{cid_a}/{mid4}/admin_target.bin/1.0",
    headers={"Authorization": f"Bearer {admin_tok}"}
)
remaining = _versions_of(token_a, cid_a, mid4, "admin_target.bin")
if resp.status_code == 200 and len(remaining) == 0:
    ok("Admin deleted version successfully")
else:
    fail(f"status={resp.status_code}, remaining={remaining}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 5 — unauthenticated delete is rejected
# ---------------------------------------------------------------------------
print("\nTest 5: Unauthenticated delete is rejected")

mid5 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid5, "noauth.bin", "1.0")

resp = requests.delete(
    f"{BASE_URL}/api/files/delete/{cid_a}/{mid5}/noauth.bin/1.0"
)
if resp.status_code in (401, 403):
    ok(f"Got {resp.status_code} as expected")
else:
    fail(f"Expected 401/403, got {resp.status_code}: {resp.text}")


# ===========================================================================
# File download
# ===========================================================================

# ---------------------------------------------------------------------------
# Test 6 — customer can download their own file
# ---------------------------------------------------------------------------
print("\nTest 6: Customer can download their own file")

mid6 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid6, "download_me.bin", "1.0")

resp = requests.get(
    f"{BASE_URL}/api/files/download/{cid_a}/{mid6}/download_me.bin/1.0",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 200:
    ok("Download returned 200")
else:
    fail(f"status={resp.status_code}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 7 — downloaded content matches what was uploaded
# ---------------------------------------------------------------------------
print("\nTest 7: Downloaded content matches uploaded content")

expected_content = "hello from test 7"
mid7 = _create_machine(token_a, cid_a)
_upload_file(token_a, cid_a, mid7, "check_content.txt", "1.0", content=expected_content)

resp = requests.get(
    f"{BASE_URL}/api/files/download/{cid_a}/{mid7}/check_content.txt/1.0",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 200 and resp.content.decode() == expected_content:
    ok("Content matches exactly")
elif resp.status_code == 200:
    fail(f"Status 200 but content mismatch. Got: {resp.content[:100]}")
else:
    fail(f"status={resp.status_code}, body={resp.text}")


# ---------------------------------------------------------------------------
# Test 8 — customer cannot download another customer's file (403)
# ---------------------------------------------------------------------------
print("\nTest 8: Customer cannot download another customer's file")

resp = requests.get(
    f"{BASE_URL}/api/files/download/{cid_a}/{mid6}/download_me.bin/1.0",
    headers={"Authorization": f"Bearer {token_b}"}
)
if resp.status_code == 403:
    ok("Got 403 as expected")
else:
    fail(f"Expected 403, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 9 — downloading a non-existent version returns 404
# ---------------------------------------------------------------------------
print("\nTest 9: Downloading a non-existent version returns 404")

resp = requests.get(
    f"{BASE_URL}/api/files/download/{cid_a}/{mid6}/download_me.bin/9.9",
    headers={"Authorization": f"Bearer {token_a}"}
)
if resp.status_code == 404:
    ok("Got 404 as expected")
else:
    fail(f"Expected 404, got {resp.status_code}: {resp.text}")


# ---------------------------------------------------------------------------
# Test 10 — unauthenticated download is rejected
# ---------------------------------------------------------------------------
print("\nTest 10: Unauthenticated download is rejected")

resp = requests.get(
    f"{BASE_URL}/api/files/download/{cid_a}/{mid6}/download_me.bin/1.0"
)
if resp.status_code in (401, 403):
    ok(f"Got {resp.status_code} as expected")
else:
    fail(f"Expected 401/403, got {resp.status_code}: {resp.text}")


print("\nDone.")
