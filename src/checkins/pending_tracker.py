"""
Pending Check-in Tracker

Tracks check-in messages sent to users so responses can be properly identified
and routed to the CheckinFeedbackHandler instead of the command parser.

Uses in-memory dict with TTL for tracking (simpler than Redis for small-scale use).
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
TZ = ZoneInfo("America/Sao_Paulo")


@dataclass
class PendingCheckin:
    """Represents a check-in message that was sent and awaiting response"""
    checkin_id: str  # Unique ID for this check-in instance
    user_id: str  # User who received the check-in
    person_name: str  # Person's name
    checkin_type: str  # Type: "metas", "planning", "status", "closing", etc.
    checkin_message: str  # The message text that was sent
    sent_timestamp: datetime  # When it was sent
    response_window_minutes: int = 120  # How long to accept responses (default 2 hours)

    @property
    def is_expired(self) -> bool:
        """Check if response window has closed"""
        elapsed = (datetime.now(TZ) - self.sent_timestamp).total_seconds()
        return elapsed > (self.response_window_minutes * 60)


class PendingCheckinTracker:
    """
    Tracks pending check-ins by user to enable proper response routing.

    When a check-in is sent, we store it temporarily.
    When a response comes in from the same user within the response window,
    we route it to CheckinFeedbackHandler instead of CommandProcessor.
    """

    def __init__(self, cleanup_interval_seconds: int = 300):
        """
        Initialize tracker

        Args:
            cleanup_interval_seconds: How often to clean up expired entries (default 5 min)
        """
        # Dict mapping user_id -> PendingCheckin
        self._pending: Dict[str, PendingCheckin] = {}

        # Track last cleanup time
        self._last_cleanup = datetime.now(TZ)
        self._cleanup_interval = timedelta(seconds=cleanup_interval_seconds)

        logger.info("PendingCheckinTracker initialized")

    def record_sent_checkin(
        self,
        user_id: str,
        person_name: str,
        checkin_type: str,
        checkin_message: str,
        response_window_minutes: int = 120
    ) -> str:
        """
        Record that a check-in was sent to a user

        Args:
            user_id: User identifier
            person_name: Person's name
            checkin_type: Type of check-in ("metas", "planning", "status", "closing", etc)
            checkin_message: The message text that was sent
            response_window_minutes: Minutes to accept responses (default 120 = 2 hours)

        Returns:
            checkin_id for this sent check-in
        """
        # Generate unique ID for this check-in instance
        checkin_id = f"checkin-{user_id}-{datetime.now(TZ).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

        pending = PendingCheckin(
            checkin_id=checkin_id,
            user_id=user_id,
            person_name=person_name,
            checkin_type=checkin_type,
            checkin_message=checkin_message,
            sent_timestamp=datetime.now(TZ),
            response_window_minutes=response_window_minutes
        )

        self._pending[user_id] = pending

        logger.info(
            f"✓ Recorded check-in for {person_name}: "
            f"type={checkin_type}, id={checkin_id}, window={response_window_minutes}min"
        )

        # Cleanup if needed
        self._cleanup_if_needed()

        return checkin_id

    def get_pending_checkin(self, user_id: str) -> Optional[PendingCheckin]:
        """
        Get the pending check-in for a user, if any

        Args:
            user_id: User identifier

        Returns:
            PendingCheckin if user has an active pending check-in, None otherwise
        """
        self._cleanup_if_needed()

        if user_id not in self._pending:
            return None

        pending = self._pending[user_id]

        # Check if expired
        if pending.is_expired:
            logger.info(f"Check-in for {pending.person_name} expired (window closed)")
            del self._pending[user_id]
            return None

        return pending

    def clear_pending_checkin(self, user_id: str) -> bool:
        """
        Clear the pending check-in for a user (after processing response)

        Args:
            user_id: User identifier

        Returns:
            True if was cleared, False if wasn't pending
        """
        if user_id in self._pending:
            pending = self._pending[user_id]
            logger.info(f"✓ Cleared check-in for {pending.person_name}")
            del self._pending[user_id]
            return True

        return False

    def _cleanup_if_needed(self):
        """
        Periodically remove expired check-ins to avoid memory leak

        This is called automatically by other methods.
        """
        now = datetime.now(TZ)

        if (now - self._last_cleanup) < self._cleanup_interval:
            return  # Not time to cleanup yet

        # Find and remove expired entries
        expired_users = [
            user_id
            for user_id, pending in self._pending.items()
            if pending.is_expired
        ]

        for user_id in expired_users:
            pending = self._pending[user_id]
            logger.debug(f"Auto-cleanup: removing expired check-in for {pending.person_name}")
            del self._pending[user_id]

        if expired_users:
            logger.info(f"✓ Cleaned up {len(expired_users)} expired check-ins")

        self._last_cleanup = now

    def get_stats(self) -> Dict:
        """Get statistics about pending check-ins"""
        self._cleanup_if_needed()

        return {
            "total_pending": len(self._pending),
            "pending_users": list(self._pending.keys()),
            "pending_types": list(set(p.checkin_type for p in self._pending.values()))
        }


# Global singleton instance
_tracker: Optional[PendingCheckinTracker] = None


def get_pending_checkin_tracker() -> PendingCheckinTracker:
    """
    Get or create the global pending check-in tracker

    Returns:
        PendingCheckinTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = PendingCheckinTracker()
    return _tracker
