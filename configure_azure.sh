#!/bin/bash

echo "🔧 Azure Storage Configuration"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to update config value
update_config() {
    local key=$1
    local value=$2
    local file="config.env"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
    else
        # Linux
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    fi
}

print_status "This script will help you configure Azure Storage credentials."
echo ""

# Get Azure Storage Account Name
read -p "Enter your Azure Storage Account Name: " account_name
if [ -z "$account_name" ]; then
    print_warning "Account name is required. Exiting..."
    exit 1
fi

# Get Azure Storage Account Key
read -s -p "Enter your Azure Storage Account Key: " account_key
echo ""
if [ -z "$account_key" ]; then
    print_warning "Account key is required. Exiting..."
    exit 1
fi

# Get Container Name
read -p "Enter your Azure Storage Container Name: " container_name
if [ -z "$container_name" ]; then
    print_warning "Container name is required. Exiting..."
    exit 1
fi

# Build the connection string
connection_string="DefaultEndpointsProtocol=https;AccountName=${account_name};AccountKey=${account_key};EndpointSuffix=core.windows.net"

print_status "Updating config.env with Azure Storage credentials..."

# Update the configuration
update_config "AZURE_STORAGE_CONNECTION_STRING" "$connection_string"
update_config "AZURE_STORAGE_CONTAINER_NAME" "$container_name"

print_success "Azure Storage configuration updated!"
echo ""
print_status "Configuration details:"
echo "  Account Name: $account_name"
echo "  Container Name: $container_name"
echo "  Connection String: [HIDDEN]"
echo ""
print_status "You can now start the backend server with: ./start_backend.sh" 