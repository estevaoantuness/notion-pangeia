-- Migration: Create Check-in Feedback Table
-- Date: 2025-11-10
-- Purpose: Store user responses to random check-in questions

CREATE TABLE IF NOT EXISTS checkin_feedback (
    id SERIAL PRIMARY KEY,

    -- User and Check-in Reference
    user_id VARCHAR(255) NOT NULL,
    checkin_id VARCHAR(255) NOT NULL,  -- e.g., "random_checkin-estevao-20251110-0923"

    -- Check-in Details
    checkin_window VARCHAR(20) NOT NULL,  -- morning, afternoon, evening, late_night
    checkin_message TEXT NOT NULL,  -- The message that was sent

    -- Response Data
    response_text TEXT NOT NULL,  -- User's response
    response_intent VARCHAR(50) NOT NULL DEFAULT 'other',  -- progressing, blocked, completed, question, reflection, other

    -- Timestamps
    checkin_timestamp TIMESTAMP NOT NULL,  -- When check-in was sent
    response_timestamp TIMESTAMP NOT NULL,  -- When user responded
    response_time_seconds INTEGER,  -- Seconds between send and response

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for common queries
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX idx_checkin_feedback_user_id ON checkin_feedback(user_id);
CREATE INDEX idx_checkin_feedback_created_at ON checkin_feedback(created_at);
CREATE INDEX idx_checkin_feedback_response_intent ON checkin_feedback(response_intent);
CREATE INDEX idx_checkin_feedback_window ON checkin_feedback(checkin_window);
CREATE INDEX idx_checkin_feedback_user_created ON checkin_feedback(user_id, created_at DESC);

-- Add comment
COMMENT ON TABLE checkin_feedback IS 'Stores user responses to random check-in messages for analysis and feedback collection';
COMMENT ON COLUMN checkin_feedback.response_intent IS 'NLP classification of user response: progressing, blocked, completed, question, reflection, other';
COMMENT ON COLUMN checkin_feedback.response_time_seconds IS 'Time in seconds from check-in delivery to user response';
