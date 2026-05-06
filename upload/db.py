import os
import datetime
import bcrypt
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def _get_secret(key, default=None):
    """Retrieves secrets from Streamlit or environment variables."""
    try:
        return st.secrets.get(key) or os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)

@st.cache_resource
def get_connection():
    """
    Returns a cached connection object. 
    Strictly uses PostgreSQL (Supabase). No SQLite fallback allowed.
    """
    host = _get_secret("DB_HOST")
    
    if not host:
        print("[DB DEBUG] CRITICAL: DB_HOST not found")
        raise ConnectionError("CRITICAL: DB_HOST not found. Cannot connect to Supabase.")
    
    try:
        conn = psycopg2.connect(
            host=host,
            database=_get_secret("DB_NAME", "postgres"),
            user=_get_secret("DB_USER", "postgres"),
            password=_get_secret("DB_PASS"),
            port=_get_secret("DB_PORT", "5432"),
            connect_timeout=10
        )
        print("[DB DEBUG] Connected to Supabase")
        return conn
    except Exception as e:
        err = f"CRITICAL: Failed to connect to Supabase: {e}"
        print(f"[DB DEBUG] {err}")
        raise ConnectionError(err)

# --- CORE DATABASE FUNCTIONS ---

@st.cache_data
def fetch_subjects():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM subjects ORDER BY name ASC")
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

@st.cache_data
def fetch_units(subject_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM units WHERE subject_id = %s ORDER BY name ASC", (subject_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

@st.cache_data
def fetch_sections(unit_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM sections WHERE unit_id = %s ORDER BY name ASC", (unit_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

@st.cache_data
def fetch_topics(section_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM topics WHERE section_id = %s ORDER BY name ASC", (section_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

@st.cache_data
def fetch_subtopics(topic_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name FROM subtopics WHERE topic_id = %s ORDER BY name ASC", (topic_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

@st.cache_data
def fetch_subtopics_all():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, topic_id, name, tags FROM subtopics")
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

def insert_note(topic_id, content, file_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (topic_id, content, file_path) VALUES (%s, %s, %s)", (topic_id, content, file_path))
    conn.commit()
    cur.close()

def insert_question(topic_id, question_text, difficulty, answer, explanation, file_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO questions (topic_id, question_text, difficulty, answer, explanation, file_path) VALUES (%s, %s, %s, %s, %s, %s)", 
                (topic_id, question_text, difficulty, answer, explanation, file_path))
    conn.commit()
    cur.close()

def get_topic_details(topic_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT s.name as subject, u.name as unit, sec.name as section, t.name as topic
        FROM topics t
        LEFT JOIN sections sec ON t.section_id = sec.id
        LEFT JOIN units u ON sec.unit_id = u.id
        LEFT JOIN subjects s ON u.subject_id = s.id
        WHERE t.id = %s
    """, (topic_id,))
    res = cur.fetchone()
    cur.close()
    return dict(res) if res else None

def get_notes(topic_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM notes WHERE topic_id = %s ORDER BY created_at DESC", (topic_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(row) for row in res]

def get_questions(topic_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM questions WHERE topic_id = %s ORDER BY created_at DESC", (topic_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(row) for row in res]

def mark_topic_studied(user_id, topic_id):
    details = get_topic_details(topic_id)
    if not details: return
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Detect Dialect
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    pk_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    print(f"[DB DEBUG] Initializing tables (Dialect: {'Postgres' if is_postgres else 'SQLite'})...")

    try:
        # 1. USERS TABLE
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. OTP TABLE
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS otp_store (
                id {pk_type},
                email TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. UPLOADS (ACADEMIC CONTENT)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS subjects (
                id {pk_type},
                name TEXT NOT NULL UNIQUE
            )
        """)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS units (
                id {pk_type},
                subject_id INTEGER REFERENCES subjects(id),
                name TEXT NOT NULL
            )
        """)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS notes (
                id {pk_type},
                topic_id INTEGER,
                content TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. ADMIN REQUESTS
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS admin_requests (
                id {pk_type},
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("[DB DEBUG] Schema check complete. Tables verified/created.")
    except Exception as e:
        print(f"[DB DEBUG] CRITICAL ERROR during init_db: {e}")
        conn.rollback()
    finally:
        conn.close()
    
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

    # --- SEED CORE CURRICULUM FROM JSON ---
    cur.execute("SELECT COUNT(*) FROM subjects")
    subject_count = cur.fetchone()[0]
    
    if subject_count < 4:
        # Clear out the incomplete/old hardcoded data
        cur.execute("DELETE FROM subtopics")
        cur.execute("DELETE FROM topics")
        cur.execute("DELETE FROM sections")
        cur.execute("DELETE FROM units")
        cur.execute("DELETE FROM subjects")
        
        seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'seed_data.json')
        if os.path.exists(seed_path):
            try:
                with open(seed_path, 'r') as f:
                    data = json.load(f)
                
                # We must map old IDs to new auto-incremented IDs to preserve relationships
                id_map = {'subjects': {}, 'units': {}, 'sections': {}, 'topics': {}, 'subtopics': {}}
                
                for s in data.get('subjects', []):
                    cur.execute("INSERT INTO subjects (name) VALUES (?)", (s['name'],))
                    id_map['subjects'][s['id']] = cur.lastrowid
                    
                for u in data.get('units', []):
                    new_sub_id = id_map['subjects'].get(u['subject_id'])
                    if new_sub_id:
                        cur.execute("INSERT INTO units (subject_id, name) VALUES (?, ?)", (new_sub_id, u['name']))
                        id_map['units'][u['id']] = cur.lastrowid
                        
                for sec in data.get('sections', []):
                    new_unit_id = id_map['units'].get(sec['unit_id'])
                    if new_unit_id:
                        cur.execute("INSERT INTO sections (unit_id, name) VALUES (?, ?)", (new_unit_id, sec['name']))
                        id_map['sections'][sec['id']] = cur.lastrowid
                        
                for t in data.get('topics', []):
                    new_sec_id = id_map['sections'].get(t['section_id'])
                    if new_sec_id:
                        cur.execute("INSERT INTO topics (section_id, name, description) VALUES (?, ?, ?)", 
                                    (new_sec_id, t['name'], t.get('description')))
                        id_map['topics'][t['id']] = cur.lastrowid
                        
                for st in data.get('subtopics', []):
                    new_top_id = id_map['topics'].get(st['topic_id'])
                    if new_top_id:
                        cur.execute("INSERT INTO subtopics (topic_id, name, tags, difficulty) VALUES (?, ?, ?, ?)", 
                                    (new_top_id, st['name'], st.get('tags'), st.get('difficulty')))
                                    
                for n in data.get('notes', []):
                    new_top_id = id_map['topics'].get(n['topic_id'])
                    if new_top_id:
                        cur.execute("INSERT INTO notes (topic_id, content, file_path) VALUES (?, ?, ?)", 
                                    (new_top_id, n.get('content'), n.get('file_path')))
                                    
                for q in data.get('questions', []):
                    new_top_id = id_map['topics'].get(q['topic_id'])
                    if new_top_id:
                        cur.execute("INSERT INTO questions (topic_id, question_text, difficulty, answer, explanation, file_path) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (new_top_id, q.get('question_text'), q.get('difficulty'), q.get('answer'), q.get('explanation'), q.get('file_path')))
            except Exception as e:
                print(f"Error seeding database: {e}")

    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    cur.close()

def mark_topic_completed(user_id, topic_id):
    details = get_topic_details(topic_id)
    if not details: return
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE progress SET completed = TRUE, score = 100 WHERE topic = %s AND user_id = %s", (details['topic'], user_id))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO progress (user_id, subject, topic, completed, score) VALUES (%s, %s, %s, TRUE, 100)", 
                    (user_id, details['subject'], details['topic']))
    conn.commit()
    cur.close()
    return True

def update_practice(user_id, topic_id, is_correct):
    details = get_topic_details(topic_id)
    if not details: return
    
    score = 100 if is_correct else 0
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, score FROM progress WHERE topic = %s AND user_id = %s", (details['topic'], user_id))
    row = cur.fetchone()
    
    if row:
        cur.execute("UPDATE progress SET score = %s WHERE id = %s", (score, row[0]))
    else:
        cur.execute("INSERT INTO progress (user_id, subject, topic, completed, score) VALUES (%s, %s, %s, FALSE, %s)", 
                    (user_id, details['subject'], details['topic'], score))
    
    conn.commit()
    cur.close()

@st.cache_data
def get_all_user_progress(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM progress WHERE user_id = %s", (user_id,))
    res = cur.fetchall()
    cur.close()
    return {r['topic']: dict(r) for r in res}

def get_progress(user_id, topic_id):
    details = get_topic_details(topic_id)
    if not details: return None
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM progress WHERE topic = %s AND user_id = %s", (details['topic'], user_id))
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None

def get_practice_topics(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT p.topic_id, t.name as topic_name, p.attempts, p.correct
        FROM progress p
        JOIN topics t ON p.topic_id = t.id
        WHERE p.practiced = TRUE AND p.user_id = %s
    """, (user_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(row) for row in res]

def get_user_profile(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, username, email, role, profile_photo, join_date FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None

def update_profile(user_id, name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
    conn.commit()
    cur.close()
    return True

def update_profile_photo(user_id, photo_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_photo = %s WHERE id = %s", (photo_path, user_id))
    conn.commit()
    cur.close()
    return True

def remove_profile_photo(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET profile_photo = NULL WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    return True

def change_password(user_id, hashed_pw):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id))
    conn.commit()
    cur.close()
    return True

def get_dashboard_stats(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    stats = {}
    
    # 1. Main Dashboard Stats (using score and completed)
    query = """
    SELECT
        COUNT(*) AS total_topics,
        COUNT(CASE WHEN completed = TRUE THEN 1 END) AS completed_topics,
        COALESCE(AVG(score), 0) AS avg_score
    FROM progress
    WHERE user_id = %s
    """
    cur.execute(query, (user_id,))
    res = cur.fetchone()
    
    stats['topics_completed'] = res['completed_topics']
    stats['avg_accuracy'] = float(res['avg_score'])
    stats['total_attempts'] = res['total_topics']
    
    # 2. Active Topics (where completed = FALSE)
    cur.execute("""
        SELECT topic as name, created_at as last_accessed
        FROM progress
        WHERE completed = FALSE AND user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    stats['active_topics'] = [dict(r) for r in cur.fetchall()]
    
    # 3. Weak Topics (where score < 50)
    cur.execute("""
        SELECT topic as name, score as attempts, 0 as correct
        FROM progress
        WHERE score < 50 AND user_id = %s
        ORDER BY score ASC
    """, (user_id,))
    stats['weak_topics'] = [dict(r) for r in cur.fetchall()]
    
    # 4. Recently Studied (Join removed to prevent crash if topics table is missing)
    cur.execute("""
        SELECT topic as name, created_at as last_accessed, id as topic_id, completed
        FROM progress
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))
    stats['recently_studied'] = [dict(r) for r in cur.fetchall()]
    
    # 5. Weak Count (topics in progress)
    cur.execute("SELECT COUNT(*) as c FROM progress WHERE completed = FALSE AND user_id = %s", (user_id,))
    stats['weak_count'] = cur.fetchone()['c']

    # 6. Total Available (Best guess based on new schema)
    cur.execute("SELECT COUNT(*) as c FROM progress")
    stats['total_topics_available'] = cur.fetchone()['c']

    cur.close()
    return stats

def get_overall_progress_data(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM progress WHERE user_id = %s AND completed = TRUE) as completed,
            (SELECT COUNT(*) FROM progress WHERE user_id = %s AND completed = FALSE) as learning,
            ((SELECT COUNT(*) FROM progress) - (SELECT COUNT(*) FROM progress WHERE user_id = %s)) as unstarted
    """, (user_id, user_id, user_id))
    res = cur.fetchone()
    cur.close()
    return dict(res) if res else {"completed": 0, "learning": 0, "unstarted": 0}

def get_subject_completion_stats(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            s.name as subject,
            COUNT(t.id) as total_topics,
            SUM(CASE WHEN p.completed = TRUE THEN 1 ELSE 0 END) as completed_topics
        FROM subjects s
        LEFT JOIN units u ON s.id = u.subject_id
        LEFT JOIN sections sec ON u.id = sec.unit_id
        LEFT JOIN topics t ON sec.id = t.section_id
        LEFT JOIN progress p ON t.name = p.topic AND p.user_id = %s
        GROUP BY s.id, s.name
    """, (user_id,))
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

def get_user_achievements(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    achievements = []
    
    cur.execute("SELECT COUNT(*) as c FROM progress WHERE user_id = %s", (user_id,))
    interaction_count = cur.fetchone()['c']
    if interaction_count >= 1: achievements.append({"title": "First Steps", "icon": "🌱", "desc": "Started studying a topic."})
    if interaction_count >= 10: achievements.append({"title": "Dedicated Scholar", "icon": "📚", "desc": "Interacted with 10+ topics."})
        
    cur.execute("SELECT COUNT(*) as c FROM progress WHERE user_id = %s AND score >= 80", (user_id,))
    high_acc_count = cur.fetchone()['c']
    if high_acc_count >= 1: achievements.append({"title": "Sharp Mind", "icon": "🎯", "desc": "Scored 80%+ on a topic."})
    if high_acc_count >= 5: achievements.append({"title": "Master Learner", "icon": "🏆", "desc": "Mastered 5+ topics with high accuracy."})
        
    cur.close()
    return achievements

def hard_reset_academic_progress(user_id):
    conn = get_connection()
    cur = conn.cursor()
    tables = ["progress", "user_progress", "subtopic_progress", "study_sessions", "practice_attempts"]
    try:
        for table in tables:
            cur.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        cur.close()
    return success

def get_pending_admin_requests():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM admin_requests WHERE status = 'pending' ORDER BY created_at DESC")
    res = cur.fetchall()
    cur.close()
    return [dict(r) for r in res]

def approve_admin_request(request_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM admin_requests WHERE id = %s", (request_id,))
    req = cur.fetchone()
    if not req:
        cur.close()
        return False
    
    try:
        cur.execute("INSERT INTO users (name, username, email, password, role) VALUES (%s, %s, %s, %s, 'admin')", 
                    (req['name'], req['username'], req['email'], req['password']))
        cur.execute("UPDATE admin_requests SET status = 'approved' WHERE id = %s", (request_id,))
        conn.commit()
        success = True
        print("[DB DEBUG] Admin request approved")
    except Exception as e:
        print(f"[DB DEBUG] Error approving admin: {e}")
        success = False
    finally:
        cur.close()
    return success

def reject_admin_request(request_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE admin_requests SET status = 'rejected' WHERE id = %s", (request_id,))
    conn.commit()
    cur.close()
    return True

def get_user_by_id(user_id):
    return get_user_profile(user_id)

def init_db():
    """Initializes the database schema for PostgreSQL if tables do not exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        profile_photo TEXT,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subjects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS units (
        id SERIAL PRIMARY KEY,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sections (
        id SERIAL PRIMARY KEY,
        unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS topics (
        id SERIAL PRIMARY KEY,
        section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS subtopics (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        tags TEXT
    );

    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        content TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        question_text TEXT,
        difficulty VARCHAR(20),
        answer TEXT,
        explanation TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS progress (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        subject VARCHAR(100),
        topic VARCHAR(255),
        completed BOOLEAN DEFAULT FALSE,
        score FLOAT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        cur.execute(schema)
        conn.commit()
        print("[DB DEBUG] Database schema initialized successfully.")
    except Exception as e:
        print(f"[DB DEBUG] Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
