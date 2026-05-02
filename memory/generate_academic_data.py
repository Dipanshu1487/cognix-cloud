import json
import sqlite3
import os

# Syllabus Expansion Data
syllabus_data = [
    {
        "subject": "Mathematics",
        "units": [
            {
                "name": "Ordinary Differential Equations",
                "topics": [
                    {
                        "name": "First Order Differential Equations",
                        "subtopics": [
                            {"name": "Linear Equations", "tags": "linear, integrating factor", "difficulty": "medium"},
                            {"name": "Exact Equations", "tags": "exact, partial derivatives", "difficulty": "hard"},
                            {"name": "Bernoulli Equations", "tags": "bernoulli, substitution", "difficulty": "medium"}
                        ]
                    },
                    {
                        "name": "Higher Order Linear Differential Equations",
                        "subtopics": [
                            {"name": "Constant Coefficients", "tags": "homogeneous, auxiliary equation", "difficulty": "easy"},
                            {"name": "Cauchy-Euler Equations", "tags": "variable coefficients", "difficulty": "medium"}
                        ]
                    }
                ]
            },
            {
                "name": "Laplace Transform",
                "topics": [
                    {
                        "name": "Definition and Properties",
                        "subtopics": [
                            {"name": "Linearity Property", "tags": "linearity, transform", "difficulty": "easy"},
                            {"name": "First Shifting Theorem", "tags": "shifting, translation", "difficulty": "medium"}
                        ]
                    },
                    {
                        "name": "Inverse Laplace Transform",
                        "subtopics": [
                            {"name": "Partial Fractions", "tags": "decomposition, algebraic", "difficulty": "medium"},
                            {"name": "Convolution Theorem", "tags": "convolution, integral", "difficulty": "hard"}
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
                        "name": "Binary Search Tree",
                        "subtopics": [
                            {"name": "Inorder Traversal", "tags": "recursion, sorting", "difficulty": "easy"},
                            {"name": "BST Insertion", "tags": "leaf node, recursive", "difficulty": "easy"},
                            {"name": "BST Deletion", "tags": "successor, predecessor", "difficulty": "hard"}
                        ]
                    },
                    {
                        "name": "AVL Trees",
                        "subtopics": [
                            {"name": "LL and RR Rotations", "tags": "single rotation, balance", "difficulty": "medium"},
                            {"name": "LR and RL Rotations", "tags": "double rotation, balance", "difficulty": "hard"}
                        ]
                    }
                ]
            },
            {
                "name": "Graphs",
                "topics": [
                    {
                        "name": "Graph Traversals",
                        "subtopics": [
                            {"name": "BFS", "tags": "queue, shortest path", "difficulty": "medium"},
                            {"name": "DFS", "tags": "stack, recursion, cycle detection", "difficulty": "medium"}
                        ]
                    }
                ]
            }
        ]
    }
]

def generate():
    sql_statements = []
    keyword_mapping = {}
    
    # 1. SQL Inserts
    for subj in syllabus_data:
        sql_statements.append(f"INSERT OR IGNORE INTO subjects (name) VALUES ('{subj['subject']}');")
        
        for unit in subj['units']:
            sql_statements.append(f"INSERT OR IGNORE INTO units (subject_id, name) SELECT id, '{unit['name']}' FROM subjects WHERE name = '{subj['subject']}';")
            
            for topic in unit['topics']:
                sql_statements.append(f"INSERT OR IGNORE INTO topics (unit_id, name) SELECT id, '{topic['name']}' FROM units WHERE name = '{unit['name']}';")
                
                for sub in topic['subtopics']:
                    sql_statements.append(f"INSERT OR IGNORE INTO subtopics (topic_id, name, tags, difficulty) SELECT id, '{sub['name']}', '{sub['tags']}', '{sub['difficulty']}' FROM topics WHERE name = '{topic['name']}';")
                    
                    # 2. Keyword Mapping
                    name_key = sub['name'].lower()
                    keyword_mapping[name_key] = sub['name']
                    for tag in sub['tags'].split(","):
                        keyword_mapping[tag.strip().lower()] = sub['name']

    # 3. Clean JSON Output
    print(json.dumps(syllabus_data, indent=2))
    print("\n--- SQL INSERTS ---\n")
    print("\n".join(sql_statements))
    print("\n--- KEYWORD MAPPING ---\n")
    print(json.dumps(keyword_mapping, indent=2))

if __name__ == "__main__":
    generate()
