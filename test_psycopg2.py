#!/usr/bin/env python3

import psycopg2

try:
    conn = psycopg2.connect(
        host='172.18.0.2',  # Docker container IP
        port=5432,
        user='user',
        password='password',
        dbname='medical_db'
    )
    print('✅ Connected successfully to PostgreSQL!')

    # Get version
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    version = cursor.fetchone()
    print(f'📊 PostgreSQL Version: {version[0][:50]}...')

    # Get database name
    cursor.execute('SELECT current_database()')
    db_name = cursor.fetchone()
    print(f'🗄️  Database: {db_name[0]}')

    cursor.close()
    conn.close()
    print('✅ Connection closed successfully')

except psycopg2.Error as e:
    print(f'❌ PostgreSQL Error: {e}')
except Exception as e:
    print(f'❌ Error: {e}')