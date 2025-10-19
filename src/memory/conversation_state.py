"""
Conversation State - Tracking de Estado e Contexto da Conversa.

Monitora tópicos discutidos, preferências do usuário e contexto acumulado.
"""

import logging
from typing import Dict, List, Set, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ConversationState:
    """
    Gerencia estado e contexto de conversas.

    Rastreia:
    - Tópicos já discutidos
    - Perguntas já feitas
    - Preferências do usuário
    - Respostas importantes
    """

    def __init__(self):
        """Inicializa o gerenciador de estado."""
        # Perguntas já feitas por user_id
        self.asked_questions: Dict[str, Set[str]] = {}

        # Tópicos discutidos por user_id
        self.discussed_topics: Dict[str, Set[str]] = {}

        # Preferências coletadas por user_id
        self.user_preferences: Dict[str, Dict[str, str]] = {}

        # Última informação importante por user_id
        self.last_important_info: Dict[str, str] = {}

        logger.info("ConversationState inicializado")

    def mark_question_asked(self, user_id: str, question_type: str) -> None:
        """
        Marca que uma pergunta foi feita.

        Args:
            user_id: ID do usuário
            question_type: Tipo da pergunta (ex: "como_voce_esta", "suas_tarefas")
        """
        if user_id not in self.asked_questions:
            self.asked_questions[user_id] = set()

        self.asked_questions[user_id].add(question_type.lower())

    def was_question_asked(self, user_id: str, question_type: str) -> bool:
        """
        Verifica se uma pergunta já foi feita.

        Args:
            user_id: ID do usuário
            question_type: Tipo da pergunta

        Returns:
            True se já foi perguntado
        """
        if user_id not in self.asked_questions:
            return False

        return question_type.lower() in self.asked_questions[user_id]

    def add_discussed_topic(self, user_id: str, topic: str) -> None:
        """
        Adiciona tópico à lista de discutidos.

        Args:
            user_id: ID do usuário
            topic: Tópico (ex: "saude_mental", "tarefas", "familia")
        """
        if user_id not in self.discussed_topics:
            self.discussed_topics[user_id] = set()

        self.discussed_topics[user_id].add(topic.lower())

    def was_topic_discussed(self, user_id: str, topic: str) -> bool:
        """
        Verifica se um tópico já foi discutido.

        Args:
            user_id: ID do usuário
            topic: Tópico

        Returns:
            True se já foi discutido
        """
        if user_id not in self.discussed_topics:
            return False

        return topic.lower() in self.discussed_topics[user_id]

    def save_preference(self, user_id: str, key: str, value: str) -> None:
        """
        Salva preferência do usuário.

        Args:
            user_id: ID do usuário
            key: Chave da preferência (ex: "horario_preferido")
            value: Valor
        """
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        self.user_preferences[user_id][key] = value
        logger.debug(f"Preferência salva para {user_id}: {key} = {value}")

    def get_preference(self, user_id: str, key: str) -> Optional[str]:
        """
        Obtém preferência do usuário.

        Args:
            user_id: ID do usuário
            key: Chave da preferência

        Returns:
            Valor ou None
        """
        if user_id not in self.user_preferences:
            return None

        return self.user_preferences[user_id].get(key)

    def save_important_info(self, user_id: str, info: str) -> None:
        """
        Salva última informação importante dita pelo usuário.

        Args:
            user_id: ID do usuário
            info: Informação (ex: "to beleza", "estou cansado")
        """
        self.last_important_info[user_id] = info

    def get_last_important_info(self, user_id: str) -> Optional[str]:
        """
        Obtém última informação importante.

        Args:
            user_id: ID do usuário

        Returns:
            Informação ou None
        """
        return self.last_important_info.get(user_id)

    def extract_context_from_history(
        self,
        user_id: str,
        history: List[Dict]
    ) -> Dict:
        """
        Extrai contexto útil do histórico de conversa.

        Args:
            user_id: ID do usuário
            history: Histórico de mensagens

        Returns:
            Dict com contexto extraído
        """
        context = {
            "user_mentioned_feeling": None,
            "user_mentioned_tasks": False,
            "user_mentioned_family": False,
            "user_mentioned_health": False,
            "last_user_message": None,
            "questions_asked_count": 0
        }

        # Analisa histórico
        for msg in history:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                context["last_user_message"] = msg.get("content", "")

                # Detectar sentimento mencionado
                feelings = {
                    "to beleza": "bem",
                    "tô bem": "bem",
                    "estou bem": "bem",
                    "to cansado": "cansado",
                    "estou cansado": "cansado",
                    "to estressado": "estressado",
                    "tô de boa": "tranquilo"
                }

                for phrase, feeling in feelings.items():
                    if phrase in content:
                        context["user_mentioned_feeling"] = feeling
                        self.save_important_info(user_id, msg.get("content", ""))
                        break

                # Detectar tópicos
                if any(word in content for word in ["tarefa", "task", "fazer", "projeto"]):
                    context["user_mentioned_tasks"] = True
                    self.add_discussed_topic(user_id, "tarefas")

                if any(word in content for word in ["família", "familia", "filho", "esposa", "marido"]):
                    context["user_mentioned_family"] = True
                    self.add_discussed_topic(user_id, "familia")

                if any(word in content for word in ["saúde", "saude", "doente", "médico", "medico"]):
                    context["user_mentioned_health"] = True
                    self.add_discussed_topic(user_id, "saude")

            elif msg.get("role") == "assistant":
                content = msg.get("content", "").lower()

                # Contar perguntas feitas pelo bot
                if "?" in content:
                    context["questions_asked_count"] += 1

                # Identificar tipos de perguntas já feitas
                if "como você está" in content or "como você tá" in content:
                    self.mark_question_asked(user_id, "como_voce_esta")

                if "suas tarefas" in content or "quais tarefas" in content:
                    self.mark_question_asked(user_id, "suas_tarefas")

        return context

    def should_avoid_repetition(self, user_id: str, question_type: str) -> bool:
        """
        Verifica se deve evitar repetir uma pergunta.

        Args:
            user_id: ID do usuário
            question_type: Tipo da pergunta

        Returns:
            True se deve evitar
        """
        return self.was_question_asked(user_id, question_type)

    def build_context_summary(self, user_id: str) -> str:
        """
        Constrói resumo do contexto para o system prompt.

        Args:
            user_id: ID do usuário

        Returns:
            String com resumo contextual
        """
        parts = []

        # Última informação importante
        last_info = self.get_last_important_info(user_id)
        if last_info:
            parts.append(f"Lembrete: usuário disse '{last_info}' recentemente")

        # Tópicos já discutidos
        if user_id in self.discussed_topics and self.discussed_topics[user_id]:
            topics_list = ", ".join(self.discussed_topics[user_id])
            parts.append(f"Tópicos já discutidos: {topics_list}")

        # Perguntas já feitas
        if user_id in self.asked_questions and self.asked_questions[user_id]:
            # Evitar mencionar todas, apenas destacar que já houve conversa
            parts.append("Já houve conversa anterior - evite repetir perguntas")

        # Preferências
        if user_id in self.user_preferences and self.user_preferences[user_id]:
            prefs = self.user_preferences[user_id]
            for key, value in prefs.items():
                parts.append(f"Preferência: {key} = {value}")

        if not parts:
            return ""

        return "\n".join(["**CONTEXTO DA CONVERSA:**"] + parts)

    def clear_user_state(self, user_id: str) -> None:
        """
        Limpa estado de um usuário.

        Args:
            user_id: ID do usuário
        """
        if user_id in self.asked_questions:
            del self.asked_questions[user_id]

        if user_id in self.discussed_topics:
            del self.discussed_topics[user_id]

        if user_id in self.user_preferences:
            del self.user_preferences[user_id]

        if user_id in self.last_important_info:
            del self.last_important_info[user_id]

        logger.info(f"Estado limpo para {user_id}")


# Singleton
_state_instance = None


def get_conversation_state() -> ConversationState:
    """Obtém instância singleton do conversation state."""
    global _state_instance
    if _state_instance is None:
        _state_instance = ConversationState()
    return _state_instance
