import sqlite3
import os

db_path = 'jarvis.db'

def rebuild_dsa():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Advanced Data Structures"

    try:
        # --- STEP 1: DELETE OLD DATA ---
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        res = cur.fetchone()
        if res:
            subject_id = res[0]
            print(f"Deleting existing DSA data (ID: {subject_id})...")
            
            # 1. subtopics
            cur.execute("""
                DELETE FROM subtopics WHERE topic_id IN (
                    SELECT id FROM topics WHERE section_id IN (
                        SELECT id FROM sections WHERE unit_id IN (
                            SELECT id FROM units WHERE subject_id = ?
                        )
                    )
                )
            """, (subject_id,))
            
            # 2. topics
            cur.execute("""
                DELETE FROM topics WHERE section_id IN (
                    SELECT id FROM sections WHERE unit_id IN (
                        SELECT id FROM units WHERE subject_id = ?
                    )
                )
            """, (subject_id,))
            
            # 3. sections
            cur.execute("""
                DELETE FROM sections WHERE unit_id IN (
                    SELECT id FROM units WHERE subject_id = ?
                )
            """, (subject_id,))
            
            # 4. units
            cur.execute("DELETE FROM units WHERE subject_id = ?", (subject_id,))
            
            # 5. subject
            cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            print("Old DSA data cleared.")
        else:
            print("No existing DSA data found.")

        # --- STEP 2: BUILD CLEAN HIERARCHY ---
        print("Inserting fresh DSA hierarchy...")
        
        # Subject
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
        subject_id = cur.lastrowid
        
        syllabus = [
            {
                "unit": "UNIT 1: Advanced Trees",
                "sections": [
                    {
                        "name": "Trees",
                        "topics": [
                            {"name": "Basic Terminologies", "subtopics": ["Basic Terminologies"]},
                            {"name": "Binary Trees", "subtopics": ["Binary Trees"]},
                            {
                                "name": "Binary Search Trees", 
                                "subtopics": ["Inorder", "Preorder", "Postorder", "Insert", "Delete", "Search"]
                            }
                        ]
                    },
                    {
                        "name": "AVL Trees",
                        "topics": [
                            {"name": "Rotations", "subtopics": ["Rotations"]},
                            {"name": "Insertions", "subtopics": ["Insertions"]},
                            {"name": "Deletions", "subtopics": ["Deletions"]},
                            {"name": "Complexity Analysis", "subtopics": ["Complexity Analysis"]}
                        ]
                    },
                    {
                        "name": "Red Black Trees",
                        "topics": [
                            {"name": "Properties", "subtopics": ["Properties"]},
                            {"name": "Insertions", "subtopics": ["Insertions"]},
                            {"name": "Deletions", "subtopics": ["Deletions"]},
                            {"name": "Applications", "subtopics": ["Applications"]}
                        ]
                    },
                    {
                        "name": "B-Trees",
                        "topics": [
                            {"name": "Properties", "subtopics": ["Properties"]},
                            {"name": "Insertions", "subtopics": ["Insertions"]},
                            {"name": "Deletions", "subtopics": ["Deletions"]},
                            {"name": "Search Operations", "subtopics": ["Search Operations"]}
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 2: Hashing",
                "sections": [
                    {
                        "name": "Basics",
                        "topics": [
                            {"name": "General Idea", "subtopics": ["General Idea"]},
                            {"name": "Hash Function", "subtopics": ["Hash Function"]},
                            {"name": "Separate Chaining", "subtopics": ["Separate Chaining"]}
                        ]
                    },
                    {
                        "name": "Open Addressing",
                        "topics": [
                            {"name": "Linear Probing", "subtopics": ["Linear Probing"]},
                            {"name": "Quadratic Probing", "subtopics": ["Quadratic Probing"]},
                            {"name": "Double Hashing", "subtopics": ["Double Hashing"]}
                        ]
                    },
                    {
                        "name": "Advanced Hashing",
                        "topics": [
                            {"name": "Universal Hashing", "subtopics": ["Universal Hashing"]},
                            {"name": "Extendible Hashing", "subtopics": ["Extendible Hashing"]}
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 3: Heaps and Priority Queues",
                "sections": [
                    {
                        "name": "Binary Heap",
                        "topics": [
                            {"name": "Structure", "subtopics": ["Structure"]},
                            {"name": "Insertions", "subtopics": ["Insertions"]},
                            {"name": "Deletions", "subtopics": ["Deletions"]}
                        ]
                    },
                    {
                        "name": "Binomial Heap",
                        "topics": [
                            {"name": "Structure", "subtopics": ["Structure"]},
                            {"name": "Operations", "subtopics": ["Operations"]},
                            {"name": "Complexity Analysis", "subtopics": ["Complexity Analysis"]}
                        ]
                    },
                    {
                        "name": "Fibonacci Heap",
                        "topics": [
                            {"name": "Structure", "subtopics": ["Structure"]},
                            {"name": "Decrease Key", "subtopics": ["Decrease Key"]},
                            {"name": "Delete", "subtopics": ["Delete"]},
                            {"name": "Amortized Analysis", "subtopics": ["Amortized Analysis"]}
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 4: Graph Data Structures",
                "sections": [
                    {
                        "name": "Representation",
                        "topics": [
                            {"name": "Adjacency List", "subtopics": ["Adjacency List"]},
                            {"name": "Adjacency Matrix", "subtopics": ["Adjacency Matrix"]},
                            {"name": "Edge List", "subtopics": ["Edge List"]}
                        ]
                    },
                    {
                        "name": "Traversal",
                        "topics": [
                            {"name": "BFS", "subtopics": ["BFS"]},
                            {"name": "DFS", "subtopics": ["DFS"]}
                        ]
                    },
                    {
                        "name": "Algorithms",
                        "topics": [
                            {"name": "Topological Sort", "subtopics": ["Topological Sort"]},
                            {"name": "Dijkstra", "subtopics": ["Dijkstra"]},
                            {"name": "Bellman-Ford", "subtopics": ["Bellman-Ford"]},
                            {"name": "Floyd-Warshall", "subtopics": ["Floyd-Warshall"]}
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 5: Advanced Topics",
                "sections": [
                    {
                        "name": "Disjoint Set",
                        "topics": [
                            {"name": "Equivalence Relation", "subtopics": ["Equivalence Relation"]},
                            {"name": "Union-Find", "subtopics": ["Union-Find"]},
                            {"name": "Path Compression", "subtopics": ["Path Compression"]}
                        ]
                    },
                    {
                        "name": "String Matching",
                        "topics": [
                            {"name": "Naive Algorithm", "subtopics": ["Naive Algorithm"]},
                            {"name": "Rabin-Karp Algorithm", "subtopics": ["Rabin-Karp Algorithm"]}
                        ]
                    }
                ]
            }
        ]

        for u_data in syllabus:
            cur.execute("INSERT INTO units (subject_id, name) VALUES (?, ?)", (subject_id, u_data["unit"]))
            unit_id = cur.lastrowid
            
            for sec in u_data["sections"]:
                cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (unit_id, sec["name"]))
                section_id = cur.lastrowid
                
                for t in sec["topics"]:
                    cur.execute("INSERT INTO topics (section_id, name) VALUES (?, ?)", (section_id, t["name"]))
                    topic_id = cur.lastrowid
                    for st_name in t["subtopics"]:
                        cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, st_name))

        conn.commit()
        print("DSA syllabus rebuilt successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error rebuilding DSA: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    rebuild_dsa()
