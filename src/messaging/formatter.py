"""
Formatador de mensagens para WhatsApp.

Este módulo coordena a formatação de mensagens usando os templates
e adiciona lógica de formatação customizada.
"""

import logging
from typing import Dict, List, Optional

from src.messaging import templates
from src.notion.tasks import TasksManager
from src.messaging.humanizer import get_humanizer

logger = logging.getLogger(__name__)


class MessageFormatter:
    """
    Formata mensagens para envio via WhatsApp.

    Coordena templates e lógica de formatação.
    """

    def __init__(self, tasks_manager: Optional[TasksManager] = None):
        """
        Inicializa o formatador.

        Args:
            tasks_manager: Gerenciador de tasks (cria um novo se não fornecido)
        """
        self.tasks_manager = tasks_manager or TasksManager()
        self.humanizer = get_humanizer()
        logger.info("MessageFormatter inicializado")

    def format_daily_tasks(
        self,
        person_name: str,
        include_progress: bool = True
    ) -> tuple[str, Dict[str, List[Dict]]]:
        """
        Formata mensagem diária com tasks de um colaborador.

        Args:
            person_name: Nome do colaborador
            include_progress: Se True, inclui estatísticas de progresso

        Returns:
            Tuple (mensagem_formatada, tasks_agrupadas)
        """
        logger.info(f"Formatando mensagem diária para {person_name}")

        try:
            # Busca tasks
            tasks_grouped = self.tasks_manager.get_person_tasks(person_name)

            # Calcula progresso
            progress = {}
            if include_progress:
                progress = self.tasks_manager.calculate_progress(person_name)

            # Verifica se tem tasks
            total_tasks = sum(len(tasks) for tasks in tasks_grouped.values())

            if total_tasks == 0:
                message = templates.format_no_tasks_message(person_name)
            else:
                message = templates.format_daily_tasks_message(
                    person_name=person_name,
                    tasks_grouped=tasks_grouped,
                    progress=progress
                )

            logger.info(f"Mensagem formatada com sucesso: {total_tasks} tasks")

            return message, tasks_grouped

        except Exception as e:
            logger.error(f"Erro ao formatar mensagem para {person_name}: {e}")
            raise

    def format_confirmation(
        self,
        action: str,
        task_name: str,
        person_name: str
    ) -> str:
        """
        Formata mensagem de confirmação de ação.

        Args:
            action: Tipo de ação (done, in_progress, blocked)
            task_name: Nome da task
            person_name: Nome do colaborador

        Returns:
            Mensagem de confirmação formatada
        """
        logger.info(f"Formatando confirmação de {action} para {person_name}")

        try:
            # Mapeia action para tipo de mensagem do catálogo
            action_map = {
                "done": "concluir",
                "in_progress": "andamento",
                "blocked": "bloqueada"
            }

            message_type = action_map.get(action, "concluir")

            # Usa mensagem humanizada
            message = self.humanizer.get_message(
                message_type,
                {
                    "task_title": task_name,
                    "task_number": ""  # Placeholder vazio
                }
            )

            return message

        except Exception as e:
            logger.error(f"Erro ao formatar confirmação: {e}")
            return "✅ Ação realizada com sucesso!"

    def format_help(self) -> str:
        """
        Formata mensagem de ajuda.

        Returns:
            Mensagem de ajuda formatada
        """
        # Usa mensagem humanizada do catálogo YAML
        return self.humanizer.get_help_message(short=False)

    def format_error(self, error_type: str = "generic") -> str:
        """
        Formata mensagem de erro.

        Args:
            error_type: Tipo do erro

        Returns:
            Mensagem de erro formatada
        """
        return templates.format_error_message(error_type)

    def format_checkin_question(
        self,
        checkin_type: str,
        question_number: int,
        question_text: str
    ) -> str:
        """
        Formata pergunta de check-in.

        Args:
            checkin_type: Tipo do check-in
            question_number: Número da pergunta
            question_text: Texto da pergunta

        Returns:
            Pergunta formatada
        """
        return templates.format_checkin_question(
            checkin_type=checkin_type,
            question_number=question_number,
            question_text=question_text
        )
