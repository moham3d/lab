#!/usr/bin/env python3
"""
Script to create initial admin user
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import create_initial_admin


async def main():
    """Main function to create admin user"""
    try:
        print("Creating initial admin user...")
        await create_initial_admin()
        print("Admin user creation completed successfully!")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())