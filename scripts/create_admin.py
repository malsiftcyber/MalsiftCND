#!/usr/bin/env python3
"""
Create admin user directly in database
"""
import sys
sys.path.insert(0, '/app')

import asyncio
import uuid
import base64
from datetime import datetime, timezone
from sqlalchemy import text
from app.core.database import async_engine, init_db
from app.auth.auth_service import AuthService

async def main():
    if len(sys.argv) < 4:
        print("Usage: python /app/scripts/create_admin.py <username> <email> <password>")
        print("Or with base64 password: python /app/scripts/create_admin.py <username> <email> <base64_password> --base64")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password_input = sys.argv[3]
    use_base64 = len(sys.argv) > 4 and sys.argv[4] == "--base64"
    
    print(f"\n=== Create Admin User ===")
    print(f"Username: {username}")
    print(f"Email: {email}")
    
    # Decode password if base64 encoded
    if use_base64:
        try:
            password = base64.b64decode(password_input).decode('utf-8')
            print("Password: (decoded from base64)")
        except Exception as e:
            print(f"❌ Failed to decode base64 password: {e}")
            sys.exit(1)
    else:
        password = password_input
        print(f"Password length: {len(password)}")
    
    # Initialize database
    try:
        await init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"Note: {e}")
    
    # Hash password
    auth_service = AuthService()
    hashed_password = auth_service.get_password_hash(password)
    # Use UUID object directly (PostgreSQL accepts UUID strings too, but being explicit)
    user_id = uuid.uuid4()
    
    async with async_engine.begin() as conn:
        # Check if user already exists
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        )
        existing = result.fetchone()
        
        if existing:
            print(f"\n⚠️  User already exists! Updating password...")
            await conn.execute(
                text("""
                    UPDATE users 
                    SET hashed_password = :password,
                        is_active = true,
                        is_admin = true,
                        auth_type = 'local'
                    WHERE username = :username
                """),
                {
                    "username": username,
                    "password": hashed_password
                }
            )
            print(f"✅ Password updated for user '{username}'")
        else:
            # Create new user
            await conn.execute(
                text("""
                    INSERT INTO users (id, username, email, hashed_password, is_active, is_admin, mfa_enabled, created_at, auth_type)
                    VALUES (:id, :username, :email, :password, :is_active, :is_admin, :mfa_enabled, :created_at, :auth_type)
                """),
                {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "is_active": True,
                    "is_admin": True,
                    "mfa_enabled": False,
                    "created_at": datetime.now(timezone.utc),  # Use timezone-aware datetime
                    "auth_type": "local"
                }
            )
            print(f"✅ Admin user '{username}' created successfully!")
    
    # Verify the user was created
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT username, email, is_active, is_admin, auth_type FROM users WHERE username = :username"),
            {"username": username}
        )
        user = result.fetchone()
        if user:
            print(f"\nVerification:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
            print(f"  Admin: {user.is_admin}")
            print(f"  Auth Type: {user.auth_type}")
            print(f"\n✅ User ready for login!")

if __name__ == "__main__":
    asyncio.run(main())

