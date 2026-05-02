import sqlite3
import os

db_path = 'jarvis.db'

def reseed_oop():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Object Oriented Programming"

    try:
        # 1. Subject
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
            subject_id = cur.lastrowid
        else:
            subject_id = res[0]
            
            # Delete existing data for OOP to replace it
            print(f"Deleting existing data for OOP (ID: {subject_id})...")
            
            cur.execute("""
                DELETE FROM subtopic_progress WHERE subtopic_id IN (
                    SELECT id FROM subtopics WHERE topic_id IN (
                        SELECT id FROM topics WHERE unit_id IN (
                            SELECT id FROM units WHERE subject_id = ?
                        )
                    )
                )
            """, (subject_id,))
            
            cur.execute("""
                DELETE FROM subtopics WHERE topic_id IN (
                    SELECT id FROM topics WHERE unit_id IN (
                        SELECT id FROM units WHERE subject_id = ?
                    )
                )
            """, (subject_id,))
            
            cur.execute("""
                DELETE FROM topics WHERE unit_id IN (
                    SELECT id FROM units WHERE subject_id = ?
                )
            """, (subject_id,))
            
            cur.execute("DELETE FROM units WHERE subject_id = ?", (subject_id,))

        print("Inserting new hierarchy...")
        
        syllabus = [
            {
                "unit": "UNIT 1: OOP Fundamentals",
                "topics": [
                    {"name": "Introduction to OOP", "subtopics": ["Introduction to OOP"]},
                    {"name": "Procedural vs Object-Oriented Programming", "subtopics": ["Procedural vs Object-Oriented Programming"]},
                    {"name": "Classes and Objects", "subtopics": ["Classes and Objects"]},
                    {"name": "Encapsulation", "subtopics": ["Encapsulation"]},
                    {"name": "Abstraction", "subtopics": ["Abstraction"]},
                    {"name": "Data Hiding", "subtopics": ["Data Hiding"]},
                    {"name": "Access Modifiers", "subtopics": ["Access Modifiers"]}
                ]
            },
            {
                "unit": "UNIT 2: Inheritance & Polymorphism",
                "topics": [
                    {"name": "Inheritance", "subtopics": ["Types of Inheritance", "Access Control in Inheritance"]},
                    {"name": "Compile-time Polymorphism", "subtopics": ["Function Overloading", "Operator Overloading"]},
                    {"name": "Runtime Polymorphism", "subtopics": ["Method Overriding", "Virtual Functions"]}
                ]
            },
            {
                "unit": "UNIT 3: Constructors & Destructors",
                "topics": [
                    {"name": "Constructors", "subtopics": ["Default Constructor", "Parameterized Constructor", "Copy Constructor", "Constructor Overloading"]},
                    {"name": "Destructors", "subtopics": ["Destructors"]}
                ]
            },
            {
                "unit": "UNIT 4: Exception Handling",
                "topics": [
                    {"name": "Exception Basics", "subtopics": ["Exception Basics"]},
                    {"name": "Try-Catch Blocks", "subtopics": ["Try-Catch Blocks"]},
                    {"name": "Throw Keyword", "subtopics": ["Throw Keyword"]},
                    {"name": "Multiple Catch", "subtopics": ["Multiple Catch"]},
                    {"name": "Custom Exceptions", "subtopics": ["Custom Exceptions"]}
                ]
            },
            {
                "unit": "UNIT 5: Advanced OOP Concepts",
                "topics": [
                    {"name": "Templates / Generics", "subtopics": ["Templates / Generics"]},
                    {"name": "File Handling", "subtopics": ["File Handling"]},
                    {"name": "Standard Template Library (STL)", "subtopics": ["Standard Template Library (STL)"]},
                    {"name": "Friend Functions", "subtopics": ["Friend Functions"]},
                    {"name": "Inline Functions", "subtopics": ["Inline Functions"]}
                ]
            }
        ]

        for u_data in syllabus:
            cur.execute("INSERT INTO units (subject_id, name) VALUES (?, ?)", (subject_id, u_data["unit"]))
            unit_id = cur.lastrowid
            
            for t in u_data["topics"]:
                cur.execute("INSERT INTO topics (unit_id, name) VALUES (?, ?)", (unit_id, t["name"]))
                topic_id = cur.lastrowid
                for st_name in t["subtopics"]:
                    cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, st_name))

        conn.commit()
        print("OOP syllabus updated successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating OOP: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reseed_oop()
