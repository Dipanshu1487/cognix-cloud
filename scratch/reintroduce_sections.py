import sqlite3
import os

db_path = 'jarvis.db'

def reintroduce_sections():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("Re-introducing 'sections' layer...")
        
        # 0. Drop view that depends on topics
        cur.execute("DROP VIEW IF EXISTS topic_progress;")
        
        # 1. Create sections table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
            )
        """)
        
        # 2. Add section_id to topics
        cur.execute("PRAGMA table_info(topics);")
        columns = [col[1] for col in cur.fetchall()]
        if 'section_id' not in columns:
            cur.execute("ALTER TABLE topics ADD COLUMN section_id INTEGER;")
            
        # 3. Create a default section for every unit and move topics there
        cur.execute("SELECT id, name FROM units")
        units = cur.fetchall()
        for unit_id, unit_name in units:
            # Create "General" or use unit name as section name for now
            section_name = "General Content"
            
            # Smart logic for DSA: if unit is "Advanced Trees", we might need more sections.
            # But for a general fix, we'll start with one section per unit.
            cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (unit_id, section_name))
            section_id = cur.lastrowid
            
            # Move topics from this unit to this section
            cur.execute("UPDATE topics SET section_id = ? WHERE unit_id = ?", (section_id, unit_id))
            
        # 4. Recreate topics table to remove unit_id and enforce section_id
        cur.execute("ALTER TABLE topics RENAME TO topics_old;")
        cur.execute("""
            CREATE TABLE topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE
            )
        """)
        
        cur.execute("""
            INSERT INTO topics (id, section_id, name, description)
            SELECT id, section_id, name, description FROM topics_old
        """)
        
        cur.execute("DROP TABLE topics_old;")

        # 5. Recreate view
        cur.execute("""
            CREATE VIEW topic_progress AS
            SELECT 
                t.id as topic_id,
                t.name as topic_name,
                COUNT(st.id) as total_subtopics,
                AVG(sp.accuracy) as avg_accuracy,
                SUM(sp.attempts) as total_attempts
            FROM topics t
            LEFT JOIN subtopics st ON t.id = st.topic_id
            LEFT JOIN subtopic_progress sp ON st.id = sp.subtopic_id
            GROUP BY t.id;
        """)
        
        print("Database schema restored to 5 levels (Subject -> Unit -> Section -> Topic).")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reintroduce_sections()
