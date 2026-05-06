import sqlite3
import os
import datetime
import bcrypt
import json
import logging

logger = logging.getLogger("cognix.db")

# Path for local SQLite (Fallback)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cognix.db')

def _get_secret(key, default=None):
    try:
        import streamlit as st
        return st.secrets.get(key) or os.getenv(key, default)
    except Exception:
        return os.getenv(key, default)

def get_connection():
    """
    Returns a connection object. 
    Switches to PostgreSQL (Supabase) if DB_HOST is set, else SQLite.
    """
    host = _get_secret("DB_HOST")
    
    if host and host != "localhost":
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                database=_get_secret("DB_NAME", "postgres"),
                user=_get_secret("DB_USER", "postgres"),
                password=_get_secret("DB_PASS"),
                port=_get_secret("DB_PORT", "5432"),
                connect_timeout=5
            )
            return conn
        except Exception as e:
            print(f"[DB DEBUG] FAIL: {e}")
            return sqlite3.connect(DB_PATH)
    else:
        return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database. Idempotent."""
    conn = get_connection()
    cur = conn.cursor()
    is_postgres = hasattr(conn, 'get_dsn_parameters')
    pk_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"

    try:
        cur.execute(f"CREATE TABLE IF NOT EXISTS users (id {pk_type}, name TEXT, username TEXT UNIQUE, email TEXT, password TEXT, role TEXT DEFAULT 'user')")
        cur.execute(f"CREATE TABLE IF NOT EXISTS subjects (id {pk_type}, name TEXT UNIQUE)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS units (id {pk_type}, subject_id INTEGER, name TEXT)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS sections (id {pk_type}, unit_id INTEGER, name TEXT)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS topics (id {pk_type}, section_id INTEGER, name TEXT, description TEXT)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS notes (id {pk_type}, topic_id INTEGER, content TEXT, file_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS questions (id {pk_type}, topic_id INTEGER, question_text TEXT, difficulty TEXT, answer TEXT, explanation TEXT, file_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS progress (id {pk_type}, user_id INTEGER, topic_id INTEGER, studied INTEGER DEFAULT 0, practiced INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0, completed INTEGER DEFAULT 0, last_accessed TIMESTAMP)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS admin_requests (id {pk_type}, name TEXT, username TEXT UNIQUE, email TEXT, password TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        conn.close()

# --- HELPER TO GET DICT CURSOR ---
def _get_cursor(conn):
    if hasattr(conn, 'get_dsn_parameters'):
        from psycopg2.extras import RealDictCursor
        return conn.cursor(cursor_factory=RealDictCursor)
    conn.row_factory = sqlite3.Row
    return conn.cursor()

# --- REFACTORED FUNCTIONS ---

def fetch_subjects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subjects")
    res = cur.fetchall()
    conn.close()
    return res

def fetch_units(subject_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM units WHERE subject_id = ?", (subject_id,))
    res = cur.fetchall()
    conn.close()
    return res

def get_user_by_id(user_id):
    conn = get_connection()
    cur = _get_cursor(conn)
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    res = cur.fetchone()
    conn.close()
    return dict(res) if res else None

def change_password(user_id, hashed_pw):
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
    conn.close()
    return True

def update_profile(user_id, name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    conn.close()
    return True

# ... [Placeholder for other functions, ensuring they use get_connection]
