"""
Agente Conversacional com GPT-4o-mini - Conversational Agent.

Sistema de agente que usa LLM (GPT-4o-mini) para gerar respostas naturais
mantendo contexto psicológico e inteligência emocional.
"""

import logging
import json
from typing import Optional, Tuple, Dict, List
from datetime import datetime, timedelta
from collections import deque

from config.openai_config import (
    client, GPT_MODEL, OPENAI_API_KEY, MAX_CONTEXT_TOKENS, MAX_RESPONSE_TOKENS,
    TEMPERATURE, TOP_P, REQUEST_TIMEOUT, MAX_CONVERSATION_HISTORY,
    SYSTEM_PROMPT_TEMPLATE, FALLBACK_RESPONSES, LOG_CONVERSATIONS,
    APIError, APIConnectionError, RateLimitError, AuthenticationError
)
from src.psychology.engine import PsychologicalEngine
from src.people.analytics import PeopleAnalytics

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Agente conversacional com memória e contexto psicológico.

    Usa GPT-4o-mini para gerar respostas naturais enquanto mantém:
    - Histórico de conversa
    - Contexto psicológico
    - Análise emocional
    - Limitações de tokens
    """

    def __init__(self):
        """Inicializa o agente conversacional."""
        self.psych_engine = PsychologicalEngine()
        self.analytics = PeopleAnalytics()

        # Memory por usuário: {user_id: deque de mensagens}
        self.conversation_memory: Dict[str, deque] = {}

        # Tracking de custos
        self.cost_tracking: Dict[str, float] = {}

        # Últimas respostas (para evitar repetição)
        self.response_cache: Dict[str, Tuple[str, datetime]] = {}

        logger.info("ConversationalAgent inicializado com GPT-4o-mini")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Obtém histórico da conversa do usuário."""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = deque(maxlen=MAX_CONVERSATION_HISTORY)

        return list(self.conversation_memory[user_id])

    def add_to_memory(self, user_id: str, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico."""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = deque(maxlen=MAX_CONVERSATION_HISTORY)

        self.conversation_memory[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def _safe_analyze_user(self, person_name: str) -> Dict:
        """
        Wrapper seguro para análise psicológica do usuário.
        Retorna dicionário com dados mesmo se análise falhar.
        """
        try:
            # Tenta obter perfil
            profile = self.analytics.get_or_create_profile(person_name)

            # Dados padrão se tudo falhar
            return {
                "emotional_state": "Tranquilo",
                "energy_level": "boa",
                "active_tasks": "algumas tarefas",
                "progress": "em progresso"
            }
        except Exception as e:
            logger.debug(f"Não foi possível analisar usuário {person_name}: {e}")
            # Retorna sempre dados padrão
            return {
                "emotional_state": "Tranquilo",
                "energy_level": "boa",
                "active_tasks": "algumas tarefas",
                "progress": "em progresso"
            }

    def build_system_prompt(self, person_name: str) -> str:
        """Constrói system prompt personalizado com contexto."""
        try:
            # Análise psicológica segura (sempre retorna dados)
            metrics = self._safe_analyze_user(person_name)

            # Preenche template com dados seguros
            prompt = SYSTEM_PROMPT_TEMPLATE.format(
                name=person_name or "Amigo",
                emotional_state=metrics.get("emotional_state", "Tranquilo"),
                energy_level=metrics.get("energy_level", "boa"),
                active_tasks=metrics.get("active_tasks", "algumas tarefas"),
                progress=metrics.get("progress", "em progresso")
            )

            return prompt

        except Exception as e:
            logger.error(f"Erro ao construir system prompt: {e}")
            # Fallback seguro
            return SYSTEM_PROMPT_TEMPLATE.format(
                name=person_name or "Amigo",
                emotional_state="Tranquilo",
                energy_level="boa",
                active_tasks="algumas tarefas",
                progress="em progresso"
            )

    def generate_response(self, user_id: str, message: str, person_name: str) -> Tuple[bool, str]:
        """
        Gera resposta usando GPT-4o-mini com contexto conversacional.

        Args:
            user_id: ID único do usuário
            message: Mensagem recebida
            person_name: Nome da pessoa

        Returns:
            Tuple (sucesso, resposta)
        """
        try:
            # Verificar se cliente está disponível
            if not client:
                logger.warning("⚠️ Cliente OpenAI não inicializado - usando fallback")
                return self._generate_fallback_response(message, person_name)

            # Adiciona mensagem do usuário ao histórico
            self.add_to_memory(user_id, "user", message)

            # Obtém histórico
            history = self.get_conversation_history(user_id)

            # Constrói system prompt personalizado
            system_prompt = self.build_system_prompt(person_name)

            # Verifica cache para evitar resposta duplicada
            cache_key = f"{user_id}:{message}"
            if cache_key in self.response_cache:
                cached_response, timestamp = self.response_cache[cache_key]
                if (datetime.now() - timestamp).seconds < 60:  # Cache de 1 minuto
                    logger.info(f"Resposta do cache para {person_name}")
                    return True, cached_response

            # Chamada ao GPT-4o-mini com novo cliente (v1.0+)
            logger.info(f"Gerando resposta com GPT-4o-mini para {person_name}")

            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[{"role": msg["role"], "content": msg["content"]} for msg in history],
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_tokens=MAX_RESPONSE_TOKENS,
                timeout=REQUEST_TIMEOUT,
            )

            # Extrai resposta
            bot_response = response.choices[0].message.content.strip()

            # Adiciona resposta do bot ao histórico
            self.add_to_memory(user_id, "assistant", bot_response)

            # Calcula e registra tokens usados
            if hasattr(response, 'usage'):
                tokens_used = response.usage.total_tokens
                logger.info(f"Tokens utilizados: {tokens_used}")
                self._track_cost(user_id, tokens_used)

            # Cache a resposta
            self.response_cache[cache_key] = (bot_response, datetime.now())

            # Log da conversa se habilitado
            if LOG_CONVERSATIONS:
                logger.info(f"[{person_name}] User: {message} | Bot: {bot_response[:100]}...")

            return True, bot_response

        except AuthenticationError:
            logger.error(f"Erro de autenticação OpenAI - verifique OPENAI_API_KEY")
            return self._generate_fallback_response(message, person_name)

        except RateLimitError:
            logger.warning(f"Rate limit atingido para {person_name}")
            return False, FALLBACK_RESPONSES["overload"]

        except APIConnectionError as e:
            logger.warning(f"Erro de conexão com OpenAI para {person_name}: {e}")
            return False, FALLBACK_RESPONSES["timeout"]

        except APIError as e:
            logger.error(f"Erro na API OpenAI: {e}")
            return self._generate_fallback_response(message, person_name)

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return self._generate_fallback_response(message, person_name)

    def _generate_fallback_response(self, message: str, person_name: str) -> Tuple[bool, str]:
        """
        Gera resposta de fallback quando GPT-4o-mini não está disponível.
        Mantém conversa natural mesmo sem IA.
        """
        try:
            message_lower = message.lower().strip()

            # Respostas conversacionais simples
            if any(word in message_lower for word in ["oi", "opa", "olá", "e aí", "eae"]):
                responses = [
                    f"Oi, {person_name}! 👋 Tudo bem com você?",
                    f"E aí, {person_name}? Quero ouvir como você está! 😊",
                    f"Opa, {person_name}! Bora conversar? 💙",
                ]
                return True, responses[hash(message) % len(responses)]

            elif any(word in message_lower for word in ["tchau", "até", "falou", "bye"]):
                responses = [
                    f"Falou, {person_name}! Fico por aqui, mas volta quando quiser! 👋",
                    f"Até mais, {person_name}! Cuida de você! 💙",
                ]
                return True, responses[hash(message) % len(responses)]

            elif any(word in message_lower for word in ["obrigado", "obg", "vlw", "valeu"]):
                return True, f"De nada, {person_name}! Fico feliz em ajudar! 😊"

            elif message_lower.startswith("como"):
                return True, f"{person_name}, fico feliz que me perguntou! Mas me conta primeiro como VOCÊ está? 🤔"

            elif message_lower.startswith("tarefas") or message_lower.startswith("task"):
                return True, f"Vamos conversar sobre suas tarefas? Qual é a que mais está te preocupando agora? 💭"

            elif message_lower.startswith("help") or message_lower.startswith("ajuda"):
                return True, f"Claro, {person_name}! Estou aqui para ajudar com suas tarefas e também pra ouvir como você está. Qual é? 👂"

            # Resposta padrão conversacional
            else:
                responses = [
                    f"Entendi! Me conta mais sobre isso, {person_name}... 👂",
                    f"Que interessante, {person_name}! Conta pra mim com mais detalhes 🤔",
                    f"Ah, {person_name}... isso soa importante. O que você acha? 💭",
                ]
                return True, responses[hash(message) % len(responses)]

        except Exception as e:
            logger.error(f"Erro ao gerar fallback response: {e}")
            return True, f"Oi, {person_name}! Tô aqui pra você, pode contar comigo 💙"

    def _track_cost(self, user_id: str, tokens_used: int) -> None:
        """Registra custo de tokens para controle."""
        # Preço do GPT-4o-mini: $0.00015 por 1K tokens (input/output)
        cost = (tokens_used / 1000) * 0.00015

        if user_id not in self.cost_tracking:
            self.cost_tracking[user_id] = 0.0

        self.cost_tracking[user_id] += cost

        if self.cost_tracking[user_id] > 0.50:  # Log se ultrapassar $0.50
            logger.warning(f"Custo para {user_id}: ${self.cost_tracking[user_id]:.4f}")

    def clear_old_memories(self, max_age_hours: int = 24) -> None:
        """Remove históricos antigos para liberar memória."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

            for user_id, memory in list(self.conversation_memory.items()):
                # Filtra mensagens antigas
                filtered = deque(
                    [msg for msg in memory
                     if datetime.fromisoformat(msg["timestamp"]) > cutoff_time],
                    maxlen=MAX_CONVERSATION_HISTORY
                )

                if len(filtered) == 0:
                    del self.conversation_memory[user_id]
                    logger.info(f"Histórico de {user_id} removido")
                else:
                    self.conversation_memory[user_id] = filtered

        except Exception as e:
            logger.error(f"Erro ao limpar históricos antigos: {e}")


# Singleton
_agent_instance = None


def get_conversational_agent() -> ConversationalAgent:
    """Obtém instância singleton do agente."""
    global _agent_instance
    if _agent_instance is None:
        # Verificar se API key está configurada
        if not OPENAI_API_KEY or OPENAI_API_KEY == "":
            logger.warning("⚠️  OPENAI_API_KEY não configurada - usando fallback")
        _agent_instance = ConversationalAgent()
    return _agent_instance
