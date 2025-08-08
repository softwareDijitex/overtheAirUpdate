from flask import  request, jsonify, send_file
from app.models.file import File
from app.models.machine import Machine
from app.utils.auth import admin_required, customer_required
from app import get_database
from fastapi import APIRouter
import io

file_bp = APIRouter()

@file_bp.route('/upload', methods=['POST'])
@customer_required
def upload_file():
    """Upload a file to a specific machine"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get customer_id from authenticated user
        customer_id = request.customer_id
        
        # Get machine_id from form data
        machine_id = request.form.get('machine_id')
        if not machine_id:
            return jsonify({'error': 'Machine ID is required'}), 400
        
        # Check if machine exists and belongs to customer
        machine = Machine.find_by_machine_id(customer_id, machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        filename = file.filename
        file_data = file.read()
        version = request.form.get('version')
        
        # Create and save file
        file_obj = File(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=filename,
            file_data=file_data,
            version=version
        )
        
        file_id = file_obj.save()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'filename': filename,
            'version': file_obj.version
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/customer/<customer_id>/machine/<machine_id>/upload', methods=['POST'])
@customer_required
def upload_file_to_machine(customer_id, machine_id):
    """Upload a file to a specific machine for a specific customer (URL-based)"""
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        version = request.form.get('version')
        if not version:
            return jsonify({'error': 'Version is required'}), 400
        file_data = file.read()
        file_model = File(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=file.filename,
            file_data=file_data,
            version=version
        )
        save_result = file_model.save()
        if save_result is None:
            return jsonify({'error': 'Failed to save file'}), 500
        return jsonify({'message': 'File uploaded successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/download/<customer_id>/<machine_id>/<filename>/<version>', methods=['GET'])
@customer_required
def download_file(customer_id, machine_id, filename, version):
    """Download a specific version of a file"""
    try:
        # For customers, they can only download their own files
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get file
        file_data = File.get_file(customer_id, machine_id, filename, version)
        if not file_data:
            return jsonify({'error': 'File not found'}), 404
        
        # Create file-like object
        file_stream = io.BytesIO(file_data['content'])
        file_stream.seek(0)
        
        # Remove version suffix from filename for download
        download_filename = filename
        if f"_v{version}" in download_filename:
            download_filename = download_filename.replace(f"_v{version}", "")
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/versions/<customer_id>/<machine_id>/<filename>', methods=['GET'])
@customer_required
def get_file_versions(customer_id, machine_id, filename):
    """Get all versions of a file for a specific machine"""
    try:
        # For customers, they can only see their own files
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        versions = File.get_all_versions(customer_id, machine_id, filename)
        return jsonify({'versions': versions}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/customer/<customer_id>/machine/<machine_id>', methods=['GET'])
@customer_required
def get_customer_machine_files(customer_id, machine_id):
    """Get all files for a specific machine of a specific customer (URL-based)"""
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        files = File.get_machine_files(customer_id, machine_id)
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/machine/<customer_id>/<machine_id>', methods=['GET'])
@customer_required
def get_machine_files(customer_id, machine_id):
    """Get all files for a specific machine"""
    try:
        # For customers, they can only see their own files
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        files = File.get_machine_files(customer_id, machine_id)
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/customer/<customer_id>', methods=['GET'])
@customer_required
def get_customer_files(customer_id):
    """Get all files for a customer across all machines"""
    try:
        # For customers, they can only see their own files
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        files = File.get_customer_files(customer_id)
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/delete/<customer_id>/<machine_id>/<filename>/<version>', methods=['DELETE'])
@customer_required
def delete_file(customer_id, machine_id, filename, version):
    """Delete a specific version of a file"""
    try:
        # For customers, they can only delete their own files
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        File.delete_file(customer_id, machine_id, filename, version)
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes for managing any customer's files
@file_bp.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload_file():
    """Admin: Upload a file to any customer's machine"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get customer_id and machine_id from form data
        customer_id = request.form.get('customer_id')
        machine_id = request.form.get('machine_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID is required'}), 400
        if not machine_id:
            return jsonify({'error': 'Machine ID is required'}), 400
        
        # Check if customer exists
        db = get_database()
        customer = db.customers.find_one({'customer_id': customer_id})
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Check if machine exists
        machine = Machine.find_by_machine_id(customer_id, machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        filename = file.filename
        file_data = file.read()
        version = request.form.get('version')
        
        # Create and save file
        file_obj = File(
            customer_id=customer_id,
            machine_id=machine_id,
            filename=filename,
            file_data=file_data,
            version=version
        )
        
        file_id = file_obj.save()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': file_id,
            'filename': filename,
            'version': file_obj.version
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/admin/download/<customer_id>/<machine_id>/<filename>/<version>', methods=['GET'])
@admin_required
def admin_download_file(customer_id, machine_id, filename, version):
    """Admin: Download any file"""
    try:
        # Get file
        file_data = File.get_file(customer_id, machine_id, filename, version)
        if not file_data:
            return jsonify({'error': 'File not found'}), 404
        
        # Create file-like object
        file_stream = io.BytesIO(file_data['content'])
        file_stream.seek(0)
        
        # Remove version suffix from filename for download
        download_filename = filename
        if f"_v{version}" in download_filename:
            download_filename = download_filename.replace(f"_v{version}", "")
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/admin/versions/<customer_id>/<machine_id>/<filename>', methods=['GET'])
@admin_required
def admin_get_file_versions(customer_id, machine_id, filename):
    """Admin: Get all versions of any file"""
    try:
        versions = File.get_all_versions(customer_id, machine_id, filename)
        return jsonify({'versions': versions}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/admin/machine/<customer_id>/<machine_id>', methods=['GET'])
@admin_required
def admin_get_machine_files(customer_id, machine_id):
    """Admin: Get all files for any machine"""
    try:
        files = File.get_machine_files(customer_id, machine_id)
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/admin/customer/<customer_id>', methods=['GET'])
@admin_required
def admin_get_customer_files(customer_id):
    """Admin: Get all files for any customer"""
    try:
        files = File.get_customer_files(customer_id)
        return jsonify({'files': files}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/admin/delete/<customer_id>/<machine_id>/<filename>/<version>', methods=['DELETE'])
@admin_required
def admin_delete_file(customer_id, machine_id, filename, version):
    """Admin: Delete any file"""
    try:
        File.delete_file(customer_id, machine_id, filename, version)
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 