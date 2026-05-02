import sqlite3
import os

def sync_dbs():
    src_db = 'jarvis.db'
    dst_db = 'cognix.db'
    
    if not os.path.exists(src_db):
        print(f"Source database {src_db} not found")
        return
        
    src_conn = sqlite3.connect(src_db)
    dst_conn = sqlite3.connect(dst_db)
    
    tables_to_sync = ['subjects', 'units', 'sections', 'topics', 'subtopics', 'notes', 'questions', 'progress', 'user_progress', 'subtopic_progress']
    
    for table in tables_to_sync:
        print(f"Syncing table: {table}...")
        # Get data from source
        src_cur = src_conn.cursor()
        src_cur.execute(f"SELECT * FROM {table}")
        rows = src_cur.fetchall()
        
        # Get column names
        src_cur.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in src_cur.fetchall()]
        col_placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join(cols)
        
        dst_cur = dst_conn.cursor()
        # Clear existing data in destination (to avoid duplicates/conflicts)
        dst_cur.execute(f"DELETE FROM {table}")
        
        # Insert data into destination
        dst_cur.executemany(f"INSERT INTO {table} ({col_names}) VALUES ({col_placeholders})", rows)
        print(f"  Inserted {len(rows)} rows into {table}")
    
    dst_conn.commit()
    src_conn.close()
    dst_conn.close()
    print("Sync complete!")

if __name__ == "__main__":
    sync_dbs()
