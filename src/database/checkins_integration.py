"""
Integração entre CheckinsManager e o Scheduler/Bot.

Gerencia a criação de checkins e registro de respostas.
"""

import logging
from typing import Optional
from datetime import date

from src.database.checkins_manager import get_checkins_manager
from src.database.users_manager import get_users_manager

logger = logging.getLogger(__name__)


class CheckinsIntegration:
    """
    Integra o gerenciamento de checkins com o bot.
    """

    def __init__(self):
        """Inicializa a integração."""
        self.checkins_manager = get_checkins_manager()
        self.users_manager = get_users_manager()
        logger.info("CheckinsIntegration inicializado")

    def create_daily_checkin(
        self,
        person_name: str,
        morning_q: str = "Como você amanheceu hoje?",
        afternoon_q: str = "Como está o ritmo do dia?",
        evening_q: str = "Como foi seu dia?"
    ) -> bool:
        """
        Cria um novo checkin do dia para uma pessoa.

        Deve ser chamado UMA VEZ por dia (no começo do dia).

        Args:
            person_name: Nome da pessoa
            morning_q: Pergunta da manhã
            afternoon_q: Pergunta da tarde
            evening_q: Pergunta da noite

        Returns:
            True se sucesso, False se erro
        """
        try:
            # Buscar ID do usuário
            user_id = self.users_manager.get_user(person_name)

            if not user_id or not user_id.get("id"):
                logger.warning(f"⚠️ Usuário não encontrado: {person_name}")
                return False

            user_id_value = user_id["id"]

            # Criar checkin com as 3 perguntas
            success = self.checkins_manager.create_checkin(
                user_id=user_id_value,
                morning_q=morning_q,
                afternoon_q=afternoon_q,
                evening_q=evening_q
            )

            if success:
                logger.info(f"✅ Checkin diário criado para {person_name}")
            else:
                logger.error(f"❌ Erro ao criar checkin para {person_name}")

            return success

        except Exception as e:
            logger.error(f"Erro em create_daily_checkin para {person_name}: {e}")
            return False

    def register_checkin_response(
        self,
        person_name: str,
        period: str,
        answer: str
    ) -> bool:
        """
        Registra resposta a uma pergunta do checkin.

        Deve ser chamado quando pessoa responde a uma pergunta.

        Args:
            person_name: Nome da pessoa
            period: 'morning', 'afternoon' ou 'evening'
            answer: Resposta da pessoa

        Returns:
            True se sucesso, False se erro
        """
        try:
            # Buscar ID do usuário
            user_data = self.users_manager.get_user(person_name)

            if not user_data or not user_data.get("id"):
                logger.warning(f"⚠️ Usuário não encontrado: {person_name}")
                return False

            user_id = user_data["id"]

            # Verificar se existe checkin de hoje
            checkin = self.checkins_manager.get_today_checkin(user_id)

            if not checkin:
                logger.warning(f"⚠️ Sem checkin de hoje para {person_name}")
                return False

            # Salvar resposta
            success = self.checkins_manager.save_answer(
                user_id=user_id,
                period=period,
                answer=answer
            )

            if success:
                logger.info(f"✅ Resposta registrada para {person_name} ({period})")
                # Atualizar última interação
                self.users_manager.update_last_interaction(person_name)
            else:
                logger.error(f"❌ Erro ao registrar resposta para {person_name}")

            return success

        except Exception as e:
            logger.error(f"Erro em register_checkin_response para {person_name}: {e}")
            return False

    def get_checkin_status(self, person_name: str) -> dict:
        """
        Retorna status do checkin de hoje da pessoa.

        Útil para mostrar progresso: quantas perguntas foram respondidas.

        Args:
            person_name: Nome da pessoa

        Returns:
            Dict com perguntas, respostas e status
        """
        try:
            user_data = self.users_manager.get_user(person_name)

            if not user_data:
                return {"error": "Usuário não encontrado"}

            user_id = user_data["id"]
            checkin = self.checkins_manager.get_today_checkin(user_id)

            if not checkin:
                return {"error": "Sem checkin para hoje"}

            # Contar quantas respostas foram dadas
            answered = 0
            if checkin["morning_answer"]:
                answered += 1
            if checkin["afternoon_answer"]:
                answered += 1
            if checkin["evening_answer"]:
                answered += 1

            return {
                "person": person_name,
                "date": str(checkin["date"]),
                "total_questions": 3,
                "answered": answered,
                "progress": f"{answered}/3",
                "morning": {
                    "question": checkin["morning_question"],
                    "answered": bool(checkin["morning_answer"]),
                    "answer": checkin["morning_answer"]
                },
                "afternoon": {
                    "question": checkin["afternoon_question"],
                    "answered": bool(checkin["afternoon_answer"]),
                    "answer": checkin["afternoon_answer"]
                },
                "evening": {
                    "question": checkin["evening_question"],
                    "answered": bool(checkin["evening_answer"]),
                    "answer": checkin["evening_answer"]
                }
            }

        except Exception as e:
            logger.error(f"Erro em get_checkin_status para {person_name}: {e}")
            return {"error": str(e)}


# Instância global
_checkins_integration: Optional[CheckinsIntegration] = None


def get_checkins_integration() -> CheckinsIntegration:
    """
    Retorna instância singleton da integração.

    Returns:
        CheckinsIntegration pronto para usar
    """
    global _checkins_integration

    if _checkins_integration is None:
        _checkins_integration = CheckinsIntegration()

    return _checkins_integration
