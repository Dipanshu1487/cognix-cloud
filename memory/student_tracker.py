import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

class StudentTracker:
    def __init__(self, db_config):
        self.config = db_config

    def _get_connection(self):
        return psycopg2.connect(**self.config)

    def detect_topic(self, query):
        q = query.lower()
        topic_map = {
            "differentiation": 1,
            "derivative": 1,
            "calculus": 1,
            "stack": 2,
            "lifo": 2,
            "queue": 3,
            "fifo": 3,
            "sorting": 4,
            "algorithm": 4
        }
        for keyword, t_id in topic_map.items():
            if keyword in q:
                return t_id
        return None

    def log_activity(self, student_id, topic_id, accuracy, time_spent):
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            query = """
            INSERT INTO activities (student_id, topic_id, accuracy, time_spent)
            VALUES (%s, %s, %s, %s)
            """
            cur.execute(query, (student_id, topic_id, accuracy, time_spent))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_topic_progress(self, student_id, topic_id):
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            query = """
            SELECT 
                AVG(accuracy) as avg_accuracy,
                COUNT(*) as total_attempts
            FROM activities
            WHERE student_id = %s AND topic_id = %s
            """
            cur.execute(query, (student_id, topic_id))
            result = cur.fetchone()
            return result
        finally:
            cur.close()
            conn.close()

    def classify_proficiency(self, avg_accuracy):
        if avg_accuracy is None:
            return "unknown"
        if avg_accuracy < 0.4:
            return "weak"
        if avg_accuracy > 0.75:
            return "strong"
        return "intermediate"
