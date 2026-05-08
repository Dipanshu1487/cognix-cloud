import sqlite3
import os
import difflib
from upload.db import DB_PATH

class TopicRouter:
    def __init__(self, db_config=None):
        self.db_path = DB_PATH

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def identify_topic(self, query):
        if not query:
            return None
            
        conn = self._get_connection()
        cur = conn.cursor()
        
        # Fetch Subtopics and their parent topic_ids for keyword routing
        try:
            cur.execute("SELECT id, topic_id, name, tags FROM subtopics")
            subtopics = cur.fetchall()
        except sqlite3.Error as e:
            print(f"[TopicRouter] DB Error fetching subtopics: {e}")
            subtopics = []
        finally:
            conn.close()

        if not subtopics:
            return None

        query_lower = query.lower()
        
        # 1. Exact/Partial Match on Name or Tags
        for sub_id, top_id, name, tags in subtopics:
            if not name: continue
            
            # Check name
            if query_lower == name.lower() or name.lower() in query_lower:
                res = {"subtopic_id": sub_id, "topic_id": top_id, "name": name, "confidence": 1.0, "method": "keyword"}
                print(f"[TopicRouter] Detected Topic: {name} (ID: {top_id}) via Keyword")
                return res
            
            # Check tags
            if tags:
                tag_list = [t.strip().lower() for t in tags.split(",")]
                for tag in tag_list:
                    if tag and tag in query_lower:
                        res = {"subtopic_id": sub_id, "topic_id": top_id, "name": name, "confidence": 0.9, "method": "tag_match"}
                        print(f"[TopicRouter] Detected Topic: {name} (ID: {top_id}) via Tag: {tag}")
                        return res

        # 2. Fuzzy Match
        best_match = None
        highest_ratio = 0
        for sub_id, top_id, name, _ in subtopics:
            if not name: continue
            ratio = difflib.SequenceMatcher(None, query_lower, name.lower()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = {"subtopic_id": sub_id, "topic_id": top_id, "name": name}
        
        if highest_ratio > 0.6 and best_match:
            res = {**best_match, "confidence": round(highest_ratio, 2), "method": "fuzzy"}
            print(f"[TopicRouter] Detected Topic: {best_match['name']} (ID: {best_match['topic_id']}) via Fuzzy ({highest_ratio})")
            return res

        print("[TopicRouter] No topic detected for query")
        return None

    def get_topic_name(self, topic_id):
        if topic_id is None: return "Unknown Topic"
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT name FROM topics WHERE id = ?", (topic_id,))
            res = cur.fetchone()
            return res[0] if res and res[0] else "Unknown Topic"
        except sqlite3.Error:
            return "Unknown Topic"
        finally:
            conn.close()

    def get_topic_details(self, topic_id):
        if topic_id is None: return None
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT t.name, t.description, s.name as subject, u.name as unit
                FROM topics t
                LEFT JOIN sections sec ON t.section_id = sec.id
                LEFT JOIN units u ON sec.unit_id = u.id
                LEFT JOIN subjects s ON u.subject_id = s.id
                WHERE t.id = ?
            """, (topic_id,))
            res = cur.fetchone()
            if res:
                details = {
                    "name": res[0] or "Unnamed Topic", 
                    "description": res[1] or "No description available.",
                    "subject": res[2] or "Unknown Subject",
                    "unit": res[3] or "Unknown Unit"
                }
                print(f"[TopicRouter] Fetched details for topic_id {topic_id}: {details['name']}")
                return details
        except sqlite3.Error as e:
            print(f"[TopicRouter] Error fetching topic details: {e}")
        finally:
            conn.close()
        return None

    def validate_hierarchy(self, topic_id):
        """Validates that subject, unit, and topic exist for this topic_id."""
        if topic_id is None: return False
        details = self.get_topic_details(topic_id)
        if not details: return False
        
        # Check if basic info exists
        if details['subject'] == "Unknown Subject" or details['unit'] == "Unknown Unit":
            print(f"[TopicRouter] Hierarchy Validation FAILED for topic_id {topic_id}")
            return False
        
        print(f"[TopicRouter] Hierarchy Validation PASSED for topic_id {topic_id}")
        return True
