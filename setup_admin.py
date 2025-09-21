#!/usr/bin/env python3
"""
Script to create admin user in PostgreSQL database for Patient Visit Management System.
This script connects directly to PostgreSQL and inserts the admin user with proper password hashing.
"""

import asyncio
import asyncpg
from passlib.context import CryptContext

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "medical_db"
}

# Password hashing context (same as the application)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create admin user in the database."""

    # Generate password hash for 'admin'
    password = "admin"
    hashed_password = pwd_context.hash(password)

    print(f"Generated hash for password '{password}': {hashed_password}")

    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        print("Connected to PostgreSQL database")

        # Check if admin user already exists
        existing_user = await conn.fetchval("""
            SELECT user_id FROM users WHERE username = 'admin'
        """)

        if existing_user:
            print("Admin user already exists. Updating password...")
            await conn.execute("""
                UPDATE users
                SET password_hash = $1, email = $2, full_name = $3, role = $4
                WHERE username = 'admin'
            """, hashed_password, 'admin@healthcare.local', 'System Administrator', 'admin')
            print("Admin user updated successfully")
        else:
            print("Creating new admin user...")
            await conn.execute("""
                INSERT INTO users (username, email, full_name, role, password_hash)
                VALUES ('admin', 'admin@healthcare.local', 'System Administrator', 'admin', $1)
            """, hashed_password)
            print("Admin user created successfully")

        # Verify the user was created/updated
        user_data = await conn.fetchrow("""
            SELECT user_id, username, email, full_name, role
            FROM users WHERE username = 'admin'
        """)

        if user_data:
            print("Admin user verification:")
            print(f"  User ID: {user_data['user_id']}")
            print(f"  Username: {user_data['username']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Full Name: {user_data['full_name']}")
            print(f"  Role: {user_data['role']}")
            print("  Password hash is set (not displayed for security)")

        await conn.close()
        print("Database connection closed")

    except asyncpg.exceptions.InvalidCatalogNameError:
        print("Error: Database 'medical_db' does not exist.")
        print("Please create the database first or run the application to initialize it.")
    except asyncpg.exceptions.InvalidPasswordError:
        print("Error: Invalid database password.")
        print("Please check your PostgreSQL credentials.")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure PostgreSQL is running and the database exists.")

async def test_login():
    """Test login with the admin credentials."""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)

        # Get the stored hash
        stored_hash = await conn.fetchval("""
            SELECT password_hash FROM users WHERE username = 'admin'
        """)

        if stored_hash:
            # Test password verification
            is_valid = pwd_context.verify("admin", stored_hash)
            print(f"Password verification test: {'PASSED' if is_valid else 'FAILED'}")
        else:
            print("No admin user found for testing")

        await conn.close()

    except Exception as e:
        print(f"Login test error: {e}")

async def main():
    """Main function."""
    print("Patient Visit Management System - Admin User Setup")
    print("=" * 50)

    await create_admin_user()

    print("\nTesting login...")
    await test_login()

    print("\nSetup complete!")
    print("You can now login to the API with:")
    print("  Username: admin")
    print("  Password: admin")

if __name__ == "__main__":
    asyncio.run(main())