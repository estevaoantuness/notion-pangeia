"""
Message Deduplicator - Evita envio de mensagens duplicadas.
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class MessageDeduplicator:
    """Evita envio de mensagens duplicadas."""

    IDENTICAL_TIMEOUT = 30  # segundos
    SIMILAR_TIMEOUT = 60
    SIMILARITY_THRESHOLD = 0.85

    def __init__(self):
        self.message_history: Dict[str, list] = {}

    def should_send(
        self,
        user_id: str,
        message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica se mensagem deve ser enviada.

        Returns:
            (should_send, reason)
        """
        now = datetime.now()

        if user_id not in self.message_history:
            self.message_history[user_id] = []

        # Limpar antigas
        cutoff = now - timedelta(seconds=self.SIMILAR_TIMEOUT * 2)
        self.message_history[user_id] = [
            (msg, ts) for msg, ts in self.message_history[user_id]
            if ts > cutoff
        ]

        # Verificar duplicidade
        for prev_msg, prev_time in self.message_history[user_id]:
            time_diff = (now - prev_time).total_seconds()

            # Idêntica
            if message == prev_msg and time_diff < self.IDENTICAL_TIMEOUT:
                return False, f"Idêntica há {time_diff:.0f}s"

            # Similar
            similarity = SequenceMatcher(None, message, prev_msg).ratio()
            if similarity >= self.SIMILARITY_THRESHOLD and time_diff < self.SIMILAR_TIMEOUT:
                return False, f"Similar ({similarity:.0%}) há {time_diff:.0f}s"

        # Adicionar ao histórico
        self.message_history[user_id].append((message, now))

        # Limitar tamanho
        if len(self.message_history[user_id]) > 10:
            self.message_history[user_id] = self.message_history[user_id][-10:]

        return True, None


# Instância global
_deduplicator = None


def get_deduplicator() -> MessageDeduplicator:
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = MessageDeduplicator()
    return _deduplicator
