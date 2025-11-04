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

echo "1. Checking users in database..."
docker compose exec -T app python -c "
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f'Found {len(users)} users:')
        for user in users:
            print(f'  - Username: {user.username}')
            print(f'    Email: {user.email}')
            print(f'    Admin: {user.is_admin}')
            print(f'    Active: {user.is_active}')
            print(f'    Auth Type: {user.auth_type}')
            print(f'    Password Hash (first 30 chars): {user.hashed_password[:30]}...')
            print()

asyncio.run(list_users())
"

echo ""
echo "2. To test authentication, run:"
echo "   docker compose exec app python /app/scripts/test_auth.py <username> <password>"
echo ""
echo "   Or to list all users:"
echo "   docker compose exec app python /app/scripts/test_auth.py --list-users"
echo ""

