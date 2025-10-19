"""
Conversation Memory - Memória de Longo Prazo para Conversações.

Mantém contexto de longo prazo sobre:
- Preferências do usuário
- Tópicos já discutidos
- Insights compartilhados
- Padrões de conversa

Diferente do RedisMemoryManager (histórico de mensagens),
este módulo mantém CONHECIMENTO sobre a pessoa.
"""

import logging
import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class UserPreference:
    """Preferência do usuário."""
    key: str  # ex: "communication_style"
    value: str  # ex: "direct_no_fluff"
    learned_at: str  # timestamp
    confidence: float  # 0-1


@dataclass
class DiscussedTopic:
    """Tópico já discutido."""
    topic: str
    last_discussed: str  # timestamp
    discussion_count: int
    key_points: List[str]


@dataclass
class SharedInsight:
    """Insight já compartilhado."""
    insight_type: str  # ex: "pattern_detected"
    content: str
    shared_at: str  # timestamp
    user_reaction: Optional[str]  # "positive", "negative", "neutral"


class ConversationMemory:
    """
    Memória de longo prazo para conversações.

    Armazena conhecimento sobre a pessoa ao longo do tempo,
    permitindo conversas mais naturais e contextuais.
    """

    def __init__(self, storage_backend=None):
        """
        Inicializa memória de conversação.

        Args:
            storage_backend: Backend de persistência (Redis, DB, etc.)
                            Se None, usa memória local (não persistente)
        """
        self.storage = storage_backend

        # Memória local (fallback se sem storage)
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = defaultdict(dict)
        self.discussed_topics: Dict[str, Dict[str, DiscussedTopic]] = defaultdict(dict)
        self.shared_insights: Dict[str, List[SharedInsight]] = defaultdict(list)
        self.conversation_context: Dict[str, Dict] = defaultdict(dict)

        logger.info("ConversationMemory inicializada")

    def learn_preference(
        self,
        user_id: str,
        key: str,
        value: str,
        confidence: float = 0.8
    ):
        """
        Aprende uma preferência do usuário.

        Args:
            user_id: ID do usuário
            key: Chave da preferência (ex: "communication_style")
            value: Valor da preferência
            confidence: Confiança (0-1)
        """
        preference = UserPreference(
            key=key,
            value=value,
            learned_at=datetime.now().isoformat(),
            confidence=confidence
        )

        self.user_preferences[user_id][key] = preference

        if self.storage:
            self._save_to_storage(user_id, "preferences")

        logger.info(f"Preferência aprendida: {user_id} -> {key}={value}")

    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """
        Recupera preferência do usuário.

        Returns:
            Valor da preferência ou None
        """
        if self.storage:
            self._load_from_storage(user_id, "preferences")

        pref = self.user_preferences[user_id].get(key)
        return pref.value if pref else None

    def mark_topic_discussed(
        self,
        user_id: str,
        topic: str,
        key_points: Optional[List[str]] = None
    ):
        """
        Marca tópico como discutido.

        Args:
            user_id: ID do usuário
            topic: Tópico discutido
            key_points: Pontos-chave da discussão
        """
        if topic in self.discussed_topics[user_id]:
            # Tópico já existe, incrementa contador
            existing = self.discussed_topics[user_id][topic]
            existing.last_discussed = datetime.now().isoformat()
            existing.discussion_count += 1

            if key_points:
                existing.key_points.extend(key_points)
        else:
            # Novo tópico
            self.discussed_topics[user_id][topic] = DiscussedTopic(
                topic=topic,
                last_discussed=datetime.now().isoformat(),
                discussion_count=1,
                key_points=key_points or []
            )

        if self.storage:
            self._save_to_storage(user_id, "topics")

        logger.info(f"Tópico marcado: {user_id} -> {topic}")

    def was_topic_discussed_recently(
        self,
        user_id: str,
        topic: str,
        days: int = 7
    ) -> bool:
        """
        Verifica se tópico foi discutido recentemente.

        Args:
            user_id: ID do usuário
            topic: Tópico
            days: Últimos N dias

        Returns:
            True se discutido nos últimos N dias
        """
        if self.storage:
            self._load_from_storage(user_id, "topics")

        discussed = self.discussed_topics[user_id].get(topic)

        if not discussed:
            return False

        last_discussed = datetime.fromisoformat(discussed.last_discussed)
        cutoff = datetime.now() - timedelta(days=days)

        return last_discussed > cutoff

    def record_shared_insight(
        self,
        user_id: str,
        insight_type: str,
        content: str,
        user_reaction: Optional[str] = None
    ):
        """
        Registra insight compartilhado.

        Args:
            user_id: ID do usuário
            insight_type: Tipo de insight
            content: Conteúdo do insight
            user_reaction: Reação do usuário
        """
        insight = SharedInsight(
            insight_type=insight_type,
            content=content,
            shared_at=datetime.now().isoformat(),
            user_reaction=user_reaction
        )

        self.shared_insights[user_id].append(insight)

        if self.storage:
            self._save_to_storage(user_id, "insights")

        logger.info(f"Insight registrado: {user_id} -> {insight_type}")

    def was_insight_shared_recently(
        self,
        user_id: str,
        insight_type: str,
        days: int = 7
    ) -> bool:
        """
        Verifica se insight já foi compartilhado recentemente.

        Evita repetir insights parecidos.

        Args:
            user_id: ID do usuário
            insight_type: Tipo de insight
            days: Últimos N dias

        Returns:
            True se já foi compartilhado
        """
        if self.storage:
            self._load_from_storage(user_id, "insights")

        cutoff = datetime.now() - timedelta(days=days)

        for insight in self.shared_insights[user_id]:
            if insight.insight_type == insight_type:
                shared_at = datetime.fromisoformat(insight.shared_at)
                if shared_at > cutoff:
                    return True

        return False

    def get_conversation_summary(self, user_id: str) -> Dict:
        """
        Retorna resumo do que sabemos sobre o usuário.

        Returns:
            Dict com preferências, tópicos discutidos, etc.
        """
        if self.storage:
            self._load_from_storage(user_id, "preferences")
            self._load_from_storage(user_id, "topics")
            self._load_from_storage(user_id, "insights")

        # Top 5 tópicos mais discutidos
        topics = sorted(
            self.discussed_topics[user_id].values(),
            key=lambda t: t.discussion_count,
            reverse=True
        )[:5]

        # Preferências ativas
        preferences = {
            key: pref.value
            for key, pref in self.user_preferences[user_id].items()
            if pref.confidence >= 0.5
        }

        # Insights recentes (últimos 7 dias)
        cutoff = datetime.now() - timedelta(days=7)
        recent_insights = [
            insight for insight in self.shared_insights[user_id]
            if datetime.fromisoformat(insight.shared_at) > cutoff
        ]

        return {
            "preferences": preferences,
            "top_topics": [
                {
                    "topic": t.topic,
                    "count": t.discussion_count,
                    "last_discussed": t.last_discussed
                }
                for t in topics
            ],
            "recent_insights_count": len(recent_insights),
            "total_discussions": sum(
                t.discussion_count for t in self.discussed_topics[user_id].values()
            )
        }

    def update_context(self, user_id: str, key: str, value):
        """
        Atualiza contexto da conversa atual.

        Contexto de curto prazo (sessão atual).

        Args:
            user_id: ID do usuário
            key: Chave do contexto
            value: Valor
        """
        self.conversation_context[user_id][key] = value

    def get_context(self, user_id: str, key: str, default=None):
        """
        Recupera contexto da conversa.

        Returns:
            Valor do contexto ou default
        """
        return self.conversation_context[user_id].get(key, default)

    def clear_session_context(self, user_id: str):
        """Limpa contexto de sessão (mas mantém memória de longo prazo)."""
        self.conversation_context[user_id] = {}
        logger.info(f"Contexto de sessão limpo: {user_id}")

    def _save_to_storage(self, user_id: str, data_type: str):
        """Salva dados no backend de armazenamento."""
        if not self.storage:
            return

        try:
            if data_type == "preferences":
                data = {
                    key: asdict(pref)
                    for key, pref in self.user_preferences[user_id].items()
                }
            elif data_type == "topics":
                data = {
                    topic: asdict(discussed)
                    for topic, discussed in self.discussed_topics[user_id].items()
                }
            elif data_type == "insights":
                data = [asdict(insight) for insight in self.shared_insights[user_id]]
            else:
                return

            key = f"conversation_memory:{user_id}:{data_type}"
            self.storage.set(key, json.dumps(data), ex=60*60*24*90)  # 90 dias TTL

        except Exception as e:
            logger.error(f"Erro ao salvar no storage: {e}")

    def _load_from_storage(self, user_id: str, data_type: str):
        """Carrega dados do backend de armazenamento."""
        if not self.storage:
            return

        try:
            key = f"conversation_memory:{user_id}:{data_type}"
            data_json = self.storage.get(key)

            if not data_json:
                return

            data = json.loads(data_json)

            if data_type == "preferences":
                self.user_preferences[user_id] = {
                    key: UserPreference(**pref_data)
                    for key, pref_data in data.items()
                }
            elif data_type == "topics":
                self.discussed_topics[user_id] = {
                    topic: DiscussedTopic(**topic_data)
                    for topic, topic_data in data.items()
                }
            elif data_type == "insights":
                self.shared_insights[user_id] = [
                    SharedInsight(**insight_data)
                    for insight_data in data
                ]

        except Exception as e:
            logger.error(f"Erro ao carregar do storage: {e}")


# Singleton global
_conversation_memory = None


def get_conversation_memory(storage_backend=None) -> ConversationMemory:
    """Retorna instância singleton de ConversationMemory."""
    global _conversation_memory

    if _conversation_memory is None:
        _conversation_memory = ConversationMemory(storage_backend)

    return _conversation_memory
