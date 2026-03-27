import sqlite3
import os

# Check if database exists and try to remove it
db_file = 'database.db'
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f"Deleted corrupted {db_file}")
    except Exception as e:
        print(f"Could not delete file: {e}")
        print("Attempting to overwrite...")

# Create fresh database
try:
    conn = sqlite3.connect(db_file, timeout=10)
    c = conn.cursor()
    
    # Drop existing tables (if any)
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('DROP TABLE IF EXISTS usage')
    
    # Create tables
    c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    
    c.execute('''
    CREATE TABLE usage (
        id INTEGER PRIMARY KEY,
        username TEXT,
        appliance TEXT,
        power REAL,
        hours REAL,
        units REAL,
        date TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Fresh database created successfully!")
    print("✓ Tables: users, usage")
    
except Exception as e:
    print(f"Error: {e}")
