"""
Gerenciador de Daily Checkins usando Supabase (Postgres).

Controla as 3 perguntas diárias de cada pessoa e suas respostas.
"""

import logging
from typing import Optional, Dict, List
from datetime import date, datetime
import pytz
from sqlalchemy import text

from src.database.connection import get_db_engine

logger = logging.getLogger(__name__)


class CheckinsManager:
    """
    Gerencia daily checkins (3 perguntas por dia) de usuários.
    """

    def __init__(self):
        """Inicializa o gerenciador de checkins."""
        self.engine = get_db_engine()
        self.timezone = pytz.timezone("America/Sao_Paulo")
        logger.info("CheckinsManager inicializado (Postgres/Supabase)")

    def get_user_id(self, name: str) -> Optional[int]:
        """
        Busca ID do usuário pelo nome.

        Args:
            name: Nome do usuário

        Returns:
            ID do usuário ou None se não encontrado
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id FROM users WHERE name = :name"),
                    {"name": name}
                )
                row = result.fetchone()
                return row[0] if row else None

        except Exception as e:
            logger.error(f"Erro ao buscar ID do usuário {name}: {e}")
            return None

    def get_today_checkin(self, user_id: int) -> Optional[Dict]:
        """
        Busca checkin de hoje do usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Dict com checkin de hoje ou None se não existe
        """
        try:
            today = date.today()

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """SELECT id, user_id, date, morning_question, afternoon_question,
                           evening_question, morning_answer, afternoon_answer, evening_answer,
                           created_at, updated_at
                           FROM daily_checkins
                           WHERE user_id = :user_id AND date = :today"""
                    ),
                    {"user_id": user_id, "today": today}
                )
                row = result.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "date": row[2],
                        "morning_question": row[3],
                        "afternoon_question": row[4],
                        "evening_question": row[5],
                        "morning_answer": row[6],
                        "afternoon_answer": row[7],
                        "evening_answer": row[8],
                        "created_at": row[9],
                        "updated_at": row[10],
                    }

                return None

        except Exception as e:
            logger.error(f"Erro ao buscar checkin de hoje para user {user_id}: {e}")
            return None

    def create_checkin(
        self,
        user_id: int,
        morning_q: str,
        afternoon_q: str,
        evening_q: str
    ) -> bool:
        """
        Cria um novo checkin do dia.

        Args:
            user_id: ID do usuário
            morning_q: Pergunta da manhã
            afternoon_q: Pergunta da tarde
            evening_q: Pergunta da noite

        Returns:
            True se sucesso, False se erro
        """
        try:
            today = date.today()

            with self.engine.connect() as conn:
                # Verificar se já existe checkin de hoje
                existing = self.get_today_checkin(user_id)

                if existing:
                    logger.info(f"Checkin de hoje já existe para user {user_id}")
                    return True

                # Criar novo checkin
                conn.execute(
                    text(
                        """INSERT INTO daily_checkins
                        (user_id, date, morning_question, afternoon_question, evening_question)
                        VALUES (:user_id, :today, :morning_q, :afternoon_q, :evening_q)"""
                    ),
                    {"user_id": user_id, "today": today, "morning_q": morning_q, "afternoon_q": afternoon_q, "evening_q": evening_q}
                )
                conn.commit()

                logger.info(f"✅ Checkin criado para user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Erro ao criar checkin para user {user_id}: {e}")
            return False

    def save_answer(
        self,
        user_id: int,
        period: str,
        answer: str
    ) -> bool:
        """
        Salva resposta a uma pergunta do checkin.

        Args:
            user_id: ID do usuário
            period: 'morning', 'afternoon' ou 'evening'
            answer: Resposta do usuário

        Returns:
            True se sucesso, False se erro
        """
        try:
            today = date.today()

            # Mapear período para coluna
            answer_column = f"{period}_answer"

            with self.engine.connect() as conn:
                conn.execute(
                    text(
                        f"""UPDATE daily_checkins
                        SET {answer_column} = :answer
                        WHERE user_id = :user_id AND date = :today"""
                    ),
                    {"answer": answer, "user_id": user_id, "today": today}
                )
                conn.commit()

                logger.info(f"✅ Resposta salva para user {user_id} ({period})")
                return True

        except Exception as e:
            logger.error(f"Erro ao salvar resposta para user {user_id}: {e}")
            return False

    def get_user_checkins(self, user_id: int, limit: int = 7) -> List[Dict]:
        """
        Busca histórico de checkins do usuário.

        Args:
            user_id: ID do usuário
            limit: Número de últimos checkins (default 7 dias)

        Returns:
            Lista de checkins
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """SELECT id, user_id, date, morning_question, afternoon_question,
                           evening_question, morning_answer, afternoon_answer, evening_answer,
                           created_at, updated_at
                           FROM daily_checkins
                           WHERE user_id = :user_id
                           ORDER BY date DESC
                           LIMIT :limit"""
                    ),
                    {"user_id": user_id, "limit": limit}
                )

                checkins = []
                for row in result:
                    checkins.append({
                        "id": row[0],
                        "user_id": row[1],
                        "date": row[2],
                        "morning_question": row[3],
                        "afternoon_question": row[4],
                        "evening_question": row[5],
                        "morning_answer": row[6],
                        "afternoon_answer": row[7],
                        "evening_answer": row[8],
                        "created_at": row[9],
                        "updated_at": row[10],
                    })

                return checkins

        except Exception as e:
            logger.error(f"Erro ao buscar checkins de user {user_id}: {e}")
            return []

    def get_checkin_summary(self, user_id: int) -> Dict:
        """
        Retorna resumo de respostas do dia.

        Args:
            user_id: ID do usuário

        Returns:
            Dict com perguntas e respostas de hoje
        """
        checkin = self.get_today_checkin(user_id)

        if not checkin:
            return {"error": "Sem checkin para hoje"}

        return {
            "date": checkin["date"],
            "morning": {
                "question": checkin["morning_question"],
                "answer": checkin["morning_answer"]
            },
            "afternoon": {
                "question": checkin["afternoon_question"],
                "answer": checkin["afternoon_answer"]
            },
            "evening": {
                "question": checkin["evening_question"],
                "answer": checkin["evening_answer"]
            }
        }


# Instância global
_checkins_manager: Optional['CheckinsManager'] = None


def get_checkins_manager() -> CheckinsManager:
    """
    Retorna instância singleton do CheckinsManager.

    Returns:
        CheckinsManager pronto para usar
    """
    global _checkins_manager

    if _checkins_manager is None:
        _checkins_manager = CheckinsManager()

    return _checkins_manager
