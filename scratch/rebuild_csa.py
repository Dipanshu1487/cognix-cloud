import sqlite3
import os

db_path = 'jarvis.db'

def rebuild_csa():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    subject_names = ["Computer Architecture", "CSA", "COMPUTER ARCHITECTURE (CSA)"]

    try:
        # 1. DELETE existing data
        for name in subject_names:
            cur.execute("SELECT id FROM subjects WHERE name = ?", (name,))
            res = cur.fetchone()
            if res:
                subject_id = res[0]
                print(f"Deleting existing data for: {name} (ID: {subject_id})")
                
                # Nested delete using parent IDs
                cur.execute("""
                    DELETE FROM subtopics WHERE topic_id IN (
                        SELECT id FROM topics WHERE section_id IN (
                            SELECT id FROM sections WHERE unit_id IN (
                                SELECT id FROM units WHERE subject_id = ?
                            )
                        )
                    )
                """, (subject_id,))
                
                cur.execute("""
                    DELETE FROM topics WHERE section_id IN (
                        SELECT id FROM sections WHERE unit_id IN (
                            SELECT id FROM units WHERE subject_id = ?
                        )
                    )
                """, (subject_id,))
                
                cur.execute("""
                    DELETE FROM sections WHERE unit_id IN (
                        SELECT id FROM units WHERE subject_id = ?
                    )
                """, (subject_id,))
                
                cur.execute("DELETE FROM units WHERE subject_id = ?", (subject_id,))
                cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))

        # 2. INSERT fresh data
        main_subject = "COMPUTER ARCHITECTURE (CSA)"
        cur.execute("INSERT INTO subjects (name) VALUES (?)", (main_subject,))
        subject_id = cur.lastrowid

        syllabus = [
            {
                "unit": "Unit 1: Introduction to Computer Technology",
                "sections": [
                    {
                        "name": "Introduction",
                        "topics": [
                            {"name": "Evolution of Computers", "subtopics": ["Evolution of Computers"]},
                            {"name": "Components of Computer", "subtopics": ["Components of Computer"]},
                            {"name": "Performance Measurement", "subtopics": ["Performance Measurement"]},
                            {"name": "Von Neumann Architecture", "subtopics": ["Von Neumann Architecture"]},
                            {"name": "Data Representation", "subtopics": ["Fixed Point", "Floating Point", "Error Detection & Correction"]},
                            {"name": "Multi-core Systems", "subtopics": ["Multi-core Systems"]}
                        ]
                    }
                ]
            },
            {
                "unit": "Unit 2: Instructions & Computer Organization",
                "sections": [
                    {
                        "name": "Sequential Circuits",
                        "topics": [
                            {"name": "Latches", "subtopics": ["Latches"]},
                            {"name": "Flip Flops", "subtopics": ["SR Flip Flop", "JK Flip Flop", "D Flip Flop", "T Flip Flop"]},
                            {"name": "Master Slave Flip Flops", "subtopics": ["Master Slave Flip Flops"]},
                            {"name": "Excitation Table", "subtopics": ["Excitation Table"]},
                            {"name": "Realization of Flip Flops", "subtopics": ["Realization of Flip Flops"]}
                        ]
                    },
                    {
                        "name": "Registers & Counters",
                        "topics": [
                            {"name": "Registers", "subtopics": ["Registers"]},
                            {"name": "Shift Registers", "subtopics": ["Shift Registers"]},
                            {"name": "Counters", "subtopics": ["Counters"]}
                        ]
                    },
                    {
                        "name": "Instruction System",
                        "topics": [
                            {"name": "Instruction Codes", "subtopics": ["Instruction Codes"]},
                            {"name": "Instruction Cycle", "subtopics": ["Instruction Cycle"]},
                            {"name": "Timing & Control", "subtopics": ["Timing & Control"]},
                            {"name": "Memory Reference Instructions", "subtopics": ["Memory Reference Instructions"]}
                        ]
                    },
                    {
                        "name": "CPU Organization & Architecture",
                        "topics": [
                            {"name": "CPU Organization", "subtopics": ["CPU Organization"]},
                            {"name": "Stack Organization", "subtopics": ["Stack Organization"]},
                            {"name": "Instruction Formats", "subtopics": ["Instruction Formats"]},
                            {"name": "Addressing Modes", "subtopics": ["Addressing Modes"]},
                            {"name": "Data Transfer & Manipulation", "subtopics": ["Data Transfer & Manipulation"]},
                            {"name": "CISC vs RISC", "subtopics": ["CISC vs RISC"]}
                        ]
                    }
                ]
            },
            {
                "unit": "Unit 3: Computer Arithmetic & Micro-Operations",
                "sections": [
                    {
                        "name": "Arithmetic Operations",
                        "topics": [
                            {"name": "Arithmetic Operations", "subtopics": ["Addition", "Subtraction", "Multiplication", "Division"]},
                            {"name": "Floating Point Arithmetic", "subtopics": ["Floating Point Arithmetic"]},
                            {"name": "Decimal Arithmetic", "subtopics": ["Decimal Arithmetic"]}
                        ]
                    },
                    {
                        "name": "Micro Operations",
                        "topics": [
                            {"name": "Register Transfer", "subtopics": ["Register Transfer"]},
                            {"name": "Bus & Memory Transfer", "subtopics": ["Bus & Memory Transfer"]},
                            {"name": "Arithmetic Micro Ops", "subtopics": ["Arithmetic Micro Ops"]},
                            {"name": "Logic Micro Ops", "subtopics": ["Logic Micro Ops"]},
                            {"name": "Shift Micro Ops", "subtopics": ["Shift Micro Ops"]},
                            {"name": "ALU", "subtopics": ["ALU"]}
                        ]
                    },
                    {
                        "name": "Microprogrammed Control",
                        "topics": [
                            {"name": "Control Memory", "subtopics": ["Control Memory"]},
                            {"name": "Address Sequencing", "subtopics": ["Address Sequencing"]},
                            {"name": "Microprogram Example", "subtopics": ["Microprogram Example"]},
                            {"name": "Control Unit Design", "subtopics": ["Control Unit Design"]}
                        ]
                    }
                ]
            },
            {
                "unit": "Unit 4: Memory Hierarchy & Storage",
                "sections": [
                    {
                        "name": "Memory & Cache",
                        "topics": [
                            {"name": "Memory Hierarchy", "subtopics": ["Memory Hierarchy"]},
                            {"name": "Semiconductor Memory", "subtopics": ["RAM", "ROM"]},
                            {"name": "Cache Memory", "subtopics": ["Mapping Techniques", "Performance Factors"]},
                            {"name": "Virtual Memory", "subtopics": ["Paging", "Segmentation"]}
                        ]
                    },
                    {
                        "name": "Storage & I/O",
                        "topics": [
                            {"name": "Secondary Storage", "subtopics": ["RAID"]},
                            {"name": "Input Output Organization", "subtopics": ["I/O Interface"]},
                            {"name": "Programmed I/O", "subtopics": ["Programmed I/O"]},
                            {"name": "Memory Mapped I/O", "subtopics": ["Memory Mapped I/O"]},
                            {"name": "Interrupt Driven I/O", "subtopics": ["Interrupt Driven I/O"]},
                            {"name": "DMA", "subtopics": ["DMA"]}
                        ]
                    }
                ]
            },
            {
                "unit": "Unit 5: Advanced Topics & Parallel Processing",
                "sections": [
                    {
                        "name": "Pipeline & Parallelism",
                        "topics": [
                            {"name": "Pipeline Architecture", "subtopics": ["Pipeline Architecture"]},
                            {"name": "Instruction Pipelining", "subtopics": ["Instruction Pipelining"]},
                            {"name": "Parallel Processing Basics", "subtopics": ["Multi-core Systems"]},
                            {"name": "Multiprocessors", "subtopics": ["Interconnection Structures", "Arbitration", "Communication & Synchronization", "Cache Coherence"]}
                        ]
                    },
                    {
                        "name": "Optimization",
                        "topics": [
                            {"name": "Performance Optimization", "subtopics": ["Performance Optimization"]},
                            {"name": "Amdahl’s Law", "subtopics": ["Amdahl’s Law"]},
                            {"name": "Parallel Programming Techniques", "subtopics": ["Parallel Programming Techniques"]}
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
        print("CSA syllabus rebuilt successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error rebuilding CSA: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    rebuild_csa()
