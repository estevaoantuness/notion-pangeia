"""
Processador de comandos.

Este módulo orquestra o fluxo completo de processamento de comandos:
parse → handler → resposta.

Agora com sistema NLP robusto:
- Normalização de acentos, pontuação e emojis
- Conversão de números por extenso
- Mapeamento de sinônimos
- Fuzzy matching para equivalência
- Slot-filling para comandos incompletos
- Desambiguação inteligente (sem "não entendi")
"""

import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from src.commands.parser import CommandParser
from src.commands.normalizer import parse as nlp_parse, ParseResult, is_confirmation
from src.commands.handlers import CommandHandlers
from config.colaboradores import get_colaborador_by_phone
from src.messaging.humanizer import get_humanizer
from src.onboarding.manager import get_onboarding_manager
from src.psychology.engine import PsychologicalEngine
from src.psychology.communicator import EmpatheticCommunicator
from src.people.analytics import PeopleAnalytics

logger = logging.getLogger(__name__)


class CommandProcessor:
    """
    Processa comandos recebidos via WhatsApp com NLP robusto.

    Orquestra: identificação de pessoa → parse NLP → slot-filling → execução → resposta.

    Features:
    - Parse com normalização completa (acentos, sinônimos, números)
    - Desambiguação inteligente (sem "não entendi")
    - Slot-filling para comandos incompletos
    - Tratamento de confirmações e contexto
    - Detecção de mensagens repetidas
    """

    # Confidence threshold para aceitar comando
    CONFIDENCE_THRESHOLD = 0.75

    # Timeout para slot-filling (segundos)
    SLOT_FILLING_TIMEOUT = 120

    def __init__(self, handlers: Optional[CommandHandlers] = None):
        """
        Inicializa o processador com suporte conversacional e psicologia.

        Args:
            handlers: Handlers de comandos (cria um novo se não fornecido)
        """
        self.parser = CommandParser()  # Mantido para retrocompatibilidade
        self.handlers = handlers or CommandHandlers()
        self.humanizer = get_humanizer()
        self.onboarding = get_onboarding_manager()

        # Componentes psicológicos
        self.psych_engine = PsychologicalEngine()
        self.empathetic_communicator = EmpatheticCommunicator()
        self.people_analytics = PeopleAnalytics()

        # Estado de slot-filling por usuário
        self.user_states: Dict[str, Dict[str, Any]] = {}

        # Cache de mensagens recentes (para detectar repetições)
        self.recent_messages: Dict[str, Tuple[str, datetime]] = {}

        logger.info("CommandProcessor inicializado com NLP robusto + inteligência psicológica")

    def _check_repeated_message(self, user_id: str, message: str) -> bool:
        """
        Verifica se a mensagem foi enviada recentemente (< 30s)

        Returns:
            True se é repetição
        """
        now = datetime.now()

        if user_id in self.recent_messages:
            prev_message, prev_time = self.recent_messages[user_id]

            # Se mensagem igual em < 30s
            if prev_message == message and (now - prev_time).total_seconds() < 30:
                return True

        # Atualizar cache
        self.recent_messages[user_id] = (message, now)
        return False

    def _get_user_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna o estado atual do usuário (slot-filling)"""
        if user_id not in self.user_states:
            return None

        state = self.user_states[user_id]

        # Verificar timeout
        if "timestamp" in state:
            elapsed = (datetime.now() - state["timestamp"]).total_seconds()
            if elapsed > self.SLOT_FILLING_TIMEOUT:
                # Expirou
                del self.user_states[user_id]
                return None

        return state

    def _set_user_state(self, user_id: str, state: Dict[str, Any]) -> None:
        """Define estado do usuário (slot-filling)"""
        state["timestamp"] = datetime.now()
        self.user_states[user_id] = state

    def _clear_user_state(self, user_id: str) -> None:
        """Limpa estado do usuário"""
        if user_id in self.user_states:
            del self.user_states[user_id]

    def _get_disambiguation_message(self) -> str:
        """Retorna mensagem de desambiguação com sugestões"""
        return """Posso ajudar com:

• *tarefas* - ver suas tarefas
• *progresso* - ver andamento do dia
• *feito N* - marcar tarefa N como concluída
• *andamento N* - marcar tarefa N em andamento
• *ajuda* - ver todos os comandos

O que você precisa?"""

    def _get_contextual_greeting(self, person_name: str) -> Tuple[str, Optional[str]]:
        """
        Retorna saudação contextual baseada no horário + lista de comandos

        Returns:
            Tuple (mensagem, ação_pendente)
        """
        hour = datetime.now().hour

        # Saudação contextual
        if hour < 12:
            greeting = "Bom dia!"
        elif hour < 18:
            greeting = "Boa tarde!"
        else:
            greeting = "Boa noite!"

        # Adiciona lista de comandos
        commands_list = """

Comandos disponíveis:

• *tarefas* - ver suas tarefas
• *progresso* - ver andamento do dia
• *feito N* - marcar tarefa N como concluída
• *feito 2 5 6* - marcar múltiplas tarefas
• *andamento N* - marcar tarefa N em andamento
• *ajuda* - ver todos os comandos"""

        return greeting + commands_list, None

    def process(
        self,
        from_number: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa comando recebido via WhatsApp com NLP robusto.

        Args:
            from_number: Número do WhatsApp (formato: whatsapp:+XXXXXXXXXXX)
            message: Mensagem recebida

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando mensagem de {from_number}: '{message}'")

        # Identifica pessoa pelo telefone
        person_name = get_colaborador_by_phone(from_number)

        # Se não encontrar, cria usuário automaticamente com número
        if not person_name:
            logger.info(f"Usuário novo detected: {from_number}")
            person_name = from_number  # Usa o número como nome temporário

            # Tenta criar perfil automaticamente
            try:
                self.people_analytics.get_or_create_profile(person_name)
                logger.info(f"✅ Perfil criado automaticamente para {from_number}")
            except Exception as e:
                logger.debug(f"Não foi possível criar perfil em Notion: {e}")
                # Continua mesmo se não conseguir criar em Notion

        logger.info(f"Mensagem de: {person_name}")

        # Usar nome como user_id
        return self._process_with_nlp(person_name, message)

    def _process_with_nlp(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Lógica principal de processamento com NLP

        Args:
            person_name: Nome do colaborador
            message: Mensagem recebida

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        user_id = person_name

        # DEBUG: Log de estados
        is_waiting = self.onboarding.is_waiting_onboarding_answer(person_name)
        is_waiting_help = self.onboarding.is_waiting_help_answer(person_name)
        is_first = self.onboarding.is_first_time_user(person_name)

        logger.info(f"[DEBUG] {person_name} - waiting_onboarding: {is_waiting}, waiting_help: {is_waiting_help}, first_time: {is_first}")

        # 1. Verificar PRIMEIRO se está aguardando resposta de onboarding
        if is_waiting:
            logger.info(f"Processando resposta de onboarding de {person_name}")
            processed, response = self.onboarding.handle_onboarding_response(person_name, message)
            return True, response

        # 2. Verificar se está aguardando resposta de ajuda
        if is_waiting_help:
            logger.info(f"Processando resposta de ajuda de {person_name}")
            processed, response = self.onboarding.handle_help_response(person_name, message)
            return True, response

        # 3. Verificar se é primeira interação (onboarding) - DEPOIS dos checks de estado
        if is_first:
            logger.info(f"Primeira interação de {person_name} - iniciando onboarding")
            return True, self.onboarding.start_onboarding(person_name)

        # 4. Verificar repetição
        if self._check_repeated_message(user_id, message):
            logger.info(f"Mensagem repetida de {person_name}")
            return True, "Já registrei isso há pouco. Quer que eu confirme novamente?"

        # 5. Verificar se há slot-filling pendente
        pending_state = self._get_user_state(user_id)

        if pending_state:
            # Usuário tem contexto pendente (ex: bloqueada sem motivo)
            return self._handle_slot_filling(person_name, message, pending_state)

        # 3. Parse NLP
        result: ParseResult = nlp_parse(message, log_result=True)

        logger.info(
            f"NLP Parse Result",
            extra={
                "user": person_name,
                "text": message,
                "normalized": result.normalized_text,
                "intent": result.intent,
                "confidence": result.confidence,
                "entities": result.entities
            }
        )

        # 4. Verificar confiança
        if not result.is_confident(self.CONFIDENCE_THRESHOLD):
            logger.info(f"Baixa confiança ({result.confidence:.2f}) para: '{message}'")
            return True, self._get_disambiguation_message()

        # 5. Processar intent
        try:
            return self._execute_intent(person_name, result)

        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            import traceback
            traceback.print_exc()

            error_msg = self.humanizer.get_error_message('technical_error')
            return False, error_msg

    def _handle_slot_filling(
        self,
        person_name: str,
        message: str,
        pending_state: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Trata slot-filling (completar informações pendentes)

        Args:
            person_name: Nome do colaborador
            message: Mensagem recebida
            pending_state: Estado pendente

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Slot-filling para {person_name}: {pending_state}")

        # Verificar se é confirmação de ação pendente
        if "pending_confirm" in pending_state:
            confirmation = is_confirmation(message)

            if confirmation is True:
                # Executar ação pendente
                action = pending_state["pending_confirm"].get("action")
                self._clear_user_state(person_name)

                if action == "review_day":
                    return self.handlers.handle_progress(person_name)
                elif action == "show_tasks":
                    return self.handlers.handle_list(person_name)
                else:
                    return True, "Ok! 👍"

            elif confirmation is False:
                self._clear_user_state(person_name)
                return True, "Tranquilo! Se quiser, peça 'tarefas' quando for a hora."

            # Ambíguo - não é confirmação clara, processar como mensagem normal
            # Não limpar estado ainda

        intent = pending_state.get("intent")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SLOT-FILLING BLOQUEADA - DESABILITADO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # if intent == "blocked_task":
        #     # Esperando motivo do bloqueio
        #     task_index = pending_state.get("index")
        #
        #     # Verificar se é cancelamento
        #     confirmation = is_confirmation(message)
        #     if confirmation is False:
        #         self._clear_user_state(person_name)
        #         return True, "Ok, cancelei. Se precisar, é só chamar!"
        #
        #     # Usar a mensagem como motivo
        #     reason = message.strip()
        #
        #     # Limpar estado
        #     self._clear_user_state(person_name)
        #
        #     # Executar comando bloqueada
        #     return self.handlers.handle_blocked(
        #         person_name=person_name,
        #         task_number=task_index,
        #         reason=reason
        #     )

        # Estado desconhecido
        self._clear_user_state(person_name)
        return True, "Desculpe, perdi o contexto. Pode repetir o que você precisa?"

    def _execute_intent(
        self,
        person_name: str,
        result: ParseResult
    ) -> Tuple[bool, str]:
        """
        Executa handler baseado na intent detectada

        Args:
            person_name: Nome do colaborador
            result: Resultado do parse NLP

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        intent = result.intent
        entities = result.entities

        # Saudações
        if intent == "greet":
            greeting, pending_action = self._get_contextual_greeting(person_name)

            # Salvar contexto de confirmação
            if pending_action:
                self._set_user_state(person_name, {
                    "pending_confirm": {"action": pending_action}
                })

            return True, greeting

        # Despedidas
        if intent == "goodbye":
            return True, "Até logo! Qualquer coisa é só chamar. 👋"

        # Agradecimentos
        if intent == "thanks" or intent == "thanks_closing":
            return True, "Por nada! Estou aqui pra ajudar. 😊"

        # Smalltalk
        if intent == "smalltalk_mood":
            return True, "Tudo certo! Posso te ajudar com 'tarefas' ou 'progresso'. O que prefere?"

        # Ajuda - oferece tutorial completo ou básico
        if intent == "help":
            help_type = entities.get("help_type", "help") if isinstance(entities, dict) else "help"

            try:
                if help_type == "help_comandos" or help_type == "comandos":
                    return True, """Comandos disponíveis:

• *tarefas* - ver suas tarefas
• *progresso* - ver andamento do dia
• *feito N* - marcar tarefa N como concluída
• *andamento N* - marcar tarefa N em andamento
• *criar tarefa* - criar nova tarefa
• *ajuda* - ver este guia"""

                elif help_type == "help_exemplos" or help_type == "exemplos":
                    return True, """Exemplos de uso:

• tarefas
• feito 2
• andamento 3
• progresso
• ajuda"""

                else:
                    # Ajuda padrão - oferece tutorial
                    return True, self.onboarding.start_help_flow(person_name)

            except Exception as e:
                logger.error(f"Erro no handler de ajuda: {e}")
                # Fallback seguro
                return True, """Posso ajudar com:

• *tarefas* - ver suas tarefas
• *progresso* - ver andamento
• *feito N* - marcar tarefa
• *ajuda* - ver comandos"""

        # Listar tarefas
        if intent == "list_tasks" or intent == "resend_list":
            return self.handlers.handle_list(person_name)

        # Ver mais (lista completa)
        if intent == "show_more":
            return self.handlers.handle_show_more(person_name)

        # Progresso
        if intent == "progress":
            return self.handlers.handle_progress(person_name)

        # Mostrar detalhes de tarefa
        if intent == "show_task":
            task_index = entities.get('index')
            if task_index:
                return self.handlers.handle_show_task(person_name, task_index)
            else:
                return True, "❌ Informe o número da tarefa.\n\nExemplo: mostre 2"

        # Tarefas concluídas (1 ou múltiplas)
        if intent == "done_task":
            # Verifica se são múltiplas ou única
            task_numbers = entities.get("indices")
            task_number = entities.get("index")

            if task_numbers:
                # Múltiplas tarefas
                responses = []
                for task_num in task_numbers:
                    success, response = self.handlers.handle_done(
                        person_name=person_name,
                        task_number=task_num
                    )
                    if success:
                        responses.append(f"✅ Tarefa {task_num}")
                    else:
                        responses.append(f"❌ Tarefa {task_num}: {response}")

                return True, "\n".join(responses)

            elif task_number:
                # Tarefa única
                return self.handlers.handle_done(
                    person_name=person_name,
                    task_number=task_number
                )

            else:
                return True, "Me diga o número da tarefa. Ex: 'feito 2' ou 'feito 2 5 6'"

        # Tarefas em andamento (1 ou múltiplas)
        if intent == "in_progress_task":
            # Verifica se são múltiplas ou única
            task_numbers = entities.get("indices")
            task_number = entities.get("index")

            if task_numbers:
                # Múltiplas tarefas
                responses = []
                for task_num in task_numbers:
                    success, response = self.handlers.handle_in_progress(
                        person_name=person_name,
                        task_number=task_num
                    )
                    if success:
                        responses.append(f"✅ Tarefa {task_num}")
                    else:
                        responses.append(f"❌ Tarefa {task_num}: {response}")

                return True, "\n".join(responses)

            elif task_number:
                # Tarefa única
                return self.handlers.handle_in_progress(
                    person_name=person_name,
                    task_number=task_number
                )

            else:
                return True, "Qual o número da tarefa? Ex: 'andamento 3' ou 'andamento 2 3'"

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COMANDO BLOQUEADA - DESABILITADO
        # Manter código comentado caso precise reativar no futuro
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # # Tarefa bloqueada (com motivo)
        # if intent == "blocked_task":
        #     task_number = entities.get("index")
        #     reason = entities.get("reason")
        #
        #     if not task_number:
        #         return True, "Qual tarefa está bloqueada? Ex: 'bloqueada 4 - sem acesso'"
        #
        #     if not reason:
        #         # Slot-filling: pedir motivo
        #         self._set_user_state(person_name, {
        #             "intent": "blocked_task",
        #             "index": task_number
        #         })
        #         return True, f"Entendi que a tarefa {task_number} está bloqueada. Qual o motivo?"
        #
        #     return self.handlers.handle_blocked(
        #         person_name=person_name,
        #         task_number=task_number,
        #         reason=reason
        #     )
        #
        # # Tarefa bloqueada (sem motivo) - slot-filling
        # if intent == "blocked_task_no_reason":
        #     task_number = entities.get("index")
        #
        #     if not task_number:
        #         return True, "Qual tarefa está bloqueada? Ex: 'bloqueada 4'"
        #
        #     # Iniciar slot-filling
        #     self._set_user_state(person_name, {
        #         "intent": "blocked_task",
        #         "index": task_number
        #     })
        #     return True, f"Entendi que a tarefa {task_number} está bloqueada. Qual o motivo?"

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # COMANDOS DE TUTORIAIS DIRETOS
        # Respondem imediatamente sem perguntar ao usuário
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # Tutorial completo
        if intent == "tutorial_complete":
            return self.handlers.handle_tutorial_complete(person_name)

        # Tutorial básico/rápido
        if intent == "tutorial_quick":
            return self.handlers.handle_tutorial_quick(person_name)

        # Começar do zero
        if intent == "start_from_scratch":
            return self.handlers.handle_start_from_scratch(person_name)

        # Mostrar exemplos
        if intent == "show_examples":
            return self.handlers.handle_show_examples(person_name)

        # Mostrar dicas
        if intent == "show_tips":
            return self.handlers.handle_show_tips(person_name)

        # Confirmações (contextuais)
        if intent == "confirm_yes":
            # Verificar se há contexto pendente
            pending_state = self._get_user_state(person_name)

            if pending_state and "pending_confirm" in pending_state:
                # Executar ação pendente
                action = pending_state["pending_confirm"].get("action")
                self._clear_user_state(person_name)

                if action == "review_day":
                    return self.handlers.handle_progress(person_name)
                elif action == "show_tasks":
                    return self.handlers.handle_list(person_name)
                else:
                    return True, "Ok! 👍"
            else:
                # Sem contexto - dar CTA útil
                return True, "Beleza! Me diga: 'tarefas' ou 'progresso' 😉"

        if intent == "confirm_no":
            # Limpar qualquer contexto pendente
            self._clear_user_state(person_name)
            return True, "Tranquilo! Se quiser, peça 'tarefas' quando for a hora."

        # Intent desconhecido
        logger.warning(f"Intent não tratado: {intent}")
        return True, self._get_disambiguation_message()

    def process_by_name(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa comando usando nome diretamente (útil para testes).

        Agora usa o mesmo sistema NLP robusto com:
        - Normalização completa
        - Slot-filling
        - Desambiguação inteligente

        Args:
            person_name: Nome do colaborador
            message: Mensagem/comando

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando mensagem de {person_name}: '{message}'")

        # Usar mesma lógica NLP
        return self._process_with_nlp(person_name, message)
