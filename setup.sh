#!/bin/bash

echo "🚀 Setting up Customer Management System..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check if Node.js is installed
print_status "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed. Please install Node.js 14+ first."
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed."
    exit 1
fi
print_success "npm found: $(npm --version)"

echo ""
print_status "Setting up backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional dependencies that might be missing
# print_status "Installing additional dependencies..."
# pip install flask-cors Flask-PyMongo

print_success "Backend dependencies installed!"

echo ""
print_status "Setting up frontend..."

# Navigate to frontend directory and install dependencies
cd frontend
print_status "Installing Node.js dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed!"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

cd ..

echo ""
print_status "Configuring environment variables..."

# Create config.env if it doesn't exist
if [ ! -f "config.env" ]; then
    print_status "Creating config.env file..."
    cp config.env.example config.env
    print_success "config.env file created"
else
    print_warning "config.env already exists, skipping creation"
fi

echo ""
print_status "Setting up environment variables..."

# Function to update config value
update_config() {
    local key=$1
    local value=$2
    local file="config.env"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^${key}=.*/${key}=${value}/" "$file"
    else
        # Linux
        sed -i "s/^${key}=.*/${key}=${value}/" "$file"
    fi
}

# Update MongoDB URI to localhost
print_status "Setting MongoDB URI to localhost..."
update_config "MONGO_URI" "mongodb://localhost:27017/customer_management"
update_config "DB_NAME" "customer_management"

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
print_status "Generating secure secret key..."
update_config "SECRET_KEY" "$SECRET_KEY"

# Set Azure Storage to test values (user can update later)
print_status "Setting Azure Storage test configuration..."
update_config "AZURE_STORAGE_CONNECTION_STRING" "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
update_config "AZURE_STORAGE_CONTAINER_NAME" "test-container"

# Set FastAPI configuration
update_config "FASTAPI_APP" "app.py"
update_config "FASTAPI_ENV" "development"
update_config "MAX_FILE_SIZE_MB" "10"

print_success "Environment variables configured!"

echo ""
print_status "Creating startup scripts..."

# Create backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "Starting Customer Management System Backend..."
echo "=============================================="
source venv/bin/activate
python3 app.py
EOF

# Create frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "Starting Customer Management System Frontend..."
echo "=============================================="
cd frontend
npm start
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh

print_success "Startup scripts created!"

echo ""
print_status "Checking MongoDB availability..."

# Check if MongoDB is running
if command -v mongod &> /dev/null; then
    if pgrep -x "mongod" > /dev/null; then
        print_success "MongoDB is running"
    else
        print_warning "MongoDB is installed but not running"
        print_status "To start MongoDB:"
        echo "  - On macOS with Homebrew: brew services start mongodb-community"
        echo "  - On Linux: sudo systemctl start mongod"
        echo "  - Or run: mongod"
    fi
else
    print_warning "MongoDB is not installed"
    print_status "To install MongoDB:"
    echo "  - On macOS: brew install mongodb-community"
    echo "  - On Ubuntu: sudo apt-get install mongodb"
    echo "  - Or download from: https://www.mongodb.com/try/download/community"
fi

echo ""
print_success "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start MongoDB (if not already running)"
echo "2. Start the backend: ./start_backend.sh"
echo "3. Start the frontend: ./start_frontend.sh"
echo ""
echo "Or run both simultaneously:"
echo "  Terminal 1: ./start_backend.sh"
echo "  Terminal 2: ./start_frontend.sh"
echo ""
echo "Application URLs:"
echo "  Backend API: http://localhost:5001"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@example.com"
echo "  Password: admin123"
echo ""
echo "Note: Update config.env with your actual Azure Storage credentials for production use." 