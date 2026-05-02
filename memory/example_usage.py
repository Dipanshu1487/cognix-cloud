from memory.student_tracker import StudentTracker

db_config = {
    "dbname": "jarvis_db",
    "user": "postgres",
    "password": "yourpassword",
    "host": "localhost",
    "port": "5432"
}

tracker = StudentTracker(db_config)

# 1. Detect topic from user query
user_query = "Can you explain differentiation again?"
topic_id = tracker.detect_topic(user_query)

if topic_id:
    # 2. Simulate activity logging (e.g., after a quick quiz)
    # student_id=101, topic_id=topic_id, accuracy=0.85, time_spent=120s
    tracker.log_activity(101, topic_id, 0.85, 120)

    # 3. Get progress
    progress = tracker.get_topic_progress(101, topic_id)
    print(f"Progress: {progress}")

    # 4. Classify performance
    status = tracker.classify_proficiency(progress['avg_accuracy'])
    print(f"Status: {status}")
else:
    print("Topic not detected.")
