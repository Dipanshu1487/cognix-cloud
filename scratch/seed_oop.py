import sqlite3
import os

db_path = 'jarvis.db'

def seed_oop():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Object Oriented Programming"

    try:
        # 1. Subject
        cur.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subject_name,))
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        subject_id = cur.fetchone()[0]

        syllabus = [
            {
                "unit": "UNIT 1: Prerequisites",
                "sections": [
                    {
                        "name": "Prerequisites",
                        "topics": [
                            {
                                "name": "Basic Programming Knowledge",
                                "subtopics": ["Variables", "Data Types", "Control Structures", "Functions"]
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 2: OOP Foundations & Design",
                "sections": [
                    {
                        "name": "OOP Fundamentals",
                        "topics": [
                            {
                                "name": "OOP Fundamentals",
                                "subtopics": ["Principles of OOP", "Modularity", "Reusability", "Maintainability"]
                            }
                        ]
                    },
                    {
                        "name": "System Design",
                        "topics": [
                            {
                                "name": "Problem Solving & System Design",
                                "subtopics": ["Real-world Problem Analysis", "Software Modeling"]
                            }
                        ]
                    },
                    {
                        "name": "UML Modeling",
                        "topics": [
                            {
                                "name": "UML",
                                "subtopics": ["Class Diagram", "Sequence Diagram"]
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 3: Programming Implementation",
                "sections": [
                    {
                        "name": "Language Implementation",
                        "topics": [
                            {
                                "name": "OOP in Programming Languages",
                                "subtopics": ["C++", "Java", "Python", "C#"]
                            },
                            {
                                "name": "Programming Concepts",
                                "subtopics": ["Language Independence", "Adaptability"]
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 4: Core OOP Concepts",
                "sections": [
                    {
                        "name": "Core Pillars",
                        "topics": [
                            {
                                "name": "Core Concepts",
                                "subtopics": ["Encapsulation", "Inheritance", "Polymorphism", "Abstraction", "Exception Handling", "Generic Programming"]
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 5: Design & Development Practices",
                "sections": [
                    {
                        "name": "Design Principles",
                        "topics": [
                            {
                                "name": "Design Principles",
                                "subtopics": ["Best Practices", "Real-world Development"]
                            }
                        ]
                    },
                    {
                        "name": "Skill Development",
                        "topics": [
                            {
                                "name": "Skill Development",
                                "subtopics": ["Problem Solving", "Logical Thinking", "Design Thinking", "UML-based Labs", "Mini Projects"]
                            }
                        ]
                    }
                ]
            }
        ]

        for unit_data in syllabus:
            cur.execute("INSERT OR IGNORE INTO units (subject_id, name) VALUES (?, ?)", (subject_id, unit_data["unit"]))
            cur.execute("SELECT id FROM units WHERE subject_id = ? AND name = ?", (subject_id, unit_data["unit"]))
            unit_id = cur.fetchone()[0]
            
            for section in unit_data["sections"]:
                cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (unit_id, section["name"]))
                section_id = cur.lastrowid
                
                for t in section["topics"]:
                    cur.execute("INSERT INTO topics (section_id, name) VALUES (?, ?)", (section_id, t["name"]))
                    topic_id = cur.lastrowid
                    for st_name in t["subtopics"]:
                        cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, st_name))

        conn.commit()
        print("OOP syllabus integrated successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding OOP: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_oop()
