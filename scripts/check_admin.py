#!/usr/bin/env python3
"""
Check admin user in database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import async_session


async def check_admin():
    """Check admin user details"""
    try:
        async with async_session() as session:
            result = await session.execute(
                text('SELECT id, username, first_name, last_name, role, is_active FROM users WHERE username = :username'),
                {'username': 'admin'}
            )
            user = result.fetchone()

            if user:
                print("✅ Admin user found in database:")
                print(f"   ID: {user[0]}")
                print(f"   Username: {user[1]}")
                print(f"   First Name: {user[2]}")
                print(f"   Last Name: {user[3]}")
                print(f"   Role: {user[4]}")
                print(f"   Active: {user[5]}")

                # Check if first_name or last_name are NULL
                if user[2] is None or user[3] is None:
                    print("\n❌ Issue found: first_name or last_name is NULL")
                    print("Need to update the admin user with proper values")
                else:
                    print("\n✅ Admin user looks good!")
            else:
                print("❌ No admin user found in database")

    except Exception as e:
        print(f"❌ Error checking admin user: {e}")


if __name__ == "__main__":
    asyncio.run(check_admin())