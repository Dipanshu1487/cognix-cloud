import psycopg2
from psycopg2.extras import RealDictCursor
from .evaluator import AnswerEvaluator

class PracticeEngine:
    def __init__(self, db_config, tracker):
        self.config = db_config
        self.tracker = tracker

    def _get_connection(self):
        return psycopg2.connect(**self.config)

    def get_question(self, topic_id=None, difficulty=None):
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            query = "SELECT * FROM questions WHERE 1=1"
            params = []
            if topic_id:
                query += " AND topic_id = %s"
                params.append(topic_id)
            if difficulty:
                query += " AND difficulty_level = %s"
                params.append(difficulty)
            
            query += " ORDER BY RANDOM() LIMIT 1"
            cur.execute(query, params)
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def submit_answer(self, student_id, question_id, student_answer, session_id=None):
        conn = self._get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
            q = cur.fetchone()
            if not q: return None

            score = AnswerEvaluator.evaluate(student_answer, q['correct_answer'], q['question_type'])
            
            self.tracker.log_activity(
                student_id=student_id,
                topic_id=q['topic_id'],
                accuracy=score,
                time_spent=30,
                activity_type='practice',
                session_id=session_id,
                question_id=question_id
            )
            return {"score": score, "correct_answer": q['correct_answer']}
        finally:
            cur.close()
            conn.close()
