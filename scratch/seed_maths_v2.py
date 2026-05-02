import sqlite3
import os

db_path = 'jarvis.db'

def reseed_maths():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Mathematics"

    try:
        # 1. Subject
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO subjects (name) VALUES (?)", (subject_name,))
            subject_id = cur.lastrowid
        else:
            subject_id = res[0]
            
            # Delete existing data for Mathematics to replace it
            print(f"Deleting existing data for Mathematics (ID: {subject_id})...")
            
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
                "unit": "Unit 1: Ordinary Differential Equations (ODE)",
                "topics": [
                    {"name": "First Order Differential Equations", "subtopics": ["Separable Equations", "Homogeneous Equations"]},
                    {"name": "Higher Order Linear Differential Equations", "subtopics": ["Complementary Function", "Particular Integral"]},
                    {"name": "Euler Homogeneous Equations", "subtopics": ["Euler Homogeneous Equations"]},
                    {"name": "Method of Variation of Parameters", "subtopics": ["Method of Variation of Parameters"]}
                ]
            },
            {
                "unit": "Unit 2: Laplace Transform",
                "topics": [
                    {"name": "Basics of Laplace Transform", "subtopics": ["Definition", "Properties"]},
                    {"name": "Laplace of Derivatives & Integrals", "subtopics": ["Laplace of Derivatives & Integrals"]},
                    {"name": "Inverse Laplace Transform", "subtopics": ["Inverse Laplace Transform"]},
                    {"name": "Special Functions", "subtopics": ["Unit Step Function", "Dirac Delta Function"]},
                    {"name": "Convolution Theorem", "subtopics": ["Convolution Theorem"]},
                    {"name": "Applications of Laplace Transform", "subtopics": ["Applications of Laplace Transform"]}
                ]
            },
            {
                "unit": "Unit 3: Fourier Series",
                "topics": [
                    {"name": "Periodic Functions", "subtopics": ["Periodic Functions"]},
                    {"name": "Fourier Series Representation", "subtopics": ["Euler Formula"]},
                    {"name": "Types of Functions", "subtopics": ["Even Functions", "Odd Functions"]},
                    {"name": "Change of Interval", "subtopics": ["Change of Interval"]},
                    {"name": "Half Range Series", "subtopics": ["Sine Series", "Cosine Series"]}
                ]
            },
            {
                "unit": "Unit 4: Partial Differential Equations (PDE)",
                "topics": [
                    {"name": "Introduction to PDE", "subtopics": ["Introduction to PDE"]},
                    {"name": "Linear Partial Differential Equations", "subtopics": ["Linear Partial Differential Equations"]},
                    {"name": "Method of Separation of Variables", "subtopics": ["Method of Separation of Variables"]}
                ]
            },
            {
                "unit": "Unit 5: Statistical Techniques",
                "topics": [
                    {"name": "Measures of Central Tendency", "subtopics": ["Mean", "Median", "Mode"]},
                    {"name": "Moments", "subtopics": ["Moments"]},
                    {"name": "Moment Generating Function (MGF)", "subtopics": ["Moment Generating Function (MGF)"]},
                    {"name": "Skewness & Kurtosis", "subtopics": ["Skewness & Kurtosis"]},
                    {"name": "Correlation", "subtopics": ["Karl Pearson Correlation", "Rank Correlation"]},
                    {"name": "Regression Analysis", "subtopics": ["Regression Lines", "Regression Coefficients"]}
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
        print("Mathematics syllabus updated successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating Mathematics: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reseed_maths()
