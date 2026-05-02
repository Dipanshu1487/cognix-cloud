import sqlite3
import os

def migrate():
    db_path = 'cognix.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    tables_to_migrate = ['progress', 'user_progress', 'subtopic_progress']
    
    for table in tables_to_migrate:
        print(f"Migrating {table}...")
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER REFERENCES users(id)")
            print(f"  Added user_id to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  Column already exists in {table}")
            else:
                print(f"  Error migrating {table}: {e}")
                
    # Also add email to users if not present
    try:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("  Added email to users")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  Email column already exists in users")
        else:
            print(f"  Error migrating users: {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
