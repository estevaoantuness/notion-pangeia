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
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from src.commands.parser import CommandParser
from src.commands.normalizer import (
    parse as nlp_parse,
    ParseResult,
    is_confirmation,
    normalize_indices,
)
from src.commands.handlers import CommandHandlers
from config.colaboradores import get_colaborador_by_phone
from src.messaging.humanizer import get_humanizer
from src.onboarding.manager import get_onboarding_manager

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

        # Estado de slot-filling por usuário
        self.user_states: Dict[str, Dict[str, Any]] = {}

        # Cache de mensagens recentes (para detectar repetições)
        self.recent_messages: Dict[str, Tuple[str, datetime]] = {}

        logger.info("CommandProcessor inicializado com NLP robusto (modo simples - gestão de tasks)")

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
        """Retorna mensagem de desambiguação conversacional"""
        return """Hmm, não entendi bem... 😊

Posso te ajudar com suas tarefas ou o progresso do dia. O que você prefere?"""

    def _get_contextual_greeting(self, person_name: str) -> Tuple[str, Optional[str]]:
        """
        Retorna saudação contextual com sugestão implícita

        Returns:
            Tuple (mensagem, ação_pendente)
        """
        # Usar get_greeting() que já tem a lógica correta de hora e dia da semana
        greeting = self.humanizer.get_greeting(name=person_name)

        # Adiciona sugestão implícita (conversacional, sem lista de comandos)
        suggestion = "\n\nQuer ver suas tarefas ou como está o progresso do dia?"

        # Retornar com ação pendente para routing de resposta
        return greeting + suggestion, "ask_task_or_progress"

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

            # Perfil será criado quando necessário pelo CommandHandlers

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

        # 3. DESABILITADO: Onboarding automático (apenas via comando "ajuda")
        # Durante MVP, não forçar onboarding em usuários conhecidos
        if is_first and False:  # Temporariamente desabilitado
            logger.info(f"Primeira interação de {person_name} - onboarding desabilitado no MVP")
            # return True, self.onboarding.start_onboarding(person_name)

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
            logger.info(f"Baixa confiança ({result.confidence:.2f}) para: '{message}' - delegando para SmartTaskAgent")
            return False, None  # Delegar para SmartTaskAgent (GPT-4o-mini)

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

        # Slot-filling para comandos de tarefas (feito / andamento)
        if intent in {"done_task", "in_progress_task"}:
            if is_confirmation(message) is False:
                self._clear_user_state(person_name)
                return True, "Sem problemas! Quando quiser é só me dizer o número da tarefa. 😊"

            indices = normalize_indices(message)
            if not indices:
                error_key = "missing_index_done" if intent == "done_task" else "missing_index_in_progress"
                return True, self.humanizer.get_error_message(error_key)

            self._clear_user_state(person_name)
            return self._process_task_indices(person_name, intent, indices)

        if intent == "show_task":
            if is_confirmation(message) is False:
                self._clear_user_state(person_name)
                return True, "Tudo bem! Quando quiser ver detalhes é só me dizer o número. 👌"

            indices = normalize_indices(message)
            if not indices:
                return True, self.humanizer.get_error_message("missing_index_show_task")

            self._clear_user_state(person_name)
            return self.handlers.handle_show_task(person_name, indices[0])

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CRIAR TAREFA - FLUXO DE 3 PERGUNTAS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if intent == "create_task":
            step = pending_state.get("step", 1)

            # STEP 1: Receber título
            if step == 1:
                title = message.strip()

                # Validar se não é cancelamento
                if is_confirmation(title) is False:
                    self._clear_user_state(person_name)
                    return True, "Ok, cancelei a criação. Avise quando quiser criar! 🚀"

                # Salvar título e ir para step 2
                self._set_user_state(person_name, {
                    "intent": "create_task",
                    "step": 2,  # Step 2: esperando projeto
                    "title": title,
                    "project": None,
                    "description": None
                })

                return self.handlers.handle_create_task_get_project(person_name, title)

            # STEP 2: Receber projeto
            elif step == 2:
                project = message.strip()
                title = pending_state.get("title")

                # Validar se não é cancelamento
                if is_confirmation(project) is False:
                    self._clear_user_state(person_name)
                    return True, "Ok, cancelei a criação. Avise quando quiser criar! 🚀"

                # Salvar projeto e ir para step 3
                self._set_user_state(person_name, {
                    "intent": "create_task",
                    "step": 3,  # Step 3: esperando descrição
                    "title": title,
                    "project": project,
                    "description": None
                })

                return self.handlers.handle_create_task_get_description(person_name, title, project)

            # STEP 3: Receber descrição e finalizar
            elif step == 3:
                description = message.strip()
                title = pending_state.get("title")
                project = pending_state.get("project")

                # Validar se não é cancelamento
                if is_confirmation(description) is False:
                    self._clear_user_state(person_name)
                    return True, "Ok, cancelei a criação. Avise quando quiser criar! 🚀"

                # Limpar estado antes de finalizar (importante!)
                self._clear_user_state(person_name)

                # Finalizar criação
                return self.handlers.handle_create_task_finalize(
                    person_name=person_name,
                    title=title,
                    project=project,
                    description=description
                )

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

        # Saudações - responder com cumprimento contextual
        if intent == "greet":
            logger.info(f"Intent 'greet' detectado - respondendo com saudação")
            greeting, pending_action = self._get_contextual_greeting(person_name)
            # Setar estado pendente para que próxima resposta (sim/não/quero/não quero) seja roteada corretamente
            if pending_action:
                self._set_user_state(person_name, {
                    "pending_confirm": {
                        "action": pending_action,
                        "question": "ask_task_or_progress"
                    }
                })
            return True, greeting

        # Despedidas, Agradecimentos, Smalltalk - respostas com humanizer
        if intent == "goodbye":
            logger.info(f"Intent 'goodbye' detectado")
            farewell = self.humanizer.pick("acknowledgments", "positive")
            return True, f"{farewell} Até logo! 👋"

        if intent == "thanks":
            logger.info(f"Intent 'thanks' detectado")
            gratitude_response = self.humanizer.pick("gratitude_responses", "casual")
            return True, gratitude_response

        if intent in ["thanks_closing", "smalltalk_mood"]:
            logger.info(f"Intent '{intent}' detectado - resposta casual")
            filler = self.humanizer.pick("fillers", "casual")
            return True, f"{filler} Tudo bem por aqui! 😊"

        # Ajuda - oferece orientação natural
        if intent == "help":
            help_type = entities.get("help_type", "help") if isinstance(entities, dict) else "help"

            try:
                if help_type == "help_comandos" or help_type == "comandos":
                    return True, """Posso te ajudar de várias formas:

📋 *Suas tarefas* - peça para ver suas tarefas do dia
📊 *Progresso* - veja como está o progresso
✅ *Marcar concluído* - pode dizer "terminei a tarefa 2" ou "pronto 3"
🔄 *Começar* - pode dizer "comecei a 2" ou "estou trabalhando na 3"
➕ *Criar tarefa* - me conte sobre uma nova tarefa que você quer adicionar

Qualquer dúvida, é só chamar! 😊"""

                elif help_type == "help_exemplos" or help_type == "exemplos":
                    return True, """Aqui estão exemplos de como conversar comigo:

"Ver minhas tarefas"
"Como está o progresso?"
"Terminei a tarefa 2"
"Comecei a 3"
"Preciso de ajuda"

Você pode falar de forma natural, como com um colega!"""

                else:
                    # Ajuda padrão - oferece tutorial
                    return True, self.onboarding.start_help_flow(person_name)

            except Exception as e:
                logger.error(f"Erro no handler de ajuda: {e}")
                # Fallback seguro
                return True, """Posso te ajudar com suas tarefas ou progresso do dia.

Pode me dizer o que você gostaria de fazer! 😊"""

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
                self._set_user_state(person_name, {
                    "intent": "show_task",
                    "expected": "index"
                })
                return True, self.humanizer.get_error_message("missing_index_show_task")

        # Tarefas concluídas (1 ou múltiplas)
        if intent == "done_task":
            # Verifica se são múltiplas ou única
            task_numbers = entities.get("indices")
            task_number = entities.get("index")

            if task_numbers:
                return self._process_task_indices(person_name, "done_task", task_numbers)
            elif task_number:
                return self._process_task_indices(person_name, "done_task", [task_number])

            self._set_user_state(person_name, {
                "intent": "done_task",
                "expected": "indices"
            })
            return True, self.humanizer.get_error_message("missing_index_done")

        # Tarefas em andamento (1 ou múltiplas)
        if intent == "in_progress_task":
            # Verifica se são múltiplas ou única
            task_numbers = entities.get("indices")
            task_number = entities.get("index")

            if task_numbers:
                return self._process_task_indices(person_name, "in_progress_task", task_numbers)
            elif task_number:
                return self._process_task_indices(person_name, "in_progress_task", [task_number])

            self._set_user_state(person_name, {
                "intent": "in_progress_task",
                "expected": "indices"
            })
            return True, self.humanizer.get_error_message("missing_index_in_progress")

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

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CRIAR TAREFA - FLUXO DE 3 PERGUNTAS (SLOT-FILLING)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if intent == "create_task":
            # Iniciar fluxo de criação de tarefa
            success, response = self.handlers.handle_create_task_start(person_name)

            # Configurar estado de slot-filling para próxima resposta
            self._set_user_state(person_name, {
                "intent": "create_task",
                "step": 1,  # Step 1: esperando título
                "title": None,
                "project": None,
                "description": None
            })

            return success, response

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
                    confirmation = self.humanizer.pick("confirmations", "positive")
                    return True, confirmation
            else:
                # Sem contexto - dar CTA útil
                confirmation = self.humanizer.pick("confirmations", "positive")
                return True, f"{confirmation} Me diga: 'tarefas' ou 'progresso' 😉"

        if intent == "confirm_no":
            # Limpar qualquer contexto pendente
            self._clear_user_state(person_name)
            acknowledgment = self.humanizer.pick("acknowledgments", "professional")
            return True, f"{acknowledgment} Se quiser, peça 'tarefas' quando for a hora."

        # Expressões de desejo/vontade (resposta a perguntas do bot)
        if intent == "want_clarification":
            logger.info(f"Intent 'want_clarification' detectado - roteando para ação pendente")
            pending_state = self._get_user_state(person_name)

            if pending_state and "pending_confirm" in pending_state:
                # Usuário respondeu a pergunta do bot com expressão de desejo
                question = pending_state.get("pending_confirm", {}).get("question")
                self._clear_user_state(person_name)

                # Se a pergunta era sobre tarefas ou progresso, oferece escolha
                if question == "ask_task_or_progress":
                    # Extrair o que o usuário quer
                    normalized = result.normalized_text if hasattr(result, 'normalized_text') else ""

                    # Se mencionou "tarefa" ou "ver" → mostrar tarefas
                    if any(word in normalized for word in ["tarefa", "tasks", "lista", "ver"]):
                        return self.handlers.handle_list(person_name)
                    # Se mencionou "progresso" ou "como" → mostrar progresso
                    elif any(word in normalized for word in ["progresso", "progress", "status", "como", "quanto"]):
                        return self.handlers.handle_progress(person_name)
                    # Caso contrário, pedir para clarificar
                    else:
                        confirmation = self.humanizer.pick("confirmations", "positive")
                        return True, f"{confirmation} Você quer ver:\n• Tarefas\n• Progresso\n\nMe diga qual dos dois! 😊"
                else:
                    # Outro tipo de pergunta pendente
                    confirmation = self.humanizer.pick("confirmations", "positive")
                    return True, confirmation
            else:
                # Expressão de desejo sem contexto de pergunta
                # Pode ser "quero tarefas" ou "quero progresso"
                normalized = result.normalized_text if hasattr(result, 'normalized_text') else ""

                if any(word in normalized for word in ["tarefa", "tasks", "lista", "ver"]):
                    return self.handlers.handle_list(person_name)
                elif any(word in normalized for word in ["progresso", "progress", "status"]):
                    return self.handlers.handle_progress(person_name)
                else:
                    confirmation = self.humanizer.pick("confirmations", "positive")
                    return True, f"{confirmation} Você quer ver tarefas ou progresso?"

        # Intent desconhecido
        logger.warning(f"Intent não tratado: {intent}")
        return True, self._get_disambiguation_message()

    def _process_task_indices(
        self,
        person_name: str,
        intent: str,
        indices: List[int]
    ) -> Tuple[bool, str]:
        """Executa handlers de tarefas para uma lista de índices normalizados."""
        if not indices:
            return True, ""

        handler = (
            self.handlers.handle_done
            if intent == "done_task"
            else self.handlers.handle_in_progress
        )

        if len(indices) == 1:
            return handler(person_name=person_name, task_number=indices[0])

        responses = []
        for task_num in indices:
            success, response = handler(
                person_name=person_name,
                task_number=task_num
            )
            if success:
                responses.append(f"✅ Tarefa {task_num}")
            else:
                responses.append(f"❌ Tarefa {task_num}: {response}")

        return True, "\n".join(responses)

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
