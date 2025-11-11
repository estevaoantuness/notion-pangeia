"""
Simple Intent Classifier for Check-in Responses

Classifies user responses to check-in messages using the existing NLP normalizer.
Maps general intents to specific ResponseIntent categories used by CheckinFeedbackHandler.
"""

import logging
from typing import Dict, Any
from src.commands.normalizer import parse as nlp_parse

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifies intent of check-in responses.

    Uses the existing NLP normalizer to detect high-level intents
    and maps them to ResponseIntent categories for feedback storage.
    """

    def __init__(self):
        """Initialize classifier"""
        logger.info("IntentClassifier initialized")

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify the intent of a user response.

        Args:
            text: User's response text

        Returns:
            Dict with 'intent' key and confidence
        """
        try:
            # Use existing NLP normalizer
            result = nlp_parse(text)

            # Map NLP intent to simple category
            mapped_intent = self._map_intent(result.intent, text)

            return {
                "intent": mapped_intent,
                "confidence": result.confidence,
                "original_intent": result.intent,
                "text": text
            }

        except Exception as e:
            logger.warning(f"Error classifying intent: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "original_intent": "error",
                "text": text
            }

    def _map_intent(self, nlp_intent: str, text: str) -> str:
        """
        Map NLP intent to ResponseIntent category.

        Args:
            nlp_intent: Intent detected by normalizer
            text: Original text for context

        Returns:
            Mapped intent for feedback storage
        """
        # Map common intents
        intent_map = {
            "create_task": "question",  # User creating task
            "list_tasks": "reflection",  # User reflecting on tasks
            "update_task": "progressing",  # User updating task
            "done_task": "completed",  # User marking task complete
            "help": "question",  # User asking for help
            "block_task": "blocked",  # User reporting blocker
            "in_progress_task": "progressing",  # User saying task in progress
            "progress": "reflection",  # User asking about progress
            "greet": "reflection",  # Greeting/conversational
            "goodbye": "reflection",  # Ending conversation
            "thanks": "reflection",  # Thanking bot
        }

        # Return mapped intent, default to "other" if not found
        return intent_map.get(nlp_intent, "other")
