import upload.db as db
from psycopg2.extras import RealDictCursor

class StudentTrackerV2:
    def __init__(self, db_config=None):
        # db_config is legacy
        pass

    def _get_connection(self):
        """Standardized connection helper."""
        return db.get_connection()

    def log_activity(self, student_id, topic_id, accuracy, time_spent, activity_type='chat', session_id=None, question_id=None):
        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            # user_id is missing from some calls in this file, we should use student_id
            cur.execute("SELECT id, attempts, accuracy FROM user_progress WHERE topic_id = %s AND user_id = %s", (topic_id, student_id))
            row = cur.fetchone()
            if row:
                old_attempts = row['attempts']
                old_accuracy = row['accuracy']
                new_attempts = old_attempts + 1
                new_accuracy = ((old_accuracy * old_attempts) + accuracy) / new_attempts
                cur.execute("UPDATE user_progress SET attempts = %s, accuracy = %s, last_score = %s, last_updated = CURRENT_TIMESTAMP WHERE topic_id = %s AND user_id = %s", 
                            (new_attempts, new_accuracy, accuracy, topic_id, student_id))
            else:
                cur.execute("INSERT INTO user_progress (user_id, topic_id, attempts, accuracy, last_score) VALUES (%s, %s, 1, %s, %s)", 
                            (student_id, topic_id, accuracy, accuracy))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[DB DEBUG] StudentTrackerV2.log_activity error: {e}")
            return False
        finally:
            conn.close()

    def get_topic_status(self, student_id, topic_id):
        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT accuracy, attempts FROM user_progress WHERE topic_id = %s AND user_id = %s", (topic_id, student_id))
            row = cur.fetchone()
            if not row or row['attempts'] == 0: return "unknown"
            acc = row['accuracy']
            if acc < 0.4: return "weak"
            if acc > 0.75: return "strong"
            return "intermediate"
        except Exception as e:
            print(f"[DB DEBUG] StudentTrackerV2.get_topic_status error: {e}")
            return "unknown"
        finally:
            cur.close()
            conn.close()

    def get_avg_accuracy(self, student_id, topic_id):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT accuracy FROM user_progress WHERE topic_id = %s AND user_id = %s", (topic_id, student_id))
            row = cur.fetchone()
            return row[0] if row else 0.0
        except Exception as e:
            print(f"[DB DEBUG] StudentTrackerV2.get_avg_accuracy error: {e}")
            return 0.0
        finally:
            cur.close()
            conn.close()

    def analyze_trend(self, student_id, topic_id):
        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT accuracy, last_score FROM user_progress WHERE topic_id = %s AND user_id = %s", (topic_id, student_id))
            row = cur.fetchone()
            if not row: return "stable"
            acc, last_score = row['accuracy'], row['last_score']
            diff = last_score - acc
            if diff > 0.1: return "improving"
            if diff < -0.1: return "declining"
            return "stable"
        except Exception as e:
            print(f"[DB DEBUG] StudentTrackerV2.analyze_trend error: {e}")
            return "stable"
        finally:
            cur.close()
            conn.close()

    def get_attempts(self, student_id, topic_id):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT attempts FROM user_progress WHERE topic_id = %s AND user_id = %s", (topic_id, student_id))
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print(f"[DB DEBUG] StudentTrackerV2.get_attempts error: {e}")
            return 0
        finally:
            cur.close()
            conn.close()
