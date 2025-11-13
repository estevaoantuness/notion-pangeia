"""
Handler para respostas de checkins diários.

Este módulo integra o sistema de checkins com o processador de comandos,
permitindo que respostas a perguntas de checkin sejam detectadas e registradas
automaticamente.

Fluxo:
1. Scheduler envia pergunta de checkin
2. Usuário responde a qualquer hora
3. response_handler.py detecta a resposta como checkin
4. Registra a resposta no sistema de checkins
5. Fornece feedback ao usuário
"""

import logging
from typing import Tuple, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database.checkins_integration import get_checkins_integration
from src.checkins.pending_tracker import get_pending_checkin_tracker
from src.messaging.humanizer import get_humanizer

logger = logging.getLogger(__name__)
TZ = ZoneInfo("America/Sao_Paulo")


class CheckinResponseHandler:
    """
    Handler especializado para respostas de checkins diários.

    Detecta quando uma resposta é um checkin e a registra no sistema.
    """

    def __init__(self):
        """Inicializa o handler."""
        self.checkins_integration = get_checkins_integration()
        self.pending_tracker = get_pending_checkin_tracker()
        self.humanizer = get_humanizer()
        logger.info("CheckinResponseHandler inicializado")

    def is_checkin_response(self, person_name: str) -> bool:
        """
        Verifica se o usuário tem um checkin pendente.

        Args:
            person_name: Nome da pessoa

        Returns:
            True se há checkin pendente aguardando resposta
        """
        pending = self.pending_tracker.get_pending_checkin(person_name)
        return pending is not None

    def handle_checkin_response(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa resposta a um checkin.

        Args:
            person_name: Nome da pessoa respondendo
            message: Resposta do usuário

        Returns:
            Tuple (processado_com_sucesso, mensagem_resposta)
        """
        try:
            # 1. Verifica se há checkin pendente
            pending_checkin = self.pending_tracker.get_pending_checkin(person_name)

            if not pending_checkin:
                logger.warning(f"Nenhum checkin pendente para {person_name}")
                return False, ""

            checkin_type = pending_checkin.checkin_type

            # 2. Mapeia tipo de checkin para período (morning, afternoon, evening)
            period_map = {
                "metas": "morning",
                "planning": "afternoon",
                "status": "afternoon",
                "consolidado": "afternoon",
                "closing": "evening",
                "reflection": "evening",
                "weekend_digest": "evening"
            }

            period = period_map.get(checkin_type, "afternoon")

            logger.info(f"Registrando resposta de checkin para {person_name} ({checkin_type})")

            # 3. Registra resposta no banco de dados
            success = self.checkins_integration.register_checkin_response(
                person_name=person_name,
                period=period,
                answer=message
            )

            if not success:
                logger.error(f"Erro ao registrar resposta de checkin para {person_name}")
                return False, "Desculpe, tive um erro ao registrar sua resposta."

            # 4. Marca checkin como respondido no tracker
            self.pending_tracker.clear_pending_checkin(person_name)

            logger.info(f"✅ Resposta de checkin registrada para {person_name}")

            # 5. Gera resposta ao usuário
            response_msg = self._generate_acknowledgment(person_name, checkin_type)

            return True, response_msg

        except Exception as e:
            logger.error(f"Erro ao processar resposta de checkin: {e}", exc_info=True)
            return False, "Desculpe, tive um erro ao processar sua resposta."

    def _generate_acknowledgment(self, person_name: str, checkin_type: str) -> str:
        """
        Gera mensagem de confirmação personalizada.

        Args:
            person_name: Nome da pessoa
            checkin_type: Tipo de checkin

        Returns:
            Mensagem de confirmação
        """
        first_name = person_name.split()[0]

        # Diferentes mensagens por tipo de checkin
        acknowledgments = {
            "metas": f"Ótimo, {first_name}! 📋 Suas metas foram anotadas.",
            "planning": f"Perfeito! 🎯 Seu planejamento foi registrado.",
            "status": f"Ótimo! 📊 Obrigado pelo update de status.",
            "consolidado": f"Legal! 📈 Seu consolidado foi anotado.",
            "closing": f"Excelente! ✅ Seu fechamento foi registrado.",
            "reflection": f"Obrigado pela reflexão! 🌟 Anotei para você.",
            "weekend_digest": f"Legal! 🏖️ Seu status foi registrado."
        }

        return acknowledgments.get(checkin_type, f"✅ Sua resposta foi registrada, {first_name}!")

    def get_checkin_status(self, person_name: str) -> Optional[dict]:
        """
        Retorna status do checkin de hoje.

        Args:
            person_name: Nome da pessoa

        Returns:
            Dict com status ou None se erro
        """
        try:
            status = self.checkins_integration.get_checkin_status(person_name)

            if "error" in status:
                logger.warning(f"Erro ao obter status: {status.get('error')}")
                return None

            return status

        except Exception as e:
            logger.error(f"Erro ao obter status de checkin: {e}")
            return None

    def format_checkin_status(self, status: dict) -> str:
        """
        Formata status do checkin para exibição.

        Args:
            status: Dict com status do checkin

        Returns:
            Mensagem formatada
        """
        try:
            first_name = status.get("person", "").split()[0]
            progress = status.get("progress", "0/3")

            msg = f"📋 *Seu progresso de hoje: {progress}*\n\n"

            # Morning
            morning = status.get("morning", {})
            morning_icon = "✅" if morning.get("answered") else "⏳"
            msg += f"{morning_icon} *Manhã:* {morning.get('question', '')}\n"
            if morning.get("answer"):
                msg += f"   → {morning.get('answer', '')}\n"
            msg += "\n"

            # Afternoon
            afternoon = status.get("afternoon", {})
            afternoon_icon = "✅" if afternoon.get("answered") else "⏳"
            msg += f"{afternoon_icon} *Tarde:* {afternoon.get('question', '')}\n"
            if afternoon.get("answer"):
                msg += f"   → {afternoon.get('answer', '')}\n"
            msg += "\n"

            # Evening
            evening = status.get("evening", {})
            evening_icon = "✅" if evening.get("answered") else "⏳"
            msg += f"{evening_icon} *Noite:* {evening.get('question', '')}\n"
            if evening.get("answer"):
                msg += f"   → {evening.get('answer', '')}\n"

            return msg

        except Exception as e:
            logger.error(f"Erro ao formatar status: {e}")
            return "Desculpe, tive um erro ao formatar o status."


# Instância global
_handler_instance: Optional[CheckinResponseHandler] = None


def get_checkin_response_handler() -> CheckinResponseHandler:
    """
    Retorna instância singleton do handler.

    Returns:
        CheckinResponseHandler pronto para usar
    """
    global _handler_instance

    if _handler_instance is None:
        _handler_instance = CheckinResponseHandler()

    return _handler_instance
