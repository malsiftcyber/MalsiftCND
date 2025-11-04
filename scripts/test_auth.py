#!/usr/bin/env python3
"""
Test script to verify user authentication
Run this inside the app container to test authentication
"""
import asyncio
import sys
from app.auth.auth_service import AuthService
from app.core.database import AsyncSessionLocal
from sqlalchemy import select, text
from app.models.user import User

async def test_auth():
    auth_service = AuthService()
    
    if len(sys.argv) < 3:
        print("Usage: python test_auth.py <username> <password>")
        print("Or: python test_auth.py --list-users")
        sys.exit(1)
    
    if sys.argv[1] == "--list-users":
        # List all users
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"\nFound {len(users)} users in database:")
            for user in users:
                print(f"  - Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}, Active: {user.is_active}, Auth Type: {user.auth_type}")
                print(f"    Password hash (first 50 chars): {user.hashed_password[:50]}...")
        return
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"\nTesting authentication for user: {username}")
    print(f"Password length: {len(password)}")
    
    # First, check if user exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"ERROR: User '{username}' not found in database!")
            
            # List all users
            result = await session.execute(select(User))
            all_users = result.scalars().all()
            print(f"\nFound {len(all_users)} users in database:")
            for u in all_users:
                print(f"  - {u.username}")
            sys.exit(1)
        
        print(f"✓ User found: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Admin: {user.is_admin}")
        print(f"  Active: {user.is_active}")
        print(f"  Auth Type: {user.auth_type}")
        print(f"  Password hash: {user.hashed_password[:50]}...")
    
    # Test authentication
    print(f"\nTesting password verification...")
    user_data = await auth_service._get_local_user(username)
    
    if not user_data:
        print("ERROR: Could not retrieve user data from auth service")
        sys.exit(1)
    
    print(f"✓ User data retrieved from auth service")
    
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

if __name__ == "__main__":
    asyncio.run(test_auth())

