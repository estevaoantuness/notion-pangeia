"""
Check-in Feedback Handler

Processes user responses to check-in messages.
Classifies intent via NLP and stores feedback.
"""

import logging
from datetime import datetime
from typing import Optional
from src.checkins.feedback_model import CheckinFeedback, ResponseIntent, CheckinFeedbackRepository
from src.nlp.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


class CheckinFeedbackHandler:
    """Handles check-in response feedback collection and processing"""

    def __init__(self, db_connection, redis_client=None):
        """
        Initialize feedback handler

        Args:
            db_connection: PostgreSQL database connection
            redis_client: Optional Redis client for caching
        """
        self.db = db_connection
        self.redis_client = redis_client
        self.repository = CheckinFeedbackRepository(db_connection)
        self.intent_classifier = IntentClassifier()

        logger.info("CheckinFeedbackHandler initialized")

    def process_checkin_response(
        self,
        user_id: str,
        response_text: str,
        checkin_id: str,
        checkin_window: str,
        checkin_message: str,
        checkin_timestamp: datetime,
        response_timestamp: Optional[datetime] = None
    ) -> Optional[CheckinFeedback]:
        """
        Process a user's response to a check-in message

        Args:
            user_id: User ID
            response_text: User's response text
            checkin_id: Unique ID of the check-in (e.g., "random_checkin-user123-20251110-0923")
            checkin_window: Which window (morning, afternoon, evening, late_night)
            checkin_message: The message that was sent
            checkin_timestamp: When check-in was sent
            response_timestamp: When user responded (defaults to now)

        Returns:
            CheckinFeedback instance if successful, None otherwise
        """
        try:
            if response_timestamp is None:
                response_timestamp = datetime.utcnow()

            # Calculate response time
            response_time_seconds = int((response_timestamp - checkin_timestamp).total_seconds())

            # Classify user's intent
            intent = self._classify_intent(response_text)

            # Create feedback record
            feedback = CheckinFeedback(
                user_id=user_id,
                checkin_id=checkin_id,
                checkin_window=checkin_window,
                checkin_message=checkin_message,
                response_text=response_text,
                response_intent=intent,
                response_timestamp=response_timestamp,
                checkin_timestamp=checkin_timestamp,
                response_time_seconds=response_time_seconds
            )

            # Save to database
            feedback_id = self.repository.save_feedback(feedback)

            if feedback_id:
                feedback.id = feedback_id
                logger.info(
                    f"✓ Feedback recorded for {user_id}: {intent.value} "
                    f"(responded in {response_time_seconds}s)"
                )
                return feedback
            else:
                logger.error(f"Failed to save feedback for {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error processing check-in response: {e}")
            return None

    def _classify_intent(self, text: str) -> ResponseIntent:
        """
        Classify user response intent via NLP

        Args:
            text: User's response text

        Returns:
            ResponseIntent classification
        """
        try:
            # Use existing intent classifier
            intent_result = self.intent_classifier.classify(text)

            # Map NLP intent to ResponseIntent enum
            intent_map = {
                "create_task": ResponseIntent.QUESTION,
                "list_tasks": ResponseIntent.REFLECTION,
                "update_task": ResponseIntent.PROGRESSING,
                "help": ResponseIntent.QUESTION,
                "block_task": ResponseIntent.BLOCKED,
                "complete_task": ResponseIntent.COMPLETED,
            }

            nlp_intent = intent_result.get("intent")
            return intent_map.get(nlp_intent, ResponseIntent.OTHER)

        except Exception as e:
            logger.warning(f"Error classifying intent: {e}")
            return ResponseIntent.OTHER

    def get_user_stats(self, user_id: str) -> dict:
        """
        Get feedback statistics for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.repository.get_feedback_statistics(user_id)
            logger.info(f"Stats for {user_id}: {stats['total_responses']} responses")
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_responses": 0, "by_intent": {}}

    def get_recent_feedback(self, user_id: str, limit: int = 10) -> list:
        """
        Get recent feedback for user

        Args:
            user_id: User ID
            limit: Maximum number of records

        Returns:
            List of CheckinFeedback instances
        """
        try:
            feedback_list = self.repository.get_feedback_for_user(user_id, limit)
            return [f.to_dict() for f in feedback_list]
        except Exception as e:
            logger.error(f"Error retrieving feedback: {e}")
            return []


# Global instance
_handler: Optional[CheckinFeedbackHandler] = None


def get_feedback_handler(db_connection, redis_client=None) -> CheckinFeedbackHandler:
    """
    Get global feedback handler instance (singleton)

    Args:
        db_connection: PostgreSQL connection
        redis_client: Optional Redis client

    Returns:
        CheckinFeedbackHandler instance
    """
    global _handler
    if _handler is None:
        _handler = CheckinFeedbackHandler(db_connection, redis_client)
    return _handler
