# # app/routes/machineHardware_routes.py
# import os
# import re
# import mimetypes
# from typing import Tuple, Literal

# from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
# from fastapi.responses import StreamingResponse
# import gridfs

# from app import get_database
# from app.models.machine import Machine   # to validate machine existence

# # Create the APIRouter (FastAPI equivalent of Flask Blueprint)
# hardware_bp = APIRouter()

# Env = Literal["dev", "production"]

# # ---------- helpers ----------
# _RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$", re.IGNORECASE)

# def parse_range_header(range_value: str, file_size: int) -> Tuple[int, int]:
#     m = _RANGE_RE.match(range_value.strip())
#     if not m:
#         raise HTTPException(status_code=400, detail="Invalid Range header")
#     start_s, end_s = m.groups()
#     if start_s and end_s:
#         start, end = int(start_s), int(end_s)
#     elif start_s:                            # bytes=START-
#         start, end = int(start_s), file_size - 1
#     elif end_s:                              # bytes=-SUFFIX
#         n = int(end_s)
#         if n <= 0:
#             raise HTTPException(status_code=400, detail="Invalid Range header")
#         start, end = max(file_size - n, 0), file_size - 1
#     else:
#         raise HTTPException(status_code=400, detail="Invalid Range header")
#     if start > end or start >= file_size:
#         raise HTTPException(status_code=416, detail="Requested range not satisfiable")
#     return start, min(end, file_size - 1)

# def guess_media_type(name: str) -> str:
#     return mimetypes.guess_type(name)[0] or "application/octet-stream"

# def gridfs_bucket():
#     db = get_database()
#     return gridfs.GridFS(db, collection="machine_files"), db["machine_files.files"]

# # ---------- 1) UPLOAD: add new file to a machine ----------
# @hardware_bp.post("/files/upload")
# async def upload_machine_file(
#     customer_id: str = Form(...),
#     machine_id: str = Form(...),
#     env: Env = Form(...),                      # dev or production
#     file: UploadFile = File(...),              # the binary
# ):
#     # Ensure the machine exists under that customer
#     # m = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
#     # if not m:
#     #     raise HTTPException(status_code=404, detail="Machine not found for customer")

#     fs, files_coll = gridfs_bucket()

#     # Store in GridFS with metadata so we can query the "latest" later
#     try:
#         _id = fs.put(
#             file.file,
#             filename=file.filename or f"{machine_id}-{env}.bin",
#             content_type=file.content_type or guess_media_type(file.filename or ""),
#             metadata={
#                 "customer_id": customer_id,
#                 "machine_id": machine_id,
#                 "env": env,
#             },
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

#     # Fetch the files doc for response
#     doc = files_coll.find_one({"_id": _id})
#     return {
#         "id": str(_id),
#         "filename": doc.get("filename"),
#         "length": int(doc.get("length", 0)),
#         "content_type": doc.get("contentType"),
#         "uploadDate": doc.get("uploadDate"),
#         "metadata": doc.get("metadata", {}),
#         "message": "File uploaded successfully",
#     }

# # ---------- 2) DOWNLOAD: fetch latest file for (cid, mid, env) ----------
# @hardware_bp.post("/files/latest")
# async def download_latest_file(
#     request: Request,
#     customer_id: str = Form(...),
#     machine_id: str = Form(...),
#     env: Env = Form(...),
# ):
#     fs, files_coll = gridfs_bucket()

#     # newest by uploadDate
#     latest = files_coll.find_one(
#         {
#             "metadata.customer_id": customer_id,
#             "metadata.machine_id": machine_id,
#             "metadata.env": env,
#         },
#         sort=[("uploadDate", -1)],
#     )
#     if not latest:
#         raise HTTPException(status_code=404, detail="No file found for this machine/env")

#     try:
#         grid_out = fs.get(latest["_id"])  # file-like: read(), seek()
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to open file stream")

#     total = int(latest["length"])
#     filename = latest.get("filename") or f"{machine_id}-{env}-latest.bin"
#     media_type = latest.get("contentType") or guess_media_type(filename)

#     range_header = request.headers.get("range") or request.headers.get("Range")
#     if not range_header:
#         # stream full file
#         def stream_full(chunk=1024 * 1024):
#             while True:
#                 data = grid_out.read(chunk)
#                 if not data:
#                     break
#                 yield data
#         headers = {
#             "Accept-Ranges": "bytes",
#             "Content-Disposition": f'attachment; filename="{filename}"',
#             "Content-Length": str(total),
#         }
#         return StreamingResponse(stream_full(), media_type=media_type, headers=headers)

#     # partial (resume) download
#     if not range_header.lower().startswith("bytes="):
#         raise HTTPException(status_code=400, detail="Invalid Range header")
#     start, end = parse_range_header(range_header.split("=", 1)[1], total)
#     length = end - start + 1

#     def stream_range(start_pos: int, length: int, chunk=1024 * 1024):
#         grid_out.seek(start_pos)
#         remaining = length
#         while remaining > 0:
#             data = grid_out.read(min(chunk, remaining))
#             if not data:
#                 break
#             remaining -= len(data)
#             yield data

#     headers = {
#         "Content-Range": f"bytes {start}-{end}/{total}",
#         "Accept-Ranges": "bytes",
#         "Content-Length": str(length),
#         "Content-Disposition": f'attachment; filename="{filename}"',
#     }
#     return StreamingResponse(stream_range(start, length), status_code=206, media_type=media_type, headers=headers)
import os
import re
import mimetypes
from datetime import datetime, timezone
from typing import Tuple, Literal

from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError

hardware_bp = APIRouter()

Env = Literal["dev", "production"]
_RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$", re.IGNORECASE)


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


@hardware_bp.post("/files/upload")
async def upload_machine_file(
    customer_id: str = Form(...),
    machine_id: str = Form(...),
    env: Env = Form(...),
    file: UploadFile = File(...),
):
    container = get_container_client()
    blob_name = make_blob_name(customer_id, machine_id, env, file.filename or "")
    content_type = file.content_type or guess_media_type(file.filename or "")

    try:
        # Stream upload directly from the incoming request file-like object
        container.upload_blob(
            name=blob_name,
            data=file.file,
            overwrite=False,
            metadata={
                "customer_id": customer_id,
                "machine_id": machine_id,
                "env": env,
                "orig_filename": file.filename or "",
            },
            content_settings=ContentSettings(content_type=content_type),
        )
        props = container.get_blob_client(blob_name).get_blob_properties()
        return {
            "id": blob_name,  # blob path serves as ID
            "filename": file.filename or "",
            "length": int(props.size),
            "content_type": props.content_settings.content_type or "application/octet-stream",
            "uploadDate": props.last_modified.isoformat(),
            "metadata": props.metadata,
            "message": "File uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@hardware_bp.post("/files/latest")
async def download_latest_file(
    request: Request,
    customer_id: str = Form(...),
    machine_id: str = Form(...),
    env: Env = Form(...),
):
    container = get_container_client()
    prefix = prefix_for(customer_id, machine_id, env)

    # Find most recent by last_modified
    try:
        latest = None
        for b in container.list_blobs(name_starts_with=prefix):
            if latest is None or b.last_modified > latest.last_modified:
                latest = b
        if latest is None:
            raise HTTPException(status_code=404, detail="No file found for this machine/env")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blobs: {e}")

    bc = container.get_blob_client(latest.name)
    try:
        props = bc.get_blob_properties()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch blob properties")

    total = int(props.size)
    filename = (props.metadata or {}).get("orig_filename") or latest.name.rsplit("/", 1)[-1]
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

    # Partial download (HTTP Range)
    if not range_header.lower().startswith("bytes="):
        raise HTTPException(status_code=400, detail="Invalid Range header")
    # start, end = parse_range_header(range_header.split("=", 1)[1], total)
    start, end = parse_range_header(range_header, total)

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
