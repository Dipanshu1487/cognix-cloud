import sqlite3
import os

db_path = 'jarvis.db'

def clean_oop_units():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM subjects WHERE name = 'Object Oriented Programming'")
        subj = cur.fetchone()
        if not subj:
            print("Subject not found")
            return
            
        subj_id = subj[0]
        
        # Select units that don't start with 'UNIT'
        cur.execute("SELECT id, name FROM units WHERE subject_id = ? AND name NOT LIKE 'UNIT %'", (subj_id,))
        old_units = cur.fetchall()
        
        for unit in old_units:
            unit_id = unit[0]
            unit_name = unit[1]
            print(f"Deleting old unit: {unit_name} (ID: {unit_id})")
            
            # Delete subtopic_progress for subtopics of topics in this unit
            cur.execute("""
                DELETE FROM subtopic_progress WHERE subtopic_id IN (
                    SELECT id FROM subtopics WHERE topic_id IN (
                        SELECT id FROM topics WHERE unit_id = ?
                    )
                )
            """, (unit_id,))
            
            # Delete subtopics
            cur.execute("""
                DELETE FROM subtopics WHERE topic_id IN (
                    SELECT id FROM topics WHERE unit_id = ?
                )
            """, (unit_id,))
            
            # Delete topics
            cur.execute("DELETE FROM topics WHERE unit_id = ?", (unit_id,))
            
            # Delete unit
            cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
            
        conn.commit()
        print("Cleanup successful.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_oop_units()
