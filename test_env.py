#!/usr/bin/env python3
"""
Quick test script to verify Python 3.13 compatibility
"""

import sys
print(f"Python version: {sys.version}")

# Test key imports
tests = [
    ("pydantic_settings", "from pydantic_settings import BaseSettings"),
    ("sqlalchemy", "from sqlalchemy import create_engine"),
    ("fastapi", "from fastapi import FastAPI"),
    ("alembic", "import alembic"),
    ("pydantic", "from pydantic import BaseModel"),
]

print("\nTesting imports:")
for package, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f"✅ {package}: OK")
    except Exception as e:
        print(f"❌ {package}: Failed - {e}")

# Test app imports
print("\nTesting app imports:")
app_tests = [
    ("Config", "from app.core.config import settings"),
    ("FileHandler", "from app.utils.file_handler import FileHandler"),
    ("Document schemas", "from app.schemas.document import DocumentCreate"),
]

for component, import_stmt in app_tests:
    try:
        exec(import_stmt)
        print(f"✅ {component}: OK")
    except Exception as e:
        print(f"❌ {component}: Failed - {e}")

print("\nIf all tests pass, your environment is ready!")
print("If any tests fail, run: python upgrade_env.py")