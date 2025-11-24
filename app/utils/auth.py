# import jwt
# from datetime import datetime, timedelta
# from functools import wraps
# from flask import request, jsonify
# from app.config import Config

# def generate_token(customer_id, email, is_admin=False):
#     """Generate JWT token for customer or admin"""
#     payload = {
#         'customer_id': customer_id,
#         'email': email,
#         'is_admin': is_admin,
#         'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
#         'iat': datetime.utcnow()
#     }
#     return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

# def verify_token(token):
#     """Verify JWT token and return payload"""
#     try:
#         payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None

# def token_required(f):
#     """Decorator to require valid JWT token"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             try:
#                 token = auth_header.split(" ")[1]
#             except IndexError:
#                 return jsonify({'message': 'Invalid token format'}), 401
        
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
        
#         payload = verify_token(token)
#         if not payload:
#             return jsonify({'message': 'Token is invalid or expired'}), 401
        
#         request.customer_id = payload['customer_id']
#         request.email = payload['email']
#         request.is_admin = payload.get('is_admin', False)
        
#         return f(*args, **kwargs)
    
#     return decorated

# def customer_required(f):
#     """Decorator to require customer authentication (not admin)"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             try:
#                 token = auth_header.split(" ")[1]
#             except IndexError:
#                 return jsonify({'message': 'Invalid token format'}), 401
        
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
        
#         payload = verify_token(token)
#         if not payload:
#             return jsonify({'message': 'Token is invalid or expired'}), 401
        
#         # Check if user is not an admin (i.e., is a customer)
#         if payload.get('is_admin', False):
#             return jsonify({'message': 'Customer access required'}), 403
        
#         request.customer_id = payload['customer_id']
#         request.email = payload['email']
#         request.is_admin = payload.get('is_admin', False)
        
#         return f(*args, **kwargs)
    
#     return decorated

# def admin_required(f):
#     """Decorator to require admin privileges"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             try:
#                 token = auth_header.split(" ")[1]
#             except IndexError:
#                 return jsonify({'message': 'Invalid token format'}), 401
        
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
        
#         payload = verify_token(token)
#         if not payload:
#             return jsonify({'message': 'Token is invalid or expired'}), 401
        
#         # Check if user is an admin
#         if not payload.get('is_admin', False):
#             return jsonify({'message': 'Admin privileges required'}), 403
        
#         request.customer_id = payload['customer_id']
#         request.email = payload['email']
#         request.is_admin = payload.get('is_admin', False)
        
#         return f(*args, **kwargs)
    
#     return decorated 



# app/auth_deps.py

import jwt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.config import Config

# ---------------------------
# Token utils (unchanged API)
# ---------------------------

def generate_token(customer_id: str, email: str, is_admin: bool = False) -> str:
    """Generate JWT token for customer or admin"""
    payload = {
        "customer_id": customer_id,
        "email": email,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload (or None if invalid/expired)"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ---------------------------
# Models
# ---------------------------

class CurrentUser(BaseModel):
    customer_id: str
    email: EmailStr
    is_admin: bool = False

# ---------------------------
# Helpers
# ---------------------------

def _extract_bearer_token(authorization: Optional[str]) -> str:
    """
    Expect header like: Authorization: Bearer <token>
    Raises HTTP 401 if missing/invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'.",
        )
    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
        )
    return token

def _payload_to_user(request: Request, payload: dict) -> CurrentUser:
    """Populate request.state (optional) and return CurrentUser."""
    customer_id = payload.get("customer_id")
    email = payload.get("email")
    is_admin = bool(payload.get("is_admin", False))

    if not customer_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing required fields",
        )

    # Optional: make available to other layers
    request.state.customer_id = customer_id
    request.state.email = email
    request.state.is_admin = is_admin

    return CurrentUser(customer_id=customer_id, email=email, is_admin=is_admin)

# --------------------------------
# FastAPI dependencies (use Depends)
# --------------------------------

async def token_required(
    request: Request,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> CurrentUser:
    """
    Accepts any valid token (admin or customer).
    Usage: current_user: CurrentUser = Depends(token_required)
    """
    token = _extract_bearer_token(authorization)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
    return _payload_to_user(request, payload)

async def customer_required(
    request: Request,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> CurrentUser:
    """
    Requires a valid token AND non-admin (customer) user.
    Usage: current_user: CurrentUser = Depends(customer_required)
    """
    token = _extract_bearer_token(authorization)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
    if payload.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )
    return _payload_to_user(request, payload)

async def admin_required(
    request: Request,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> CurrentUser:
    """
    Requires a valid token AND admin privileges.
    Usage: current_user: CurrentUser = Depends(admin_required)
    """
    token = _extract_bearer_token(authorization)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )
    if not payload.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return _payload_to_user(request, payload)
