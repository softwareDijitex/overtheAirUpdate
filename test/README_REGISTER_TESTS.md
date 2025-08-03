# Register Endpoint Tests

This directory contains comprehensive tests for the `/api/customers/register` endpoint.

## Test Files

### 1. `test_register_endpoint.py` - Unit Tests
Comprehensive unit tests using pytest that test the register endpoint with mocked dependencies.

**Features:**
- Tests successful registration
- Tests validation errors (missing/empty fields)
- Tests duplicate email handling
- Tests database error scenarios
- Tests token generation errors
- Tests password hashing
- Tests UUID generation

**To run:**
```bash
# Install pytest if not already installed
pip install pytest

# Run the unit tests
pytest test_register_endpoint.py -v

# Run with coverage
pytest test_register_endpoint.py -v --cov=app.routes.customer_routes
```

### 2. `test_register_integration.py` - Integration Tests
Integration tests that test the actual registration flow with a running server.

**Features:**
- Tests successful registration with real server
- Tests duplicate email rejection
- Tests missing field validation
- Tests empty field validation
- Tests invalid JSON handling
- Tests complete register -> login flow

**To run:**
```bash
# Make sure the server is running on localhost:8000
python test_register_integration.py
```

## Test Scenarios Covered

### Unit Tests (`test_register_endpoint.py`)

1. **Successful Registration**
   - Validates correct response format
   - Checks customer_id generation
   - Verifies token generation
   - Confirms password hashing

2. **Validation Errors**
   - Missing required fields (name, email, phone, address, password)
   - Empty required fields
   - Invalid JSON data

3. **Business Logic**
   - Duplicate email rejection
   - UUID generation for customer_id
   - Password hashing with bcrypt

4. **Error Handling**
   - Database connection errors during save
   - Database errors during email check
   - Token generation failures

### Integration Tests (`test_register_integration.py`)

1. **End-to-End Flow**
   - Complete registration process
   - Login with registered credentials
   - Customer ID consistency between register and login

2. **Real Server Testing**
   - Tests against actual running server
   - Validates HTTP status codes
   - Checks response format

## Prerequisites

### For Unit Tests:
- pytest
- unittest.mock (built-in)
- Flask test client

### For Integration Tests:
- requests library
- Running server on localhost:8000

## Expected Test Results

### Unit Tests:
```
test_register_endpoint.py::TestRegisterEndpoint::test_successful_registration PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_missing_required_fields PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_empty_required_fields PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_duplicate_email_registration PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_invalid_json_data PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_database_error_during_save PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_database_error_during_email_check PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_token_generation_error PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_password_hashing PASSED
test_register_endpoint.py::TestRegisterEndpoint::test_customer_id_generation PASSED
```

### Integration Tests:
```
🧪 Testing Register Endpoint
==================================================

1. Testing successful registration...
   Status Code: 201
   ✅ Registration successful
   Customer ID: 12345678-1234-5678-9abc-123456789abc
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   Message: Customer registered successfully

2. Testing duplicate email registration...
   Status Code: 400
   ✅ Duplicate email correctly rejected
   Error: Email already registered

...

🎉 All register endpoint tests passed!
```

## API Endpoint Details

**Endpoint:** `POST /api/customers/register`

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, State 12345",
    "password": "securepassword123"
}
```

**Success Response (201):**
```json
{
    "message": "Customer registered successfully",
    "customer_id": "12345678-1234-5678-9abc-123456789abc",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request`: Missing/empty required fields, duplicate email
- `500 Internal Server Error`: Database errors, token generation failures

## Notes

- The unit tests use mocking to isolate the endpoint logic from external dependencies
- The integration tests require a running server and test against the actual database
- Both test suites provide comprehensive coverage of the registration functionality
- The tests follow the existing project patterns and conventions 