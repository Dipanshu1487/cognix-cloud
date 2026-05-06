import os
import sqlite3
from .topic_router import TopicRouter

class StudentIntelligenceSystem:
    def __init__(self, db_config):
        self.router = TopicRouter(db_config)
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cognix.db")

    def process_chat_interaction(self, user_id, query):
        res = self.router.identify_topic(query)
        if res:
            topic_id = res['subtopic_id'] # Note: identifier is subtopic_id in router
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("UPDATE user_progress SET attempts = attempts + 1, last_updated = CURRENT_TIMESTAMP WHERE topic_id = ? AND user_id = ?", (topic_id, user_id))
            if cur.rowcount == 0:
                cur.execute("INSERT INTO user_progress (user_id, topic_id, attempts) VALUES (?, ?, 1)", (user_id, topic_id))
            conn.commit()
            cur.close()
            conn.close()
            return res
        return None

    def get_topic_name(self, topic_id):
        return self.router.get_topic_name(topic_id)

    def get_topic_details(self, topic_id):
        return self.router.get_topic_details(topic_id)

    def get_subject_structure(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT s.name as subject, u.name as unit, sec.name as section, t.id as topic_id, t.name as topic_name
            FROM subjects s
            JOIN units u ON s.id = u.subject_id
            JOIN sections sec ON u.id = sec.unit_id
            JOIN topics t ON sec.id = t.section_id
            ORDER BY s.id, u.id, sec.id, t.id
        """)
        rows = cur.fetchall()
        
        structure = {}
        for row in rows:
            s, u, sec = row['subject'], row['unit'], row['section']
            if s not in structure: structure[s] = {}
            if u not in structure[s]: structure[s][u] = {}
            if sec not in structure[s][u]: structure[s][u][sec] = []
            structure[s][u][sec].append({"id": row['topic_id'], "name": row['topic_name']})
        conn.close()
        return structure

    def get_topic_status(self, user_id, topic_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT attempts, accuracy FROM user_progress WHERE topic_id = ? AND user_id = ?", (topic_id, user_id))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {"attempts": 0, "accuracy": 0}
