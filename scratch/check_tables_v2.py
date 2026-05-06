import psycopg2
import os

def get_connection():
    # Attempt to get secrets similar to how upload.db does
    # This is a bit hacky but should work if env vars are set
    host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS")
    port = os.getenv("DB_PORT", "5432")
    
    return psycopg2.connect(
        host=host,
        database=db_name,
        user=user,
        password=password,
        port=port
    )

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    print("Tables found in public schema:")
    for t in tables:
        print(f" - {t[0]}")
        
    # Also check columns of progress table
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'progress'")
    cols = cur.fetchall()
    print("\nColumns in 'progress' table:")
    for c in cols:
        print(f" - {c[0]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
