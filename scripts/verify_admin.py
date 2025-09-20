#!/usr/bin/env python3
"""
Script to verify admin user creation
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import async_session
from app.models.user import User


async def verify_admin():
    """Verify admin user exists"""
    try:
        async with async_session() as session:
            # Check if admin user exists
            result = await session.execute(
                text('SELECT id, username, email, first_name, last_name, role, is_active FROM users WHERE username = :username'),
                {'username': 'admin'}
            )
            user = result.fetchone()

            if user:
                print("✅ Admin user found in database:")
                print(f"   ID: {user[0]}")
                print(f"   Username: {user[1]}")
                print(f"   Email: {user[2]}")
                print(f"   Name: {user[3]} {user[4]}")
                print(f"   Role: {user[5]}")
                print(f"   Active: {user[6]}")
                print("\n🔐 Login credentials:")
                print("   Username: admin")
                print("   Password: admin")
            else:
                print("❌ Admin user not found in database")

    except Exception as e:
        print(f"❌ Error verifying admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(verify_admin())