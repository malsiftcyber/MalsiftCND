#!/bin/bash
# Quick Ubuntu 24.04 LTS Installation Script for MalsiftCND Prerequisites
# This is a simplified version for direct execution

set -e

echo "=========================================="
echo "MalsiftCND Prerequisites Installation"
echo "Ubuntu 24.04 LTS - Quick Version"
echo "=========================================="
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "ERROR: This script should not be run as root. Please run as a regular user with sudo privileges."
    exit 1
fi

# Check sudo privileges
if ! sudo -n true 2>/dev/null; then
    echo "ERROR: This script requires sudo privileges. Please run with sudo access."
    exit 1
fi

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Docker..."
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

echo "Installing Python 3.11..."
# Add deadsnakes PPA for Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-pip python3.11-distutils
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

echo "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Installing Redis..."
sudo apt install -y redis-server redis-tools
sudo systemctl start redis-server
sudo systemctl enable redis-server

echo "Installing network scanning tools..."
sudo apt install -y nmap masscan

echo "Installing additional dependencies..."
sudo apt install -y git curl wget openssl ca-certificates htop iotop

echo "Setting up database..."
# Create database and user
sudo -u postgres psql -c "CREATE DATABASE malsift;" 2>/dev/null || echo "Database 'malsift' may already exist"
sudo -u postgres psql -c "CREATE USER malsift WITH PASSWORD 'malsift';" 2>/dev/null || echo "User 'malsift' may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;" 2>/dev/null || echo "Privileges may already be granted"
sudo -u postgres psql -c "ALTER USER malsift CREATEDB;" 2>/dev/null || echo "User privileges may already be set"

echo "Testing installations..."
# Test Docker
if sudo docker run hello-world >/dev/null 2>&1; then
    echo "✓ Docker test successful"
else
    echo "✗ Docker test failed"
fi

# Test Redis
if redis-cli ping >/dev/null 2>&1; then
    echo "✓ Redis test successful"
else
    echo "✗ Redis test failed"
fi

echo
echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Logout and login again to activate Docker group membership"
echo "2. Clone MalsiftCND repository: git clone https://github.com/malsiftcyber/MalsiftCND.git"
echo "3. Follow the installation guide in docs/installation.md"
echo
echo "For Docker group membership, you can also run:"
echo "  newgrp docker"
echo
echo "To test Docker without sudo:"
echo "  docker run hello-world"
echo
