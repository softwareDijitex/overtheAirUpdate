# Customer Management System

A full-stack web application for customer management with file upload capabilities, version control, and role-based access.

## Features

### Backend (Flask + MongoDB + Azure Blob Storage)

- Customer registration and authentication with unique customer ID generation
- JWT-based authentication with role-based access (Customer/Admin)
- File upload with version control (max 2MB per file)
- Azure Blob Storage integration for file storage
- MongoDB for customer and file metadata persistence
- Secure password hashing with bcrypt
- Input validation and sanitization
- CORS support for frontend integration

### Frontend (React + Bootstrap)

- Responsive design that works on desktop and mobile devices
- Customer registration and login interface
- Admin login with separate dashboard
- File upload with drag-and-drop support
- File version history viewing and management
- File download functionality
- Customer dashboard with personal file management
- Admin dashboard with comprehensive customer and file overview
- Modern UI with Bootstrap components

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- MongoDB instance (local or cloud)
- Azure Storage Account with Blob Storage
- Git

## Project Structure

```
cursor/
├── app/                          # Backend application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration management
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── customer.py          # Customer model with authentication
│   │   └── file.py              # File model with version control
│   ├── routes/                  # API routes
│   │   ├── __init__.py
│   │   ├── customer_routes.py   # Customer and admin routes
│   │   └── file_routes.py       # File management routes
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── auth.py              # JWT authentication utilities
├── frontend/                    # React frontend application
│   ├── public/
│   │   └── index.html           # Main HTML file
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── AdminDashboard.js    # Admin interface
│   │   │   ├── AdminLogin.js        # Admin login
│   │   │   ├── CustomerDashboard.js # Customer interface
│   │   │   ├── Login.js             # Customer login
│   │   │   ├── Navbar.js            # Navigation bar
│   │   │   └── Register.js          # Customer registration
│   │   ├── contexts/
│   │   │   └── AuthContext.js       # Authentication context
│   │   ├── App.js               # Main React component
│   │   ├── index.js             # React entry point
│   │   └── index.css            # Global styles
│   └── package.json             # Frontend dependencies
├── app.py                       # Main Flask application
├── requirements.txt             # Python dependencies
├── config.env.example           # Environment variables template
├── setup.sh                     # Automated setup script
└── README.md                    # This file
```

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**

   ```bash
   ./setup.sh
   ```

2. **Configure environment variables:**

   ```bash
   cp config.env.example config.env
   # Edit config.env with your credentials
   ```

3. **Start the application:**

   ```bash
   # Terminal 1 - Start backend
   python app.py

   # Terminal 2 - Start frontend
   cd frontend
   npm start
   ```

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to project directory:**

   ```bash
   cd cursor
   ```

2. **Create and activate virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp config.env.example config.env
   ```

5. **Edit `config.env` with your actual values:**

   ```env
   # Azure Cosmos DB for MongoDB
   MONGO_URI=mongodb://localhost:27017/customer_management
   DB_NAME=customer_management

   # Azure Blob Storage
   AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string_here
   AZURE_STORAGE_CONTAINER_NAME=your_storage_container_name_here

   # JWT Secret Key for signing tokens
   SECRET_KEY=your_very_secret_and_secure_key_please_change_this

   # Application settings
   MAX_FILE_SIZE_MB=10
   ```

6. **Start the backend server:**
   source venv/bin/activate

   ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

## API Documentation

### Authentication Endpoints

#### Customer Registration

```http
POST /api/customers/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "password": "securepassword"
}
```

#### Customer Login

```http
POST /api/customers/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Admin Login

```http
POST /api/customers/admin/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### Customer Management Endpoints

#### Get All Customers (Admin Only)

```http
GET /api/customers/
Authorization: Bearer <admin_token>
```

#### Get Customer Details

```http
GET /api/customers/<customer_id>
Authorization: Bearer <token>
```

#### Get Current Customer Profile

```http
GET /api/customers/profile
Authorization: Bearer <customer_token>
```

### File Management Endpoints

#### Upload File

```http
POST /api/files/upload
Authorization: Bearer <customer_token>
Content-Type: multipart/form-data

file: <file_data>
```

#### Download File

```http
GET /api/files/download/<customer_id>/<filename>/<version>
Authorization: Bearer <token>
```

#### Get File Versions

```http
GET /api/files/versions/<customer_id>/<filename>
Authorization: Bearer <token>
```

#### Get Customer Files

```http
GET /api/files/customer/<customer_id>
Authorization: Bearer <token>
```

#### Get Current Customer's Files

```http
GET /api/files/my-files
Authorization: Bearer <customer_token>
```

#### Get All Files (Admin Only)

```http
GET /api/files/all
Authorization: Bearer <admin_token>
```

## Usage Guide

### Customer Flow

1. **Registration:**

   - Navigate to `/register`
   - Fill in all required fields (name, email, phone, address, password)
   - Submit to create account

2. **Login:**

   - Navigate to `/login`
   - Enter email and password
   - Access customer dashboard

3. **File Management:**
   - Upload files (max 2MB each)
   - View uploaded files with version information
   - Download latest or specific versions
   - View version history for each file

### Admin Flow

1. **Admin Login:**

   - Navigate to `/admin/login`
   - Use default credentials: `admin@example.com` / `admin123`
   - Access admin dashboard

2. **Customer Management:**

   - View all registered customers
   - See customer details and registration dates
   - Access customer files

3. **File Overview:**
   - View all files across all customers
   - Download any customer's files
   - Monitor system usage

## Default Credentials

### Admin Account

- **Email:** `admin@example.com`
- **Password:** `admin123`

## Security Features

- **Password Security:** Bcrypt hashing for all passwords
- **JWT Authentication:** Secure token-based authentication
- **Role-Based Access:** Separate permissions for customers and admins
- **Input Validation:** Server-side validation for all inputs
- **File Security:** Size limits and type validation
- **CORS Protection:** Configured for secure cross-origin requests

## Configuration Options

### Environment Variables

| Variable                          | Description               | Default  |
| --------------------------------- | ------------------------- | -------- |
| `MONGO_URI`                       | MongoDB connection string | Required |
| `DB_NAME`                         | Database name             | Required |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection  | Required |
| `AZURE_STORAGE_CONTAINER_NAME`    | Azure container name      | Required |
| `SECRET_KEY`                      | JWT secret key            | Required |
| `MAX_FILE_SIZE_MB`                | Maximum file size in MB   | 2        |

### File Upload Limits

- **Maximum file size:** 2MB per file
- **Supported formats:** All file types
- **Version control:** Automatic versioning for duplicate filenames
- **Storage:** Azure Blob Storage with organized folder structure

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error:**

   ```
   Solution: Verify MongoDB is running and connection string is correct
   ```

2. **Azure Storage Error:**

   ```
   Solution: Check Azure Storage credentials and container exists
   ```

3. **CORS Error:**

   ```
   Solution: Backend includes CORS configuration for development
   ```

4. **File Upload Failure:**

   ```
   Solution: Check file size (max 2MB) and Azure Storage permissions
   ```

5. **JWT Token Expired:**
   ```
   Solution: Tokens expire after 24 hours, re-login required
   ```

### Development Commands

```bash
# Backend development
python app.py

# Frontend development
cd frontend
npm start

# Install new Python dependencies
pip install package_name
pip freeze > requirements.txt

# Install new Node.js dependencies
cd frontend
npm install package_name
```

## Technologies Used

### Backend Stack

- **Flask 3.1.1** - Web framework
- **PyMongo 4.13.2** - MongoDB driver
- **Flask-Bcrypt 1.0.1** - Password hashing
- **PyJWT 2.10.1** - JWT token management
- **Azure Storage Blob 12.25.1** - Cloud file storage
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **python-dotenv 1.1.0** - Environment variable management

### Frontend Stack

- **React 18.2.0** - UI library
- **React Router DOM 6.3.0** - Client-side routing
- **Axios 1.4.0** - HTTP client
- **Bootstrap 5.3.0** - CSS framework
- **React Bootstrap 2.8.0** - Bootstrap components for React

## License

This project is created for educational and demonstration purposes.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure environment variables are correctly configured
4. Check console logs for detailed error messages

✅ Running on http://localhost:5001
✅ Frontend: Running on http://localhost:3000

Email: admin@example.com
Password: admin123

generate deployable flask
zip -r flask-backend.zip app main.py requirements.txt frontendapp

deployment
az login
az webapp deploy --resource-group on-the-fly-update --name onTheFlyUpdate --src-path flask-backend.zip --type zip
