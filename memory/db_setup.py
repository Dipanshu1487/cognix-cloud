import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    # Configuration - Change these if needed
    # Configuration - Use env vars or defaults
    db_name = os.getenv("DB_NAME", "cognix_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "admin") # Default for local safety
    host = os.getenv("DB_HOST", "localhost")

    try:
        # 1. Connect to default 'postgres' db to create the new database
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database if not exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created.")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cur.close()
        conn.close()

        # 2. Connect to the new database and create tables
        conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
        cur = conn.cursor()
        
        # Create tables
        schema = """
        CREATE TABLE IF NOT EXISTS topics (
            topic_id SERIAL PRIMARY KEY,
            subject VARCHAR(100) NOT NULL,
            chapter VARCHAR(100) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            UNIQUE(subject, chapter, topic)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            topic_id INTEGER REFERENCES topics(topic_id),
            accuracy FLOAT CHECK (accuracy >= 0 AND accuracy <= 1),
            time_spent INTEGER NOT NULL,
            activity_type VARCHAR(50) DEFAULT 'chat',
            session_id VARCHAR(100),
            question_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(schema)
        print("Schema applied.")

        # 3. Seed data
        sample_topics = [
            ('Math', 'Calculus', 'Differentiation'),
            ('Math', 'Calculus', 'Integration'),
            ('Math', 'Algebra', 'Matrices'),
            ('DSA', 'Trees', 'Binary Search Tree'),
            ('DSA', 'Stacks', 'Expression Evaluation')
        ]
        
        for subj, chap, top in sample_topics:
            cur.execute("""
                INSERT INTO topics (subject, chapter, topic) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (subject, chapter, topic) DO NOTHING
            """, (subj, chap, top))
        
        conn.commit()
        print(f"Seeded {len(sample_topics)} sample topics.")
        
        cur.close()
        conn.close()
        print("\n[SUCCESS] Database setup complete. Refresh your cogniX UI.")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nEnsure:")
        print("1. PostgreSQL is installed and running.")
        print(f"2. User '{user}' exists and password matches.")
        print("3. You have permissions to create databases.")

if __name__ == "__main__":
    setup_database()
