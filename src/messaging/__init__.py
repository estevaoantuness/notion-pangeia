"""
M�dulo de Messaging - Otimiza��o de mensagens.
"""

from .chunker import MessageChunker
from .deduplicator import MessageDeduplicator, get_deduplicator

__all__ = [
    "MessageChunker",
    "MessageDeduplicator",
    "get_deduplicator"
]
