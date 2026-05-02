import sqlite3
import os

db_path = 'jarvis.db'

def inspect_ode():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("--- Subjects ---")
    cur.execute("SELECT id, name FROM subjects")
    subjects = cur.fetchall()
    for s in subjects:
        print(s)
        
    print("\n--- Units for Subject 'Ordinary Differential Equations' (if it exists) ---")
    cur.execute("SELECT id, name FROM subjects WHERE name = 'Ordinary Differential Equations'")
    ode_subj = cur.fetchone()
    if ode_subj:
        ode_subj_id = ode_subj[0]
        cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (ode_subj_id,))
        units = cur.fetchall()
        for u in units:
            print(f"Unit: {u}")
            # Check sections/topics under this unit
            cur.execute("SELECT id, name FROM sections WHERE unit_id = ?", (u[0],))
            sections = cur.fetchall()
            for sec in sections:
                print(f"  Section: {sec}")
                cur.execute("SELECT id, name FROM topics WHERE section_id = ?", (sec[0],))
                topics = cur.fetchall()
                for t in topics:
                    print(f"    Topic: {t}")
    else:
        print("Subject 'Ordinary Differential Equations' not found.")
        
    print("\n--- Mathematics Subject ---")
    cur.execute("SELECT id, name FROM subjects WHERE name = 'Mathematics'")
    math_subj = cur.fetchone()
    if math_subj:
        print(math_subj)
        cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (math_subj[0],))
        math_units = cur.fetchall()
        for u in math_units:
            print(f"Math Unit: {u}")
    else:
        print("Mathematics subject not found.")
        
    conn.close()

if __name__ == "__main__":
    inspect_ode()
