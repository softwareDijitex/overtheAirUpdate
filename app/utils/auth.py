import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from app.config import Config

def generate_token(customer_id, email, is_admin=False):
    """Generate JWT token for customer or admin"""
    payload = {
        'customer_id': customer_id,
        'email': email,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        request.customer_id = payload['customer_id']
        request.email = payload['email']
        request.is_admin = payload.get('is_admin', False)
        
        return f(*args, **kwargs)
    
    return decorated

def customer_required(f):
    """Decorator to require customer authentication (not admin)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Check if user is not an admin (i.e., is a customer)
        if payload.get('is_admin', False):
            return jsonify({'message': 'Customer access required'}), 403
        
        request.customer_id = payload['customer_id']
        request.email = payload['email']
        request.is_admin = payload.get('is_admin', False)
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Check if user is an admin
        if not payload.get('is_admin', False):
            return jsonify({'message': 'Admin privileges required'}), 403
        
        request.customer_id = payload['customer_id']
        request.email = payload['email']
        request.is_admin = payload.get('is_admin', False)
        
        return f(*args, **kwargs)
    
    return decorated 