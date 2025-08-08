from flask import  request, jsonify
from app.models.customer import Customer
from app.utils.auth import generate_token, token_required, admin_required
from app import get_database, hash_password
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

customer_bp = APIRouter()

# Pydantic models for request/response
class CustomerRegister(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    password: str

class CustomerLogin(BaseModel):
    email: str
    password: str

class AdminLogin(BaseModel):
    email: str
    password: str

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    created_at: str
    updated_at: str

class LoginResponse(BaseModel):
    message: str
    customer_id: str
    token: str

class RegisterResponse(BaseModel):
    message: str
    customer_id: str
    token: str

"""
The only changes made here was the validation code was removed
Since that is not needed in FastAPI, probably does it internally
"""
@customer_bp.post('/register', response_model=RegisterResponse)
async def register(customer_data: CustomerRegister):
    """Register a new customer"""
    try:
        # Uses a pydantic model instead of raw JSON
        # No manual validation needed for required fields in FastAPI


        # Check if email already exists
        existing_customer = Customer.find_by_email(customer_data.email)
        if existing_customer:
            raise HTTPException(status_code=400, detail='Email already registered')
        
        # Always generate a new UUID for customer_id
        import uuid
        customer_id = str(uuid.uuid4())
        
        # Create new customer with hashed password
        hashed_password = hash_password(customer_data.password)
        customer = Customer(
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            address=customer_data.address,
            password=hashed_password,
            customer_id=customer_id
        )
        customer.save()
        
        # Generate token
        token = generate_token(customer.customer_id, customer.email)
        
        return RegisterResponse(
            message='Customer registered successfully',
            customer_id=customer.customer_id,
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
1. Same for this one, automated validation using pydantic model
The CustomerLogin model is used to validate the request body

2. FastAPI automatically serializes Pydantic response models to JSON.
This makes the response type-safe and self-documenting (via Swagger / OpenAPI).
Clean separation of business logic and serialization.
"""
@customer_bp.post('/login', response_model=LoginResponse)
async def login(customer_data: CustomerLogin):
    """Customer login"""
    try:
        print(f"Login attempt for email: {customer_data.email}")
        
        # Find customer by email
        customer = Customer.find_by_email(customer_data.email)
        if not customer:
            print(f"Customer not found for email: {customer_data.email}")
            raise HTTPException(status_code=401, detail='Invalid email or password')
        
        # Check password
        if not customer.check_password(customer_data.password):
            print(f"Invalid password for email: {customer_data.email}")
            raise HTTPException(status_code=401, detail='Invalid email or password')
        
        # Generate token
        token = generate_token(customer.customer_id, customer.email)
        print(f"Login successful for customer: {customer.customer_id}")
        
        return LoginResponse(
            message='Login successful',
            customer_id=customer.customer_id,
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@customer_bp.post('/admin/login', response_model=LoginResponse)
async def admin_login(admin_data: AdminLogin):
    """Admin login"""
    try:
        # For demo purposes, using a simple admin check
        # In production, you should have a separate admin collection
        if admin_data.email == 'admin@example.com' and admin_data.password == 'admin123':
            token = generate_token('admin', admin_data.email, is_admin=True)
            return LoginResponse(
                message='Admin login successful',
                customer_id='admin',
                token=token
            )
        else:
            raise HTTPException(status_code=401, detail='Invalid admin credentials')
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Token verification happens behind the scenes via decorator in Flask using @token_required
In FastAPI, it is done inline, gives clear control over auth logic per route
Maybe returns proper error messages, but not sure, since we control and define them.
"""
@customer_bp.get('/{customer_id}', response_model=CustomerResponse)
async def get_customer(customer_id: str, request: Request):
    """Get customer details by customer_id"""
    try:
        # Get token from request headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Token is missing')
        
        token = auth_header.split(" ")[1]
        from app.utils.auth import verify_token
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail='Token is invalid or expired')
        
        # Check if user is admin or the customer themselves
        if not payload.get('is_admin', False) and payload['customer_id'] != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized access')
        
        customer = Customer.find_by_customer_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')
        
        return CustomerResponse(**customer.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
In this one, the token validation is done inline, rather than using a decorator
which is done in flask using @@token_required, @admin_required etc
This makes it easier to migrate one route at a time, especially if decorators 
are tightly coupled to Flask.
"""

@customer_bp.get('/', response_model=list[CustomerResponse])
async def get_all_customers(request: Request):
    """Get all customers (admin only)"""
    try:
        # Get token from request headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Token is missing')
        
        token = auth_header.split(" ")[1]
        from app.utils.auth import verify_token
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail='Token is invalid or expired')
        
        # Check if user is an admin
        if not payload.get('is_admin', False):
            raise HTTPException(status_code=403, detail='Admin privileges required')
        
        customers = Customer.get_all_customers()
        return [CustomerResponse(**customer.to_dict()) for customer in customers]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@customer_bp.get('/profile', response_model=CustomerResponse)
async def get_profile(request: Request):
    """Get current customer profile"""
    try:
        # Get token from request headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Token is missing')
        
        token = auth_header.split(" ")[1]
        from app.utils.auth import verify_token
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail='Token is invalid or expired')
        
        customer = Customer.find_by_customer_id(payload['customer_id'])
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')
        
        return CustomerResponse(**customer.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@customer_bp.get('/test-db')
async def test_database():
    """Test database connection - no auth required"""
    try:
        # Test if MongoDB is connected
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail='MongoDB connection not available')
        
        # Test a simple query
        customer_count = db.customers.count_documents({})
        
        return {
            "message": "Database connection successful",
            "customer_count": customer_count,
            "database_name": db.name
        }
        
    except Exception as e:
        print(f"Database test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}') 