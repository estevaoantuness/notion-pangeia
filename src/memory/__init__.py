"""
Memory Module - Gerenciamento de Memória e Contexto.

Gerencia persistência de conversas e contexto usando Redis.
"""

from .redis_manager import RedisMemoryManager
from .conversation_state import ConversationState, get_conversation_state

__all__ = ['RedisMemoryManager', 'ConversationState', 'get_conversation_state']
