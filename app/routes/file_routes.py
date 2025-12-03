from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.file import File as FileModel
from app.models.machine import Machine
from app.utils.auth import admin_required, customer_required
from app import get_database
import io
from typing import Optional

file_bp = APIRouter()

@file_bp.post('/upload') # this is for admin 
async def upload_file(
    file: UploadFile = File(...),
    machine_id: str = Form(...),
    version: Optional[str] = Form(None),
    current_user=Depends(customer_required)
):
    """Upload a file to a specific machine"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail='No file selected')
        
        # Get customer_id from authenticated user
        customer_id = current_user.customer_id
        
        # Check if machine exists and belongs to customer
        machine = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        
        file_data = await file.read()
        
        from app.config import Config
        if len(file_data) > Config.MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max {Config.MAX_UPLOAD_MB} MB"
            )


        # Create and save file
        file_obj = FileModel(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=file.filename,
            file_data=file_data,
            version=version
        )
        
        file_id = file_obj.save()
        
        return {
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'filename': file.filename,
            'version': file_obj.version
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.post('/customer/{customer_id}/machine/{machine_id}/upload') # this is for customer 
async def upload_file_to_machine(
    customer_id: str,
    machine_id: str,
    file: UploadFile = File(...),
    version: str = Form(...),
    current_user=Depends(customer_required)
):
    """Upload a file to a specific machine for a specific customer (URL-based)"""
    try:
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
            
        if not file.filename:
            raise HTTPException(status_code=400, detail='No file selected')
        
        file_data = await file.read()
        
        file_model = FileModel(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=file.filename,
            file_data=file_data,
            version=version
        )
        
        save_result = file_model.save()
        if save_result is None:
            raise HTTPException(status_code=500, detail='Failed to save file')
            
        return {'message': 'File uploaded successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/download/{customer_id}/{machine_id}/{filename}/{version}')
async def download_file(
    customer_id: str,
    machine_id: str,
    filename: str,
    version: str,
    current_user=Depends(customer_required)
):
    """Download a specific version of a file"""
    try:
        # For customers, they can only download their own files
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
        
        # Get file
        file_data = FileModel.get_file(customer_id, machine_id, filename, version)
        if not file_data:
            raise HTTPException(status_code=404, detail='File not found')
        
        # Create file-like object
        file_stream = io.BytesIO(file_data['content'])
        file_stream.seek(0)
        
        # Remove version suffix from filename for download
        download_filename = filename
        if f"_v{version}" in download_filename:
            download_filename = download_filename.replace(f"_v{version}", "")
        
        return StreamingResponse(
            io.BytesIO(file_data['content']),
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/versions/{customer_id}/{machine_id}/{filename}')
async def get_file_versions(
    customer_id: str,
    machine_id: str,
    filename: str,
    current_user=Depends(customer_required)
):
    """Get all versions of a file for a specific machine"""
    try:
        # For customers, they can only see their own files
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
        
        versions = FileModel.get_all_versions(customer_id, machine_id, filename)
        return {'versions': versions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/customer/{customer_id}/machine/{machine_id}')
async def get_customer_machine_files(
    customer_id: str,
    machine_id: str,
    current_user=Depends(customer_required)
):
    """Get all files for a specific machine of a specific customer (URL-based)"""
    try:
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
            
        files = FileModel.get_machine_files(customer_id, machine_id)
        return {'files': files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/machine/{customer_id}/{machine_id}')
async def get_machine_files(
    customer_id: str,
    machine_id: str,
    current_user=Depends(customer_required)
):
    # Basically when you click on a machine in the customer dashboard, this route is called - to get all files for that machine
    """Get all files for a specific machine"""
    try:
        # For customers, they can only see their own files
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
        
        files = FileModel.get_machine_files(customer_id, machine_id)
        return {'files': files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/customer/{customer_id}')
async def get_customer_files(
    customer_id: str,
    # current_user=Depends(customer_required)
):
    """Get all files for a customer across all machines"""
    try:
        # For customers, they can only see their own files
        # if current_user.customer_id != customer_id:
        #     raise HTTPException(status_code=403, detail='Unauthorized')
        
        files = FileModel.get_customer_files(customer_id)
        return {'files': files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.delete('/delete/{customer_id}/{machine_id}/{filename}/{version}')
async def delete_file(
    customer_id: str,
    machine_id: str,
    filename: str,
    version: str,
    current_user=Depends(customer_required)
):
    """Delete a specific version of a file"""
    try:
        # For customers, they can only delete their own files
        if current_user.customer_id != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized')
        
        FileModel.delete_file(customer_id, machine_id, filename, version)
        return {'message': 'File deleted successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin routes for managing any customer's files
@file_bp.post('/admin/upload')
async def admin_upload_file(
    file: UploadFile = File(...),
    customer_id: str = Form(...),
    machine_id: str = Form(...),
    version: Optional[str] = Form(None),
    current_user=Depends(admin_required)
):
    """Admin: Upload a file to any customer's machine"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail='No file selected')
        
        # Check if customer exists
        db = get_database()
        customer = db.customers.find_one({'customer_id': customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')
        
        # Check if machine exists
        machine = Machine.find_by_machine_id_for_customer(customer_id, machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail='Machine not found')
        
        file_data = await file.read()

        from app.config import Config
        if len(file_data) > Config.MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max {Config.MAX_UPLOAD_MB} MB"
            )

        
        # Create and save file
        file_obj = FileModel(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=file.filename,
            file_data=file_data,
            version=version
        )
        
        file_id = file_obj.save()
        
        return {
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'filename': file.filename,
            'version': file_obj.version
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/admin/download/{customer_id}/{machine_id}/{filename}/{version}')
async def admin_download_file(
    customer_id: str,
    machine_id: str,
    filename: str,
    version: str,
    current_user=Depends(admin_required)
):
    """Admin: Download any file"""
    try:
        # Get file
        file_data = FileModel.get_file(customer_id, machine_id, filename, version)
        if not file_data:
            raise HTTPException(status_code=404, detail='File not found')
        
        # Remove version suffix from filename for download
        download_filename = filename
        if f"_v{version}" in download_filename:
            download_filename = download_filename.replace(f"_v{version}", "")
        
        return StreamingResponse(
            io.BytesIO(file_data['content']),
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/admin/versions/{customer_id}/{machine_id}/{filename}')
async def admin_get_file_versions(
    customer_id: str,
    machine_id: str,
    filename: str,
    current_user=Depends(admin_required)
):
    """Admin: Get all versions of any file"""
    try:
        versions = FileModel.get_all_versions(customer_id, machine_id, filename)
        return {'versions': versions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/admin/machine/{customer_id}/{machine_id}')
async def admin_get_machine_files(
    customer_id: str,
    machine_id: str,
    current_user=Depends(admin_required)
):
    # Basically when you click on a machine in the admin dashboard, this route is called - to get all files for that machine for that customer

    """Admin: Get all files for any machine""" 

    try:
        files = FileModel.get_machine_files(customer_id, machine_id)
        return {'files': files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.get('/admin/customer/{customer_id}')
async def admin_get_customer_files(
    customer_id: str,
    current_user=Depends(admin_required)
):
    """Admin: Get all machines for any customer"""
    try:
        files = FileModel.get_customer_files(customer_id)
        return {'files': files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@file_bp.delete('/admin/delete/{customer_id}/{machine_id}/{filename}/{version}')
async def admin_delete_file(
    customer_id: str,
    machine_id: str,
    filename: str,
    version: str,
    current_user=Depends(admin_required)
):
    """Admin: Delete any file"""
    try:
        FileModel.delete_file(customer_id, machine_id, filename, version)
        return {'message': 'File deleted successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))