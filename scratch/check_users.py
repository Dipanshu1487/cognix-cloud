import sqlite3
import os

def check_users(db_name):
    if not os.path.exists(db_name):
        print(f"{db_name} not found")
        return
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, username FROM users")
        users = cur.fetchall()
        print(f"{db_name} Users: {users}")
    except Exception as e:
        print(f"Error in {db_name}: {e}")
    conn.close()

if __name__ == "__main__":
    check_users('cognix.db')
    check_users('jarvis.db')
