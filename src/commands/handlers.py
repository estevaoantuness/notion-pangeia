"""
Handlers de comandos específicos.

Este módulo contém handlers para cada tipo de comando,
executando as ações necessárias e retornando respostas.
"""

import logging
from typing import Optional, Tuple

from src.notion.updater import TaskUpdater
# from src.cache.task_mapper import get_task_mapper  # TODO: implementar se necessário
from src.whatsapp.sender import WhatsAppSender
from src.messaging.humanizer import get_humanizer

logger = logging.getLogger(__name__)


class CommandHandlers:
    """
    Handlers para comandos específicos.

    Cada método processa um tipo de comando e retorna a resposta.
    """

    def __init__(
        self,
        task_updater: Optional[TaskUpdater] = None,
        whatsapp_sender: Optional[WhatsAppSender] = None
    ):
        """
        Inicializa os handlers focados em gestão de tasks.

        Args:
            task_updater: Atualizador de tasks
            whatsapp_sender: Sender de WhatsApp
        """
        self.task_updater = task_updater or TaskUpdater()
        self.whatsapp_sender = whatsapp_sender or WhatsAppSender()
        self.task_mapper = get_task_mapper()
        self.humanizer = get_humanizer()
        logger.info("CommandHandlers inicializado (modo simples - gestão de tasks)")

    def handle_done(
        self,
        person_name: str,
        task_number: int
    ) -> Tuple[bool, str]:
        """
        Handler para comando "feito".

        Args:
            person_name: Nome do colaborador
            task_number: Número da task

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'feito' de {person_name} para task {task_number}")

        # Busca task no mapper
        task = self.task_mapper.get_task(person_name, task_number)

        if not task:
            # Busca total de tasks para mensagem de erro
            all_tasks = self.task_mapper.get_all_tasks(person_name)
            total = len(all_tasks) if all_tasks else 0

            error_msg = self.humanizer.get_error_message(
                'invalid_index',
                index=task_number,
                total=total
            )
            return False, error_msg

        # PASSO 1: Buscar progresso ANTES de atualizar no Notion
        from src.notion.tasks import TasksManager
        tasks_manager = TasksManager()
        progress_before = tasks_manager.calculate_progress(person_name)

        done_before = progress_before["concluidas"]
        total_tasks = progress_before["total"]
        old_percent = progress_before["percentual"]

        logger.info(f"[ANTES] Progresso: {done_before}/{total_tasks} ({old_percent:.0f}%)")

        # PASSO 2: Atualizar task no Notion
        success, error = self.task_updater.mark_as_done(task["id"])

        if not success:
            logger.error(f"Erro ao marcar task como concluída: {error}")
            error_msg = self.humanizer.get_error_message('technical_error')
            return False, error_msg

        # PASSO 3: Buscar progresso DEPOIS da atualização (dados FRESCOS do Notion!)
        progress_after = tasks_manager.calculate_progress(person_name)
        done_after = progress_after["concluidas"]
        new_percent = progress_after["percentual"]

        is_first = (done_before == 0)
        is_last = (done_after == total_tasks)
        is_high_priority = task.get("prioridade") == "Alta"

        logger.info(f"[DEPOIS] Progresso: {done_after}/{total_tasks} ({new_percent:.0f}%)")
        logger.info(f"[DELTA] {done_before}/{total_tasks} ({old_percent:.0f}%) → {done_after}/{total_tasks} ({new_percent:.0f}%)")

        # Cria mensagem contextual
        message = self.humanizer.get_task_completed_message(
            task_number=task_number,
            task_title=task["nome"],
            is_first=is_first,
            is_last=is_last,
            is_high_priority=is_high_priority,
            old_percent=old_percent,
            new_percent=new_percent
        )

        # Envia confirmação
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Confirmação já foi enviada

    def handle_in_progress(
        self,
        person_name: str,
        task_number: int
    ) -> Tuple[bool, str]:
        """
        Handler para comando "andamento".

        Args:
            person_name: Nome do colaborador
            task_number: Número da task

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'andamento' de {person_name} para task {task_number}")

        # Busca task
        task = self.task_mapper.get_task(person_name, task_number)

        if not task:
            all_tasks = self.task_mapper.get_all_tasks(person_name)
            total = len(all_tasks) if all_tasks else 0

            error_msg = self.humanizer.get_error_message(
                'invalid_index',
                index=task_number,
                total=total
            )
            return False, error_msg

        # Atualiza no Notion
        success, error = self.task_updater.mark_in_progress(task["id"])

        if not success:
            logger.error(f"Erro ao marcar task como em andamento: {error}")
            error_msg = self.humanizer.get_error_message('technical_error')
            return False, error_msg

        # Determina prioridade para mensagem contextual
        priority_map = {"Alta": "high", "Média": "medium", "Baixa": "low"}
        priority = priority_map.get(task.get("prioridade", "Média"), "medium")

        # Cria mensagem contextual
        message = self.humanizer.get_task_in_progress_message(
            task_number=task_number,
            task_title=task["nome"],
            priority=priority
        )

        # Envia confirmação
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMANDO BLOQUEADA - DESABILITADO
    # Manter código comentado caso precise reativar no futuro
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # def handle_blocked(
    #     self,
    #     person_name: str,
    #     task_number: int,
    #     reason: str
    # ) -> Tuple[bool, str]:
    #     """
    #     Handler para comando "bloqueada".
    #
    #     Args:
    #         person_name: Nome do colaborador
    #         task_number: Número da task
    #         reason: Motivo do bloqueio
    #
    #     Returns:
    #         Tuple (sucesso, mensagem_resposta)
    #     """
    #     logger.info(
    #         f"Processando comando 'bloqueada' de {person_name} "
    #         f"para task {task_number}. Motivo: {reason}"
    #     )
    #
    #     # Busca task
    #     task = self.task_mapper.get_task(person_name, task_number)
    #
    #     if not task:
    #         all_tasks = self.task_mapper.get_all_tasks(person_name)
    #         total = len(all_tasks) if all_tasks else 0
    #
    #         error_msg = self.humanizer.get_error_message(
    #             'invalid_index',
    #             index=task_number,
    #             total=total
    #         )
    #         return False, error_msg
    #
    #     # Atualiza no Notion
    #     success, error = self.task_updater.mark_as_blocked(
    #         task_id=task["id"],
    #         reason=reason,
    #         notify_manager=True
    #     )
    #
    #     if not success:
    #         logger.error(f"Erro ao marcar task como bloqueada: {error}")
    #         error_msg = self.humanizer.get_error_message('technical_error')
    #         return False, error_msg
    #
    #     # Verifica se é alta prioridade
    #     is_high_priority = task.get("prioridade") == "Alta"
    #
    #     # Cria mensagem contextual
    #     message = self.humanizer.get_task_blocked_message(
    #         task_number=task_number,
    #         task_title=task["nome"],
    #         reason=reason,
    #         is_high_priority=is_high_priority
    #     )
    #
    #     # Envia confirmação
    #     self.whatsapp_sender.send_message(person_name, message)
    #
    #     return True, ""

    def handle_list(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "minhas tarefas".

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'lista' de {person_name}")

        # Envia tasks diárias (vai criar novo mapeamento)
        success, sid, error = self.whatsapp_sender.send_daily_tasks(person_name)

        if not success:
            logger.error(f"Erro ao enviar lista de tasks: {error}")
            return False, "❌ Erro ao buscar suas tasks. Tente novamente."

        return True, ""  # Mensagem já foi enviada

    def handle_show_more(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "ver mais" - mostra lista completa de tarefas.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'ver mais' de {person_name}")

        from src.notion.tasks import TasksManager
        from src.messaging.templates import format_full_task_list

        # Busca tasks do colaborador
        tasks_manager = TasksManager()
        tasks_grouped = tasks_manager.get_person_tasks(person_name)

        # Verifica se tem tasks
        total_tasks = sum(len(tasks) for tasks in tasks_grouped.values())

        if total_tasks == 0:
            return True, "✨ Você não tem tarefas pendentes no momento!"

        # Calcula progresso
        progress = tasks_manager.calculate_progress(person_name)

        # Formata mensagem completa
        message = format_full_task_list(
            person_name=person_name,
            tasks_grouped=tasks_grouped,
            progress=progress
        )

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        # Atualiza mapeamento (importante para os comandos "feito N" funcionarem)
        self.task_mapper.create_mapping(person_name, tasks_grouped)

        return True, ""  # Mensagem já foi enviada

    def handle_progress(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "progresso" - Relatório visual completo.

        Mostra TODAS as tarefas do dia agrupadas por status:
        - ✅ Concluídas
        - 🔵 Em andamento
        - 🔴 Bloqueadas
        - ⚪ Pendentes

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'progresso' de {person_name}")

        from src.notion.tasks import TasksManager
        from src.messaging.templates import format_progress_report

        tasks_manager = TasksManager()

        # Busca TODAS as tasks (incluindo concluídas)
        tasks_grouped = tasks_manager.get_person_tasks(person_name, include_completed=True)
        progress = tasks_manager.calculate_progress(person_name)

        if progress["total"] == 0:
            return True, "✨ Você não tem tarefas para hoje!"

        # Formata relatório visual
        message = format_progress_report(
            person_name=person_name,
            tasks_grouped=tasks_grouped,
            progress=progress
        )

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_show_task(self, person_name: str, task_number: int) -> Tuple[bool, str]:
        """
        Handler para comando "mostre" - Mostra detalhes de uma tarefa.

        Args:
            person_name: Nome do colaborador
            task_number: Número da task

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'mostre' de {person_name} para task {task_number}")

        from src.notion.client import NotionClient
        from src.messaging.task_details import format_task_details

        # Busca task no mapper
        task = self.task_mapper.get_task(person_name, task_number)

        if not task:
            all_tasks = self.task_mapper.get_all_tasks(person_name)
            total = len(all_tasks) if all_tasks else 0

            error_msg = self.humanizer.get_error_message(
                'invalid_index',
                index=task_number,
                total=total
            )
            return False, error_msg

        # Buscar detalhes completos no Notion
        notion = NotionClient()
        task_details = notion.get_task_details(task["id"])

        if not task_details:
            logger.error(f"Erro ao buscar detalhes da task {task_number}")
            return False, "❌ Erro ao buscar detalhes da tarefa. Tente novamente."

        # Formatar mensagem
        message = format_task_details(task_details, task_number)

        # Enviar mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_help(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "ajuda".

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'ajuda' de {person_name}")

        # Envia mensagem de ajuda
        success, sid, error = self.whatsapp_sender.send_help(person_name)

        if not success:
            logger.error(f"Erro ao enviar ajuda: {error}")
            return False, "❌ Erro ao processar comando. Tente novamente."

        return True, ""  # Mensagem já foi enviada

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMANDOS DE TUTORIAIS DIRETOS
    # Respondem imediatamente sem perguntar ao usuário
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def handle_tutorial_complete(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "tutorial" - Mostra tutorial completo.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'tutorial completo' de {person_name}")

        from src.onboarding.manager import get_onboarding_manager

        onboarding = get_onboarding_manager()
        message = onboarding._get_full_tutorial()

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_tutorial_quick(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "básico" - Mostra tutorial rápido.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'tutorial básico' de {person_name}")

        from src.onboarding.manager import get_onboarding_manager

        onboarding = get_onboarding_manager()
        message = onboarding._get_quick_explanation()

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_start_from_scratch(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "começar" - Mostra tutorial completo + primeira interação.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'começar do zero' de {person_name}")

        from src.onboarding.manager import get_onboarding_manager

        onboarding = get_onboarding_manager()

        # Mostra tutorial completo
        tutorial = onboarding._get_full_tutorial()

        # Adiciona CTA para pedir lista de tarefas
        message = f"{tutorial}\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "✨ *Pronto para começar?*\n\n"
        message += "Digite: *tarefas*"

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_show_examples(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "exemplos" - Mostra exemplos práticos.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'exemplos' de {person_name}")

        message = "💡 *EXEMPLOS PRÁTICOS*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*📋 VER TAREFAS*\n\n"
        message += "Você: tarefas\n"
        message += "Bot: 📋 Suas tarefas de hoje:\n"
        message += "     1️⃣ Reunião com cliente\n"
        message += "     2️⃣ Revisar documento\n"
        message += "     3️⃣ Ligar fornecedor\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*✅ MARCAR COMO CONCLUÍDA*\n\n"
        message += "Você: feito 2\n"
        message += "Bot: ✅ Task 2 concluída!\n"
        message += "     Revisar documento ✓\n\n"
        message += "Você: feito 1 3\n"
        message += "Bot: ✅ 2 tasks concluídas!\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*🔵 MARCAR EM ANDAMENTO*\n\n"
        message += "Você: andamento 1\n"
        message += "Bot: 🔵 Task 1 em andamento!\n"
        message += "     Reunião com cliente\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*📊 VER PROGRESSO*\n\n"
        message += "Você: progresso\n"
        message += "Bot: 📊 Progresso de hoje:\n"
        message += "     ✅ 2/5 concluídas (40%)\n"
        message += "     🔵 1 em andamento\n"
        message += "     ⚪ 2 pendentes\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "Digite: *tarefas* para começar!"

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada

    def handle_show_tips(self, person_name: str) -> Tuple[bool, str]:
        """
        Handler para comando "dicas" - Mostra dicas de uso.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, mensagem_resposta)
        """
        logger.info(f"Processando comando 'dicas' de {person_name}")

        message = "💡 *DICAS E TRUQUES*\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*🎯 PRODUTIVIDADE*\n\n"
        message += "1️⃣ *Marque várias de uma vez*\n"
        message += "   Digite: feito 1 2 3\n"
        message += "   (economiza tempo!)\n\n"
        message += "2️⃣ *Use sinônimos naturais*\n"
        message += "   • feito = pronto = concluí\n"
        message += "   • andamento = fazendo = comecei\n"
        message += "   • tarefas = lista = minhas tarefas\n\n"
        message += "3️⃣ *Sempre atualize antes de marcar*\n"
        message += "   Digite 'tarefas' antes de 'feito N'\n"
        message += "   (os números mudam!)\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*⏰ NOTIFICAÇÕES*\n\n"
        message += "• 08:00 → Lista do dia\n"
        message += "• 13:30, 15:30, 17:00, 21:00 → Check-ins\n"
        message += "  (responda para manter seu progresso atualizado)\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*📱 COMANDOS RÁPIDOS*\n\n"
        message += "• 'tarefas' → ver lista\n"
        message += "• 'progresso' → resumo do dia\n"
        message += "• 'ver mais' → lista completa\n"
        message += "• 'mostre 2' → detalhes da task 2\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*🚀 BÔNUS*\n\n"
        message += "• Tarefas concluídas somem da lista\n"
        message += "• Alta prioridade aparece primeiro\n"
        message += "• Use emojis: 👍 ✅ para confirmar\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "Digite: *tarefas* para começar!"

        # Envia mensagem
        self.whatsapp_sender.send_message(person_name, message)

        return True, ""  # Mensagem já foi enviada
