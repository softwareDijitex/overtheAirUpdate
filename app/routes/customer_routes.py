from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid

# Import your existing modules
from app.models.customer import Customer
from app.utils.auth import generate_token, verify_token
from app import get_database, hash_password

customer_bp = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class CustomerRegister(BaseModel):
    name: str
    email: EmailStr  # Now using EmailStr with proper validation
    phone: str
    address: str
    password: str

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LoginResponse(BaseModel):
    message: str
    customer_id: str
    token: str

class RegisterResponse(BaseModel):
    message: str
    customer_id: str
    token: str

# Dependency for token verification
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify token and return user info"""
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail='Token is invalid or expired')
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail='Token is invalid or expired')

# Dependency for admin verification
async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Verify admin privileges"""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Admin privileges required')
    return current_user

@customer_bp.post('/register', response_model=RegisterResponse)
async def register(customer_data: CustomerRegister):
    """Register a new customer"""
    try:
        # Check if email already exists
        existing_customer = Customer.find_by_email(customer_data.email)
        if existing_customer:
            raise HTTPException(status_code=400, detail='Email already registered')
        
        # Generate a new UUID for customer_id
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
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        # For demo purposes - in production, use a proper admin system
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


@customer_bp.get('/test-db')
async def test_database():
    """Test database connection - no auth required"""
    try:
        # Test if MongoDB is connected
        db = get_database()
        if db is None:
            raise HTTPException(status_code=500, detail='MongoDB connection not available')
        
        # Test a simple query with timeout
        customer_count = db.customers.count_documents({})
        
        return {
            "message": "Database connection successful",
            "customer_count": customer_count,
            "database_name": db.name
        }
        
    except Exception as e:
        print(f"Database test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')
        
@customer_bp.get('/{customer_id}', response_model=CustomerResponse)
async def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    """Get customer details by customer_id"""
    try:
        # Check if user is admin or the customer themselves
        if not current_user.get('is_admin', False) and current_user['customer_id'] != customer_id:
            raise HTTPException(status_code=403, detail='Unauthorized access')
        
        customer = Customer.find_by_customer_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')
        
        return CustomerResponse(**customer.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get customer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@customer_bp.get('/', response_model=List[CustomerResponse])
async def get_all_customers(admin_user: dict = Depends(get_admin_user)):
    """Get all customers (admin only)"""
    try:
        customers = Customer.get_all_customers()
        return [CustomerResponse(**customer.to_dict()) for customer in customers]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get all customers error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@customer_bp.get('/profile', response_model=CustomerResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current customer profile"""
    try:
        customer = Customer.find_by_customer_id(current_user['customer_id'])
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')
        
        return CustomerResponse(**customer.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

