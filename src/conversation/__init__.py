"""
Conversation Management - Gerenciamento de Conversas.

Módulo para gerenciar, registrar e analisar conversas.
"""

from .logger import ConversationLogger, get_conversation_logger

__all__ = [
    "ConversationLogger",
    "get_conversation_logger",
]
