"""
Conversation History - Sistema de Memória Conversacional.

Armazena histórico de conversas com limite de 10 mensagens por usuário.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class ConversationHistory:
    """
    Gerencia histórico de conversas por usuário.

    Mantém as últimas 10 mensagens de cada usuário para contexto conversacional.
    """

    MAX_MESSAGES = 10  # Máximo de mensagens no histórico

    def __init__(self):
        """Inicializa o gerenciador de histórico."""
        # Formato: {user_id: deque([{msg}, {msg}, ...])}
        self._histories: Dict[str, deque] = {}
        logger.info(f"ConversationHistory inicializado (max {self.MAX_MESSAGES} msgs)")

    def add_message(
        self,
        user_id: str,
        message: str,
        role: str = "user",
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Adiciona mensagem ao histórico.

        Args:
            user_id: ID do usuário (ex: nome ou número)
            message: Conteúdo da mensagem
            role: "user" ou "assistant"
            metadata: Dados adicionais (intent, status, etc.)
        """
        # Criar histórico se não existe
        if user_id not in self._histories:
            self._histories[user_id] = deque(maxlen=self.MAX_MESSAGES)

        # Adicionar mensagem
        msg_data = {
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self._histories[user_id].append(msg_data)

        logger.debug(
            f"Mensagem adicionada ao histórico de {user_id}: "
            f"{role} - '{message[:50]}...' "
            f"({len(self._histories[user_id])}/{self.MAX_MESSAGES})"
        )

    def get_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Retorna histórico de mensagens do usuário.

        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens (None = todas)

        Returns:
            Lista de mensagens ordenadas (mais antiga → mais recente)
        """
        if user_id not in self._histories:
            return []

        history = list(self._histories[user_id])

        if limit:
            history = history[-limit:]  # Últimas N mensagens

        return history

    def get_context_for_llm(self, user_id: str, max_messages: int = 10) -> List[Dict]:
        """
        Retorna histórico formatado para LLM (OpenAI format).

        Args:
            user_id: ID do usuário
            max_messages: Máximo de mensagens

        Returns:
            Lista no formato [{"role": "user/assistant", "content": "..."}]
        """
        history = self.get_history(user_id, limit=max_messages)

        # Converter para formato OpenAI
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in history
        ]

    def clear_history(self, user_id: str) -> None:
        """
        Limpa histórico de um usuário.

        Args:
            user_id: ID do usuário
        """
        if user_id in self._histories:
            self._histories[user_id].clear()
            logger.info(f"Histórico limpo para {user_id}")

    def get_last_user_message(self, user_id: str) -> Optional[str]:
        """
        Retorna última mensagem do usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Conteúdo da última mensagem ou None
        """
        history = self.get_history(user_id)

        # Buscar última mensagem do usuário
        for msg in reversed(history):
            if msg["role"] == "user":
                return msg["content"]

        return None

    def get_summary(self, user_id: str) -> Dict:
        """
        Retorna resumo do histórico.

        Args:
            user_id: ID do usuário

        Returns:
            Dict com estatísticas
        """
        history = self.get_history(user_id)

        user_msgs = sum(1 for msg in history if msg["role"] == "user")
        assistant_msgs = sum(1 for msg in history if msg["role"] == "assistant")

        return {
            "total_messages": len(history),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "oldest_message": history[0]["timestamp"] if history else None,
            "newest_message": history[-1]["timestamp"] if history else None
        }


# Instância global
_conversation_history = None


def get_conversation_history() -> ConversationHistory:
    """
    Retorna instância global do ConversationHistory.

    Returns:
        ConversationHistory singleton
    """
    global _conversation_history
    if _conversation_history is None:
        _conversation_history = ConversationHistory()
    return _conversation_history
