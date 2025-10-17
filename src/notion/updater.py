"""
Atualizador de Tasks no Notion.

Este módulo gerencia atualizações de status e propriedades de tasks,
incluindo marcação como concluída, em andamento e bloqueada.
"""

import logging
from typing import Optional, Tuple
from datetime import datetime

from src.notion.client import NotionClient
from config.settings import settings

logger = logging.getLogger(__name__)


class TaskUpdater:
    """
    Atualiza tasks no Notion.

    Responsável por modificar status, adicionar comentários e
    registrar alterações nas tasks.
    """

    def __init__(self, notion_client: Optional[NotionClient] = None):
        """
        Inicializa o atualizador de tasks.

        Args:
            notion_client: Cliente Notion (cria um novo se não fornecido)
        """
        self.notion_client = notion_client or NotionClient()
        logger.info("TaskUpdater inicializado")

    def mark_as_done(
        self,
        task_id: str,
        completed_via: str = "WhatsApp"
    ) -> Tuple[bool, Optional[str]]:
        """
        Marca task como concluída.

        Args:
            task_id: ID da task no Notion
            completed_via: Origem da conclusão (WhatsApp, Manual, API)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        logger.info(f"Marcando task {task_id} como concluída")

        try:
            # Prepara propriedades para atualizar
            properties = {}

            # Atualiza Status com formato correto (status type, não select)
            properties["Status"] = {
                "status": {"name": "Concluído"}
            }

            # Atualiza a página
            self.notion_client.update_page(
                page_id=task_id,
                properties=properties
            )

            # Adiciona comentário
            try:
                self.notion_client.append_block_children(
                    block_id=task_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"✅ Marcado como concluído via {completed_via}"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                )
            except Exception as e:
                logger.warning(f"Não foi possível adicionar comentário: {e}")

            logger.info(f"✅ Task {task_id} marcada como concluída")
            return True, None

        except Exception as e:
            error_msg = f"Erro ao marcar task como concluída: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def mark_in_progress(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """
        Marca task como em andamento.

        Args:
            task_id: ID da task no Notion

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        logger.info(f"Marcando task {task_id} como em andamento")

        try:
            # Atualiza com status type usando nome correto em português
            self.notion_client.update_page(
                page_id=task_id,
                properties={
                    "Status": {
                        "status": {"name": "Em Andamento"}
                    }
                }
            )

            # Adiciona comentário
            try:
                self.notion_client.append_block_children(
                    block_id=task_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "⏳ Marcado como em andamento via WhatsApp"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                )
            except Exception as e:
                logger.warning(f"Não foi possível adicionar comentário: {e}")

            logger.info(f"✅ Task {task_id} marcada como em andamento")
            return True, None

        except Exception as e:
            error_msg = f"Erro ao marcar task como em andamento: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def mark_as_blocked(
        self,
        task_id: str,
        reason: str,
        notify_manager: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Marca task como bloqueada.

        Args:
            task_id: ID da task no Notion
            reason: Motivo do bloqueio
            notify_manager: Se True, notifica o gestor (futuro)

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        logger.info(f"Marcando task {task_id} como bloqueada. Motivo: {reason}")

        try:
            # Tenta com select
            try:
                self.notion_client.update_page(
                    page_id=task_id,
                    properties={
                        "Status": {
                            "select": {"name": "Bloqueada"}
                        }
                    }
                )
            except:
                # Tenta com status
                self.notion_client.update_page(
                    page_id=task_id,
                    properties={
                        "Status": {
                            "status": {"name": "Blocked"}
                        }
                    }
                )

            # Adiciona comentário com motivo
            try:
                self.notion_client.append_block_children(
                    block_id=task_id,
                    children=[
                        {
                            "object": "block",
                            "type": "callout",
                            "callout": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"🚫 BLOQUEADA\n\nMotivo: {reason}"
                                        }
                                    }
                                ],
                                "icon": {
                                    "emoji": "🚫"
                                },
                                "color": "red_background"
                            }
                        }
                    ]
                )
            except Exception as e:
                logger.warning(f"Não foi possível adicionar comentário: {e}")

            logger.info(f"✅ Task {task_id} marcada como bloqueada")

            # TODO: Implementar notificação ao gestor
            if notify_manager:
                logger.info("Notificação ao gestor será implementada futuramente")

            return True, None

        except Exception as e:
            error_msg = f"Erro ao marcar task como bloqueada: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def add_comment(self, task_id: str, comment: str) -> Tuple[bool, Optional[str]]:
        """
        Adiciona comentário a uma task.

        Args:
            task_id: ID da task no Notion
            comment: Texto do comentário

        Returns:
            Tuple (sucesso, mensagem_erro)
        """
        logger.info(f"Adicionando comentário à task {task_id}")

        try:
            self.notion_client.append_block_children(
                block_id=task_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": comment
                                    }
                                }
                            ]
                        }
                    }
                ]
            )

            logger.info(f"✅ Comentário adicionado à task {task_id}")
            return True, None

        except Exception as e:
            error_msg = f"Erro ao adicionar comentário: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
