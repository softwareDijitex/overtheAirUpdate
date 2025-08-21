from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import uuid
from datetime import datetime
import re
from app import get_database  # Use the shared database instance from app
import traceback

class Machine:
    def __init__(self, name, customer_id, description="", location="", status="active", mac_address=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.customer_id = customer_id
        self.description = description
        self.location = location
        self.status = status
        self.mac_address = mac_address
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'customer_id': self.customer_id,
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'mac_address': self.mac_address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        """Save the machine as a subdocument in the customer's document"""
        try:
            print(f"Attempting to save machine as subdocument: {self.to_dict()}")
            db = get_database()
            result = db.customers.update_one(
                {'customer_id': self.customer_id},
                {'$push': {'machines': self.to_dict()}}
            )
            print(f"Save result: {result.raw_result}")
            return self.id if result.modified_count > 0 else None
        except Exception as e:
            print(f"Error saving machine: {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def from_dict(data):
        machine = Machine(
            name=data['name'],
            customer_id=data['customer_id'],
            description=data.get('description', ''),
            location=data.get('location', ''),
            status=data.get('status', 'active'),
            mac_address=data.get('mac_address', '')
        )
        machine.id = data['id']
        machine.created_at = data['created_at']
        machine.updated_at = data['updated_at']
        return machine

    @staticmethod
    def get_customer_machines(customer_id):
        try:
            db = get_database()
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return []
            return [Machine.from_dict(m) for m in customer['machines']]
        except Exception as e:
            print(f"Error finding machines by customer: {e}")
            return []

    @staticmethod
    def find_by_machine_id(customer_id, machine_id):
        try:
            db = get_database()
            customer = db.customers.find_one({'customer_id': customer_id})
            if not customer or 'machines' not in customer:
                return None
            for m in customer['machines']:
                if m['id'] == machine_id:
                    return Machine.from_dict(m)
            return None
        except Exception as e:
            print(f"Error finding machine by customer_id and machine_id: {e}")
            return None

    @staticmethod
    def update_machine(customer_id, machine_id, updates):
        try:
            updates['updated_at'] = datetime.utcnow()
            # Use positional operator to update the correct machine in the array
            db = get_database()
            result = db.customers.update_one(
                {'customer_id': customer_id, 'machines.id': machine_id},
                {'$set': {f'machines.$.{k}': v for k, v in updates.items()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating machine: {e}")
            return False

    @staticmethod
    def delete_machine_by_customer(customer_id, machine_id):
        try:
            db = get_database()
            result = db.customers.update_one(
                {'customer_id': customer_id},
                {'$pull': {'machines': {'id': machine_id}}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting machine by customer_id and machine_id: {e}")
            return False

    @staticmethod
    def is_valid_mac_address(mac_address):
        if not mac_address:
            return True
        clean_mac = re.sub(r'[:-]', '', mac_address.upper())
        if len(clean_mac) != 12:
            return False
        try:
            int(clean_mac, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def normalize_mac_address(mac_address):
        if not mac_address:
            return ""
        clean_mac = re.sub(r'[^0-9A-Fa-f]', '', mac_address.upper())
        if len(clean_mac) != 12:
            return mac_address
        return ':'.join([clean_mac[i:i+2] for i in range(0, 12, 2)])

    @staticmethod
    def mac_address_exists(mac_address):
        try:
            if not mac_address:
                return False
            normalized_mac = Machine.normalize_mac_address(mac_address)
            # Check all customers for this MAC address
            db = get_database()
            count = db.customers.count_documents({'machines.mac_address': normalized_mac})
            return count > 0
        except Exception as e:
            print(f"Error checking MAC address existence: {e}")
            return False 