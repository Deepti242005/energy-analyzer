import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Tables in database:')
for table in tables:
    table_name = table[0]
    print(f'\nTable: {table_name}')
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print('Columns:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print(f'Data ({len(rows)} rows):')
    if rows:
        for row in rows[:10]:  # Show first 10 rows
            print(f'  {row}')
        if len(rows) > 10:
            print(f'  ... and {len(rows) - 10} more rows')
    else:
        print('  No data')

conn.close()