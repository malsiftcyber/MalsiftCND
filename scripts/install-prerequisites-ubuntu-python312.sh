#!/bin/bash
# MalsiftCND Prerequisites Installation Script for Ubuntu 24.04 LTS
# This version uses Python 3.12 (default in Ubuntu 24.04) instead of Python 3.11

set -e

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user is root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to check sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges. Please run with sudo access."
        exit 1
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System packages updated"
}

# Function to install Docker
install_docker() {
    if command_exists docker; then
        print_warning "Docker is already installed"
        docker --version
        return
    fi

    print_status "Installing Docker..."
    
    # Install required packages
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    # Enable Docker to start on boot
    sudo systemctl enable docker
    sudo systemctl start docker
    
    print_success "Docker installed successfully"
    print_warning "You need to logout and login again for Docker group membership to take effect"
}

# Function to install Python 3.12 (default in Ubuntu 24.04)
install_python() {
    if command_exists python3.12; then
        print_warning "Python 3.12 is already installed"
        python3.12 --version
        return
    fi

    print_status "Installing Python 3.12..."
    
    # Install Python 3.12 and related packages (default in Ubuntu 24.04)
    sudo apt install -y python3.12 python3.12-venv python3.12-dev python3.12-pip python3.12-distutils
    sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
    
    # Create symlinks for easier access
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
    
    print_success "Python 3.12 installed successfully"
    print_warning "Note: This script uses Python 3.12 instead of Python 3.11. You may need to update requirements.txt"
}

# Function to install PostgreSQL
install_postgresql() {
    if command_exists psql; then
        print_warning "PostgreSQL is already installed"
        psql --version
        return
    fi

    print_status "Installing PostgreSQL..."
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    
    # Start and enable PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    print_success "PostgreSQL installed successfully"
}

# Function to install Redis
install_redis() {
    if command_exists redis-cli; then
        print_warning "Redis is already installed"
        redis-cli --version
        return
    fi

    print_status "Installing Redis..."
    sudo apt install -y redis-server redis-tools
    
    # Start and enable Redis
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    print_success "Redis installed successfully"
}

# Function to install network scanning tools
install_network_tools() {
    print_status "Installing network scanning tools..."
    sudo apt install -y nmap masscan
    
    print_success "Network scanning tools installed successfully"
}

# Function to install additional dependencies
install_additional_deps() {
    print_status "Installing additional dependencies..."
    sudo apt install -y git curl wget openssl ca-certificates htop iotop
    
    print_success "Additional dependencies installed successfully"
}

# Function to verify installations
verify_installations() {
    print_status "Verifying installations..."
    
    echo "Docker:"
    if command_exists docker; then
        docker --version
    else
        print_error "Docker not found"
    fi
    
    echo "Docker Compose Plugin:"
    if docker compose version >/dev/null 2>&1; then
        docker compose version
    else
        print_warning "Docker Compose plugin not available"
    fi
    
    echo "Docker Compose Standalone:"
    if command_exists docker-compose; then
        docker-compose --version
    else
        print_warning "Docker Compose standalone not found"
    fi
    
    echo "Python 3.12:"
    if command_exists python3.12; then
        python3.12 --version
    else
        print_error "Python 3.12 not found"
    fi
    
    echo "PostgreSQL:"
    if command_exists psql; then
        psql --version
    else
        print_error "PostgreSQL not found"
    fi
    
    echo "Redis:"
    if command_exists redis-cli; then
        redis-cli --version
    else
        print_error "Redis not found"
    fi
    
    echo "Nmap:"
    if command_exists nmap; then
        nmap --version
    else
        print_error "Nmap not found"
    fi
    
    echo "Masscan:"
    if command_exists masscan; then
        masscan --version
    else
        print_error "Masscan not found"
    fi
    
    print_success "Installation verification completed"
}

# Function to test Docker
test_docker() {
    print_status "Testing Docker installation..."
    if sudo docker run hello-world >/dev/null 2>&1; then
        print_success "Docker test successful"
    else
        print_error "Docker test failed"
    fi
}

# Function to test Redis
test_redis() {
    print_status "Testing Redis connection..."
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis test successful"
    else
        print_error "Redis test failed"
    fi
}

# Function to create MalsiftCND database
create_database() {
    print_status "Creating MalsiftCND database..."
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE malsift;" 2>/dev/null || print_warning "Database 'malsift' may already exist"
    sudo -u postgres psql -c "CREATE USER malsift WITH PASSWORD 'malsift';" 2>/dev/null || print_warning "User 'malsift' may already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;" 2>/dev/null || print_warning "Privileges may already be granted"
    sudo -u postgres psql -c "ALTER USER malsift CREATEDB;" 2>/dev/null || print_warning "User privileges may already be set"
    
    print_success "Database setup completed"
}

# Main installation function
main() {
    echo "=========================================="
    echo "MalsiftCND Prerequisites Installation"
    echo "Ubuntu 24.04 LTS - Python 3.12 Version"
    echo "=========================================="
    echo

    # Check prerequisites
    check_root
    check_sudo
    
    # Install components
    update_system
    install_docker
    install_python
    install_postgresql
    install_redis
    install_network_tools
    install_additional_deps
    
    # Setup database
    create_database
    
    # Verify installations
    verify_installations
    
    # Test installations
    test_docker
    test_redis
    
    echo
    echo "=========================================="
    print_success "Installation completed successfully!"
    echo "=========================================="
    echo
    echo "Next steps:"
    echo "1. Logout and login again to activate Docker group membership"
    echo "2. Clone MalsiftCND repository: git clone https://github.com/malsiftcyber/MalsiftCND.git"
    echo "3. Update requirements.txt to use Python 3.12 if needed"
    echo "4. Follow the installation guide in docs/installation.md"
    echo
    echo "For Docker group membership, you can also run:"
    echo "  newgrp docker"
    echo
    echo "To test Docker without sudo:"
    echo "  docker run hello-world"
    echo
    echo "Note: This installation uses Python 3.12 instead of Python 3.11."
    echo "You may need to update the application's requirements.txt file."
    echo
}

# Run main function
main "$@"
