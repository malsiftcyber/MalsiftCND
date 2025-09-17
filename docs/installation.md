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
   docker-compose up -d
   ```

5. **Verify installation**:
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Installation

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev postgresql redis-server nmap masscan
   
   # CentOS/RHEL
   sudo yum install python3.11 python3.11-devel postgresql-server redis nmap masscan
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

**Database connection failed**:
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**Redis connection failed**:
- Verify Redis is running
- Check Redis URL in `.env`
- Test connection: `redis-cli ping`

**Scanner not found**:
- Install nmap: `sudo apt install nmap`
- Install masscan: `sudo apt install masscan`
- Verify PATH includes scanner binaries

**SSL certificate issues**:
- Check certificate file paths
- Verify certificate validity
- Ensure proper file permissions

### Logs

View application logs:
```bash
# Docker
docker-compose logs -f app

# Manual installation
tail -f logs/malsift.log
```

### Support

For installation issues:
- Check the [troubleshooting section](troubleshooting.md)
- Review logs for error messages
- Contact support@malsift.com
