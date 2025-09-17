#!/bin/bash

# MalsiftCND Setup Script
# This script helps set up MalsiftCND for development and testing

set -e

echo "MalsiftCND Setup Script"
echo "======================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root for security reasons"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies
install_dependencies() {
    echo "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3.11-dev \
                postgresql postgresql-contrib redis-server nmap masscan \
                build-essential libssl-dev libffi-dev curl wget git
        elif command_exists yum; then
            sudo yum update -y
            sudo yum install -y python3.11 python3.11-devel postgresql-server \
                redis nmap masscan gcc openssl-devel libffi-devel curl wget git
        else
            echo "Unsupported package manager. Please install dependencies manually."
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command_exists brew; then
            brew install python@3.11 postgresql redis nmap masscan
        else
            echo "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    fi
}

# Setup PostgreSQL
setup_postgresql() {
    echo "Setting up PostgreSQL..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
        # Create database and user
        sudo -u postgres psql -c "CREATE DATABASE malsift;" || true
        sudo -u postgres psql -c "CREATE USER malsift WITH PASSWORD 'malsift';" || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;" || true
    elif [[ "$OS" == "macos" ]]; then
        brew services start postgresql
        
        # Create database and user
        createdb malsift 2>/dev/null || true
        psql -d postgres -c "CREATE USER malsift WITH PASSWORD 'malsift';" 2>/dev/null || true
        psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;" 2>/dev/null || true
    fi
}

# Setup Redis
setup_redis() {
    echo "Setting up Redis..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo systemctl start redis
        sudo systemctl enable redis
    elif [[ "$OS" == "macos" ]]; then
        brew services start redis
    fi
}

# Setup Python environment
setup_python() {
    echo "Setting up Python environment..."
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
}

# Setup environment file
setup_env() {
    echo "Setting up environment configuration..."
    
    if [[ ! -f .env ]]; then
        cp env.example .env
        
        # Generate secret keys
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        
        # Update .env file
        sed -i.bak "s/your-secret-key-here-must-be-at-least-32-characters-long/$SECRET_KEY/" .env
        sed -i.bak "s/your-jwt-secret-key-here-must-be-at-least-32-characters-long/$JWT_SECRET_KEY/" .env
        
        echo "Environment file created with generated secret keys"
    else
        echo "Environment file already exists, skipping..."
    fi
}

# Create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    
    mkdir -p data logs certs
    chmod 755 data logs certs
}

# Initialize database
init_database() {
    echo "Initializing database..."
    
    source venv/bin/activate
    python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
print('Database initialized successfully')
"
}

# Main setup function
main() {
    echo "Starting MalsiftCND setup..."
    
    # Check if we're in the right directory
    if [[ ! -f "requirements.txt" ]]; then
        echo "Please run this script from the MalsiftCND root directory"
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup services
    setup_postgresql
    setup_redis
    
    # Setup Python environment
    setup_python
    
    # Setup configuration
    setup_env
    create_directories
    
    # Initialize database
    init_database
    
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Start the application: uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo "3. Access web interface: http://localhost:8000"
    echo "4. Create admin user via API or web interface"
    echo ""
    echo "For production deployment, see docs/enterprise-deployment.md"
}

# Run main function
main "$@"
