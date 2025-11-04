#!/usr/bin/env python3
"""
Reset user password
"""
import sys
sys.path.insert(0, '/app')

import asyncio
from sqlalchemy import text
from app.core.database import async_engine
from app.auth.auth_service import AuthService

async def main():
    if len(sys.argv) < 3:
        print("Usage: python /app/scripts/reset_password.py <username> <new-password>")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    print(f"\n=== Reset Password ===")
    print(f"Username: {username}")
    print(f"New password length: {len(new_password)}")
    print()
    
    auth_service = AuthService()
    hashed_password = auth_service.get_password_hash(new_password)
    
    async with async_engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        )
        if not result.fetchone():
            print(f"❌ User '{username}' not found!")
            sys.exit(1)
        
        # Update password
        await conn.execute(
            text("""
                UPDATE users 
                SET hashed_password = :password,
                    auth_type = 'local',
                    is_active = true
                WHERE username = :username
            """),
            {"username": username, "password": hashed_password}
        )
        
        print(f"✅ Password reset successfully for user '{username}'")
        print("\nYou can now login with the new password.")

if __name__ == "__main__":
    asyncio.run(main())

