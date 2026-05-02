-- Academic System Schema v3
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subtopics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    tags TEXT, -- Comma separated keywords
    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
    FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- Tracking Tables
CREATE TABLE IF NOT EXISTS subtopic_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subtopic_id INTEGER NOT NULL,
    attempts INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(subtopic_id) REFERENCES subtopics(id) ON DELETE CASCADE
);

-- Aggregated View for Topic Progress
CREATE VIEW IF NOT EXISTS topic_progress AS
SELECT 
    t.id as topic_id,
    t.name as topic_name,
    COUNT(st.id) as total_subtopics,
    AVG(sp.accuracy) as avg_accuracy,
    SUM(sp.attempts) as total_attempts
FROM topics t
LEFT JOIN subtopics st ON t.id = st.topic_id
LEFT JOIN subtopic_progress sp ON st.id = sp.subtopic_id
GROUP BY t.id;
