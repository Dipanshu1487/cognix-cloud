import sqlite3
import os

def migrate():
    db_path = 'cognix.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Add profile_photo and join_date to users
    try:
        cur.execute("ALTER TABLE users ADD COLUMN profile_photo TEXT")
        print("Added profile_photo to users")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("profile_photo column already exists in users")
        else:
            print(f"Error migrating users (profile_photo): {e}")

    try:
        cur.execute("ALTER TABLE users ADD COLUMN join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("Added join_date to users")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("join_date column already exists in users")
        else:
            print(f"Error migrating users (join_date): {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
