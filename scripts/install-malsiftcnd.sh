#!/bin/bash
# MalsiftCND Unified Installation Script
# This script handles complete installation including prerequisites, configuration, and admin user creation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
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

print_header() {
    echo -e "\n${CYAN}==========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}==========================================${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check sudo availability
check_sudo() {
    if ! command_exists sudo; then
        print_error "This script requires sudo. Please install sudo first."
        exit 1
    fi
    # Prompt for sudo password if needed
    sudo -v
}

# Detect docker compose command (with fallback to sudo if needed)
detect_docker_compose() {
    # Try docker compose plugin first
    if docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
        DOCKER_SUDO=""
        print_success "Using Docker Compose plugin"
        return 0
    elif sudo docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
        DOCKER_SUDO="sudo"
        print_warning "Using Docker Compose plugin with sudo (user may need to logout/login)"
        return 0
    # Try docker-compose standalone
    elif command_exists docker-compose && docker-compose --version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
        DOCKER_SUDO=""
        print_success "Using Docker Compose standalone"
        return 0
    elif command_exists docker-compose && sudo docker-compose --version >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
        DOCKER_SUDO="sudo"
        print_warning "Using Docker Compose standalone with sudo (user may need to logout/login)"
        return 0
    else
        DOCKER_COMPOSE_CMD=""
        DOCKER_SUDO=""
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing=0
    
    if ! command_exists docker; then
        print_warning "Docker is not installed"
        missing=$((missing + 1))
    else
        print_success "Docker is installed: $(docker --version)"
    fi
    
    if ! detect_docker_compose; then
        print_warning "Docker Compose is not installed"
        missing=$((missing + 1))
    fi
    
    if [ $missing -gt 0 ]; then
        print_error "Some prerequisites are missing. Would you like to install them now? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "[DEBUG] About to call install_prerequisites..."
            install_prerequisites
            local install_exit_code=$?
            echo "[DEBUG] install_prerequisites returned with exit code: $install_exit_code"
            
            if [ $install_exit_code -ne 0 ]; then
                print_error "Prerequisites installation failed with exit code $install_exit_code"
                exit 1
            fi
            
            # Re-check after installation - wait a moment for services to settle
            print_status "Prerequisites installation completed. Re-checking Docker Compose availability..."
            sleep 3
            
            if ! detect_docker_compose; then
                print_warning "Docker Compose detection failed. Docker may require logout/login."
                print_status "Attempting to continue with sudo if needed..."
                # Try to detect with sudo as fallback
                if sudo docker compose version >/dev/null 2>&1 || sudo docker-compose --version >/dev/null 2>&1; then
                    print_warning "Docker works with sudo. Script will use sudo for Docker commands."
                    if sudo docker compose version >/dev/null 2>&1; then
                        DOCKER_COMPOSE_CMD="docker compose"
                        DOCKER_SUDO="sudo"
                        print_success "Using Docker Compose plugin with sudo"
                    elif sudo docker-compose --version >/dev/null 2>&1; then
                        DOCKER_COMPOSE_CMD="docker-compose"
                        DOCKER_SUDO="sudo"
                        print_success "Using Docker Compose standalone with sudo"
                    fi
                else
                    print_error "Docker Compose is still not available. Please logout/login and rerun this script."
                    print_error "Or install Docker Compose manually."
                    exit 1
                fi
            else
                print_success "Docker Compose detected successfully"
                # Check if Docker actually works without sudo - if not, use sudo
                if ! docker ps >/dev/null 2>&1; then
                    if sudo docker ps >/dev/null 2>&1; then
                        print_warning "Docker requires sudo. Setting DOCKER_SUDO=sudo"
                        DOCKER_SUDO="sudo"
                    fi
                fi
            fi
            echo "[DEBUG] Finished re-checking Docker Compose, continuing..."
        else
            print_error "Please install missing prerequisites and run this script again."
            exit 1
        fi
    fi
    
    # Ensure Docker Compose command is set
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        print_status "Ensuring Docker Compose command is set..."
        if ! detect_docker_compose; then
            print_error "Docker Compose detection failed. Cannot proceed."
            exit 1
        fi
    fi
    
    print_success "All prerequisites are available"
}

# Install prerequisites
install_prerequisites() {
    print_header "Installing Prerequisites"
    
    if [ -f "scripts/install-prerequisites-ubuntu.sh" ]; then
        print_status "Running prerequisites installation script..."
        
        # Run the script and capture output
        if bash scripts/install-prerequisites-ubuntu.sh; then
            local prereq_exit_code=0
        else
            local prereq_exit_code=$?
            print_error "Prerequisites script exited with code $prereq_exit_code"
            return $prereq_exit_code
        fi
        
        print_status "Prerequisites script finished. Continuing with post-installation steps..."
        echo "[DEBUG] Post-installation step 1: Checking docker group..."
        
        # Add user to docker group if not already added
        if ! groups | grep -q docker; then
            print_status "Adding user to docker group..."
            sudo usermod -aG docker $USER
            print_warning "User added to docker group."
            print_status "Note: Group membership takes effect after logout/login."
            print_status "For this installation, Docker commands will use sudo temporarily."
            print_status "After logout/login, Docker will work without sudo (as intended)."
            # Don't use newgrp here as it creates a subshell that exits immediately
        else
            # User is already in docker group, but may need logout/login
            print_status "User is already in docker group."
            if ! docker ps >/dev/null 2>&1; then
                print_warning "Docker group membership not active in current session."
                print_status "This is normal - group changes require logout/login."
                print_status "Using sudo temporarily for this installation."
            fi
        fi
        echo "[DEBUG] Post-installation step 2: Waiting for Docker..."
        
        # Wait a moment for Docker to be available
        sleep 2
        
        # Verify Docker is working
        echo "[DEBUG] Post-installation step 3: Verifying Docker..."
        if ! docker ps >/dev/null 2>&1; then
            print_warning "Docker may not be accessible yet. Trying with sudo..."
            if sudo docker ps >/dev/null 2>&1; then
                print_warning "Docker works with sudo. You may need to logout/login for user access."
                print_status "For now, Docker commands will work. Continuing installation..."
            else
                print_error "Docker is not working. Please ensure Docker service is running:"
                echo "  sudo systemctl start docker"
                echo "  sudo systemctl enable docker"
                return 1
            fi
        fi
        
        echo "[DEBUG] Post-installation step 4: Success!"
        print_success "Prerequisites installation completed"
        return 0
    else
        print_error "Prerequisites script not found. Please run install-prerequisites-ubuntu.sh first."
        return 1
    fi
}

# Generate random secret
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Setup environment file
setup_env() {
    print_header "Configuring Environment"
    
    if [ -f .env ]; then
        print_warning ".env file already exists. Overwrite? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_status "Using existing .env file"
            return
        fi
    fi
    
    print_status "Creating .env file from template..."
    cp env.example .env
    
    # Generate secret keys
    print_status "Generating secure secret keys..."
    SECRET_KEY=$(generate_secret)
    JWT_SECRET_KEY=$(generate_secret)
    
    # Update .env with generated keys
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-must-be-at-least-32-characters-long/$SECRET_KEY/" .env
        sed -i '' "s/your-jwt-secret-key-here-must-be-at-least-32-characters-long/$JWT_SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-must-be-at-least-32-characters-long/$SECRET_KEY/" .env
        sed -i "s/your-jwt-secret-key-here-must-be-at-least-32-characters-long/$JWT_SECRET_KEY/" .env
    fi
    
    print_success "Secret keys generated and saved to .env"
    
    # Ask about optional configuration
    echo ""
    print_status "Optional Configuration (press Enter to skip)"
    
    read -p "Enable DEBUG mode? (y/n) [n]: " debug_response
    if [[ "$debug_response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/DEBUG=false/DEBUG=true/" .env
        else
            sed -i "s/DEBUG=false/DEBUG=true/" .env
        fi
        print_success "DEBUG mode enabled"
    fi
    
    read -p "Custom database password? (press Enter for default 'malsift'): " db_password
    if [ -n "$db_password" ]; then
        # Update docker-compose.yml with custom password
        print_status "Updating docker-compose.yml with custom database password..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/POSTGRES_PASSWORD=malsift/POSTGRES_PASSWORD=$db_password/" docker-compose.yml
            sed -i '' "s|postgresql://malsift:malsift@|postgresql://malsift:$db_password@|" .env
        else
            sed -i "s/POSTGRES_PASSWORD=malsift/POSTGRES_PASSWORD=$db_password/" docker-compose.yml
            sed -i "s|postgresql://malsift:malsift@|postgresql://malsift:$db_password@|" .env
        fi
    fi
}

# Prompt for admin user
prompt_admin_user() {
    print_header "Admin User Configuration"
    
    echo "Please provide details for the initial admin user:"
    echo ""
    
    read -p "Admin username [admin]: " admin_username
    admin_username=${admin_username:-admin}
    
    read -p "Admin email: " admin_email
    while [ -z "$admin_email" ]; do
        print_error "Email is required"
        read -p "Admin email: " admin_email
    done
    
    read -sp "Admin password (min 8 chars, max 72 chars): " admin_password
    echo ""
    while [ ${#admin_password} -lt 8 ]; do
        print_error "Password must be at least 8 characters"
        read -sp "Admin password (min 8 chars, max 72 chars): " admin_password
        echo ""
    done
    
    # Check password length in bytes (bcrypt limit is 72 bytes)
    password_bytes=$(echo -n "$admin_password" | wc -c)
    if [ $password_bytes -gt 72 ]; then
        print_warning "Password exceeds 72 bytes (bcrypt limit). It will be truncated."
        print_warning "Consider using a shorter password for better compatibility."
    fi
    
    read -sp "Confirm admin password: " admin_password_confirm
    echo ""
    while [ "$admin_password" != "$admin_password_confirm" ]; do
        print_error "Passwords do not match"
        read -sp "Admin password (min 8 chars): " admin_password
        echo ""
        read -sp "Confirm admin password: " admin_password_confirm
        echo ""
    done
    
    ADMIN_USERNAME="$admin_username"
    ADMIN_EMAIL="$admin_email"
    ADMIN_PASSWORD="$admin_password"
    
    print_success "Admin user credentials configured"
}

# Create directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs certs
    print_success "Directories created"
}

# Build and start containers
start_containers() {
    print_header "Building and Starting Docker Containers"
    
    # Ensure we have docker compose command
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        if ! detect_docker_compose; then
            print_error "Docker Compose is not available. Cannot proceed."
            exit 1
        fi
    fi
    
    print_status "Building Docker images (this may take several minutes)..."
    $DOCKER_SUDO $DOCKER_COMPOSE_CMD build
    
    print_status "Starting containers..."
    $DOCKER_SUDO $DOCKER_COMPOSE_CMD up -d
    
    print_status "Waiting for services to be ready..."
    sleep 5
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if $DOCKER_SUDO $DOCKER_COMPOSE_CMD exec -T db pg_isready -U malsift >/dev/null 2>&1; then
            print_success "Database is ready"
            break
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    echo ""
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Database did not become ready in time"
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD logs db
        print_status "Checking container status..."
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD ps
        exit 1
    fi
    
    # Wait for app to be ready
    print_status "Waiting for application to start..."
    attempt=0
    local app_health_ok=false
    while [ $attempt -lt $max_attempts ]; do
        # Check both container health and HTTP endpoint
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            app_health_ok=true
            print_success "Application is ready"
            break
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    echo ""
    
    if [ "$app_health_ok" != "true" ]; then
        print_warning "Application may not be fully ready. Check logs with: $DOCKER_SUDO $DOCKER_COMPOSE_CMD logs app"
        print_status "Checking container status..."
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD ps
        print_status "The application may still be starting. Admin user creation will retry..."
    fi
}

# Create admin user via database
create_admin_user() {
    print_header "Creating Admin User"
    
    if [ -z "$ADMIN_USERNAME" ] || [ -z "$ADMIN_EMAIL" ] || [ -z "$ADMIN_PASSWORD" ]; then
        print_error "Admin user credentials not set. Cannot create admin user."
        return 1
    fi
    
    # Ensure we have docker compose command
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        if ! detect_docker_compose; then
            print_error "Docker Compose is not available. Cannot create admin user."
            return 1
        fi
    fi
    
    # Wait for app container to be ready and health endpoint responding
    print_status "Waiting for application to be ready..."
    local max_attempts=60
    local attempt=0
    local app_ready=false
    
    while [ $attempt -lt $max_attempts ]; do
        # Check if app container is running
        if ! $DOCKER_SUDO $DOCKER_COMPOSE_CMD ps app | grep -q "Up"; then
            attempt=$((attempt + 1))
            echo -n "."
            sleep 2
            continue
        fi
        
        # Check if health endpoint responds (this confirms app is running and database is initialized)
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            app_ready=true
            break
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    echo ""
    
    if [ "$app_ready" != "true" ]; then
        print_error "Application did not become ready in time"
        print_status "Checking container status..."
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD ps
        print_status "Checking health endpoint..."
        curl -v http://localhost:8000/health || true
        print_status "Checking app logs..."
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD logs app | tail -30
        print_error "You can create the admin user manually later using:"
        echo "  sudo docker compose exec app python /app/scripts/create_admin.py $ADMIN_USERNAME $ADMIN_EMAIL <password>"
        return 1
    fi
    
    print_success "Application is ready"
    
    # Give it a moment for database to be fully ready
    sleep 3
    
    # Use base64 encoding to safely pass password with special characters
    ADMIN_PASSWORD_B64=$(echo -n "$ADMIN_PASSWORD" | base64)
    
    # Copy the standalone create_admin script to container (use the one from repo)
    print_status "Setting up admin user creation script..."
    if [ -f "scripts/create_admin.py" ]; then
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD cp scripts/create_admin.py app:/app/scripts/create_admin.py
    else
        # Fallback: create inline script
        print_warning "create_admin.py not found in repo, creating inline version..."
        cat > /tmp/create_admin.py <<'PYTHON_EOF'
import sys
sys.path.insert(0, '/app')
import asyncio
import uuid
import base64
from datetime import datetime
from sqlalchemy import text
from app.core.database import async_engine, init_db
from app.auth.auth_service import AuthService

async def create_admin():
    username = sys.argv[1]
    email = sys.argv[2]
    use_base64 = len(sys.argv) > 4 and sys.argv[4] == "--base64"
    
    if use_base64:
        password_b64 = sys.argv[3]
        password = base64.b64decode(password_b64).decode('utf-8')
    else:
        password = sys.argv[3]
    
    try:
        await init_db()
    except Exception as e:
        pass  # Database may already be initialized
    
    auth_service = AuthService()
    hashed_password = auth_service.get_password_hash(password)
    user_id = str(uuid.uuid4())
    
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        )
        existing = result.fetchone()
        
        if existing:
            print(f"User {username} already exists - updating password")
            await conn.execute(
                text("UPDATE users SET hashed_password = :password, is_active = true, is_admin = true, auth_type = 'local' WHERE username = :username"),
                {"username": username, "password": hashed_password}
            )
            print(f"SUCCESS: Password updated for user '{username}'")
        else:
            await conn.execute(
                text("""
                    INSERT INTO users (id, username, email, hashed_password, is_active, is_admin, created_at, auth_type)
                    VALUES (:id, :username, :email, :password, :is_active, :is_admin, :created_at, :auth_type)
                """),
                {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "is_active": True,
                    "is_admin": True,
                    "created_at": datetime.now(),
                    "auth_type": "local"
                }
            )
            print(f"SUCCESS: Admin user '{username}' created successfully")

asyncio.run(create_admin())
PYTHON_EOF
        $DOCKER_SUDO $DOCKER_COMPOSE_CMD cp /tmp/create_admin.py app:/app/scripts/create_admin.py
    fi
    
    # Wait a moment for script to be available
    sleep 2
    
    # Run the script
    print_status "Creating admin user..."
    if $DOCKER_SUDO $DOCKER_COMPOSE_CMD exec -T app python /app/scripts/create_admin.py "$ADMIN_USERNAME" "$ADMIN_EMAIL" "$ADMIN_PASSWORD_B64" --base64 2>&1 | tee /tmp/create_admin_output.txt; then
        if grep -q "SUCCESS:" /tmp/create_admin_output.txt; then
            print_success "Admin user created successfully"
            
            # Verify the user was created
            print_status "Verifying user creation..."
            if $DOCKER_SUDO $DOCKER_COMPOSE_CMD exec -T app python -c "
import sys
sys.path.insert(0, '/app')
import asyncio
from sqlalchemy import text
from app.core.database import async_engine

async def verify():
    async with async_engine.begin() as conn:
        result = await conn.execute(text('SELECT username, email, is_active, is_admin, auth_type FROM users WHERE username = :username'), {'username': '$ADMIN_USERNAME'})
        user = result.fetchone()
        if user:
            print(f'✓ Verified: {user.username} ({user.email})')
            print(f'  Active: {user.is_active}, Admin: {user.is_admin}, Auth Type: {user.auth_type}')
            sys.exit(0)
        else:
            print('✗ ERROR: User not found after creation')
            sys.exit(1)

asyncio.run(verify())
" 2>&1; then
                print_success "User verification successful"
            else
                print_warning "Could not verify user creation, but script reported success"
            fi
        elif grep -q "already exists" /tmp/create_admin_output.txt; then
            print_warning "Admin user already exists. Password updated."
        else
            print_error "Admin user creation failed. Output:"
            cat /tmp/create_admin_output.txt
            print_status "You can manually create the admin user later using:"
            echo "  sudo docker compose exec app python /app/scripts/create_admin.py $ADMIN_USERNAME $ADMIN_EMAIL <password>"
        fi
    else
        print_error "Failed to execute admin user creation script"
        print_status "You can manually create the admin user later using:"
        echo "  sudo docker compose exec app python /app/scripts/create_admin.py $ADMIN_USERNAME $ADMIN_EMAIL <password>"
    fi
    
    # Cleanup
    rm -f /tmp/create_admin.py /tmp/create_admin_output.txt 2>/dev/null || true
}

# Main installation function
main() {
    print_header "MalsiftCND Unified Installation"
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found. Please run this script from the MalsiftCND root directory."
        exit 1
    fi
    
    # Initial checks
    check_root
    check_sudo
    
    # Installation steps
    check_prerequisites
    setup_env
    prompt_admin_user
    create_directories
    start_containers
    
    # Initialize database and create admin user
    print_status "Initializing database (this happens automatically on first start)..."
    
    # Wait a bit for app to fully initialize (tables creation, etc.)
    sleep 10
    
    create_admin_user
    
    # Final summary
    print_header "Installation Complete!"
    
    echo ""
    print_success "MalsiftCND has been installed and configured successfully!"
    echo ""
    echo "Access Information:"
    echo "  - Web Interface: http://localhost:8000"
    echo "  - API Health: http://localhost:8000/health"
    echo "  - API Docs (if DEBUG enabled): http://localhost:8000/api/docs"
    echo ""
    echo "Admin Credentials:"
    echo "  - Username: $ADMIN_USERNAME"
    echo "  - Email: $ADMIN_EMAIL"
    echo ""
    if [ "$DOCKER_SUDO" = "sudo" ]; then
        echo "⚠️  Docker Group Membership:"
        echo "  Your user has been added to the docker group."
        echo "  To use Docker without sudo (recommended), please:"
        echo "    1. Logout and login again, OR"
        echo "    2. Run: newgrp docker"
        echo ""
        echo "  After logout/login, you can use 'docker compose' instead of 'sudo docker compose'"
        echo ""
    fi
    echo "Useful Commands:"
    echo "  - View logs: $DOCKER_SUDO $DOCKER_COMPOSE_CMD logs -f app"
    echo "  - Stop services: $DOCKER_SUDO $DOCKER_COMPOSE_CMD down"
    echo "  - Restart services: $DOCKER_SUDO $DOCKER_COMPOSE_CMD restart"
    echo "  - View status: $DOCKER_SUDO $DOCKER_COMPOSE_CMD ps"
    echo ""
    print_status "You can now login to the web interface with your admin credentials!"
    echo ""
}

# Run main function
main "$@"

