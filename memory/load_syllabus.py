import sqlite3
import os
import json

def load_academic_system():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarvis.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Update Schema
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        cur.executescript(f.read())

    # 2. Syllabus Data (Normalized & Expanded)
    syllabus = [
        {
            "subject": "Ordinary Differential Equations",
            "units": [
                {
                    "name": "First Order ODE",
                    "topics": [
                        {
                            "name": "Linear Differential Equations",
                            "subtopics": [
                                {"name": "Integrating Factor Method", "tags": "linear, integrating factor", "difficulty": "medium"},
                                {"name": "Bernoulli Substitution", "tags": "bernoulli, substitution", "difficulty": "medium"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "subject": "Advanced Data Structures",
            "units": [
                {
                    "name": "Trees",
                    "topics": [
                        {
                            "name": "Binary Search Trees",
                            "subtopics": [
                                {"name": "Inorder Traversal", "tags": "inorder, sorting, recursive", "difficulty": "easy"},
                                {"name": "BST Deletion", "tags": "successor, predecessor, deletion", "difficulty": "hard"}
                            ]
                        },
                        {
                            "name": "AVL Trees",
                            "subtopics": [
                                {"name": "Self Balancing Rotations", "tags": "ll, rr, lr, rl, rotations", "difficulty": "hard"}
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    for subj_data in syllabus:
        cur.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subj_data["subject"],))
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subj_data["subject"],))
        subject_id = cur.fetchone()[0]
        
        for unit_data in subj_data["units"]:
            cur.execute("INSERT OR IGNORE INTO units (subject_id, name) VALUES (?, ?)", (subject_id, unit_data["name"]))
            cur.execute("SELECT id FROM units WHERE subject_id = ? AND name = ?", (subject_id, unit_data["name"]))
            unit_id = cur.fetchone()[0]
            
            for topic_data in unit_data["topics"]:
                cur.execute("INSERT OR IGNORE INTO topics (unit_id, name) VALUES (?, ?)", (unit_id, topic_data["name"]))
                cur.execute("SELECT id FROM topics WHERE unit_id = ? AND name = ?", (unit_id, topic_data["name"]))
                topic_id = cur.fetchone()[0]
                
                for sub in topic_data["subtopics"]:
                    cur.execute("INSERT OR IGNORE INTO subtopics (topic_id, name, tags, difficulty) VALUES (?, ?, ?, ?)",
                                (topic_id, sub["name"], sub["tags"], sub["difficulty"]))
                    sub_id = cur.lastrowid
                    cur.execute("INSERT OR IGNORE INTO subtopic_progress (subtopic_id) VALUES (?)", (sub_id,))

    conn.commit()
    conn.close()
    print("Academic System Integrated Successfully.")

if __name__ == "__main__":
    load_academic_system()
