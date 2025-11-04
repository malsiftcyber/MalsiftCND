#!/bin/bash
# Quick authentication test script

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: sudo bash scripts/quick_test_auth.sh <username> <password>"
    exit 1
fi

USERNAME="$1"
PASSWORD="$2"

echo "Testing authentication for user: $USERNAME"
echo ""

# Check if containers are running
if ! sudo docker compose ps | grep -q "app.*Up"; then
    echo "ERROR: App container is not running"
    echo "Start containers with: sudo docker compose up -d"
    exit 1
fi

# Run the test
sudo docker compose exec -T app python /app/scripts/test_auth.py "$USERNAME" "$PASSWORD"

