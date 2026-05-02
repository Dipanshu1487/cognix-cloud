import sqlite3
import os

db_path = 'jarvis.db'

def inspect_math_unit():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("--- Unit 29 Structure (Mathematics -> UNIT 1: Ordinary Differential Equations) ---")
    cur.execute("SELECT id, name FROM sections WHERE unit_id = 29")
    sections = cur.fetchall()
    for sec in sections:
        print(f"Section: {sec}")
        cur.execute("SELECT id, name FROM topics WHERE section_id = ?", (sec[0],))
        topics = cur.fetchall()
        for t in topics:
            print(f"  Topic: {t}")
            
    conn.close()

if __name__ == "__main__":
    inspect_math_unit()
