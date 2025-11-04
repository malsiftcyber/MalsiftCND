#!/usr/bin/env python3
"""
Direct database authentication test - bypasses all layers
"""
import sys
sys.path.insert(0, '/app')

import asyncio
from sqlalchemy import text
from app.core.database import async_engine
from app.auth.auth_service import AuthService

async def main():
    if len(sys.argv) < 3:
        print("Usage: python /app/scripts/direct_auth_test.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"\n=== Direct Authentication Test ===")
    print(f"Username: {username}")
    print(f"Password length: {len(password)}")
    print()
    
    # Get user directly from database
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT id, username, email, hashed_password, is_active, is_admin, auth_type
                FROM users
                WHERE username = :username
            """),
            {"username": username}
        )
        user = result.fetchone()
        
        if not user:
            print("❌ USER NOT FOUND IN DATABASE!")
            
            # Show all users
            result = await conn.execute(text("SELECT username, email, auth_type FROM users"))
            all_users = result.fetchall()
            print(f"\nFound {len(all_users)} users in database:")
            for u in all_users:
                print(f"  - {u.username} ({u.email}) - auth_type: {u.auth_type}")
            sys.exit(1)
        
        print("✓ User found in database:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Active: {user.is_active}")
        print(f"  Admin: {user.is_admin}")
        print(f"  Auth Type: {user.auth_type}")
        print(f"  Password Hash: {user.hashed_password[:60]}...")
        
        if not user.is_active:
            print("\n❌ USER IS NOT ACTIVE!")
            sys.exit(1)
        
        if user.auth_type != "local":
            print(f"\n⚠️  WARNING: Auth type is '{user.auth_type}', expected 'local'")
        
        # Test password verification
        auth_service = AuthService()
        print("\nTesting password verification...")
        is_valid = auth_service.verify_password(password, user.hashed_password)
        
        if is_valid:
            print("\n✅ PASSWORD VERIFICATION SUCCESSFUL!")
            print("\nAuthentication should work. If it doesn't, check:")
            print("  1. Application logs: sudo docker compose logs app | grep -i auth")
            print("  2. Make sure you're using the correct username (case-sensitive)")
            print("  3. Check browser console for any errors")
        else:
            print("\n❌ PASSWORD VERIFICATION FAILED!")
            print("\nThe password hash in the database doesn't match the provided password.")
            print("\nPossible solutions:")
            print("  1. The password was stored incorrectly during user creation")
            print("  2. You're using the wrong password")
            print("  3. Special characters weren't handled correctly")
            print("\nTo reset the password, run:")
            print(f"  sudo docker compose exec app python /app/scripts/reset_password.py {username} <new-password>")

if __name__ == "__main__":
    asyncio.run(main())

