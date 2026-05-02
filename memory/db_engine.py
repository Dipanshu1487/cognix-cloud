import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseEngine:
    def __init__(self, config):
        self.config = config
        self.use_sqlite = config.get('use_sqlite', True)

    def get_connection(self):
        if self.use_sqlite:
            try:
                conn = sqlite3.connect("cognix.db", check_same_thread=False)
                conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
                return conn
            except Exception as e:
                print(f"SQLite Error: {e}")
                return None
        else:
            try:
                return psycopg2.connect(**self.config, connect_timeout=2)
            except Exception as e:
                print(f"Postgres Error: {e}")
                return None

    def format_query(self, query):
        """Replaces %s with ? for SQLite compatibility"""
        if self.use_sqlite:
            return query.replace('%s', '?')
        return query

    def initialize_if_empty(self):
        if not self.use_sqlite: return
        conn = self.get_connection()
        if not conn: return
        try:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                chapter TEXT NOT NULL,
                topic TEXT NOT NULL,
                UNIQUE(subject, chapter, topic)
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                topic_id INTEGER REFERENCES topics(topic_id),
                accuracy FLOAT,
                time_spent INTEGER NOT NULL,
                activity_type TEXT DEFAULT 'chat',
                session_id TEXT,
                question_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            );
            """)
            cur.execute("SELECT count(*) as count FROM topics")
            if cur.fetchone()['count'] == 0:
                sample_topics = [
                    ('Math', 'Calculus', 'Differentiation'),
                    ('Math', 'Calculus', 'Integration'),
                    ('Math', 'Algebra', 'Matrices'),
                    ('DSA', 'Trees', 'Binary Search Tree'),
                    ('DSA', 'Stacks', 'Expression Evaluation')
                ]
                cur.executemany("INSERT INTO topics (subject, chapter, topic) VALUES (?, ?, ?)", sample_topics)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Init Error: {e}")
