#!/usr/bin/env python3
"""
Environment upgrade script for Python 3.13 compatibility
Run this script to upgrade your dependencies for Python 3.13
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main upgrade process"""
    print("🚀 Upgrading Patient Visit Management System for Python 3.13")
    print("=" * 60)

    # Check Python version
    print(f"Current Python version: {sys.version}")

    if sys.version_info < (3, 13):
        print("⚠️  Warning: You're not running Python 3.13. This upgrade is designed for Python 3.13+")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return

    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return

    # Install/upgrade dependencies
    if not run_command("pip install -r requirements.txt --upgrade", "Installing updated dependencies"):
        return

    # Alternative: if using poetry
    if os.path.exists("pyproject.toml"):
        print("\n📦 Poetry detected. Updating Poetry dependencies...")
        if not run_command("poetry update", "Updating Poetry dependencies"):
            print("Poetry update failed, but pip install succeeded. This is usually fine.")

    # Test imports
    print("\n🧪 Testing key imports...")

    test_imports = [
        ("from pydantic_settings import BaseSettings", "pydantic-settings"),
        ("from sqlalchemy import create_engine", "SQLAlchemy"),
        ("from fastapi import FastAPI", "FastAPI"),
        ("from app.core.config import settings", "Application config"),
    ]

    for import_stmt, description in test_imports:
        try:
            exec(import_stmt)
            print(f"✅ {description}: OK")
        except Exception as e:
            print(f"❌ {description}: Failed - {e}")

    print("\n" + "=" * 60)
    print("🎉 Upgrade complete!")
    print("\nNext steps:")
    print("1. Test your application: python -m uvicorn app.main:app --reload")
    print("2. Run migrations: alembic upgrade head")
    print("3. Run tests: pytest")
    print("\nIf you encounter any issues, check the error messages above.")

if __name__ == "__main__":
    main()