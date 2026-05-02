import sqlite3
import os

db_path = 'jarvis.db'

def debug_structure():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("--- RAW COUNTS ---")
    tables = ['subjects', 'units', 'sections', 'topics', 'subtopics']
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cur.fetchone()[0]}")
        
    print("\n--- QUERY TEST (INNER JOIN) ---")
    cur.execute("""
        SELECT s.name as subject, u.name as unit, sec.name as section, t.id as topic_id, t.name as topic_name
        FROM subjects s
        JOIN units u ON s.id = u.subject_id
        JOIN sections sec ON u.id = sec.unit_id
        JOIN topics t ON sec.id = t.section_id
        LIMIT 5
    """)
    rows = cur.fetchall()
    print(f"Rows found: {len(rows)}")
    for row in rows:
        print(dict(row))
        
    print("\n--- SUBJECTS LIST ---")
    cur.execute("SELECT name FROM subjects")
    for s in cur.fetchall():
        print(s[0])
        
    conn.close()

if __name__ == "__main__":
    debug_structure()
