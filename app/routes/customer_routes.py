from flask import  request, jsonify
from app.models.customer import Customer
from app.utils.auth import generate_token, token_required, admin_required
from app import mongo
from fastapi import APIRouter

customer_bp = APIRouter()

@customer_bp.route('/register', methods=['POST'])
def register():
    """Register a new customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_customer = Customer.find_by_email(data['email'])
        if existing_customer:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Always generate a new UUID for customer_id
        import uuid
        customer_id = str(uuid.uuid4())
        
        # Create new customer with hashed password
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        customer = Customer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            password=hashed_password,
            customer_id=customer_id
        )
        customer.save()
        
        # Generate token
        token = generate_token(customer.customer_id, customer.email)
        
        return jsonify({
            'message': 'Customer registered successfully',
            'customer_id': customer.customer_id,
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @customer_bp.route('/login', methods=['POST'])
@customer_bp.post('/api/customers/login')
async def login():
    """Customer login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find customer by email
        customer = Customer.find_by_email(data['email'])
        if not customer:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not customer.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(customer.customer_id, customer.email)
        
        return jsonify({
            'message': 'Login successful',
            'customer_id': customer.customer_id,
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # For demo purposes, using a simple admin check
        # In production, you should have a separate admin collection
        if data['email'] == 'admin@example.com' and data['password'] == 'admin123':
            token = generate_token('admin', data['email'], is_admin=True)
            return jsonify({
                'message': 'Admin login successful',
                'token': token
            }), 200
        else:
            return jsonify({'error': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/<customer_id>', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Get customer details by customer_id"""
    try:
        # Check if user is admin or the customer themselves
        if not request.is_admin and request.customer_id != customer_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        customer = Customer.find_by_customer_id(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/', methods=['GET'])
@token_required
@admin_required
def get_all_customers():
    """Get all customers (admin only)"""
    try:
        customers = Customer.get_all_customers()
        return jsonify([customer.to_dict() for customer in customers]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current customer profile"""
    try:
        customer = Customer.find_by_customer_id(request.customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 