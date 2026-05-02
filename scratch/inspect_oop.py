import sqlite3
import os

db_path = 'jarvis.db'

def inspect_oop_units():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM subjects WHERE name = 'Object Oriented Programming'")
    subj = cur.fetchone()
    if subj:
        subj_id = subj[0]
        cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (subj_id,))
        units = cur.fetchall()
        print("Units for OOP:")
        for u in units:
            print(u)
    else:
        print("Subject not found")
        
    conn.close()

if __name__ == "__main__":
    inspect_oop_units()
