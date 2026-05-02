import sqlite3
import os

db_path = 'jarvis.db'

def seed_math():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_name = "Mathematics"

    try:
        # 1. Subject
        cur.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subject_name,))
        cur.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        subject_id = cur.fetchone()[0]

        syllabus = [
            {
                "unit": "UNIT 1: Ordinary Differential Equations",
                "sections": [
                    {
                        "name": "Ordinary Differential Equations",
                        "topics": [
                            "First Order Differential Equations",
                            "Linear Differential Equations (nth order)",
                            "Complementary Function",
                            "Particular Integral",
                            "Euler Homogeneous Differential Equation",
                            "Method of Variation of Parameters",
                            "Applications"
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 2: Laplace Transform",
                "sections": [
                    {
                        "name": "Laplace Transform",
                        "topics": [
                            "Introduction", "Existence Theorem", "Properties", "Laplace Transform of Derivatives",
                            "Laplace Transform of Integrals", "Inverse Laplace Transform", "Laplace Transform of Periodic Functions",
                            "Unit Step Function", "Dirac Delta Function", "Convolution Theorem", "Applications"
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 3: Fourier Series",
                "sections": [
                    {
                        "name": "Fourier Series",
                        "topics": [
                            "Periodic Functions", "Fourier Series (period 2π)", "Euler’s Formula",
                            "Fourier Series (Arbitrary Period)", "Change of Intervals", "Even and Odd Functions",
                            "Half Range Sine Series", "Half Range Cosine Series"
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 4: Partial Differential Equations",
                "sections": [
                    {
                        "name": "Partial Differential Equations",
                        "topics": [
                            "Introduction", "Linear PDE (Constant Coefficients)", "Separation of Variables"
                        ]
                    }
                ]
            },
            {
                "unit": "UNIT 5: Statistical Techniques",
                "sections": [
                    {
                        "name": "Statistical Measures",
                        "topics": [
                            "Measures of Central Tendency", "Moments", "Moment Generating Function",
                            "Skewness", "Kurtosis", "Correlation", "Rank Correlation"
                        ]
                    },
                    {
                        "name": "Regression Analysis",
                        "topics": [
                            {
                                "name": "Regression Analysis",
                                "subtopics": [
                                    "Regression Line (Y on X)", "Regression Line (X on Y)",
                                    "Regression Coefficients", "Properties of Regression Coefficients"
                                ]
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
                    if isinstance(t, dict):
                        # Has subtopics
                        cur.execute("INSERT INTO topics (section_id, name) VALUES (?, ?)", (section_id, t["name"]))
                        topic_id = cur.lastrowid
                        for st_name in t["subtopics"]:
                            cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, st_name))
                    else:
                        # Simple topic
                        cur.execute("INSERT INTO topics (section_id, name) VALUES (?, ?)", (section_id, t))
                        topic_id = cur.lastrowid
                        # Auto-create subtopic for system compatibility
                        cur.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, t))

        conn.commit()
        print("Mathematics syllabus integrated successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding Math: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_math()
