import sqlite3
import os

def inspect_db(db_path):
    if not os.path.exists(db_path):
        return f"{db_path} does not exist."
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Check topics
        cur.execute("SELECT id, name FROM topics WHERE name LIKE '%Introduction to OOP%'")
        topics = cur.fetchall()
        
        # Check notes
        cur.execute("SELECT id, topic_id, content, file_path FROM notes")
        notes = cur.fetchall()
        
        # Join topics and notes
        cur.execute("""
            SELECT t.id, t.name, COUNT(n.id) 
            FROM topics t 
            LEFT JOIN notes n ON t.id = n.topic_id 
            GROUP BY t.id, t.name
            HAVING COUNT(n.id) > 0
        """)
        topic_notes_count = cur.fetchall()
        
        conn.close()
        return {
            "path": db_path,
            "oop_topics": topics,
            "total_notes": len(notes),
            "topics_with_notes": topic_notes_count
        }
    except Exception as e:
        return f"Error inspecting {db_path}: {e}"

if __name__ == "__main__":
    dbs = ["cognix.db", "jarvis.db"]
    for db in dbs:
        print(f"\n--- {db} ---")
        res = inspect_db(db)
        import json
        print(json.dumps(res, indent=2))
