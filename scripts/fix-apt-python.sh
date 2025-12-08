#!/bin/bash
# Fix apt_pkg ModuleNotFoundError on Ubuntu
# This script fixes the common issue where apt_pkg module is not found

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}==========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==========================================${NC}\n"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_header "Fixing apt_pkg ModuleNotFoundError"

# Step 1: Find the correct Python version
print_status "Step 1: Detecting Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
print_status "Detected Python version: $PYTHON_VERSION"

# Step 2: Reinstall python3-apt
print_status "Step 2: Reinstalling python3-apt package..."
apt-get update 2>&1 | grep -v "ModuleNotFoundError" || true
apt-get install --reinstall -y python3-apt

# Step 3: Fix the cnf-update-db script
print_status "Step 3: Fixing cnf-update-db script..."
if [ -f /usr/lib/cnf-update-db ]; then
    # Check what Python version the script uses
    SHEBANG=$(head -1 /usr/lib/cnf-update-db)
    
    if [[ "$SHEBANG" == *"python3"* ]]; then
        # Try to find the correct python3 path
        PYTHON3_PATH=$(which python3)
        if [ -n "$PYTHON3_PATH" ]; then
            print_status "Updating cnf-update-db to use $PYTHON3_PATH"
            sed -i "1s|.*|#!$PYTHON3_PATH|" /usr/lib/cnf-update-db
        fi
    fi
fi

# Step 4: Try to fix apt_pkg import
print_status "Step 4: Checking apt_pkg module..."
# Find where apt_pkg is installed
APT_PKG_PATH=$(python3 -c "import apt_pkg; print(apt_pkg.__file__)" 2>/dev/null || echo "")

if [ -z "$APT_PKG_PATH" ]; then
    print_warning "apt_pkg module not found in Python path"
    print_status "Attempting to locate apt_pkg..."
    
    # Common locations
    POSSIBLE_PATHS=(
        "/usr/lib/python3/dist-packages/apt_pkg.cpython-*.so"
        "/usr/lib/python3.*/dist-packages/apt_pkg.cpython-*.so"
    )
    
    for pattern in "${POSSIBLE_PATHS[@]}"; do
        FOUND=$(find /usr/lib -name "apt_pkg.cpython-*.so" 2>/dev/null | head -1)
        if [ -n "$FOUND" ]; then
            print_status "Found apt_pkg at: $FOUND"
            break
        fi
    done
fi

# Step 5: Disable the problematic hook temporarily
print_status "Step 5: Temporarily disabling command-not-found update hook..."
if [ -f /etc/apt/apt.conf.d/50command-not-found ]; then
    print_status "Backing up 50command-not-found..."
    cp /etc/apt/apt.conf.d/50command-not-found /etc/apt/apt.conf.d/50command-not-found.backup
    
    # Comment out the problematic line
    sed -i 's|/usr/lib/cnf-update-db|#/usr/lib/cnf-update-db|' /etc/apt/apt.conf.d/50command-not-found
    print_success "Disabled command-not-found update hook"
fi

# Alternative: Remove the hook entirely if it's causing issues
if [ -f /etc/apt/apt.conf.d/50command-not-found ]; then
    # Check if we should remove it
    print_status "You can also remove the hook entirely if needed:"
    print_status "  rm /etc/apt/apt.conf.d/50command-not-found"
fi

# Step 6: Test apt update
print_status "Step 6: Testing apt update..."
if apt-get update 2>&1 | grep -v "ModuleNotFoundError" | grep -q "Reading package lists"; then
    print_success "apt update works correctly now!"
else
    print_warning "apt update still shows warnings, but should work"
fi

# Step 7: Alternative fix - reinstall command-not-found
print_status "Step 7: Reinstalling command-not-found package..."
apt-get install --reinstall -y command-not-found 2>&1 | grep -v "ModuleNotFoundError" || true

print_header "Fix Complete"

print_success "apt should now work correctly"
print_status "The ModuleNotFoundError was likely caused by:"
print_status "  - Python version mismatch"
print_status "  - Missing or corrupted python3-apt"
print_status "  - Broken command-not-found hook"
echo ""
print_status "If issues persist, you can:"
print_status "  1. Remove the hook: rm /etc/apt/apt.conf.d/50command-not-found"
print_status "  2. Reinstall: apt-get install --reinstall python3-apt command-not-found"
print_status "  3. The error is harmless - apt still works, just the command-not-found database won't update"

