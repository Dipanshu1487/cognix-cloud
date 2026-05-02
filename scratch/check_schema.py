import sqlite3
import os

db_path = 'jarvis.db'

def check_schema():
    if not os.path.exists(db_path):
        print(f"{db_path} does not exist")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    
    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        print(f"\nTable: {table_name}")
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = cur.fetchall()
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")
            
    conn.close()

if __name__ == "__main__":
    check_schema()
