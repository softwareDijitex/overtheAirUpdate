#!/bin/bash

echo "📝 Manual Azure Storage Configuration"
echo "====================================="

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

print_status "You can configure Azure Storage credentials in two ways:"
echo ""
echo "1. Interactive configuration (recommended):"
echo "   ./configure_azure.sh"
echo ""
echo "2. Manual editing:"
echo "   Edit config.env and update these lines:"
echo ""
echo "   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
echo "   AZURE_STORAGE_CONTAINER_NAME=YOUR_CONTAINER_NAME"
echo ""
print_status "To get your Azure Storage credentials:"
echo "1. Go to Azure Portal (https://portal.azure.com)"
echo "2. Navigate to your Storage Account"
echo "3. Go to 'Access keys' under 'Security + networking'"
echo "4. Copy the connection string or account name and key"
echo "5. Create a container in your storage account"
echo ""
print_status "Current config.env contents:"
echo "=================================="
cat config.env
echo ""
print_status "Would you like to:"
echo "1. Run interactive configuration (./configure_azure.sh)"
echo "2. Edit config.env manually"
echo "3. Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        ./configure_azure.sh
        ;;
    2)
        print_status "Opening config.env for editing..."
        if command -v nano &> /dev/null; then
            nano config.env
        elif command -v vim &> /dev/null; then
            vim config.env
        elif command -v vi &> /dev/null; then
            vi config.env
        else
            print_warning "No text editor found. Please edit config.env manually."
            print_status "You can use any text editor to open config.env"
        fi
        ;;
    3)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_warning "Invalid choice. Exiting..."
        exit 1
        ;;
esac 