"""
Task Manager Agent - Gerenciamento Inteligente de Tarefas via Conversa.

Detecta intenções de criar, atualizar e gerenciar tarefas durante a conversa.
"""

import logging
import re
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta, date

from src.notion.tasks import TasksManager
from src.notion.task_creator import TaskCreator
from src.tasks.ai_decomposer import AITaskDecomposer

logger = logging.getLogger(__name__)


class TaskManagerAgent:
    """
    Agente inteligente para gerenciamento de tarefas via conversação.

    Detecta comandos como:
    - "cria uma tarefa pra estudar Python"
    - "terminei a tarefa X"
    - "me mostra minhas tarefas"
    - "quebra essa tarefa em subtasks"
    """

    def __init__(self):
        """Inicializa o agente de gerenciamento de tarefas."""
        self.tasks_manager = TasksManager()
        self.task_creator = TaskCreator()
        self.ai_decomposer = AITaskDecomposer()
        logger.info("TaskManagerAgent inicializado")

    def detect_intent(self, message: str) -> Tuple[str, Dict]:
        """
        Detecta intenção de gerenciar tarefas na mensagem.

        Args:
            message: Mensagem do usuário

        Returns:
            Tuple (intent, params) onde intent pode ser:
            - "create_task"
            - "complete_task"
            - "start_task"
            - "list_tasks"
            - "decompose_task"
            - "none"
        """
        message_lower = message.lower().strip()

        # Intent: Criar tarefa
        create_patterns = [
            r"cria(?:r)?\s+(?:uma\s+)?tarefa",
            r"adiciona(?:r)?\s+(?:uma\s+)?tarefa",
            r"nova\s+tarefa",
            r"preciso\s+fazer",
            r"tenho\s+que\s+fazer"
        ]

        for pattern in create_patterns:
            if re.search(pattern, message_lower):
                # Extrair título da tarefa
                title = self._extract_task_title(message)
                return "create_task", {"title": title}

        # Intent: Completar tarefa
        complete_patterns = [
            r"terminei",
            r"completei",
            r"finalizei",
            r"conclu[íi]",
            r"acabei",
            r"fiz\s+(?:a\s+)?tarefa"
        ]

        for pattern in complete_patterns:
            if re.search(pattern, message_lower):
                title = self._extract_task_title(message)
                return "complete_task", {"title": title}

        # Intent: Começar tarefa
        start_patterns = [
            r"vou\s+(?:come[çc]ar|iniciar)",
            r"comecei",
            r"to\s+fazendo",
            r"estou\s+fazendo"
        ]

        for pattern in start_patterns:
            if re.search(pattern, message_lower):
                title = self._extract_task_title(message)
                return "start_task", {"title": title}

        # Intent: Listar tarefas
        list_patterns = [
            r"(?:minhas|me mostra)\s+tarefas",
            r"quais\s+(?:s[ãa]o\s+)?(?:as\s+)?minhas\s+tarefas",
            r"o\s+que\s+(?:eu\s+)?tenho\s+(?:que\s+)?fazer",
            r"lista(?:r)?\s+(?:as\s+)?tarefas"
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                return "list_tasks", {}

        # Intent: Decompor tarefa em subtasks
        decompose_patterns = [
            r"quebra(?:r)?\s+(?:essa\s+)?tarefa",
            r"divide(?:r)?\s+(?:essa\s+)?tarefa",
            r"subtasks?",
            r"decompor"
        ]

        for pattern in decompose_patterns:
            if re.search(pattern, message_lower):
                title = self._extract_task_title(message)
                return "decompose_task", {"title": title}

        return "none", {}

    def _extract_task_title(self, message: str) -> str:
        """
        Extrai título da tarefa da mensagem.

        Args:
            message: Mensagem completa

        Returns:
            Título extraído ou mensagem inteira
        """
        # Remover palavras comuns de comando
        clean = message.lower()

        remove_words = [
            "cria", "criar", "adiciona", "adicionar", "nova", "tarefa",
            "terminei", "completei", "finalizei", "concluí", "conclui",
            "vou começar", "comecei", "to fazendo", "estou fazendo",
            "quebra", "quebrar", "divide", "dividir",
            "uma", "a", "o", "pra", "para"
        ]

        for word in remove_words:
            clean = re.sub(rf"\b{word}\b", "", clean, flags=re.IGNORECASE)

        # Limpar espaços extras
        clean = " ".join(clean.split()).strip()

        # Se ficou vazio, retornar mensagem original
        if not clean:
            return message

        # Capitalizar primeira letra
        return clean[0].upper() + clean[1:]

    def handle_create_task(
        self,
        person_name: str,
        params: Dict
    ) -> Tuple[bool, str]:
        """
        Lida com criação de tarefa.

        Args:
            person_name: Nome da pessoa
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            title = params.get("title", "Nova tarefa")

            # Criar task
            task = self.task_creator.create_task(
                title=title,
                assignee=person_name,
                category="Work"
            )

            return True, f"✅ Tarefa criada: **{title}**\n\nJá está na sua lista! Bora fazer? 💪"

        except Exception as e:
            logger.error(f"Erro ao criar task: {e}", exc_info=True)
            return False, "Ops, não consegui criar a tarefa. Tenta de novo?"

    def handle_complete_task(
        self,
        person_name: str,
        params: Dict
    ) -> Tuple[bool, str]:
        """
        Lida com conclusão de tarefa.

        Args:
            person_name: Nome da pessoa
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            title = params.get("title", "")

            # Buscar task
            task = self.task_creator.find_task_by_title(title, person_name)

            if not task:
                return False, f"Não encontrei a tarefa '{title}'. Pode me dar mais detalhes?"

            # Completar task
            self.task_creator.complete_task(task["id"])

            return True, f"🎉 Mandou bem! Tarefa **{task['title']}** concluída!\n\nCelebra essa vitória! 🏆"

        except Exception as e:
            logger.error(f"Erro ao completar task: {e}", exc_info=True)
            return False, "Ops, não consegui marcar como concluída. Tenta de novo?"

    def handle_start_task(
        self,
        person_name: str,
        params: Dict
    ) -> Tuple[bool, str]:
        """
        Lida com início de tarefa.

        Args:
            person_name: Nome da pessoa
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            title = params.get("title", "")

            # Buscar task
            task = self.task_creator.find_task_by_title(title, person_name)

            if not task:
                return False, f"Não encontrei a tarefa '{title}'. Qual é mesmo?"

            # Marcar como "Em Andamento"
            self.task_creator.start_task(task["id"])

            return True, f"💪 Partiu! Tarefa **{task['title']}** em andamento!\n\nQualquer coisa, tô aqui! 👊"

        except Exception as e:
            logger.error(f"Erro ao iniciar task: {e}", exc_info=True)
            return False, "Ops, não consegui marcar como em andamento. Tenta de novo?"

    def handle_list_tasks(
        self,
        person_name: str,
        params: Dict
    ) -> Tuple[bool, str]:
        """
        Lida com listagem de tarefas.

        Args:
            person_name: Nome da pessoa
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            tasks = self.tasks_manager.get_person_tasks(person_name, include_completed=False)
            progress = self.tasks_manager.calculate_progress(person_name)

            total_pendentes = len(tasks.get("a_fazer", [])) + len(tasks.get("em_andamento", []))
            em_andamento = len(tasks.get("em_andamento", []))
            a_fazer = len(tasks.get("a_fazer", []))

            if total_pendentes == 0:
                return True, "🎉 Você está livre! Nenhuma tarefa pendente no momento.\n\nQuer criar alguma nova?"

            # Montar lista
            lines = [
                f"📋 **Suas Tarefas** ({person_name})\n",
                f"📊 Progresso: {progress.get('percentual', 0)}%\n"
            ]

            # Em andamento
            if em_andamento > 0:
                lines.append(f"**Em Andamento** ({em_andamento}):")
                for task in tasks.get("em_andamento", [])[:3]:
                    title = task.get("title", "Sem título")
                    lines.append(f"  🔄 {title}")

                if em_andamento > 3:
                    lines.append(f"  ... e mais {em_andamento - 3}")

                lines.append("")

            # A fazer
            if a_fazer > 0:
                lines.append(f"**A Fazer** ({a_fazer}):")
                for task in tasks.get("a_fazer", [])[:3]:
                    title = task.get("title", "Sem título")
                    lines.append(f"  ⬜ {title}")

                if a_fazer > 3:
                    lines.append(f"  ... e mais {a_fazer - 3}")

            message = "\n".join(lines)
            return True, message

        except Exception as e:
            logger.error(f"Erro ao listar tasks: {e}", exc_info=True)
            return False, "Ops, não consegui buscar suas tarefas. Tenta de novo?"

    def handle_decompose_task(
        self,
        person_name: str,
        params: Dict
    ) -> Tuple[bool, str]:
        """
        Lida com decomposição de tarefa em subtasks.

        Args:
            person_name: Nome da pessoa
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            title = params.get("title", "")

            if not title:
                return False, "Qual tarefa você quer que eu quebre em subtasks?"

            # Usar AI Decomposer
            result = self.ai_decomposer.decompose_task(title, person_name)

            if not result.get("success"):
                return False, "Não consegui decompor a tarefa. Pode me dar mais detalhes sobre ela?"

            subtasks = result.get("subtasks", [])

            if len(subtasks) == 0:
                return False, "Não consegui identificar subtasks. A tarefa já parece bem simples!"

            # Criar subtasks no Notion
            created = self.task_creator.create_subtasks(
                parent_title=title,
                subtasks=subtasks,
                assignee=person_name
            )

            # Montar resposta
            lines = [
                f"✂️ **Tarefa Decomposta: {title}**\n",
                f"Criei {len(created)} subtasks pra você:\n"
            ]

            for i, subtask in enumerate(subtasks, 1):
                lines.append(f"{i}. {subtask}")

            lines.append("\nBora atacar uma de cada vez! 💪")

            return True, "\n".join(lines)

        except Exception as e:
            logger.error(f"Erro ao decompor task: {e}", exc_info=True)
            return False, "Ops, não consegui decompor a tarefa. Tenta de novo?"

    def process_message(
        self,
        person_name: str,
        message: str
    ) -> Optional[Tuple[bool, str]]:
        """
        Processa mensagem e executa ação se for comando de task.

        Args:
            person_name: Nome da pessoa
            message: Mensagem recebida

        Returns:
            Tuple (sucesso, resposta) ou None se não for comando de task
        """
        intent, params = self.detect_intent(message)

        if intent == "none":
            return None

        # Delegar para handler apropriado
        if intent == "create_task":
            return self.handle_create_task(person_name, params)

        elif intent == "complete_task":
            return self.handle_complete_task(person_name, params)

        elif intent == "start_task":
            return self.handle_start_task(person_name, params)

        elif intent == "list_tasks":
            return self.handle_list_tasks(person_name, params)

        elif intent == "decompose_task":
            return self.handle_decompose_task(person_name, params)

        return None
