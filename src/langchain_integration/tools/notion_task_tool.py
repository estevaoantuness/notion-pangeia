"""
Notion Task Tool - LangChain Tool para gerenciar tasks no Notion.

Este tool encapsula todas as operações de tasks:
- Listar tasks de uma pessoa
- Criar novas tasks
- Atualizar status
- Completar tasks
- Reatribuir tasks
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import date

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from src.notion.tasks import TasksManager
from src.notion.task_creator import TaskCreator

logger = logging.getLogger(__name__)


class NotionTaskInput(BaseModel):
    """Input schema para NotionTaskTool."""

    action: str = Field(
        description=(
            "Ação a executar: 'list', 'create', 'update_status', 'complete', 'reassign'. "
            "Use 'list' para listar tasks de alguém, 'create' para criar nova task, etc."
        )
    )
    person_name: str = Field(
        description="Nome da pessoa (ex: 'Saraiva', 'Julio'). Sempre necessário."
    )
    title: Optional[str] = Field(
        default=None,
        description="Título da task. Necessário para 'create'."
    )
    description: Optional[str] = Field(
        default=None,
        description="Descrição detalhada da task. Opcional para 'create'."
    )
    project: Optional[str] = Field(
        default=None,
        description="Projeto da task. Opcional para 'create'."
    )
    task_id: Optional[str] = Field(
        default=None,
        description="ID da task no Notion. Necessário para 'update_status', 'complete', 'reassign'."
    )
    new_status: Optional[str] = Field(
        default=None,
        description="Novo status: 'A Fazer', 'Em Andamento', 'Concluído'. Para 'update_status'."
    )
    new_assignee: Optional[str] = Field(
        default=None,
        description="Novo responsável. Para 'reassign'."
    )


class NotionTaskTool(BaseTool):
    """
    Tool para gerenciar tasks no Notion.

    Capabilities:
    - List tasks by person
    - Create new tasks
    - Update task status
    - Complete tasks
    - Reassign tasks

    Examples:
        list: {"action": "list", "person_name": "Saraiva"}
        create: {"action": "create", "person_name": "Saraiva", "title": "Nova task"}
        complete: {"action": "complete", "person_name": "Saraiva", "task_id": "xxx"}
    """

    name = "notion_tasks"
    description = (
        "Gerencia tasks no Notion. Use para listar, criar, atualizar ou completar tasks. "
        "SEMPRE especifique o person_name. "
        "Actions: 'list' (listar), 'create' (criar), 'update_status' (mudar status), "
        "'complete' (concluir), 'reassign' (reatribuir)."
    )
    args_schema = NotionTaskInput

    tasks_manager: TasksManager = None
    task_creator: TaskCreator = None

    def __init__(self):
        """Inicializa tool com managers."""
        super().__init__()
        self.tasks_manager = TasksManager()
        self.task_creator = TaskCreator()

    def _run(
        self,
        action: str,
        person_name: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        project: Optional[str] = None,
        task_id: Optional[str] = None,
        new_status: Optional[str] = None,
        new_assignee: Optional[str] = None,
    ) -> str:
        """
        Executa ação no Notion.

        Args:
            action: Tipo de ação
            person_name: Nome da pessoa
            ... outros params opcionais

        Returns:
            JSON string com resultado
        """
        try:
            logger.info(f"NotionTaskTool: {action} para {person_name}")

            if action == "list":
                return self._list_tasks(person_name)

            elif action == "create":
                return self._create_task(person_name, title, description, project)

            elif action == "update_status":
                return self._update_status(task_id, new_status)

            elif action == "complete":
                return self._complete_task(task_id)

            elif action == "reassign":
                return self._reassign_task(task_id, new_assignee)

            else:
                return json.dumps({
                    "error": f"Ação inválida: {action}",
                    "valid_actions": ["list", "create", "update_status", "complete", "reassign"]
                })

        except Exception as e:
            logger.error(f"Erro em NotionTaskTool: {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "action": action
            })

    def _list_tasks(self, person_name: str) -> str:
        """Lista tasks de uma pessoa."""
        tasks = self.tasks_manager.get_person_tasks(person_name)

        # Formata para resposta limpa
        formatted = {
            "person": person_name,
            "total": len(tasks.get("todas", [])),
            "em_andamento": [],
            "a_fazer": [],
            "concluidas": []
        }

        for task in tasks.get("em_andamento", []):
            formatted["em_andamento"].append({
                "nome": task.get("nome", "Sem título"),
                "id": task.get("id")
            })

        for task in tasks.get("a_fazer", []):
            formatted["a_fazer"].append({
                "nome": task.get("nome", "Sem título"),
                "id": task.get("id")
            })

        for task in tasks.get("concluidas", []):
            formatted["concluidas"].append({
                "nome": task.get("nome", "Sem título"),
                "id": task.get("id")
            })

        return json.dumps(formatted, ensure_ascii=False)

    def _create_task(
        self,
        person_name: str,
        title: str,
        description: Optional[str] = None,
        project: Optional[str] = None
    ) -> str:
        """Cria nova task."""
        if not title:
            return json.dumps({"error": "Título é obrigatório para criar task"})

        result = self.task_creator.create_task(
            title=title,
            assignee=person_name,
            description=description,
            project=project
        )

        return json.dumps({
            "created": True,
            "task_id": result.get("id"),
            "title": title,
            "assignee": person_name
        }, ensure_ascii=False)

    def _update_status(self, task_id: str, new_status: str) -> str:
        """Atualiza status de uma task."""
        if not task_id or not new_status:
            return json.dumps({"error": "task_id e new_status são obrigatórios"})

        result = self.task_creator.update_task_status(task_id, new_status)

        return json.dumps({
            "updated": True,
            "task_id": task_id,
            "new_status": new_status
        }, ensure_ascii=False)

    def _complete_task(self, task_id: str) -> str:
        """Completa uma task."""
        if not task_id:
            return json.dumps({"error": "task_id é obrigatório"})

        result = self.task_creator.complete_task(task_id)

        return json.dumps({
            "completed": True,
            "task_id": task_id
        }, ensure_ascii=False)

    def _reassign_task(self, task_id: str, new_assignee: str) -> str:
        """Reatribui uma task."""
        if not task_id or not new_assignee:
            return json.dumps({"error": "task_id e new_assignee são obrigatórios"})

        result = self.task_creator.reassign_task(task_id, new_assignee)

        return json.dumps({
            "reassigned": True,
            "task_id": task_id,
            "new_assignee": new_assignee
        }, ensure_ascii=False)

    async def _arun(self, *args, **kwargs):
        """Async version (não implementado - usa sync)."""
        raise NotImplementedError("NotionTaskTool não suporta async ainda")
