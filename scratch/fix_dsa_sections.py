import sqlite3
import os

db_path = 'jarvis.db'

def fix_dsa_sections():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Find the Advanced Trees unit
        cur.execute("SELECT id FROM units WHERE name LIKE '%Advanced Trees%'")
        res = cur.fetchone()
        if not res:
            print("Advanced Trees unit not found.")
            return
            
        unit_id = res[0]
        print(f"Fixing sections for Unit ID: {unit_id}")
        
        # Delete the placeholder "General Content" section for this unit
        cur.execute("DELETE FROM sections WHERE unit_id = ? AND name = 'General Content'", (unit_id,))
        
        # Create correct sections
        sections = ["Trees", "AVL Trees", "Red Black Trees", "B-Trees"]
        
        for sec_name in sections:
            cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (unit_id, sec_name))
            section_id = cur.lastrowid
            
            # Map topics to these sections based on names (simplified heuristic)
            if sec_name == "Trees":
                keywords = ["Basic Terminologies", "Binary Trees", "Binary Search Trees"]
            elif sec_name == "AVL Trees":
                keywords = ["Rotations", "Complexity Analysis"] # Simplified
            elif sec_name == "Red Black Trees":
                keywords = ["Properties"]
            else:
                keywords = ["B-Tr"] # Matches "B-Trees" topics
                
            for kw in keywords:
                cur.execute("UPDATE topics SET section_id = ? WHERE unit_id = ? AND name LIKE ?", (section_id, unit_id, f"%{kw}%"))
        
        conn.commit()
        print("DSA sections re-aligned successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_dsa_sections()
