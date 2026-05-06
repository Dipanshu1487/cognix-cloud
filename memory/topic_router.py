import os
import difflib

class TopicRouter:
    def __init__(self, db_config=None):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cognix.db")

    def _get_connection(self):
        """Standardized connection helper."""
        return db.get_connection()

    def identify_topic(self, query):
        conn = self._get_connection()
        cur = conn.cursor()
        
        # Fetch Subtopics and their parent topic_ids for keyword routing
        cur.execute("SELECT id, topic_id, name, tags FROM subtopics")
        subtopics = cur.fetchall()
        conn.close()

        query_lower = query.lower()
        
        # 1. Exact/Partial Match on Name or Tags
        for sub_id, top_id, name, tags in subtopics:
            # Check name
            if query_lower == name.lower() or name.lower() in query_lower:
                return {"subtopic_id": sub_id, "topic_id": top_id, "name": name, "confidence": 1.0, "method": "keyword"}
            
            # Check tags
            if tags:
                tag_list = [t.strip().lower() for t in tags.split(",")]
                for tag in tag_list:
                    if tag in query_lower:
                        return {"subtopic_id": sub_id, "topic_id": top_id, "name": name, "confidence": 0.9, "method": "tag_match"}

        # 2. Fuzzy Match
        best_match = None
        highest_ratio = 0
        for sub_id, top_id, name, _ in subtopics:
            ratio = difflib.SequenceMatcher(None, query_lower, name.lower()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = {"subtopic_id": sub_id, "topic_id": top_id, "name": name}
        
        if highest_ratio > 0.6:
            return {**best_match, "confidence": round(highest_ratio, 2), "method": "fuzzy"}

        return None

    def get_topic_name(self, topic_id):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM topics WHERE id = ?", (topic_id,))
        res = cur.fetchone()
        conn.close()
        return res[0] if res else "Unknown Topic"

    def get_topic_details(self, topic_id):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, description FROM topics WHERE id = ?", (topic_id,))
        res = cur.fetchone()
        conn.close()
        if res:
            return {"name": res[0], "description": res[1]}
        return None
