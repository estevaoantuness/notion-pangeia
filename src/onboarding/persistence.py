"""
Persistência de estado de onboarding usando Notion.

Este módulo gerencia o estado de onboarding dos usuários,
armazenando no Notion para persistir entre reinicializações.

IMPORTANTE: Diferente do cache em memória, isso garante que:
- Bot lembra usuários antigos
- Não repete onboarding após restart
- Rastreia última interação
"""

import logging
from typing import Optional
from datetime import datetime
import pytz

from src.notion.client import NotionClient
from config.settings import settings

logger = logging.getLogger(__name__)


class OnboardingPersistence:
    """
    Gerencia persistência de dados de onboarding no Notion.

    Usa database do Notion (NOTION_USERS_DB_ID) com as seguintes properties:
    - Nome (title): Nome do colaborador
    - Telefone (phone_number): Número do WhatsApp
    - Onboarding Completo (checkbox): Se completou onboarding
    - Data Primeiro Acesso (date): Quando acessou pela primeira vez
    - Data Último Acesso (date): Última interação
    - Tipo Onboarding (select): "completo", "básico", ou "nenhum"
    """

    def __init__(self, notion_client: Optional[NotionClient] = None):
        """
        Inicializa o gerenciador de persistência.

        Args:
            notion_client: Cliente Notion (cria um novo se não fornecido)
        """
        self.notion_client = notion_client or NotionClient()
        self.database_id = getattr(settings, 'NOTION_USERS_DB_ID', None)

        if not self.database_id:
            logger.warning(
                "⚠️ NOTION_USERS_DB_ID não configurado. "
                "Persistência de onboarding desabilitada. "
                "Estado será perdido ao reiniciar."
            )
        else:
            logger.info(f"OnboardingPersistence inicializado com DB: {self.database_id}")

    def is_enabled(self) -> bool:
        """
        Verifica se a persistência está habilitada.

        Returns:
            True se NOTION_USERS_DB_ID está configurado
        """
        return self.database_id is not None

    def get_user_record(self, person_name: str, phone_number: Optional[str] = None) -> Optional[dict]:
        """
        Busca registro do usuário no Notion.

        Args:
            person_name: Nome do colaborador
            phone_number: Número de telefone (opcional)

        Returns:
            Dict com registro do Notion ou None se não encontrado
        """
        if not self.is_enabled():
            return None

        try:
            # Busca por nome (property "Nome" é title)
            filter_condition = {
                "property": "Nome",
                "title": {
                    "equals": person_name
                }
            }

            results = self.notion_client.query_database(
                database_id=self.database_id,
                filter_condition=filter_condition
            )

            if results and len(results) > 0:
                return results[0]

            return None

        except Exception as e:
            logger.error(f"Erro ao buscar usuário {person_name}: {e}")
            return None

    def has_completed_onboarding(self, person_name: str) -> bool:
        """
        Verifica se o usuário já completou onboarding.

        Args:
            person_name: Nome do colaborador

        Returns:
            True se já completou, False caso contrário
        """
        if not self.is_enabled():
            # Fallback: assume que não completou
            return False

        try:
            record = self.get_user_record(person_name)

            if not record:
                # Novo usuário
                return False

            # Verifica checkbox "Onboarding Completo"
            properties = record.get("properties", {})
            onboarding_prop = properties.get("Onboarding Completo", {})

            completed = onboarding_prop.get("checkbox", False)

            logger.info(f"Usuário {person_name}: onboarding_completo={completed}")

            return completed

        except Exception as e:
            logger.error(f"Erro ao verificar onboarding de {person_name}: {e}")
            # Fallback: assume que não completou
            return False

    def mark_onboarding_complete(
        self,
        person_name: str,
        phone_number: Optional[str] = None,
        onboarding_type: str = "básico"
    ) -> bool:
        """
        Marca onboarding como completo no Notion.

        Args:
            person_name: Nome do colaborador
            phone_number: Número de telefone
            onboarding_type: "completo", "básico", ou "nenhum"

        Returns:
            True se sucesso, False se erro
        """
        if not self.is_enabled():
            logger.warning("Persistência desabilitada - estado não será salvo")
            return False

        try:
            now = datetime.now(pytz.timezone(settings.TIMEZONE))
            today_str = now.strftime("%Y-%m-%d")

            # Busca registro existente
            record = self.get_user_record(person_name, phone_number)

            if record:
                # Atualizar registro existente
                page_id = record["id"]

                properties = {
                    "Onboarding Completo": {"checkbox": True},
                    "Data Último Acesso": {"date": {"start": today_str}},
                    "Tipo Onboarding": {"select": {"name": onboarding_type}}
                }

                self.notion_client.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )

                logger.info(f"✅ Onboarding atualizado para {person_name} (tipo: {onboarding_type})")

            else:
                # Criar novo registro
                properties = {
                    "Nome": {"title": [{"text": {"content": person_name}}]},
                    "Onboarding Completo": {"checkbox": True},
                    "Data Primeiro Acesso": {"date": {"start": today_str}},
                    "Data Último Acesso": {"date": {"start": today_str}},
                    "Tipo Onboarding": {"select": {"name": onboarding_type}}
                }

                if phone_number:
                    properties["Telefone"] = {"phone_number": phone_number}

                self.notion_client.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties
                )

                logger.info(f"✅ Novo usuário criado: {person_name} (tipo: {onboarding_type})")

            return True

        except Exception as e:
            logger.error(f"Erro ao marcar onboarding completo para {person_name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_last_interaction(
        self,
        person_name: str,
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Atualiza data da última interação do usuário.

        Args:
            person_name: Nome do colaborador
            phone_number: Número de telefone (opcional)

        Returns:
            True se sucesso, False se erro
        """
        if not self.is_enabled():
            return False

        try:
            now = datetime.now(pytz.timezone(settings.TIMEZONE))
            today_str = now.strftime("%Y-%m-%d")

            record = self.get_user_record(person_name, phone_number)

            if record:
                # Atualizar registro
                page_id = record["id"]

                properties = {
                    "Data Último Acesso": {"date": {"start": today_str}}
                }

                self.notion_client.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )

                logger.debug(f"Data de acesso atualizada para {person_name}")
                return True

            else:
                # Criar registro inicial
                properties = {
                    "Nome": {"title": [{"text": {"content": person_name}}]},
                    "Onboarding Completo": {"checkbox": False},
                    "Data Primeiro Acesso": {"date": {"start": today_str}},
                    "Data Último Acesso": {"date": {"start": today_str}}
                }

                if phone_number:
                    properties["Telefone"] = {"phone_number": phone_number}

                self.notion_client.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties
                )

                logger.info(f"Registro inicial criado para {person_name}")
                return True

        except Exception as e:
            logger.error(f"Erro ao atualizar última interação de {person_name}: {e}")
            return False


# Instância global
_persistence = None


def get_persistence() -> OnboardingPersistence:
    """
    Retorna instância global do OnboardingPersistence.

    Returns:
        OnboardingPersistence singleton
    """
    global _persistence
    if _persistence is None:
        _persistence = OnboardingPersistence()
    return _persistence
