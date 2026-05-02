-- Migration Script: Student Tracking System v1 -> v2

-- 1. Create Question Type Enum
CREATE TYPE activity_category AS ENUM ('chat', 'practice', 'test');

-- 2. Update Topics Table for Hierarchy
ALTER TABLE topics ADD COLUMN IF NOT EXISTS parent_topic_id INTEGER REFERENCES topics(id);
ALTER TABLE topics ADD COLUMN IF NOT EXISTS keywords TEXT[]; -- For smarter keyword mapping

-- 3. Create Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    difficulty_level INTEGER DEFAULT 1, -- 1 to 5
    question_type TEXT DEFAULT 'text' -- 'mcq', 'numeric', 'descriptive'
);

-- 4. Create Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    context TEXT
);

-- 5. Upgrade Activities Table
ALTER TABLE activities ADD COLUMN IF NOT EXISTS activity_type activity_category DEFAULT 'chat';
ALTER TABLE activities ADD COLUMN IF NOT EXISTS session_id INTEGER REFERENCES sessions(id);
ALTER TABLE activities ADD COLUMN IF NOT EXISTS question_id INTEGER REFERENCES questions(id);
ALTER TABLE activities ADD COLUMN IF NOT EXISTS interaction_metadata JSONB; -- For storing raw query/response if needed

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_activity_student_topic ON activities(student_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activities(created_at);
