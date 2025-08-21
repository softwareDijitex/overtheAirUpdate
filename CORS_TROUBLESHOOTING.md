# CORS and Login Troubleshooting Guide

## 🔍 Current Issues
- CORS error in browser console
- 400 error on preflight request
- Login endpoint not working

## 🚀 Quick Fix Steps

### Step 1: Restart the FastAPI Server
```bash
# Stop the current server (Ctrl+C)
# Then restart with the updated configuration
./start_backend.sh
```

### Step 2: Test CORS Configuration
```bash
python test/test_cors_debug.py
```

### Step 3: Test Database Integration
```bash
python test/test_database_integration.py
```

### Step 4: Test Login Endpoint
```bash
python test/test_fastapi_login.py
```

## 🔧 Debugging Steps

### 1. Check Server Status
```bash
# Test if server is running
curl http://localhost:8000/health
```

### 2. Test CORS Preflight
```bash
# Test OPTIONS request
curl -X OPTIONS http://localhost:8000/api/customers/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

### 3. Test Login Endpoint Directly
```bash
# Test login with curl
curl -X POST http://localhost:8000/api/customers/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"email": "test@example.com", "password": "testpassword"}'
```

### 4. Check Browser Network Tab
1. Open browser developer tools
2. Go to Network tab
3. Try to login
4. Look for:
   - OPTIONS request (preflight)
   - POST request to /api/customers/login
   - Response headers with CORS information

## 🐛 Common Issues and Solutions

### Issue 1: CORS Preflight Failing
**Symptoms:** 400 error on OPTIONS request
**Solution:** 
- Check that CORS middleware is properly configured
- Verify origins list includes your frontend URL
- Ensure CORS middleware is added before routes

### Issue 2: Database Connection Issues
**Symptoms:** 500 error on login
**Solution:**
- Check MongoDB is running
- Verify MONGO_URI in environment variables
- Test database connection endpoint

### Issue 3: Flask-PyMongo in FastAPI Context
**Symptoms:** Import errors or database not found
**Solution:**
- Initialize Flask components properly
- Use the init_fastapi_components() function

### Issue 4: Frontend Origin Mismatch
**Symptoms:** CORS error despite correct configuration
**Solution:**
- Check what origin the frontend is actually using
- Add the correct origin to the allowed origins list
- Test with different origin variations

## 📋 Testing Checklist

### Backend Tests
- [ ] Server starts without errors
- [ ] Health endpoint responds (204)
- [ ] CORS debug endpoint works
- [ ] Database connection test passes
- [ ] Login endpoint accepts requests
- [ ] API documentation available at /docs

### Frontend Tests
- [ ] Frontend loads without console errors
- [ ] Login form submits without CORS errors
- [ ] Network tab shows successful requests
- [ ] Login response contains token

### Integration Tests
- [ ] Register new user
- [ ] Login with registered user
- [ ] Access protected endpoints with token
- [ ] Logout functionality works

## 🔍 Debug Information

### Server Logs
Look for these messages when starting the server:
```
Initializing FastAPI components
FastAPI components initialized successfully
```

### Database Logs
Check for MongoDB connection messages:
```
MONGO_URI: mongodb://localhost:27017/your_database
```

### CORS Headers
Expected response headers:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

## 🆘 Emergency Fixes

### If CORS Still Fails
1. Temporarily allow all origins:
```python
origins = ["*"]
```

2. Add more specific headers:
```python
allow_headers=["*", "Authorization", "Content-Type"]
```

### If Database Connection Fails
1. Check MongoDB is running:
```bash
mongosh
```

2. Test connection manually:
```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client.your_database
print(db.list_collection_names())
```

### If Login Still Fails
1. Check if customer exists in database
2. Verify password hashing is working
3. Test token generation
4. Check JWT secret key

## 📞 Next Steps

If the issue persists after following this guide:

1. **Run all test scripts** and share the output
2. **Check server logs** for error messages
3. **Verify environment variables** are set correctly
4. **Test with a simple curl command** to isolate the issue
5. **Check browser console** for additional error details

## 🎯 Expected Behavior After Fix

1. **CORS Preflight:** OPTIONS request returns 200 with proper headers
2. **Login Request:** POST request to /api/customers/login works
3. **Response:** JSON with token and customer_id
4. **Frontend:** Login form submits successfully and redirects to dashboard 