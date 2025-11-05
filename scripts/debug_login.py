#!/usr/bin/env python3
"""
Debug login issues - comprehensive diagnostic script
"""
import sys
sys.path.insert(0, '/app')

import asyncio
import bcrypt
from sqlalchemy import text
from app.core.database import async_engine
from app.auth.auth_service import AuthService

async def main():
    if len(sys.argv) < 2:
        print("Usage: python /app/scripts/debug_login.py <username> [password]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n=== Login Debug for user: {username} ===\n")
    
    async with async_engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(
            text("""
                SELECT id, username, email, hashed_password, is_active, is_admin, 
                       mfa_enabled, auth_type, created_at
                FROM users WHERE username = :username
            """),
            {"username": username}
        )
        user = result.fetchone()
        
        if not user:
            print(f"❌ USER NOT FOUND in database!")
            print(f"\nChecking all users in database:")
            all_users = await conn.execute(text("SELECT username, email, is_active, is_admin FROM users"))
            for u in all_users:
                print(f"  - {u.username} ({u.email}) - active: {u.is_active}, admin: {u.is_admin}")
            sys.exit(1)
        
        print(f"✓ User found in database:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Active: {user.is_active}")
        print(f"  Admin: {user.is_admin}")
        print(f"  MFA Enabled: {user.mfa_enabled}")
        print(f"  Auth Type: {user.auth_type}")
        print(f"  Created: {user.created_at}")
        print(f"\n  Password Hash (first 50 chars): {user.hashed_password[:50]}...")
        print(f"  Password Hash Length: {len(user.hashed_password)}")
        print(f"  Password Hash Starts with: {user.hashed_password[:7]}")
        
        if not user.is_active:
            print(f"\n⚠️  WARNING: User is NOT ACTIVE - this will prevent login!")
        
        if user.auth_type != "local":
            print(f"\n⚠️  WARNING: Auth type is '{user.auth_type}', not 'local'")
        
        if password:
            print(f"\n=== Testing Password Verification ===\n")
            
            # Test direct bcrypt verification
            print(f"1. Testing direct bcrypt.checkpw()...")
            try:
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                    print(f"   Password truncated to 72 bytes")
                
                hash_bytes = user.hashed_password.encode('utf-8')
                result = bcrypt.checkpw(password_bytes, hash_bytes)
                print(f"   Result: {'✓ MATCH' if result else '✗ NO MATCH'}")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Test AuthService verification
            print(f"\n2. Testing AuthService.verify_password()...")
            try:
                auth_service = AuthService()
                result = auth_service.verify_password(password, user.hashed_password)
                print(f"   Result: {'✓ MATCH' if result else '✗ NO MATCH'}")
            except Exception as e:
                print(f"   Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test full authentication
            print(f"\n3. Testing full AuthService.authenticate_user()...")
            try:
                auth_service = AuthService()
                user_dict = await auth_service.authenticate_user(username, password, "local")
                if user_dict:
                    print(f"   Result: ✓ AUTHENTICATION SUCCESS")
                    print(f"   User ID: {user_dict.get('id')}")
                    print(f"   Username: {user_dict.get('username')}")
                    print(f"   Email: {user_dict.get('email')}")
                    print(f"   Admin: {user_dict.get('is_admin')}")
                else:
                    print(f"   Result: ✗ AUTHENTICATION FAILED")
                    print(f"   (This is what the login endpoint sees)")
            except Exception as e:
                print(f"   Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test password hashing to see what we get
            print(f"\n4. Testing password hash generation...")
            try:
                auth_service = AuthService()
                new_hash = auth_service.get_password_hash(password)
                print(f"   New hash (first 50 chars): {new_hash[:50]}...")
                print(f"   New hash matches stored hash: {'✓ YES' if new_hash == user.hashed_password else '✗ NO'}")
                
                # Try verifying new hash against the password
                test_result = auth_service.verify_password(password, new_hash)
                print(f"   New hash verifies correctly: {'✓ YES' if test_result else '✗ NO'}")
            except Exception as e:
                print(f"   Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n=== No password provided for testing ===")
            print(f"Run with password to test: python /app/scripts/debug_login.py {username} <password>")

if __name__ == "__main__":
    asyncio.run(main())

