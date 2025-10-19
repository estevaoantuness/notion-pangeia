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
        category: str = "Work",
        project: Optional[str] = None
    ) -> Dict:
        """
        Cria uma nova task no Notion.

        Args:
            title: Título da task
            assignee: Nome do responsável
            description: Descrição detalhada (opcional) - vai para Notes
            due_date: Data de vencimento (opcional) - NÃO SUPORTADO pela database atual
            priority: Prioridade (Low, Medium, High, Urgent) - NÃO SUPORTADO pela database atual
            category: Categoria (Work, Personal, Learning, Health) - NÃO SUPORTADO pela database atual
            project: Nome do projeto (opcional)

        Returns:
            Dict com dados da task criada (inclui ID)
        """
        try:
            logger.info(f"Criando task: '{title}' para {assignee}")

            # Preparar propriedades
            # Schema real da database: Task (title), Status, Assignees (multi_select), Project (multi_select), Notes (rich_text), Source (url)
            properties = {
                "Task": {
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
                }
            }

            # Adicionar projeto se fornecido
            if project:
                properties["Project"] = {
                    "multi_select": [
                        {"name": project}
                    ]
                }

            # Adicionar descrição em Notes se fornecida
            if description:
                properties["Notes"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": description
                            }
                        }
                    ]
                }

            # Criar página no Notion
            new_page = self.notion_client.create_page(
                parent_database_id=self.database_id,
                properties=properties
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

            # Nota: Database atual não tem campo "Completed At"
            # Se precisar adicionar, criar a propriedade primeiro na database

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
        return self.update_task_status(page_id, "Concluído")

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

    def update_task(
        self,
        page_id: str,
        updates: Dict
    ) -> Dict:
        """
        Atualiza propriedades genéricas de uma task.

        Args:
            page_id: ID da página no Notion
            updates: Dict com propriedades a atualizar
                Exemplo: {"Priority": {"select": {"name": "High"}}}

        Returns:
            Dict com resultado da atualização
        """
        try:
            logger.info(f"Atualizando task {page_id}")

            updated = self.notion_client.update_page(
                page_id=page_id,
                properties=updates
            )

            logger.info(f"✅ Task atualizada com sucesso")

            return {
                "updated": True,
                "page_id": page_id
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar task: {e}", exc_info=True)
            raise

    def reassign_task(
        self,
        page_id: str,
        new_assignee: str
    ) -> Dict:
        """
        Reatribui task para outro responsável.

        Args:
            page_id: ID da página no Notion
            new_assignee: Nome do novo responsável

        Returns:
            Dict com resultado
        """
        try:
            logger.info(f"Reatribuindo task {page_id} para: {new_assignee}")

            updates = {
                "Assignees": {
                    "multi_select": [
                        {"name": new_assignee}
                    ]
                }
            }

            result = self.update_task(page_id, updates)

            logger.info(f"✅ Task reatribuída para: {new_assignee}")

            return {
                "updated": True,
                "new_assignee": new_assignee
            }

        except Exception as e:
            logger.error(f"Erro ao reatribuir task: {e}", exc_info=True)
            raise

    def update_project(
        self,
        page_id: str,
        project_name: str
    ) -> Dict:
        """
        Atualiza projeto de uma task.

        Args:
            page_id: ID da página no Notion
            project_name: Nome do projeto

        Returns:
            Dict com resultado
        """
        try:
            logger.info(f"Atualizando projeto da task {page_id} para: {project_name}")

            updates = {
                "Project": {
                    "multi_select": [
                        {"name": project_name}
                    ]
                }
            }

            result = self.update_task(page_id, updates)

            logger.info(f"✅ Projeto atualizado para: {project_name}")

            return {
                "updated": True,
                "project": project_name
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar projeto: {e}", exc_info=True)
            raise

    def update_notes(
        self,
        page_id: str,
        notes: str
    ) -> Dict:
        """
        Atualiza notas/descrição de uma task.

        Args:
            page_id: ID da página no Notion
            notes: Notas/descrição

        Returns:
            Dict com resultado
        """
        try:
            logger.info(f"Atualizando notas da task {page_id}")

            updates = {
                "Notes": {
                    "rich_text": [
                        {
                            "text": {
                                "content": notes
                            }
                        }
                    ]
                }
            }

            result = self.update_task(page_id, updates)

            logger.info(f"✅ Notas atualizadas")

            return {
                "updated": True,
                "notes": notes
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar notas: {e}", exc_info=True)
            raise

    def create_subtasks(
        self,
        parent_task_id: str,
        subtasks: List[str],
        assignee: str
    ) -> List[str]:
        """
        Cria múltiplas subtasks de uma vez.

        Args:
            parent_task_id: ID da task principal
            subtasks: Lista de títulos de subtasks
            assignee: Responsável

        Returns:
            Lista de IDs das tasks criadas
        """
        created_ids = []

        # Busca título da task principal
        try:
            parent_page = self.notion_client.client.pages.retrieve(page_id=parent_task_id)
            parent_title_prop = parent_page.get("properties", {}).get("Name", {})
            parent_title_content = parent_title_prop.get("title", [])
            parent_title = parent_title_content[0].get("text", {}).get("content", "") if parent_title_content else "Task Principal"
        except Exception:
            parent_title = "Task Principal"

        for subtask_title in subtasks:
            try:
                # Adicionar prefixo indicando que é subtask
                full_title = f"↳ {subtask_title}"

                task = self.create_task(
                    title=full_title,
                    assignee=assignee,
                    description=f"Subtask de: {parent_title}"
                )

                created_ids.append(task.get("id"))

            except Exception as e:
                logger.error(f"Erro ao criar subtask '{subtask_title}': {e}")
                continue

        logger.info(f"✅ {len(created_ids)} subtasks criadas para '{parent_title}'")
        return created_ids
