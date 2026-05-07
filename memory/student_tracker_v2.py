import sqlite3
import os
from upload.db import DB_PATH

class StudentTrackerV2:
    def __init__(self, db_config):
        self.config = db_config
        self.db_path = DB_PATH

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def log_activity(self, student_id, topic_id, accuracy, time_spent, activity_type='chat', session_id=None, question_id=None):
        conn = self._get_connection()
        if not conn: return False
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, attempts, accuracy FROM user_progress WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            if row:
                old_attempts = row[1]
                old_accuracy = row[2]
                new_attempts = old_attempts + 1
                new_accuracy = ((old_accuracy * old_attempts) + accuracy) / new_attempts
                cur.execute("UPDATE user_progress SET attempts = ?, accuracy = ?, last_score = ?, last_updated = CURRENT_TIMESTAMP WHERE topic_id = ?", (new_attempts, new_accuracy, accuracy, topic_id))
            else:
                cur.execute("INSERT INTO user_progress (topic_id, attempts, accuracy, last_score) VALUES (?, ?, ?, ?)", (topic_id, 1, accuracy, accuracy))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_topic_status(self, topic_id):
        conn = self._get_connection()
        if not conn: return "unknown"
        try:
            cur = conn.cursor()
            cur.execute("SELECT accuracy, attempts FROM user_progress WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            if not row or row[1] == 0: return "unknown"
            acc = row[0]
            if acc < 0.4: return "weak"
            if acc > 0.75: return "strong"
            return "intermediate"
        except:
            return "unknown"
        finally:
            conn.close()

    def get_avg_accuracy(self, student_id, topic_id):
        conn = self._get_connection()
        if not conn: return 0.0
        try:
            cur = conn.cursor()
            cur.execute("SELECT accuracy FROM user_progress WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            return row[0] if row else 0.0
        except:
            return 0.0
        finally:
            conn.close()

    def analyze_trend(self, student_id, topic_id):
        conn = self._get_connection()
        if not conn: return "stable"
        try:
            cur = conn.cursor()
            cur.execute("SELECT accuracy, last_score FROM user_progress WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            if not row: return "stable"
            acc, last_score = row
            diff = last_score - acc
            if diff > 0.1: return "improving"
            if diff < -0.1: return "declining"
            return "stable"
        except:
            return "stable"
        finally:
            conn.close()

    def get_attempts(self, student_id, topic_id):
        conn = self._get_connection()
        if not conn: return 0
        try:
            cur = conn.cursor()
            cur.execute("SELECT attempts FROM user_progress WHERE topic_id = ?", (topic_id,))
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0
        finally:
            conn.close()
