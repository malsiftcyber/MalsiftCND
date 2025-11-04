#!/bin/bash
# Debug authentication issues

echo "=========================================="
echo "MalsiftCND Authentication Debug Script"
echo "=========================================="
echo ""

# Check if containers are running
if ! docker compose ps | grep -q "app.*Up"; then
    echo "ERROR: App container is not running"
    echo "Please start containers with: sudo docker compose up -d"
    exit 1
fi

#!/bin/bash
# Debug authentication issues

echo "=========================================="
echo "MalsiftCND Authentication Debug Script"
echo "=========================================="
echo ""

# Check if containers are running
if ! sudo docker compose ps | grep -q "app.*Up"; then
    echo "ERROR: App container is not running"
    echo "Please start containers with: sudo docker compose up -d"
    exit 1
fi

echo "1. Checking users in database..."
sudo docker compose exec -T app python -c "
import sys
sys.path.insert(0, '/app')
import asyncio
from sqlalchemy import text
from app.core.database import async_engine

async def list_users():
    # Use raw SQL to avoid relationship loading issues
    async with async_engine.begin() as conn:
        result = await conn.execute(text('''
            SELECT id, username, email, is_active, is_admin, auth_type,
                   LEFT(hashed_password, 30) as password_preview
            FROM users
        '''))
        users = result.fetchall()
        print(f'Found {len(users)} users:')
        for user in users:
            print(f'  - Username: {user.username}')
            print(f'    Email: {user.email}')
            print(f'    Admin: {user.is_admin}')
            print(f'    Active: {user.is_active}')
            print(f'    Auth Type: {user.auth_type}')
            print(f'    Password Hash (first 30 chars): {user.password_preview}...')
            print()

asyncio.run(list_users())
"

echo ""
echo "2. To test authentication, run:"
echo "   sudo docker compose exec app python /app/scripts/test_auth.py <username> <password>"
echo ""
echo "   Or to list all users:"
echo "   sudo docker compose exec app python /app/scripts/test_auth.py --list-users"
echo ""


