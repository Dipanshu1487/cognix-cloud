import sqlite3
import os
import datetime
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cognix.db')

def fetch_subjects():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subjects")
    res = cur.fetchall()
    conn.close()
    return res

def fetch_units(subject_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (subject_id,))
    res = cur.fetchall()
    conn.close()
    return res

def fetch_sections(unit_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM sections WHERE unit_id = ?", (unit_id,))
    res = cur.fetchall()
    conn.close()
    return res

def fetch_topics(section_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM topics WHERE section_id = ?", (section_id,))
    res = cur.fetchall()
    conn.close()
    return res

def insert_note(topic_id, content, file_path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (topic_id, content, file_path) VALUES (?, ?, ?)", (topic_id, content, file_path))
    conn.commit()
    conn.close()

def insert_question(topic_id, question_text, difficulty, answer, explanation, file_path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO questions (topic_id, question_text, difficulty, answer, explanation, file_path) VALUES (?, ?, ?, ?, ?, ?)", (topic_id, question_text, difficulty, answer, explanation, file_path))
    conn.commit()
    conn.close()

def get_topic_details(topic_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name as subject, u.name as unit, sec.name as section, t.name as topic
        FROM topics t
        LEFT JOIN sections sec ON t.section_id = sec.id
        LEFT JOIN units u ON sec.unit_id = u.id
        LEFT JOIN subjects s ON u.subject_id = s.id
        WHERE t.id = ?
    """, (topic_id,))
    res = cur.fetchone()
    conn.close()
    return dict(res) if res else None

def get_notes(topic_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE topic_id = ? ORDER BY created_at DESC", (topic_id,))
    res = cur.fetchall()
    conn.close()
    return [dict(row) for row in res]

def get_questions(topic_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions WHERE topic_id = ? ORDER BY created_at DESC", (topic_id,))
    res = cur.fetchall()
    conn.close()
    return [dict(row) for row in res]

def mark_topic_studied(user_id, topic_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM progress WHERE topic_id = ? AND user_id = ?", (topic_id, user_id))
    row = cur.fetchone()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row:
        cur.execute("UPDATE progress SET studied = 1, last_accessed = ? WHERE topic_id = ? AND user_id = ?", (now, topic_id, user_id))
    else:
        cur.execute("INSERT INTO progress (user_id, topic_id, studied, practiced, correct, attempts, last_accessed) VALUES (?, ?, 1, 0, 0, 0, ?)", (user_id, topic_id, now))
    
    # Log session
    cur.execute("INSERT INTO study_sessions (user_id, topic_id, duration_minutes) VALUES (?, ?, ?)", (user_id, topic_id, 0)) # Placeholder duration
    
    conn.commit()
    conn.close()

def update_practice(user_id, topic_id, is_correct):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, attempts, correct FROM progress WHERE topic_id = ? AND user_id = ?", (topic_id, user_id))
    row = cur.fetchone()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    correct_inc = 1 if is_correct else 0
    if row:
        cur.execute("UPDATE progress SET practiced = 1, attempts = attempts + 1, correct = correct + ?, last_accessed = ? WHERE topic_id = ? AND user_id = ?", (correct_inc, now, topic_id, user_id))
    else:
        cur.execute("INSERT INTO progress (user_id, topic_id, studied, practiced, correct, attempts, last_accessed) VALUES (?, ?, 0, 1, ?, 1, ?)", (user_id, topic_id, correct_inc, now))
    
    # Log attempt
    cur.execute("INSERT INTO practice_attempts (user_id, topic_id, is_correct) VALUES (?, ?, ?)", (user_id, topic_id, 1 if is_correct else 0))
    
    conn.commit()
    conn.close()

def get_progress(user_id, topic_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM progress WHERE topic_id = ? AND user_id = ?", (topic_id, user_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_practice_topics(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT p.topic_id, t.name as topic_name, p.attempts, p.correct
        FROM progress p
        JOIN topics t ON p.topic_id = t.id
        WHERE p.practiced = 1 AND p.user_id = ?
    """, (user_id,))
    res = cur.fetchall()
    conn.close()
    return [dict(row) for row in res]

def get_dashboard_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    stats = {}
    
    # Topics Completed
    cur.execute("SELECT COUNT(*) as c FROM progress WHERE completed = 1 AND user_id = ?", (user_id,))
    stats['topics_completed'] = cur.fetchone()['c']
    
    # Average Accuracy
    cur.execute("SELECT SUM(correct) as sc, SUM(attempts) as sa FROM progress WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    sc = row['sc'] or 0
    sa = row['sa'] or 0
    stats['avg_accuracy'] = (sc / sa * 100) if sa > 0 else 0.0
    
    stats['total_attempts'] = sa
    
    # Active Topics (Studied but not completed)
    cur.execute("""
        SELECT t.name, p.last_accessed
        FROM progress p
        JOIN topics t ON p.topic_id = t.id
        WHERE p.studied = 1 AND p.completed = 0 AND p.user_id = ?
    """, (user_id,))
    stats['active_topics'] = [dict(r) for r in cur.fetchall()]
    
    # Weak Topics
    cur.execute("""
        SELECT t.name, p.attempts, p.correct
        FROM progress p
        JOIN topics t ON p.topic_id = t.id
        WHERE p.attempts >= 2 AND (CAST(p.correct AS FLOAT) / p.attempts) < 0.5 AND p.user_id = ?
    """, (user_id,))
    stats['weak_topics'] = [dict(r) for r in cur.fetchall()]
    
    # Recently Studied
    cur.execute("""
        SELECT t.name, p.last_accessed, p.topic_id, p.completed
        FROM progress p
        JOIN topics t ON p.topic_id = t.id
        WHERE p.user_id = ?
        ORDER BY p.last_accessed DESC
        LIMIT 5
    """, (user_id,))
    stats['recently_studied'] = [dict(r) for r in cur.fetchall()]
    
    # Weak Topics (Opened but not closed)
    cur.execute("""
        SELECT COUNT(*) as c FROM progress 
        WHERE studied = 1 AND completed = 0 AND user_id = ?
    """, (user_id,))
    stats['weak_count'] = cur.fetchone()['c']

    # Total Topics in Curriculum
    cur.execute("SELECT COUNT(*) as c FROM topics")
    stats['total_topics_available'] = cur.fetchone()['c']

    conn.close()
    return stats

def get_overall_progress_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM progress WHERE user_id = ? AND completed = 1) as completed,
            (SELECT COUNT(*) FROM progress WHERE user_id = ? AND studied = 1 AND completed = 0) as learning,
            ((SELECT COUNT(*) FROM topics) - (SELECT COUNT(*) FROM progress WHERE user_id = ?)) as unstarted
    """, (user_id, user_id, user_id))
    res = cur.fetchone()
    conn.close()
    return dict(res) if res else {"completed": 0, "learning": 0, "unstarted": 0}

def get_subject_completion_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            s.name as subject,
            COUNT(t.id) as total_topics,
            SUM(CASE WHEN p.completed = 1 THEN 1 ELSE 0 END) as completed_topics
        FROM subjects s
        LEFT JOIN units u ON s.id = u.subject_id
        LEFT JOIN sections sec ON u.id = sec.unit_id
        LEFT JOIN topics t ON sec.id = t.section_id
        LEFT JOIN progress p ON t.id = p.topic_id AND p.user_id = ?
        GROUP BY s.id
    """, (user_id,))
    
    res = [dict(row) for row in cur.fetchall()]
    conn.close()
    return res

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Ensure users table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            profile_photo TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure core academic tables exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            name TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_id INTEGER,
            name TEXT NOT NULL,
            FOREIGN KEY(unit_id) REFERENCES units(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(section_id) REFERENCES sections(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subtopics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            name TEXT NOT NULL,
            tags TEXT,
            difficulty TEXT,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)

    # Ensure notes table exists with created_at
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            content TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    
    # Ensure questions table exists with created_at and question_text
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            question_text TEXT,
            difficulty TEXT,
            answer TEXT,
            explanation TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    
    # Ensure progress table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic_id INTEGER,
            studied INTEGER DEFAULT 0,
            practiced INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            last_accessed TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    # Ensure user_progress table exists (used by SIS)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic_id INTEGER,
            attempts INTEGER DEFAULT 0,
            accuracy FLOAT DEFAULT 0,
            last_score FLOAT DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    
    # Ensure subtopic_progress table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subtopic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subtopic_id INTEGER NOT NULL,
            attempts INTEGER DEFAULT 0,
            accuracy REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(subtopic_id) REFERENCES subtopics(id)
        )
    """)

    # User-specific history tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic_id INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_minutes INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS practice_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic_id INTEGER,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_correct INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)

    # Admin Requests Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- SEED DEFAULT SUPER ADMIN ---
    cur.execute("SELECT id FROM users WHERE role = 'super_admin'")
    if not cur.fetchone():
        hashed_pw = bcrypt.hashpw(b"Dip@123", bcrypt.gensalt())
        cur.execute(
            "INSERT INTO users (name, username, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("Dipanshu", "dipanshu143", "dipanshu@example.com", hashed_pw, "super_admin")
        )

    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()
    return True

def mark_topic_completed(user_id, topic_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if record exists
    cur.execute("SELECT id FROM progress WHERE user_id = ? AND topic_id = ?", (user_id, topic_id))
    row = cur.fetchone()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row:
        cur.execute("UPDATE progress SET completed = 1, last_accessed = ? WHERE user_id = ? AND topic_id = ?", (now, user_id, topic_id))
    else:
        cur.execute("INSERT INTO progress (user_id, topic_id, studied, completed, last_accessed) VALUES (?, ?, 1, 1, ?)", (user_id, topic_id, now))
    
    conn.commit()
    conn.close()
    return True

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, username, email, role, profile_photo, join_date FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_profile(user_id, name, email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    conn.close()
    return True

def update_profile_photo(user_id, photo_path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_photo = ? WHERE id = ?", (photo_path, user_id))
    conn.commit()
    conn.close()
    return True

def remove_profile_photo(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_photo = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def get_user_achievements(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    achievements = []
    
    # 1. Total Topics Studied
    cur.execute("SELECT COUNT(*) as c FROM progress WHERE user_id = ? AND studied = 1", (user_id,))
    studied_count = cur.fetchone()['c']
    
    if studied_count >= 1:
        achievements.append({"title": "First Steps", "icon": "🌱", "desc": "Started studying a topic."})
    if studied_count >= 10:
        achievements.append({"title": "Dedicated Scholar", "icon": "📚", "desc": "Studied 10+ topics."})
        
    # 2. Perfect Accuracy Practice
    cur.execute("""
        SELECT COUNT(*) as c FROM progress 
        WHERE user_id = ? AND practiced = 1 AND attempts > 0 AND (CAST(correct AS FLOAT) / attempts) >= 0.8
    """, (user_id,))
    high_acc_count = cur.fetchone()['c']
    
    if high_acc_count >= 1:
        achievements.append({"title": "Sharp Mind", "icon": "🎯", "desc": "Scored 80%+ on a topic practice."})
    if high_acc_count >= 5:
        achievements.append({"title": "Master Learner", "icon": "🏆", "desc": "Mastered 5+ topics with high accuracy."})
        
    conn.close()
    return achievements

def hard_reset_academic_progress(user_id):
    """Deletes all academic progress data for a specific user."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Tables to clear
    tables = [
        "progress",
        "user_progress",
        "subtopic_progress",
        "study_sessions",
        "practice_attempts"
    ]
    
    try:
        for table in tables:
            cur.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
        
    return success

def get_pending_admin_requests():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin_requests WHERE status = 'pending' ORDER BY created_at DESC")
    res = [dict(row) for row in cur.fetchall()]
    conn.close()
    return res

def approve_admin_request(request_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get request details
    cur.execute("SELECT * FROM admin_requests WHERE id = ?", (request_id,))
    req = cur.fetchone()
    if not req:
        conn.close()
        return False
    
    req = dict(sqlite3.Row(cur, req))
    
    try:
        # 1. Insert into users table as admin
        cur.execute("""
            INSERT INTO users (name, username, email, password, role)
            VALUES (?, ?, ?, ?, 'admin')
        """, (req['name'], req['username'], req['email'], req['password']))
        
        # 2. Update request status
        cur.execute("UPDATE admin_requests SET status = 'approved' WHERE id = ?", (request_id,))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error approving admin: {e}")
        success = False
    finally:
        conn.close()
    return success

def reject_admin_request(request_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE admin_requests SET status = 'rejected' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return True
