"""
Agente Conversacional com GPT-4o-mini - Conversational Agent.

Sistema de agente que usa LLM (GPT-4o-mini) para gerar respostas naturais
mantendo contexto psicológico e inteligência emocional.
"""

import logging
import json
from typing import Optional, Tuple, Dict, List
from datetime import datetime, timedelta

from config.openai_config import (
    client, GPT_MODEL, OPENAI_API_KEY, MAX_CONTEXT_TOKENS, MAX_RESPONSE_TOKENS,
    TEMPERATURE, TOP_P, REQUEST_TIMEOUT, MAX_CONVERSATION_HISTORY,
    SYSTEM_PROMPT_TEMPLATE, FALLBACK_RESPONSES, LOG_CONVERSATIONS,
    APIError, APIConnectionError, RateLimitError, AuthenticationError
)
from src.psychology.engine import PsychologicalEngine, EmotionalState
from src.people.analytics import PeopleAnalytics
from src.notion.tasks import TasksManager
from src.interventions.nudge_engine import NudgeEngine
from src.interventions.personalization import PersonalizationEngine
from src.memory.redis_manager import get_memory_manager
from src.memory.conversation_state import get_conversation_state
from src.agents.task_manager_agent import TaskManagerAgent

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
        self.tasks_manager = TasksManager()
        self.nudge_engine = NudgeEngine()
        self.personalization_engine = PersonalizationEngine()
        self.task_manager_agent = TaskManagerAgent()

        # Memory compartilhada entre workers via Redis
        self.memory_manager = get_memory_manager()

        # Conversation state para tracking de contexto
        self.conversation_state = get_conversation_state()

        # Tracking de custos
        self.cost_tracking: Dict[str, float] = {}

        # Últimas respostas (para evitar repetição)
        self.response_cache: Dict[str, Tuple[str, datetime]] = {}

        storage_type = "Redis" if self.memory_manager.is_redis_available() else "Local (warning: não persiste entre workers)"
        logger.info(f"ConversationalAgent inicializado com GPT-4o-mini + Task Manager + Nudge Engine + Memory ({storage_type})")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Obtém histórico da conversa do usuário."""
        return self.memory_manager.get_history(user_id, limit=MAX_CONVERSATION_HISTORY)

    def add_to_memory(self, user_id: str, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico."""
        self.memory_manager.add_message(
            user_id=user_id,
            role=role,
            content=content,
            max_messages=MAX_CONVERSATION_HISTORY
        )

    def _safe_analyze_user(self, person_name: str) -> Dict:
        """
        Wrapper seguro para análise psicológica do usuário.
        Retorna dicionário com dados mesmo se análise falhar.
        """
        try:
            # Busca tarefas reais do Notion
            tasks = self.tasks_manager.get_person_tasks(person_name, include_completed=True)
            progress = self.tasks_manager.calculate_progress(person_name)

            # Conta tarefas por status
            total_pendentes = len(tasks.get("a_fazer", [])) + len(tasks.get("em_andamento", []))
            em_andamento = len(tasks.get("em_andamento", []))
            a_fazer = len(tasks.get("a_fazer", []))
            concluidas = progress.get("concluidas", 0)
            total = progress.get("total", 0)
            percentual = progress.get("percentual", 0)

            # Monta descrição das tarefas ativas
            if total_pendentes == 0:
                active_tasks = "nenhuma tarefa pendente no momento"
            elif total_pendentes == 1:
                active_tasks = "1 tarefa pendente"
            else:
                active_tasks = f"{total_pendentes} tarefas pendentes ({em_andamento} em andamento, {a_fazer} a fazer)"

            # Monta descrição do progresso
            if total == 0:
                progress_desc = "sem tarefas registradas no momento"
            elif percentual == 100:
                progress_desc = "todas as tarefas concluídas! 🎉"
            elif percentual >= 80:
                progress_desc = f"excelente progresso: {concluidas} de {total} tarefas concluídas ({percentual}%)"
            elif percentual >= 50:
                progress_desc = f"bom progresso: {concluidas} de {total} tarefas concluídas ({percentual}%)"
            elif percentual >= 25:
                progress_desc = f"progresso moderado: {concluidas} de {total} tarefas concluídas ({percentual}%)"
            else:
                progress_desc = f"início do dia: {concluidas} de {total} tarefas concluídas ({percentual}%)"

            # Determina nível de energia baseado na carga de trabalho
            if total_pendentes == 0:
                energy_level = "tranquila"
            elif total_pendentes <= 3:
                energy_level = "boa"
            elif total_pendentes <= 7:
                energy_level = "moderada"
            else:
                energy_level = "alta carga"

            # Estado emocional baseado no progresso
            if percentual >= 80:
                emotional_state = "Motivado"
            elif percentual >= 50:
                emotional_state = "Equilibrado"
            elif total_pendentes > 10:
                emotional_state = "Sobrecarregado"
            else:
                emotional_state = "Tranquilo"

            return {
                "emotional_state": emotional_state,
                "energy_level": energy_level,
                "active_tasks": active_tasks,
                "progress": progress_desc
            }

        except Exception as e:
            logger.error(f"Erro ao analisar usuário {person_name}: {e}", exc_info=True)
            # Retorna dados padrão em caso de erro
            return {
                "emotional_state": "Tranquilo",
                "energy_level": "boa",
                "active_tasks": "algumas tarefas",
                "progress": "em progresso"
            }

    def build_system_prompt(self, person_name: str, user_id: str, history: List[Dict]) -> str:
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

            # Adicionar contexto de conversa
            context_summary = self.conversation_state.build_context_summary(user_id)
            if context_summary:
                prompt += f"\n\n{context_summary}"

            # Extrair contexto do histórico e atualizar estado
            context = self.conversation_state.extract_context_from_history(user_id, history)

            # Adicionar nota sobre evitar repetições
            if context.get("questions_asked_count", 0) > 1:
                prompt += "\n\n**IMPORTANTE**: Já houve conversa anterior. Evite repetir perguntas. Use o contexto!"

            # Adicionar referência ao último sentimento mencionado
            if context.get("user_mentioned_feeling"):
                feeling = context["user_mentioned_feeling"]
                prompt += f"\n\n**CONTEXTO**: Usuário mencionou que está {feeling}. Faça referência a isso!"

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
            # PRIMEIRO: Verificar se é comando de task (prioridade!)
            task_result = self.task_manager_agent.process_message(person_name, message)

            if task_result:
                success, response_text = task_result

                # Adiciona mensagens ao histórico
                self.add_to_memory(user_id, "user", message)
                self.add_to_memory(user_id, "assistant", response_text)

                logger.info(f"Comando de task processado para {person_name}")
                return success, response_text

            # Verificar se cliente está disponível
            if not client:
                logger.warning("⚠️ Cliente OpenAI não inicializado - usando fallback")
                return self._generate_fallback_response(message, person_name)

            # Adiciona mensagem do usuário ao histórico
            self.add_to_memory(user_id, "user", message)

            # Obtém histórico
            history = self.get_conversation_history(user_id)

            # Constrói system prompt personalizado com contexto
            system_prompt = self.build_system_prompt(person_name, user_id, history)

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
        Foca no Método Pangeia e capacidades do sistema.
        """
        try:
            message_lower = message.lower().strip()

            # Respostas focadas em Pangeia
            if any(word in message_lower for word in ["oi", "opa", "olá", "e aí", "eae"]):
                responses = [
                    f"E aí, {person_name}! 🌍 Sou o Pange.IA, seu assistente do Método Pangeia.\n\nPosso:\n✅ Criar e gerenciar suas tarefas\n✅ Decompor tarefas complexas\n✅ Mostrar seu progresso\n\nDiz 'minhas tarefas' ou 'cria tarefa pra X'!",
                    f"Opa, {person_name}! 👋 Tô aqui pelo Método Pangeia - criar, organizar e cuidar.\n\nQuer ver suas tarefas? Ou criar uma nova? Me conta!",
                    f"Oi, {person_name}! 🚀 Pange.IA aqui. Consigo gerenciar suas tasks, prever burnout, e te ajudar a ser produtivo sem se queimar.\n\nPor onde começamos?",
                ]
                return True, responses[hash(message) % len(responses)]

            elif any(word in message_lower for word in ["tchau", "até", "falou", "bye"]):
                responses = [
                    f"Falou, {person_name}! Quando precisar de ajuda com tasks ou quiser saber mais sobre Pangeia, tô aqui! 🌍",
                    f"Até mais, {person_name}! Lembra: posso criar tasks, decompor projetos e monitorar teu progresso. Volta sempre! 💙",
                ]
                return True, responses[hash(message) % len(responses)]

            elif any(word in message_lower for word in ["obrigado", "obg", "vlw", "valeu"]):
                return True, f"Por nada, {person_name}! É pra isso que o Método Pangeia existe - te ajudar a ser produtivo de forma sustentável! 🌍"

            elif message_lower.startswith("como") or "o que você faz" in message_lower:
                return True, f"Sou o Pange.IA, {person_name}! 🌍\n\nMétodo Pangeia = Criar + Organizar + Cuidar\n\nEu:\n✅ Gerencio tasks no Notion\n✅ Decomponho tarefas grandes\n✅ Monitoro sinais de burnout\n✅ Gamificação (XP, níveis, badges)\n\nExperimenta: 'minhas tarefas' ou 'cria tarefa pra estudar X'"

            elif message_lower.startswith("tarefas") or message_lower.startswith("task"):
                return True, f"Show, {person_name}! Posso te ajudar com tasks de várias formas:\n\n📋 'minhas tarefas' - vejo todas as suas\n✅ 'terminei a tarefa X' - marco como concluída\n🎯 'cria tarefa pra Y' - adiciono no Notion\n✂️ 'quebra essa tarefa' - decomponho em subtasks\n\nQual tu quer?"

            elif message_lower.startswith("help") or message_lower.startswith("ajuda"):
                return True, f"Claro, {person_name}! Sou o assistente do Método Pangeia 🌍\n\nComandos:\n• 'minhas tarefas'\n• 'cria tarefa pra X'\n• 'terminei a tarefa Y'\n• 'quebra essa tarefa'\n\nTambém monitoro burnout, gamificação e produtividade!\n\nO que quer fazer?"

            # Resposta padrão focada em valor
            else:
                responses = [
                    f"Entendi, {person_name}! Posso te ajudar com isso criando tasks ou organizando melhor?\n\nExperimenta: 'cria tarefa pra X' ou 'minhas tarefas' 🚀",
                    f"Interessante! Quer que eu crie uma tarefa sobre isso? Ou prefere ver suas tasks atuais?\n\nPangeia é sobre criar, organizar e cuidar! 🌍",
                    f"Saquei, {person_name}. Como o Método Pangeia pode ajudar nisso? Posso:\n• Criar tasks\n• Decompor em subtasks\n• Mostrar progresso\n\nQue tal?",
                ]
                return True, responses[hash(message) % len(responses)]

        except Exception as e:
            logger.error(f"Erro ao gerar fallback response: {e}")
            return True, f"Oi, {person_name}! Sou o Pange.IA 🌍 - gerencio tasks, previno burnout e te ajudo a ser produtivo. Diz 'minhas tarefas' pra começar!"

    def _track_cost(self, user_id: str, tokens_used: int) -> None:
        """Registra custo de tokens para controle."""
        # Preço do GPT-4o-mini: $0.00015 por 1K tokens (input/output)
        cost = (tokens_used / 1000) * 0.00015

        if user_id not in self.cost_tracking:
            self.cost_tracking[user_id] = 0.0

        self.cost_tracking[user_id] += cost

        if self.cost_tracking[user_id] > 0.50:  # Log se ultrapassar $0.50
            logger.warning(f"Custo para {user_id}: ${self.cost_tracking[user_id]:.4f}")

    def get_nudge_if_appropriate(
        self,
        person_name: str,
        phone: str,
        context: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Retorna nudge apropriado se for o momento certo.

        Args:
            person_name: Nome da pessoa
            phone: Telefone da pessoa
            context: Contexto adicional (opcional)

        Returns:
            Mensagem de nudge ou None
        """
        try:
            # Obter perfil e métricas
            profile = self.analytics.get_or_create_profile(person_name, phone)

            # Buscar tarefas e calcular métricas psicológicas
            tasks = self.tasks_manager.get_person_tasks(person_name)
            progress = self.tasks_manager.calculate_progress(person_name)

            # Criar métricas psicológicas básicas
            from src.psychology.engine import PsychologicalMetrics

            metrics = PsychologicalMetrics()
            metrics.tasks_completed_today = progress.get("concluidas", 0)
            metrics.tasks_pending = progress.get("pendentes", 0)
            metrics.completion_rate = progress.get("percentual", 0) / 100.0

            # Determinar estado emocional aproximado
            total_pendentes = len(tasks.get("a_fazer", [])) + len(tasks.get("em_andamento", []))

            if total_pendentes > 10:
                metrics.emotional_state = EmotionalState.OVERWHELMED
            elif progress.get("percentual", 0) >= 80:
                metrics.emotional_state = EmotionalState.MOTIVATED
            else:
                metrics.emotional_state = EmotionalState.BALANCED

            # Selecionar melhor nudge
            nudge = self.nudge_engine.select_best_nudge(
                person_name,
                profile,
                metrics,
                context or {}
            )

            if not nudge:
                return None

            # Verificar se deve enviar
            should_send = self.personalization_engine.should_send_nudge(
                person_name,
                profile,
                metrics,
                nudge.nudge_type
            )

            if not should_send:
                logger.debug(f"Nudge suprimido para {person_name} - contexto inadequado")
                return None

            # Personalizar nudge
            personalized_nudge = self.personalization_engine.personalize_nudge(
                nudge,
                person_name,
                profile
            )

            logger.info(f"Nudge selecionado para {person_name}: {personalized_nudge.nudge_type.value}")

            return personalized_nudge.message

        except Exception as e:
            logger.error(f"Erro ao buscar nudge: {e}", exc_info=True)
            return None

    def clear_old_memories(self, max_age_hours: int = 24) -> None:
        """Remove históricos antigos para liberar memória."""
        try:
            removed = self.memory_manager.cleanup_old_conversations(max_age_hours)
            if removed > 0:
                logger.info(f"{removed} conversas antigas removidas")
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
