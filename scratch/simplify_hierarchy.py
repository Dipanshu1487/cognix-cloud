import sqlite3
import os

db_path = 'jarvis.db'

def simplify_hierarchy():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("Migrating topics to link directly to units...")
        
        # 0. Drop view that depends on topics
        cur.execute("DROP VIEW IF EXISTS topic_progress;")
        
        # 1. Add unit_id to topics if missing
        cur.execute("PRAGMA table_info(topics);")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'unit_id' not in columns:
            cur.execute("ALTER TABLE topics ADD COLUMN unit_id INTEGER;")
        
        # 2. Update unit_id based on current section_id
        cur.execute("""
            UPDATE topics
            SET unit_id = (SELECT unit_id FROM sections WHERE id = topics.section_id)
            WHERE section_id IS NOT NULL
        """)
        
        # 4. Recreate topics table to remove section_id and clean up
        cur.execute("ALTER TABLE topics RENAME TO topics_old;")
        cur.execute("""
            CREATE TABLE topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
            );
        """)
        
        cur.execute("""
            INSERT INTO topics (id, unit_id, name, description)
            SELECT id, unit_id, name, description FROM topics_old
        """)
        
        cur.execute("DROP TABLE topics_old;")
        
        # 5. Delete sections table
        cur.execute("DROP TABLE IF EXISTS sections;")

        # 6. Recreate view
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
        
        print("Database migration successful.")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    simplify_hierarchy()
