# scripts/azure_sanity.py
import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from dotenv import load_dotenv
# load values from config.env
load_dotenv("../config.env")

CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")  # same env your app uses
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER_NAME")  # same container as app

assert CONN, "Missing AZURE_STORAGE_CONNECTION_STRING"
assert CONTAINER, "Missing AZURE_STORAGE_CONTAINER_NAME"

print(f"[AZURE TEST] container={CONTAINER}")

svc = BlobServiceClient.from_connection_string(CONN)
cc = svc.get_container_client(CONTAINER)

# Ensure container exists
try:
    cc.create_container()
    print("[AZURE TEST] container created")
except ResourceExistsError:
    print("[AZURE TEST] container already exists")

# Try uploading ~6 MB
name = "sanity/test_6mb.bin"
data = os.urandom(6 * 1024 * 1024)
bc = cc.get_blob_client(name)
bc.upload_blob(data, overwrite=True, timeout=60)
print("[AZURE TEST] upload OK:", name)

