import sqlite3
import os

db_path = 'jarvis.db'

def fix_hierarchy():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. Identify incorrect subject
        cur.execute("SELECT id FROM subjects WHERE name = 'Ordinary Differential Equations'")
        res = cur.fetchone()
        if not res:
            print("Subject 'Ordinary Differential Equations' not found. Already fixed?")
        else:
            old_subj_id = res[0]
            print(f"Found incorrect subject ID: {old_subj_id}")
            
            # 2. Identify Mathematics subject
            cur.execute("SELECT id FROM subjects WHERE name = 'Mathematics'")
            res = cur.fetchone()
            if not res:
                print("Mathematics subject not found. Creating it...")
                cur.execute("INSERT INTO subjects (name) VALUES ('Mathematics')")
                math_subj_id = cur.lastrowid
            else:
                math_subj_id = res[0]
            print(f"Mathematics subject ID: {math_subj_id}")
            
            # 3. Ensure ODE unit exists under Mathematics
            cur.execute("SELECT id FROM units WHERE subject_id = ? AND name LIKE '%Ordinary Differential Equations%'", (math_subj_id,))
            res = cur.fetchone()
            if not res:
                print("ODE unit not found under Mathematics. Creating it...")
                cur.execute("INSERT INTO units (subject_id, name) VALUES (?, 'Ordinary Differential Equations')", (math_subj_id,))
                target_unit_id = cur.lastrowid
            else:
                target_unit_id = res[0]
            print(f"Target ODE unit ID: {target_unit_id}")
            
            # 4. Reassign sections from units of old subject to the target unit
            cur.execute("SELECT id FROM units WHERE subject_id = ?", (old_subj_id,))
            old_units = cur.fetchall()
            for unit_id_tuple in old_units:
                old_unit_id = unit_id_tuple[0]
                print(f"Reassigning sections from old unit {old_unit_id} to unit {target_unit_id}")
                cur.execute("UPDATE sections SET unit_id = ? WHERE unit_id = ?", (target_unit_id, old_unit_id))
            
            # 5. Delete old subject (referential integrity should handle units if ON DELETE CASCADE, 
            # but we've already moved the sections. Let's delete the old units manually just in case)
            cur.execute("DELETE FROM units WHERE subject_id = ?", (old_subj_id,))
            cur.execute("DELETE FROM subjects WHERE id = ?", (old_subj_id,))
            print("Incorrect subject 'Ordinary Differential Equations' deleted and topics reassigned.")
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error fixing hierarchy: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_hierarchy()
