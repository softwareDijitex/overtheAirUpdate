import os
import re
import mimetypes
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Literal
from azure.core.exceptions import ResourceNotFoundError

from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError
from app.models.machine import Machine
from app.models.customer import Customer
from app.models.file import File

hardware_bp = APIRouter()

Env = Literal["dev", "production"]
_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$", re.IGNORECASE)
_RANGE_VALUE_RE = re.compile(r"(\d*)-(\d*)$")


def guess_media_type(name: str) -> str:
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def parse_range_header(range_value: str, file_size: int) -> Tuple[int, int]:
    m = _RANGE_RE.match(range_value.strip())
    if not m:
        raise HTTPException(status_code=400, detail="Invalid Range header")
    start_s, end_s = m.groups()
    if start_s and end_s:
        start, end = int(start_s), int(end_s)
    elif start_s:  # bytes=START-
        start, end = int(start_s), file_size - 1
    elif end_s:   # bytes=-SUFFIX
        n = int(end_s)
        if n <= 0:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        start, end = max(file_size - n, 0), file_size - 1
    else:
        raise HTTPException(status_code=400, detail="Invalid Range header")
    if start > end or start >= file_size:
        raise HTTPException(status_code=416, detail="Requested range not satisfiable")
    return start, min(end, file_size - 1)


def parse_range_part(range_part: str, file_size: int) -> Tuple[int, int]:
    m = _RANGE_VALUE_RE.match(range_part.strip())
    if not m:
        raise HTTPException(status_code=400, detail="Invalid Range header")
    start_s, end_s = m.groups()
    if start_s and end_s:
        start, end = int(start_s), int(end_s)
    elif start_s:
        start, end = int(start_s), file_size - 1
    elif end_s:
        n = int(end_s)
        if n <= 0:
            raise HTTPException(status_code=400, detail="Invalid Range header")
        start, end = max(file_size - n, 0), file_size - 1
    else:
        raise HTTPException(status_code=400, detail="Invalid Range header")
    if start > end or start >= file_size:
        raise HTTPException(status_code=416, detail="Requested range not satisfiable")
    return start, min(end, file_size - 1)


def parse_range_header_parts(range_header: str, file_size: int) -> List[Tuple[int, int]]:
    if not range_header.lower().startswith("bytes="):
        raise HTTPException(status_code=400, detail="Invalid Range header")

    ranges = [
        parse_range_part(part, file_size)
        for part in range_header.split("=", 1)[1].split(",")
        if part.strip()
    ]
    if not ranges:
        raise HTTPException(status_code=400, detail="Invalid Range header")
    return ranges


def get_container_client():
    conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn:
        raise HTTPException(500, "AZURE_STORAGE_CONNECTION_STRING not set")
    container_name = os.getenv("BLOB_CONTAINER_NAME", "machine-files")
    svc = BlobServiceClient.from_connection_string(conn)
    container = svc.get_container_client(container_name)
    try:
        container.create_container()  # no-op if it exists
    except ResourceExistsError:
        pass
    return container


def make_blob_name(customer_id: str, machine_id: str, env: str, filename: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = filename or f"{machine_id}-{env}.bin"
    # Folder-like prefixing for easy listing by tuple
    return f"{customer_id}/{machine_id}/{env}/{ts}-{safe_name}"


def prefix_for(customer_id: str, machine_id: str, env: str) -> str:
    return f"{customer_id}/{machine_id}/{env}/"

@hardware_bp.post("/files/latest")
async def download_latest_file(
    request: Request,
    mac_address: str = Form(...),
):
    if not Machine.is_valid_mac_address(mac_address):
        raise HTTPException(
            status_code=400,
            detail="Invalid MAC address format"
        )

    customer = Customer.find_by_mac_address(mac_address)

    if not customer or not customer.get("machines"):
        raise HTTPException(
            status_code=404,
            detail="Machine not found for MAC address"
        )

    machine = customer["machines"][0]

    latest = File.get_latest_file_metadata(
            customer["customer_id"],
            machine["id"]
    )

    if not latest:
            print("No latest file metadata found")
            raise HTTPException(
                status_code=404,
                detail="No file found for this MAC address"
            )

    blob_name = latest["blob_name"]

    if not blob_name:
        raise HTTPException(
            status_code=500,
            detail="Blob name missing from metadata"
        )

    container = get_container_client()

    bc = container.get_blob_client(blob_name)
    try:
        props = bc.get_blob_properties()
    except ResourceNotFoundError as e:
        print(f"Blob not found: {blob_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Blob not found: {blob_name}"
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch blob properties"
        )

    total = int(props.size)
    filename = latest.get("filename") or blob_name.rsplit("/", 1)[-1]
    media_type = props.content_settings.content_type or guess_media_type(filename)

    range_header = request.headers.get("range") or request.headers.get("Range")
    if not range_header:
        # Full download
        downloader = bc.download_blob()
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(total),
            "ETag": props.etag,
            "Last-Modified": props.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        }

        def stream():
            for chunk in downloader.chunks():
                yield chunk

        return StreamingResponse(stream(), media_type=media_type, headers=headers)

    ranges = parse_range_header_parts(range_header, total)
    if len(ranges) > 1:
        boundary = f"hardware-download-{uuid.uuid4().hex}"
        headers = {
            "Accept-Ranges": "bytes",
            "ETag": props.etag,
            "Last-Modified": props.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        }

        def stream_multipart_ranges():
            for start, end in ranges:
                length = end - start + 1
                part_header = (
                    f"--{boundary}\r\n"
                    f"Content-Type: {media_type}\r\n"
                    f"Content-Range: bytes {start}-{end}/{total}\r\n"
                    "\r\n"
                )
                yield part_header.encode("ascii")
                downloader = bc.download_blob(offset=start, length=length)
                for chunk in downloader.chunks():
                    yield chunk
                yield b"\r\n"
            yield f"--{boundary}--\r\n".encode("ascii")

        return StreamingResponse(
            stream_multipart_ranges(),
            status_code=206,
            media_type=f"multipart/byteranges; boundary={boundary}",
            headers=headers,
        )

    start, end = ranges[0]

    length = end - start + 1

    downloader = bc.download_blob(offset=start, length=length)
    headers = {
        "Content-Range": f"bytes {start}-{end}/{total}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Disposition": f'attachment; filename="{filename}"',
        "ETag": props.etag,
        "Last-Modified": props.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    }

    def stream_range():
        for chunk in downloader.chunks():
            yield chunk

    return StreamingResponse(stream_range(), status_code=206, media_type=media_type, headers=headers)
