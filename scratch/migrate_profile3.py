import sqlite3
import os
import datetime

def migrate():
    db_path = 'cognix.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN join_date TIMESTAMP")
        print("Added join_date to users")
        
        # Update existing records with current timestamp
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("UPDATE users SET join_date = ? WHERE join_date IS NULL", (now,))
        print("Updated existing users with current join_date")
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
