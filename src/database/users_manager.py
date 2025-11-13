"""
Gerenciador de Usuários usando Supabase (Postgres).

Este módulo substitui OnboardingPersistence (Notion) por uma solução
usando Postgres/Supabase, que é mais rápida e centraliza tudo em um banco.
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime
import pytz
from sqlalchemy import text

from src.database.connection import get_db_engine

logger = logging.getLogger(__name__)


class UsersManager:
    """
    Gerencia usuários usando Postgres/Supabase.

    Mantém a mesma interface que OnboardingPersistence para compatibilidade.
    """

    def __init__(self):
        """Inicializa o gerenciador de usuários."""
        self.engine = get_db_engine()
        self.timezone = pytz.timezone("America/Sao_Paulo")
        logger.info("UsersManager inicializado (Postgres/Supabase)")

    def get_user(self, name: str) -> Optional[Dict]:
        """
        Busca usuário por nome.

        Args:
            name: Nome do usuário

        Returns:
            Dict com dados do usuário ou None se não encontrado
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id, name, phone, onboarding_complete, onboarding_type, first_access_at, last_access_at FROM users WHERE name = :name"),
                    {"name": name}
                )
                row = result.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "phone": row[2],
                        "onboarding_complete": row[3],
                        "onboarding_type": row[4],
                        "first_access_at": row[5],
                        "last_access_at": row[6],
                    }

                return None

        except Exception as e:
            logger.error(f"Erro ao buscar usuário {name}: {e}")
            return None

    def has_completed_onboarding(self, person_name: str) -> bool:
        """
        Verifica se o usuário completou onboarding.

        Args:
            person_name: Nome do usuário

        Returns:
            True se completou, False caso contrário
        """
        user = self.get_user(person_name)

        if not user:
            # Novo usuário - ainda não completou
            return False

        return user.get("onboarding_complete", False)

    def mark_onboarding_complete(
        self,
        person_name: str,
        phone_number: Optional[str] = None,
        onboarding_type: str = "básico"
    ) -> bool:
        """
        Marca onboarding como completo.

        Args:
            person_name: Nome do usuário
            phone_number: Número de telefone (opcional)
            onboarding_type: Tipo de onboarding ('completo', 'básico', 'nenhum')

        Returns:
            True se sucesso, False se erro
        """
        try:
            now = datetime.now(self.timezone)

            user = self.get_user(person_name)

            with self.engine.connect() as conn:
                if user:
                    # Atualizar usuário existente
                    conn.execute(
                        text("""UPDATE users
                        SET onboarding_complete = true,
                            onboarding_type = :onboarding_type,
                            last_access_at = :now
                        WHERE name = :person_name"""),
                        {"onboarding_type": onboarding_type, "now": now, "person_name": person_name}
                    )
                    logger.info(
                        f"✅ Onboarding atualizado para {person_name} (tipo: {onboarding_type})"
                    )
                else:
                    # Criar novo usuário
                    conn.execute(
                        text("""INSERT INTO users
                        (name, phone, onboarding_complete, onboarding_type,
                         first_access_at, last_access_at)
                        VALUES (:person_name, :phone_number, true, :onboarding_type, :now, :now)"""),
                        {"person_name": person_name, "phone_number": phone_number, "onboarding_type": onboarding_type, "now": now}
                    )
                    logger.info(
                        f"✅ Novo usuário criado: {person_name} (tipo: {onboarding_type})"
                    )

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Erro ao marcar onboarding completo para {person_name}: {e}")
            return False

    def update_last_interaction(
        self,
        person_name: str,
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Atualiza a data da última interação do usuário.

        Args:
            person_name: Nome do usuário
            phone_number: Número de telefone (opcional)

        Returns:
            True se sucesso, False se erro
        """
        try:
            now = datetime.now(self.timezone)

            user = self.get_user(person_name)

            with self.engine.connect() as conn:
                if user:
                    # Atualizar usuário existente
                    conn.execute(
                        text("UPDATE users SET last_access_at = :now WHERE name = :person_name"),
                        {"now": now, "person_name": person_name}
                    )
                    logger.debug(f"Data de acesso atualizada para {person_name}")
                else:
                    # Criar novo usuário
                    conn.execute(
                        text("""INSERT INTO users
                        (name, phone, first_access_at, last_access_at)
                        VALUES (:person_name, :phone_number, :now, :now)"""),
                        {"person_name": person_name, "phone_number": phone_number, "now": now}
                    )
                    logger.info(f"Registro inicial criado para {person_name}")

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Erro ao atualizar última interação de {person_name}: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """
        Retorna todos os usuários.

        Returns:
            Lista de usuários
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT id, name, phone, onboarding_complete, onboarding_type, first_access_at, last_access_at FROM users ORDER BY name"))
                users = []

                for row in result:
                    users.append({
                        "id": row[0],
                        "name": row[1],
                        "phone": row[2],
                        "onboarding_complete": row[3],
                        "onboarding_type": row[4],
                        "first_access_at": row[5],
                        "last_access_at": row[6],
                    })

                return users

        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []

    def add_user(
        self,
        name: str,
        phone: Optional[str] = None,
        onboarding_complete: bool = False
    ) -> bool:
        """
        Adiciona um novo usuário.

        Args:
            name: Nome do usuário
            phone: Número de telefone (opcional)
            onboarding_complete: Se completou onboarding

        Returns:
            True se sucesso, False se erro (ou já existe)
        """
        try:
            now = datetime.now(self.timezone)

            with self.engine.connect() as conn:
                conn.execute(
                    text("""INSERT INTO users
                    (name, phone, onboarding_complete, first_access_at, last_access_at)
                    VALUES (:name, :phone, :onboarding_complete, :now, :now)"""),
                    {"name": name, "phone": phone, "onboarding_complete": onboarding_complete, "now": now}
                )
                conn.commit()
                logger.info(f"✅ Usuário {name} adicionado com sucesso")
                return True

        except Exception as e:
            logger.warning(f"⚠️ Erro ao adicionar {name}: {e}")
            return False


# Instância global
_users_manager: Optional[UsersManager] = None


def get_users_manager() -> UsersManager:
    """
    Retorna instância singleton do UsersManager.

    Returns:
        UsersManager pronto para usar
    """
    global _users_manager

    if _users_manager is None:
        _users_manager = UsersManager()

    return _users_manager
