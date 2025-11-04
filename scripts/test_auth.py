#!/usr/bin/env python3
"""
Test script to verify user authentication
Run this inside the app container to test authentication
"""
import sys
import os

# Add /app to Python path
sys.path.insert(0, '/app')

import asyncio
from app.auth.auth_service import AuthService
from app.core.database import AsyncSessionLocal, async_engine
from sqlalchemy import select, text

async def test_auth():
    auth_service = AuthService()
    
    if len(sys.argv) < 2:
        print("Usage: python test_auth.py <username> <password>")
        print("Or: python test_auth.py --list-users")
        sys.exit(1)
    
    if sys.argv[1] == "--list-users":
        # List all users using raw SQL to avoid relationship issues
        async with async_engine.begin() as conn:
            result = await conn.execute(text('''
                SELECT id, username, email, is_active, is_admin, auth_type,
                       LEFT(hashed_password, 50) as password_preview
                FROM users
            '''))
            users = result.fetchall()
            print(f"\nFound {len(users)} users in database:")
            for user in users:
                print(f"  - Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}, Active: {user.is_active}, Auth Type: {user.auth_type}")
                print(f"    Password hash (first 50 chars): {user.password_preview}...")
        return
    
    if len(sys.argv) < 3:
        print("Usage: python test_auth.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"\nTesting authentication for user: {username}")
    print(f"Password length: {len(password)}")
    
    # First, check if user exists using raw SQL
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id, username, email, hashed_password, is_active, is_admin, auth_type FROM users WHERE username = :username"),
            {"username": username}
        )
        user_row = result.fetchone()
        
        if not user_row:
            print(f"ERROR: User '{username}' not found in database!")
            
            # List all users
            result = await conn.execute(text("SELECT username FROM users"))
            all_users = result.fetchall()
            print(f"\nFound {len(all_users)} users in database:")
            for u in all_users:
                print(f"  - {u.username}")
            sys.exit(1)
        
        print(f"✓ User found: {user_row.username}")
        print(f"  Email: {user_row.email}")
        print(f"  Admin: {user_row.is_admin}")
        print(f"  Active: {user_row.is_active}")
        print(f"  Auth Type: {user_row.auth_type}")
        print(f"  Password hash: {user_row.hashed_password[:50]}...")
        
        user_data = {
            "id": str(user_row.id),
            "username": user_row.username,
            "email": user_row.email,
            "hashed_password": user_row.hashed_password,
            "is_active": user_row.is_active,
            "is_admin": user_row.is_admin,
            "auth_type": user_row.auth_type or "local"
        }
    
    # Test authentication
    print(f"\nTesting password verification...")
    
    if not user_data["is_active"]:
        print("ERROR: User is not active!")
        sys.exit(1)
    
    if user_data["auth_type"] != "local":
        print(f"WARNING: User auth_type is '{user_data['auth_type']}', expected 'local'")
    
    print(f"✓ User data retrieved")
    
    # Verify password
    is_valid = auth_service.verify_password(password, user_data["hashed_password"])
    
    if is_valid:
        print("✓ Password verification SUCCESSFUL!")
        print("\nAuthentication should work.")
    else:
        print("✗ Password verification FAILED!")
        print("\nPossible issues:")
        print("  1. Password was stored incorrectly during user creation")
        print("  2. Password hash mismatch")
        print("  3. Password contains special characters that weren't handled correctly")
        
        # Try to re-hash the password to see if it matches
        new_hash = auth_service.get_password_hash(password)
        print(f"\nCurrent hash: {user_data['hashed_password'][:50]}...")
        print(f"New hash (from same password): {new_hash[:50]}...")
        print(f"Hash match: {user_data['hashed_password'] == new_hash}")
        print("\nNote: bcrypt hashes are salted, so same password will produce different hashes")

if __name__ == "__main__":
    asyncio.run(test_auth())


