#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection and print database information.
"""

import asyncio
import asyncpg

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "user",
    "password": "password",
    "database": "medical_db"
}

async def test_postgres_connection():
    """Test connection to PostgreSQL and print database information."""

    print("Testing PostgreSQL connection...")
    print("=" * 40)

    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Successfully connected to PostgreSQL!")

        # Get database version
        version = await conn.fetchval("SELECT version()")
        print(f"📊 Database Version: {version}")

        # Get current database name
        db_name = await conn.fetchval("SELECT current_database()")
        print(f"🗄️  Current Database: {db_name}")

        # Get current user
        current_user = await conn.fetchval("SELECT current_user")
        print(f"👤 Current User: {current_user}")

        # Check if medical_db exists and get table count
        try:
            table_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            print(f"📋 Tables in public schema: {table_count}")

            # List all tables
            if table_count > 0:
                tables = await conn.fetch("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                print("📋 Tables:")
                for table in tables:
                    print(f"   - {table['table_name']}")

        except Exception as e:
            print(f"⚠️  Could not query tables: {e}")

        # Test if users table exists and has data
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            print(f"👥 Users in database: {user_count}")

            if user_count > 0:
                users = await conn.fetch("""
                    SELECT username, email, role
                    FROM users
                    ORDER BY username
                """)
                print("👥 User list:")
                for user in users:
                    print(f"   - {user['username']} ({user['role']}) - {user['email']}")

        except Exception as e:
            print(f"⚠️  Could not query users table: {e}")

        await conn.close()
        print("✅ Connection closed successfully")

    except asyncpg.exceptions.InvalidCatalogNameError:
        print("❌ Error: Database 'medical_db' does not exist.")
        print("💡 Try creating it with: CREATE DATABASE medical_db;")
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Error: Invalid database password.")
        print("💡 Check your PostgreSQL credentials")
    except ConnectionRefusedError:
        print("❌ Error: Connection refused. Is PostgreSQL running?")
        print("💡 Start PostgreSQL service or check if it's running on port 5432")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure PostgreSQL is installed and running")

async def main():
    """Main function."""
    await test_postgres_connection()

if __name__ == "__main__":
    asyncio.run(main())