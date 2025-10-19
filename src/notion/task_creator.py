"""
Task Creator - Criação e Atualização de Tasks no Notion.

Permite criar, atualizar e completar tasks via conversação.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, date
import pytz

from src.notion.client import NotionClient
from config.settings import settings

logger = logging.getLogger(__name__)


class TaskCreator:
    """
    Cria e atualiza tasks no Notion.

    Integra com conversational agent para gerenciamento ativo de tarefas.
    """

    def __init__(self, notion_client: Optional[NotionClient] = None):
        """
        Inicializa o criador de tasks.

        Args:
            notion_client: Cliente Notion (cria um novo se não fornecido)
        """
        self.notion_client = notion_client or NotionClient()
        self.database_id = settings.NOTION_TASKS_DB_ID
        logger.info("TaskCreator inicializado")

    def create_task(
        self,
        title: str,
        assignee: str,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        priority: str = "Medium",
        category: str = "Work"
    ) -> Dict:
        """
        Cria uma nova task no Notion.

        Args:
            title: Título da task
            assignee: Nome do responsável
            description: Descrição detalhada (opcional)
            due_date: Data de vencimento (opcional)
            priority: Prioridade (Low, Medium, High, Urgent)
            category: Categoria (Work, Personal, Learning, Health)

        Returns:
            Dict com dados da task criada
        """
        try:
            logger.info(f"Criando task: '{title}' para {assignee}")

            # Preparar propriedades
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": "A Fazer"
                    }
                },
                "Assignees": {
                    "multi_select": [
                        {"name": assignee}
                    ]
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                },
                "Category": {
                    "select": {
                        "name": category
                    }
                }
            }

            # Adicionar data de vencimento se fornecida
            if due_date:
                properties["Due Date"] = {
                    "date": {
                        "start": due_date.isoformat()
                    }
                }

            # Adicionar descrição se fornecida
            children = []
            if description:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    }
                })

            # Criar página no Notion
            new_page = self.notion_client.create_page(
                database_id=self.database_id,
                properties=properties,
                children=children if children else None
            )

            logger.info(f"✅ Task criada com sucesso: {title}")

            return {
                "id": new_page.get("id"),
                "title": title,
                "assignee": assignee,
                "status": "A Fazer",
                "created": True
            }

        except Exception as e:
            logger.error(f"Erro ao criar task: {e}", exc_info=True)
            raise

    def update_task_status(
        self,
        page_id: str,
        new_status: str
    ) -> Dict:
        """
        Atualiza status de uma task.

        Args:
            page_id: ID da página no Notion
            new_status: Novo status (A Fazer, Em Andamento, Concluída, etc.)

        Returns:
            Dict com resultado da atualização
        """
        try:
            logger.info(f"Atualizando status da task {page_id} para: {new_status}")

            properties = {
                "Status": {
                    "status": {
                        "name": new_status
                    }
                }
            }

            # Se marcando como concluída, adicionar data de conclusão
            if new_status == "Concluída":
                tz = pytz.timezone(settings.TIMEZONE)
                now = datetime.now(tz)
                properties["Completed At"] = {
                    "date": {
                        "start": now.isoformat()
                    }
                }

            updated = self.notion_client.update_page(
                page_id=page_id,
                properties=properties
            )

            logger.info(f"✅ Status atualizado para: {new_status}")

            return {
                "updated": True,
                "new_status": new_status
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}", exc_info=True)
            raise

    def complete_task(self, page_id: str) -> Dict:
        """
        Marca task como concluída.

        Args:
            page_id: ID da página no Notion

        Returns:
            Dict com resultado
        """
        return self.update_task_status(page_id, "Concluída")

    def start_task(self, page_id: str) -> Dict:
        """
        Marca task como "Em Andamento".

        Args:
            page_id: ID da página no Notion

        Returns:
            Dict com resultado
        """
        return self.update_task_status(page_id, "Em Andamento")

    def find_task_by_title(
        self,
        title: str,
        assignee: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Busca task por título (fuzzy match).

        Args:
            title: Título ou parte do título
            assignee: Filtrar por responsável (opcional)

        Returns:
            Dict com dados da task ou None
        """
        try:
            # Buscar todas as tasks (simplificado)
            results = self.notion_client.query_database(
                database_id=self.database_id
            )

            title_lower = title.lower()

            # Buscar por título (fuzzy)
            for page in results:
                page_title_prop = page.get("properties", {}).get("Name", {})
                page_title_content = page_title_prop.get("title", [])

                if page_title_content:
                    page_title = page_title_content[0].get("text", {}).get("content", "")

                    # Match fuzzy
                    if title_lower in page_title.lower() or page_title.lower() in title_lower:
                        # Se forneceu assignee, verificar
                        if assignee:
                            assignees_prop = page.get("properties", {}).get("Assignees", {})
                            assignees = assignees_prop.get("multi_select", [])

                            # Verificar se assignee está na lista
                            assignee_match = any(
                                assignee.lower() in a.get("name", "").lower()
                                for a in assignees
                            )

                            if not assignee_match:
                                continue

                        # Retornar task encontrada
                        status_prop = page.get("properties", {}).get("Status", {})
                        status = status_prop.get("status", {}).get("name", "A Fazer")

                        return {
                            "id": page.get("id"),
                            "title": page_title,
                            "status": status,
                            "found": True
                        }

            return None

        except Exception as e:
            logger.error(f"Erro ao buscar task: {e}", exc_info=True)
            return None

    def create_subtasks(
        self,
        parent_title: str,
        subtasks: List[str],
        assignee: str
    ) -> List[Dict]:
        """
        Cria múltiplas subtasks de uma vez.

        Args:
            parent_title: Título da task principal
            subtasks: Lista de títulos de subtasks
            assignee: Responsável

        Returns:
            Lista de tasks criadas
        """
        created_tasks = []

        for subtask_title in subtasks:
            try:
                # Adicionar prefixo indicando que é subtask
                full_title = f"↳ {subtask_title}"

                task = self.create_task(
                    title=full_title,
                    assignee=assignee,
                    description=f"Subtask de: {parent_title}"
                )

                created_tasks.append(task)

            except Exception as e:
                logger.error(f"Erro ao criar subtask '{subtask_title}': {e}")
                continue

        logger.info(f"✅ {len(created_tasks)} subtasks criadas para '{parent_title}'")
        return created_tasks
