import sqlite3
import os
import json

db_path = 'jarvis.db'

def rebuild_dsa():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Advanced Data Structures"

    try:
        # A. SQL DELETE statements (safe order)
        # We find the subject ID first
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        res = cur.fetchone()
        
        if res:
            subject_id = res[0]
            print(f"Deleting old data for subject: {subject_name} (ID: {subject_id})")
            
            # Delete subtopics
            cur.execute("""
                DELETE FROM subtopics WHERE topic_id IN (
                    SELECT id FROM topics WHERE section_id IN (
                        SELECT id FROM sections WHERE unit_id IN (
                            SELECT id FROM units WHERE subject_id = ?
                        )
                    )
                )
            """, (subject_id,))
            
            # Delete topics
            cur.execute("""
                DELETE FROM topics WHERE section_id IN (
                    SELECT id FROM sections WHERE unit_id IN (
                        SELECT id FROM units WHERE subject_id = ?
                    )
                )
            """, (subject_id,))
            
            # Delete sections
            cur.execute("""
                DELETE FROM sections WHERE unit_id IN (
                    SELECT id FROM units WHERE subject_id = ?
                )
            """, (subject_id,))
            
            # Delete units
            cur.execute("DELETE FROM units WHERE subject_id = ?", (subject_id,))
            
            # Delete subject (we'll re-insert it or ignore if exists)
            cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        else:
            print(f"Subject '{subject_name}' not found, skipping delete.")

        # B. SQL INSERT statements (fully linked hierarchy)
        # 1. Subject
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
        subject_id = cur.lastrowid

        syllabus = {
            "UNIT 1: Advanced Trees": {
                "SECTION: Trees": [
                    {"topic": "Basic Terminologies", "subtopics": ["Basic Terminologies"]},
                    {"topic": "Binary Trees", "subtopics": ["Binary Trees"]},
                    {"topic": "Binary Search Trees", "subtopics": ["Inorder Traversal", "Preorder Traversal", "Postorder Traversal", "Insert Operation", "Delete Operation", "Search Operation"]}
                ],
                "SECTION: AVL Trees": [
                    {"topic": "Rotations", "subtopics": ["Rotations"]},
                    {"topic": "Insertions", "subtopics": ["Insertions"]},
                    {"topic": "Deletions", "subtopics": ["Deletions"]},
                    {"topic": "Complexity Analysis", "subtopics": ["Complexity Analysis"]}
                ],
                "SECTION: Red Black Trees": [
                    {"topic": "Properties", "subtopics": ["Properties"]},
                    {"topic": "Insertions", "subtopics": ["Insertions"]},
                    {"topic": "Deletions", "subtopics": ["Deletions"]},
                    {"topic": "Applications", "subtopics": ["Applications"]}
                ],
                "SECTION: B-Trees": [
                    {"topic": "Properties", "subtopics": ["Properties"]},
                    {"topic": "Insertions", "subtopics": ["Insertions"]},
                    {"topic": "Deletions", "subtopics": ["Deletions"]},
                    {"topic": "Search Operations", "subtopics": ["Search Operations"]}
                ]
            },
            "UNIT 2: Hashing": {
                "SECTION: Basics": [
                    {"topic": "General Idea", "subtopics": ["General Idea"]},
                    {"topic": "Hash Function", "subtopics": ["Hash Function"]},
                    {"topic": "Separate Chaining", "subtopics": ["Separate Chaining"]}
                ],
                "SECTION: Open Addressing": [
                    {"topic": "Linear Probing", "subtopics": ["Linear Probing"]},
                    {"topic": "Quadratic Probing", "subtopics": ["Quadratic Probing"]},
                    {"topic": "Double Hashing", "subtopics": ["Double Hashing"]}
                ],
                "SECTION: Advanced Hashing": [
                    {"topic": "Universal Hashing", "subtopics": ["Universal Hashing"]},
                    {"topic": "Extendible Hashing", "subtopics": ["Extendible Hashing"]}
                ]
            },
            "UNIT 3: Heaps and Priority Queues": {
                "SECTION: Binary Heap": [
                    {"topic": "Structure", "subtopics": ["Structure"]},
                    {"topic": "Insertions", "subtopics": ["Insertions"]},
                    {"topic": "Deletions", "subtopics": ["Deletions"]}
                ],
                "SECTION: Binomial Heap": [
                    {"topic": "Structure", "subtopics": ["Structure"]},
                    {"topic": "Operations", "subtopics": ["Operations"]},
                    {"topic": "Complexity Analysis", "subtopics": ["Complexity Analysis"]}
                ],
                "SECTION: Fibonacci Heap": [
                    {"topic": "Structure", "subtopics": ["Structure"]},
                    {"topic": "Decrease Key", "subtopics": ["Decrease Key"]},
                    {"topic": "Delete", "subtopics": ["Delete"]},
                    {"topic": "Amortized Analysis", "subtopics": ["Amortized Analysis"]}
                ]
            },
            "UNIT 4: Graph Data Structures": {
                "SECTION: Representation": [
                    {"topic": "Adjacency List", "subtopics": ["Adjacency List"]},
                    {"topic": "Adjacency Matrix", "subtopics": ["Adjacency Matrix"]},
                    {"topic": "Edge List", "subtopics": ["Edge List"]}
                ],
                "SECTION: Traversal": [
                    {"topic": "BFS", "subtopics": ["BFS"]},
                    {"topic": "DFS", "subtopics": ["DFS"]}
                ],
                "SECTION: Algorithms": [
                    {"topic": "Topological Sort", "subtopics": ["Topological Sort"]},
                    {"topic": "Dijkstra", "subtopics": ["Dijkstra"]},
                    {"topic": "Bellman-Ford", "subtopics": ["Bellman-Ford"]},
                    {"topic": "Floyd-Warshall", "subtopics": ["Floyd-Warshall"]}
                ]
            },
            "UNIT 5: Advanced Topics": {
                "SECTION: Disjoint Set": [
                    {"topic": "Equivalence Relation", "subtopics": ["Equivalence Relation"]},
                    {"topic": "Union-Find", "subtopics": ["Union-Find"]},
                    {"topic": "Path Compression", "subtopics": ["Path Compression"]}
                ],
                "SECTION: String Matching": [
                    {"topic": "Naive Algorithm", "subtopics": ["Naive Algorithm"]},
                    {"topic": "Rabin-Karp Algorithm", "subtopics": ["Rabin-Karp Algorithm"]}
                ]
            }
        }

        for unit_name, sections in syllabus.items():
            cur.execute("INSERT INTO units (subject_id, name) VALUES (?, ?)", (subject_id, unit_name))
            unit_id = cur.lastrowid
            
            for section_name, topics in sections.items():
                cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (unit_id, section_name))
                section_id = cur.lastrowid
                
                for t_data in topics:
                    cur.execute("INSERT INTO topics (section_id, name) VALUES (?, ?)", (section_id, t_data["topic"]))
                    topic_id = cur.lastrowid
                    
                    for st_name in t_data["subtopics"]:
                        cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, st_name))

        conn.commit()
        print("DSA Hierarchy rebuilt successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error rebuilding DSA: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    rebuild_dsa()
