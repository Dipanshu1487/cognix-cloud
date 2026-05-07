import sqlite3

def check_oop_notes(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print(f"\n--- Checking {db_path} for OOP notes ---")
    
    # 1. Find all topics with 'OOP' in the name
    cur.execute("SELECT id, name FROM topics WHERE name LIKE '%OOP%'")
    oop_topics = cur.fetchall()
    print(f"OOP Topics: {oop_topics}")
    
    # 2. Get all notes and their associated topic names
    cur.execute("""
        SELECT n.id, n.topic_id, t.name, n.content, n.file_path
        FROM notes n
        LEFT JOIN topics t ON n.topic_id = t.id
    """)
    notes = cur.fetchall()
    print(f"Total notes found: {len(notes)}")
    for note in notes:
        print(f"Note ID: {note[0]}, Topic ID: {note[1]}, Topic Name: {note[2]}, File: {note[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_oop_notes('cognix.db')
    check_oop_notes('jarvis.db')
