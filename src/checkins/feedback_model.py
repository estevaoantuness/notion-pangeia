"""
Check-in Feedback Data Model

Handles storage and retrieval of check-in responses from users.
Captures response text, NLP intent classification, and metadata.
"""

from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ResponseIntent(str, Enum):
    """Classification of user's response intent"""
    PROGRESSING = "progressing"  # User is making progress
    BLOCKED = "blocked"  # User is stuck/blocked
    COMPLETED = "completed"  # User completed a task
    QUESTION = "question"  # User asked a question
    REFLECTION = "reflection"  # User is reflecting
    OTHER = "other"  # Doesn't fit other categories


@dataclass
class CheckinFeedback:
    """Model for check-in feedback response"""
    id: Optional[int] = None
    user_id: str = ""
    checkin_id: str = ""  # Unique ID for the check-in (random_checkin-user-YYYYMMDD-HHMM)
    checkin_window: str = ""  # morning, afternoon, evening, late_night
    checkin_message: str = ""  # The message that was sent
    response_text: str = ""  # User's response
    response_intent: ResponseIntent = ResponseIntent.OTHER  # NLP classification
    response_timestamp: datetime = None  # When user responded
    checkin_timestamp: datetime = None  # When check-in was sent
    response_time_seconds: Optional[int] = None  # Time to respond
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Set default timestamps"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.response_timestamp is None and self.checkin_timestamp is not None:
            self.response_timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "checkin_id": self.checkin_id,
            "checkin_window": self.checkin_window,
            "checkin_message": self.checkin_message,
            "response_text": self.response_text,
            "response_intent": self.response_intent.value,
            "response_timestamp": self.response_timestamp.isoformat() if self.response_timestamp else None,
            "checkin_timestamp": self.checkin_timestamp.isoformat() if self.checkin_timestamp else None,
            "response_time_seconds": self.response_time_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CheckinFeedback":
        """Create instance from dictionary"""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", ""),
            checkin_id=data.get("checkin_id", ""),
            checkin_window=data.get("checkin_window", ""),
            checkin_message=data.get("checkin_message", ""),
            response_text=data.get("response_text", ""),
            response_intent=ResponseIntent(data.get("response_intent", ResponseIntent.OTHER.value)),
            response_timestamp=datetime.fromisoformat(data["response_timestamp"]) if data.get("response_timestamp") else None,
            checkin_timestamp=datetime.fromisoformat(data["checkin_timestamp"]) if data.get("checkin_timestamp") else None,
            response_time_seconds=data.get("response_time_seconds"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


class CheckinFeedbackRepository:
    """Repository for check-in feedback database operations"""

    def __init__(self, db_connection):
        """
        Initialize repository

        Args:
            db_connection: PostgreSQL database connection/engine
        """
        self.db = db_connection
        logger.info("CheckinFeedbackRepository initialized")

    def save_feedback(self, feedback: CheckinFeedback) -> Optional[int]:
        """
        Save check-in feedback to database

        Args:
            feedback: CheckinFeedback instance

        Returns:
            Feedback ID if successful, None otherwise
        """
        try:
            from sqlalchemy import text

            feedback.updated_at = datetime.utcnow()

            query = text("""
                INSERT INTO checkin_feedback (
                    user_id, checkin_id, checkin_window, checkin_message,
                    response_text, response_intent, response_timestamp,
                    checkin_timestamp, response_time_seconds, created_at, updated_at
                ) VALUES (
                    :user_id, :checkin_id, :checkin_window, :checkin_message,
                    :response_text, :response_intent, :response_timestamp,
                    :checkin_timestamp, :response_time_seconds, :created_at, :updated_at
                )
                RETURNING id
            """)

            with self.db.begin() as conn:
                result = conn.execute(query, feedback.to_dict())
                feedback_id = result.scalar()
                logger.info(f"✓ Feedback saved for {feedback.user_id} (ID: {feedback_id})")
                return feedback_id

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return None

    def get_feedback_for_user(self, user_id: str, limit: int = 50) -> List[CheckinFeedback]:
        """
        Get all feedback responses for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of CheckinFeedback instances
        """
        try:
            from sqlalchemy import text

            query = text("""
                SELECT * FROM checkin_feedback
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """)

            with self.db.connect() as conn:
                result = conn.execute(query, {"user_id": user_id, "limit": limit})
                return [CheckinFeedback.from_dict(dict(row._mapping)) for row in result]

        except Exception as e:
            logger.error(f"Error retrieving feedback for {user_id}: {e}")
            return []

    def get_feedback_statistics(self, user_id: str) -> Dict:
        """
        Get statistics on user's check-in feedback

        Args:
            user_id: User ID

        Returns:
            Dictionary with stats (total, by_intent, avg_response_time, etc)
        """
        try:
            from sqlalchemy import text

            query = text("""
                SELECT
                    COUNT(*) as total_responses,
                    response_intent,
                    AVG(response_time_seconds) as avg_response_time,
                    MIN(response_time_seconds) as min_response_time,
                    MAX(response_time_seconds) as max_response_time
                FROM checkin_feedback
                WHERE user_id = :user_id
                GROUP BY response_intent
            """)

            with self.db.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                stats = {
                    "total_responses": 0,
                    "by_intent": {},
                    "avg_response_time": None
                }

                for row in result:
                    intent = row[1]
                    stats["by_intent"][intent] = {
                        "count": row[0],
                        "avg_time": row[2],
                        "min_time": row[3],
                        "max_time": row[4]
                    }
                    stats["total_responses"] += row[0]

                return stats

        except Exception as e:
            logger.error(f"Error calculating statistics for {user_id}: {e}")
            return {"total_responses": 0, "by_intent": {}}

    def delete_old_feedback(self, days: int = 90) -> int:
        """
        Delete feedback older than N days (for cleanup)

        Args:
            days: Number of days to keep

        Returns:
            Number of records deleted
        """
        try:
            from sqlalchemy import text
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            query = text("""
                DELETE FROM checkin_feedback
                WHERE created_at < :cutoff_date
            """)

            with self.db.begin() as conn:
                result = conn.execute(query, {"cutoff_date": cutoff_date})
                deleted_count = result.rowcount
                logger.info(f"✓ Deleted {deleted_count} old feedback records")
                return deleted_count

        except Exception as e:
            logger.error(f"Error deleting old feedback: {e}")
            return 0
