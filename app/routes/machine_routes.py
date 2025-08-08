from flask import request, jsonify
from app.models.machine import Machine
from app.utils.auth import admin_required, customer_required, token_required
from app import get_database
from datetime import datetime
import traceback
from fastapi import APIRouter

machine_bp = APIRouter()


# Customer routes for managing their own machines
@machine_bp.route('/customer/<customer_id>', methods=['GET'])
@customer_required
def get_customer_machines(customer_id):
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        machines = Machine.get_customer_machines(customer_id)
        machines_data = [machine.to_dict() for machine in machines]
        return jsonify({'machines': machines_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/customer/<customer_id>', methods=['POST'])
@customer_required
def create_customer_machine(customer_id):
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        name = data.get('name')
        description = data.get('description', '')
        location = data.get('location', '')
        mac_address = data.get('mac_address', '')
        if not name:
            return jsonify({'error': 'Machine name is required'}), 400
        machine = Machine(
            name=name,
            customer_id=customer_id,
            description=description,
            location=location,
            mac_address=mac_address
        )
        machine_id = machine.save()
        if not machine_id:
            return jsonify({'error': 'Failed to create machine'}), 500
        return jsonify({
            'message': 'Machine created successfully',
            'machine_id': machine_id,
            'machine': machine.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/customer/<customer_id>/<machine_id>', methods=['GET'])
@customer_required
def get_customer_machine(customer_id, machine_id):
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        machine = Machine.find_by_machine_id(customer_id, machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        return jsonify({'machine': machine.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/customer/<customer_id>/<machine_id>', methods=['PUT'])
@customer_required
def update_customer_machine(customer_id, machine_id):
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        machine = Machine.find_by_machine_id(customer_id, machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        update_data = {}
        for field in ['name', 'description', 'location', 'status', 'mac_address']:
            if field in data:
                update_data[field] = data[field]
        if update_data:
            success = Machine.update_machine(customer_id, machine_id, update_data)
            if not success:
                return jsonify({'error': 'Failed to update machine'}), 500
        updated_machine = Machine.find_by_machine_id(customer_id, machine_id)
        return jsonify({
            'message': 'Machine updated successfully',
            'machine': updated_machine.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/customer/<customer_id>/<machine_id>', methods=['DELETE'])
@customer_required
def delete_customer_machine(customer_id, machine_id):
    try:
        user_customer_id = request.customer_id
        if user_customer_id != customer_id:
            return jsonify({'error': 'Unauthorized'}), 403
        machine = Machine.find_by_machine_id(customer_id, machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        success = Machine.delete_machine_by_customer(customer_id, machine_id)
        if not success:
            return jsonify({'error': 'Failed to delete machine'}), 500
        return jsonify({'message': 'Machine deleted successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Admin routes for managing any customer's machines
@machine_bp.route('/admin/', methods=['POST'])
@admin_required
def admin_create_machine():
    """Admin: Create a machine for any customer"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        customer_id = data.get('customer_id')
        name = data.get('name')
        description = data.get('description', '')
        location = data.get('location', '')
        mac_address = data.get('mac_address', '')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID is required'}), 400
        if not name:
            return jsonify({'error': 'Machine name is required'}), 400
        
        # Check if customer exists
        db = get_database()
        customer = db.customers.find_one({'customer_id': customer_id})
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create machine
        machine = Machine(
            name=name,
            customer_id=customer_id,
            description=description,
            location=location,
            mac_address=mac_address
        )
        
        machine_id = machine.save()
        
        if not machine_id:
            return jsonify({'error': 'Failed to create machine'}), 500
        
        return jsonify({
            'message': 'Machine created successfully',
            'machine_id': machine_id,
            'machine': machine.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/admin/customer/<customer_id>', methods=['GET'])
@admin_required
def admin_get_customer_machines(customer_id):
    """Admin: Get all machines for a customer"""
    try:
        machines = Machine.get_customer_machines(customer_id)
        machines_data = [machine.to_dict() for machine in machines]
        
        return jsonify({'machines': machines_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/admin/<machine_id>', methods=['GET'])
@admin_required
def admin_get_machine(machine_id):
    """Admin: Get a specific machine by ID"""
    try:
        machine = Machine.get_machine_by_id(machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        return jsonify({'machine': machine.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/admin/<machine_id>', methods=['PUT'])
@admin_required
def admin_update_machine(machine_id):
    """Admin: Update any machine"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if machine exists
        machine = Machine.get_machine_by_id(machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        # Update fields
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'location' in data:
            update_data['location'] = data['location']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'mac_address' in data:
            update_data['mac_address'] = data['mac_address']
        if 'customer_id' in data:
            # Verify customer exists
            db = get_database()
            customer = db.customers.find_one({'customer_id': data['customer_id']})
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            update_data['customer_id'] = data['customer_id']
        
        if update_data:
            success = Machine.update_machine(machine_id, update_data)
            if not success:
                return jsonify({'error': 'Failed to update machine'}), 500
        
        # Get updated machine
        updated_machine = Machine.get_machine_by_id(machine_id)
        
        return jsonify({
            'message': 'Machine updated successfully',
            'machine': updated_machine.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/admin/<machine_id>', methods=['DELETE'])
@admin_required
def admin_delete_machine(machine_id):
    """Admin: Delete any machine"""
    try:
        # Check if machine exists
        machine = Machine.get_machine_by_id(machine_id)
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        # Delete machine
        success = Machine.delete_machine_by_customer(machine.customer_id, machine_id)
        if not success:
            return jsonify({'error': 'Failed to delete machine'}), 500
        
        return jsonify({'message': 'Machine deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@machine_bp.route('/admin/all', methods=['GET'])
@admin_required
def admin_get_all_machines():
    """Admin: Get all machines"""
    try:
        machines = Machine.get_all_machines()
        machines_data = [machine.to_dict() for machine in machines]
        
        return jsonify({'machines': machines_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 