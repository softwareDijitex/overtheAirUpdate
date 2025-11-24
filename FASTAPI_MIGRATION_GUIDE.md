# FastAPI Migration Guide

This guide outlines all the changes needed to migrate from Flask to FastAPI.

## ✅ Completed Changes

### 1. Customer Routes (`app/routes/customer_routes.py`)

- ✅ Converted Flask routes to FastAPI endpoints
- ✅ Added Pydantic models for request/response validation
- ✅ Updated error handling to use HTTPException
- ✅ Removed Flask-specific decorators and imports
- ✅ Added proper async/await support

### 2. Main Application (`app.py`)

- ✅ Added API route imports and inclusion
- ✅ Added FastAPI metadata (title, description, version)
- ✅ Added API tags for better documentation

### 3. Server Startup (`start_backend.sh`)

- ✅ Updated to use uvicorn instead of Flask development server

## 🔄 Remaining Changes Needed

### 1. Machine Routes (`app/routes/machine_routes.py`)

**Current Issues:**

- Uses Flask imports and decorators
- Uses Flask request objects
- Uses Flask jsonify responses

**Required Changes:**

```python
# Replace Flask imports
from flask import request, jsonify
# With FastAPI imports
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add Pydantic models
class MachineCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    location: Optional[str] = ""
    mac_address: Optional[str] = ""

class MachineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    mac_address: Optional[str] = None

# Convert routes
@machine_bp.route('/customer/<customer_id>', methods=['GET'])
# To
@machine_bp.get('/customer/{customer_id}')

# Update request handling
data = request.get_json()
# To
async def create_machine(machine_data: MachineCreate, request: Request):

# Update responses
return jsonify({'machines': machines_data}), 200
# To
return {'machines': machines_data}
```

### 2. File Routes (`app/routes/file_routes.py`)

**Current Issues:**

- Uses Flask file upload handling
- Uses Flask request.files
- Uses Flask send_file

**Required Changes:**

```python
# Replace Flask imports
from flask import request, jsonify, send_file
# With FastAPI imports
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import FileResponse

# Update file upload handling
@file_bp.route('/upload', methods=['POST'])
# To
@file_bp.post('/upload')

# Update file parameter
file = request.files['file']
# To
async def upload_file(file: UploadFile = File(...), request: Request):

# Update file download
return send_file(...)
# To
return FileResponse(...)
```

### 3. Authentication Utilities (`app/utils/auth.py`)

**Current Issues:**

- Uses Flask request objects
- Uses Flask decorators

**Required Changes:**

```python
# Replace Flask imports
from flask import request, jsonify
# With FastAPI imports
from fastapi import HTTPException, Depends, Request

# Convert decorators to dependency functions
def token_required(request: Request):
    # Extract token from request headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Token is missing')

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail='Token is invalid or expired')

    return payload

# Use as dependency
@router.get('/protected')
async def protected_route(token_data: dict = Depends(token_required)):
    return {"message": "Protected route"}
```

### 4. Database Models

**Current Issues:**

- Models use Flask-PyMongo
- Need to work with FastAPI async patterns

**Required Changes:**

```python
# Consider using motor for async MongoDB operations
from motor.motor_asyncio import AsyncIOMotorClient

# Update model methods to be async
async def save(self):
    # Async database operations
    pass

async def find_by_email(email: str):
    # Async database queries
    pass
```

### 5. Configuration (`app/config.py`)

**Current Issues:**

- Uses Flask configuration patterns

**Required Changes:**

```python
# Add Pydantic settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "a_very_secret_and_secure_key_please_change_this"
    mongo_uri: str
    db_name: str
    azure_storage_connection_string: str
    azure_storage_container_name: str
    max_file_size: int = 2 * 1024 * 1024

    class Config:
        env_file = ".env"

settings = Settings()
```

### 6. Dependencies (`requirements.txt`)

**Add FastAPI dependencies:**

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
motor>=3.3.0  # For async MongoDB
```

**Remove Flask dependencies:**

```
flask
flask-cors
flask-pymongo
flask-bcrypt
```

### 7. Frontend Configuration

**Update API error handling:**

```javascript
// In AuthContext.js, update error handling
catch (error) {
  console.error("Login error:", error);
  return {
    success: false,
    error: error.response?.data?.detail || "Login failed", // FastAPI uses 'detail' instead of 'message'
  };
}
```

## 🚀 Migration Steps

### Step 1: Install FastAPI Dependencies

```bash
pip install fastapi uvicorn pydantic pydantic-settings python-multipart motor
```

### Step 2: Update Machine Routes

```bash
# Convert machine_routes.py to FastAPI format
# Follow the pattern established in customer_routes.py
```

### Step 3: Update File Routes

```bash
# Convert file_routes.py to FastAPI format
# Update file upload/download handling
```

### Step 4: Update Authentication

```bash
# Convert auth.py decorators to FastAPI dependencies
# Update token handling
```

### Step 5: Test All Endpoints

```bash
# Run the debug script
python test/test_login_debug.py

# Test all endpoints manually
```

### Step 6: Update Frontend Error Handling

```bash
# Update error handling in React components
# Test login/register flows
```

## 🔧 Testing

### Test the Login Endpoint

```bash
# Start the FastAPI server
./start_backend.sh

# Test login
curl -X POST "http://localhost:8000/api/customers/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword"}'
```

### Test API Documentation

```bash
# Visit FastAPI auto-generated docs
http://localhost:8000/docs
http://localhost:8000/redoc
```

## 📝 Benefits of FastAPI Migration

1. **Automatic API Documentation** - OpenAPI/Swagger docs
2. **Type Safety** - Pydantic models provide runtime validation
3. **Better Performance** - Async support and modern Python features
4. **Modern Development** - Better IDE support and error messages
5. **Standards Compliance** - OpenAPI 3.0 specification
6. **Automatic Validation** - Request/response validation out of the box

## ⚠️ Important Notes

1. **Database Operations**: Consider making database operations async for better performance
2. **File Uploads**: FastAPI handles file uploads differently than Flask
3. **Error Handling**: FastAPI uses `detail` field for error messages instead of `message`
4. **Authentication**: Convert decorators to dependency injection pattern
5. **Testing**: Update tests to work with FastAPI patterns

## 🎯 Next Steps

1. Complete machine routes migration
2. Complete file routes migration
3. Update authentication utilities
4. Update database models for async operations
5. Update frontend error handling
6. Comprehensive testing
7. Performance optimization
