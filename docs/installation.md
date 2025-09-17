# Installation Guide

This guide will help you install MalsiftCND on your system.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB free space
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+), macOS 10.15+, Windows 10+

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **OS**: Linux (Ubuntu 22.04 LTS)

### Network Requirements
- Outbound internet access for AI/LLM APIs
- Network access to scan targets
- Ports 8000 (HTTP) and 443 (HTTPS) for web interface

## Installation Methods

### Docker Installation (Recommended)

#### Prerequisites Installation for Ubuntu 24.04 LTS

Before installing MalsiftCND, you need to install the required system components:

**Quick Installation (Recommended)**:

**Option 1: Direct Download**:
```bash
# Download and run the installation script
wget https://raw.githubusercontent.com/malsiftcyber/MalsiftCND/main/scripts/install-prerequisites-ubuntu.sh
chmod +x install-prerequisites-ubuntu.sh
./install-prerequisites-ubuntu.sh
```

**Option 2: Clone Repository First**:
```bash
# Clone the repository first
git clone https://github.com/malsiftcyber/MalsiftCND.git
cd MalsiftCND

# Run the installation script
./scripts/install-prerequisites-ubuntu.sh
```

**Option 3: One-liner (if repository is public)**:
```bash
# Download and run in one command
curl -fsSL https://raw.githubusercontent.com/malsiftcyber/MalsiftCND/main/scripts/install-prerequisites-ubuntu.sh | bash
```

**Option 4: Inline Script (if repository access issues)**:
```bash
# Copy and paste this script directly into your terminal
cat > install-prereqs.sh << 'EOF'
#!/bin/bash
set -e
echo "Installing MalsiftCND Prerequisites for Ubuntu 24.04 LTS..."
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install Python 3.11 (add deadsnakes PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils build-essential libssl-dev libffi-dev python3-dev python3-pip
sudo python3.11 -m ensurepip --upgrade

# Install other dependencies
sudo apt install -y postgresql postgresql-contrib redis-server redis-tools nmap masscan git curl wget openssl ca-certificates htop iotop

# Setup services
sudo usermod -aG docker $USER
sudo systemctl enable docker && sudo systemctl start docker
sudo systemctl enable postgresql && sudo systemctl start postgresql
sudo systemctl enable redis-server && sudo systemctl start redis-server

# Setup database
sudo -u postgres psql -c "CREATE DATABASE malsift;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER malsift WITH PASSWORD 'malsift';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER malsift CREATEDB;" 2>/dev/null || true

echo "Installation completed! Please logout and login again for Docker group membership."
EOF
chmod +x install-prereqs.sh && ./install-prereqs.sh
```

**Manual Installation**:

1. **Update system packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker**:
   ```bash
   # Install required packages
   sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
   
   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   
   # Add Docker repository
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   
   # Install Docker Engine
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   
   # Add current user to docker group (requires logout/login)
   sudo usermod -aG docker $USER
   
   # Enable Docker to start on boot
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

3. **Install Docker Compose (if not using plugin)**:
   ```bash
   # Install Docker Compose standalone (alternative to plugin)
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Verify installation
   docker --version
   docker-compose --version
   ```

4. **Install additional dependencies**:
   ```bash
   # Install Git (if not already installed)
   sudo apt install -y git
   
   # Install network scanning tools (for manual installation)
   sudo apt install -y nmap masscan
   
   # Install Python 3.11 (for manual installation)
   sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-pip
   
   # Install PostgreSQL client tools (for manual installation)
   sudo apt install -y postgresql-client
   
   # Install Redis tools (for manual installation)
   sudo apt install -y redis-tools
   ```

5. **Verify Docker installation**:
   ```bash
   # Test Docker installation
   sudo docker run hello-world
   
   # Test Docker Compose (if using plugin)
   docker compose version
   
   # Test Docker Compose (if using standalone)
   docker-compose --version
   ```

#### MalsiftCND Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/malsiftcyber/MalsiftCND.git
   cd MalsiftCND
   ```

2. **Copy environment file**:
   ```bash
   cp env.example .env
   ```

3. **Edit configuration**:
   ```bash
   nano .env
   ```
   Update the following required settings:
   - `SECRET_KEY`: Generate a secure random key (32+ characters)
   - `JWT_SECRET_KEY`: Generate another secure random key (32+ characters)
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string

4. **Start services**:
   ```bash
   # Using Docker Compose plugin (recommended)
   docker compose up -d
   
   # Or using standalone docker-compose
   docker-compose up -d
   ```

5. **Verify installation**:
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Installation

#### Ubuntu 24.04 LTS Manual Installation

1. **Update system packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python 3.11 and development tools**:
   ```bash
   # Add deadsnakes PPA for Python 3.11
   sudo apt install -y software-properties-common
   sudo add-apt-repository -y ppa:deadsnakes/ppa
   sudo apt update
   
   # Install Python 3.11 and development tools
   sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
   sudo apt install -y build-essential libssl-dev libffi-dev python3-dev python3-pip
   
   # Install pip for Python 3.11
   sudo python3.11 -m ensurepip --upgrade
   
   # Create symlinks for easier access
   sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
   sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
   ```

3. **Install PostgreSQL**:
   ```bash
   # Install PostgreSQL
   sudo apt install -y postgresql postgresql-contrib postgresql-client
   
   # Start and enable PostgreSQL
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # Create database and user
   sudo -u postgres psql -c "CREATE DATABASE malsift;"
   sudo -u postgres psql -c "CREATE USER malsift WITH PASSWORD 'malsift';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;"
   sudo -u postgres psql -c "ALTER USER malsift CREATEDB;"
   ```

4. **Install Redis**:
   ```bash
   # Install Redis
   sudo apt install -y redis-server redis-tools
   
   # Start and enable Redis
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   
   # Test Redis connection
   redis-cli ping
   ```

5. **Install network scanning tools**:
   ```bash
   # Install Nmap and Masscan
   sudo apt install -y nmap masscan
   
   # Verify installation
   nmap --version
   masscan --version
   ```

6. **Install additional system dependencies**:
   ```bash
   # Install Git
   sudo apt install -y git
   
   # Install curl and wget
   sudo apt install -y curl wget
   
   # Install SSL/TLS tools
   sudo apt install -y openssl ca-certificates
   
   # Install process monitoring tools
   sudo apt install -y htop iotop
   ```

#### Other Linux Distributions

**CentOS/RHEL 8+**:
```bash
# Install EPEL repository
sudo yum install -y epel-release

# Install Python 3.11
sudo yum install -y python3.11 python3.11-devel python3.11-pip

# Install PostgreSQL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis

# Install network tools
sudo yum install -y nmap masscan

# Install development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel libffi-devel
```

**Debian 11+**:
```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-pip

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install network tools
sudo apt install -y nmap masscan

# Install development tools
sudo apt install -y build-essential libssl-dev libffi-dev
```

2. **Create virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**:
   ```bash
   # Create PostgreSQL database
   sudo -u postgres createdb malsift
   sudo -u postgres createuser malsift
   sudo -u postgres psql -c "ALTER USER malsift PASSWORD 'malsift';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE malsift TO malsift;"
   ```

5. **Initialize database**:
   ```bash
   python -m app.core.database init_db
   ```

6. **Start Redis**:
   ```bash
   sudo systemctl start redis
   sudo systemctl enable redis
   ```

7. **Run application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

#### Required Settings
- `SECRET_KEY`: Application secret key (32+ characters)
- `JWT_SECRET_KEY`: JWT signing key (32+ characters)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

#### Optional Settings
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `SSL_KEYFILE`: Path to SSL private key
- `SSL_CERTFILE`: Path to SSL certificate

#### AI/LLM Integration
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `GROQ_API_KEY`: Groq API key for Llama models

#### External Integrations
- `RUNZERO_API_KEY`: RunZero API key
- `TANIUM_API_KEY`: Tanium API key
- `ARMIS_API_KEY`: Armis API key
- `AD_SERVER`: Active Directory server
- `AZURE_CLIENT_ID`: Azure AD client ID

### SSL/TLS Configuration

#### LetEncrypt (Recommended)
```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Update .env
SSL_KEYFILE=/etc/letsencrypt/live/your-domain.com/privkey.pem
SSL_CERTFILE=/etc/letsencrypt/live/your-domain.com/fullchain.pem
```

#### Enterprise Certificates
```bash
# Copy certificates to certs directory
cp your-private-key.pem certs/
cp your-certificate.pem certs/

# Update .env
SSL_KEYFILE=./certs/your-private-key.pem
SSL_CERTFILE=./certs/your-certificate.pem
```

## Post-Installation

1. **Create admin user**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/users \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "email": "admin@yourcompany.com",
       "password": "secure-password",
       "is_admin": true
     }'
   ```

2. **Access web interface**:
   - Open browser to `http://localhost:8000` (or your domain)
   - Login with admin credentials
   - Configure integrations and scanning settings

3. **Verify functionality**:
   - Run a test scan
   - Check AI analysis is working
   - Verify external integrations

## Troubleshooting

### Common Issues

**Docker not found**:
- Install Docker: Follow the prerequisites installation section above
- Verify Docker is running: `sudo systemctl status docker`
- Add user to docker group: `sudo usermod -aG docker $USER` (requires logout/login)

**Docker Compose not found**:
- Install Docker Compose plugin: `sudo apt install docker-compose-plugin`
- Or install standalone: Follow the Docker Compose installation section above
- Verify installation: `docker compose version` or `docker-compose --version`

**404 Error when downloading installation script**:
- The repository might be private or not yet public
- Use Option 2: Clone the repository first, then run the script locally
- Use Option 4: Copy the inline script directly into your terminal
- Check if the repository URL is correct: `https://github.com/malsiftcyber/MalsiftCND`

**Python 3.11 package not found**:
- Ubuntu 24.04 LTS doesn't include Python 3.11 in default repositories
- Add deadsnakes PPA: `sudo add-apt-repository -y ppa:deadsnakes/ppa`
- Update package list: `sudo apt update`
- Then install: `sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-pip`
- Alternative: Use Python 3.12 (default in Ubuntu 24.04) by changing requirements.txt

**Permission denied for Docker**:
- Add user to docker group: `sudo usermod -aG docker $USER`
- Logout and login again, or run: `newgrp docker`
- Test without sudo: `docker run hello-world`

**Database connection failed**:
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in `.env`
- Ensure database exists: `sudo -u postgres psql -l`
- Test connection: `psql -h localhost -U malsift -d malsift`

**Redis connection failed**:
- Verify Redis is running: `sudo systemctl status redis-server`
- Check Redis URL in `.env`
- Test connection: `redis-cli ping`
- Check Redis logs: `sudo journalctl -u redis-server`

**Scanner not found**:
- Install nmap: `sudo apt install nmap`
- Install masscan: `sudo apt install masscan`
- Verify PATH includes scanner binaries: `which nmap masscan`
- Test scanners: `nmap --version` and `masscan --version`

**SSL certificate issues**:
- Check certificate file paths in `.env`
- Verify certificate validity: `openssl x509 -in cert.pem -text -noout`
- Ensure proper file permissions: `chmod 600 private-key.pem`
- Test SSL: `openssl s_client -connect your-domain.com:443`

**Port already in use**:
- Check what's using port 8000: `sudo lsof -i :8000`
- Stop conflicting service or change port in `.env`
- For Docker: `docker compose down` then `docker compose up -d`

**Out of disk space**:
- Check disk usage: `df -h`
- Clean Docker: `docker system prune -a`
- Clean logs: `sudo journalctl --vacuum-time=7d`

### Logs

View application logs:
```bash
# Docker (using plugin)
docker compose logs -f app

# Docker (using standalone)
docker-compose logs -f app

# Manual installation
tail -f logs/malsift.log

# System logs
sudo journalctl -u docker -f
sudo journalctl -u postgresql -f
sudo journalctl -u redis-server -f
```

### Support

For installation issues:
- Check the [troubleshooting section](troubleshooting.md)
- Review logs for error messages
- Contact support@malsift.com
