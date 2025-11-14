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
import random
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
        Gera mensagem de confirmação personalizada com múltiplas variações.

        Fornece feedback visual ao usuário confirmando que a resposta foi registrada,
        com variações para não parecer robótico.

        Args:
            person_name: Nome da pessoa
            checkin_type: Tipo de checkin (metas, planning, status, consolidado, closing, etc)

        Returns:
            Mensagem de confirmação personalizada
        """
        first_name = person_name.split()[0]
        hour = datetime.now(tz=TZ).hour

        # Variações por tipo de checkin - múltiplas opções para cada tipo
        acknowledgments = {
            "metas": [
                f"✅ Perfeito, {first_name}! 📋 Suas metas foram anotadas.",
                f"🎯 Ótimo! Suas metas estão registradas, {first_name}!",
                f"📌 Anotar metas é essencial! Já marquei as suas. 💪",
                f"✨ Excelente decisão, {first_name}! Metas salvas! 🚀",
                f"💯 Meta anotada! Vamos lá conseguir! 🔥",
                f"📝 Consegui anotar sua meta, {first_name}. Bora focar! 🎯",
            ],
            "planning": [
                f"✅ Perfeito! 🎯 Seu planejamento foi registrado, {first_name}!",
                f"📊 Planejamento salvo! Você está na trilha certa!",
                f"🎪 Bom planejamento! Já anotei tudo para você. 💼",
                f"✨ Seu planejamento está guardadinho! Sucesso! 🙌",
                f"🔧 Planejamento registrado! Agora é só executar!",
                f"📋 Ótima organização, {first_name}! Tudo salvo! ✅",
            ],
            "status": [
                f"✅ Ótimo! 📊 Obrigado pelo update de status, {first_name}!",
                f"🔄 Status atualizado! Continuamos monitorando. 👀",
                f"📈 Ótima informação! Seu status está registrado!",
                f"✨ Valeu pelo feedback! Anotei tudo. 📝",
                f"👍 Status recebido e salvo, {first_name}!",
                f"💬 Obrigado pela transparência! Tudo registrado! ✅",
            ],
            "consolidado": [
                f"✅ Legal! 📈 Seu consolidado foi anotado, {first_name}!",
                f"🎯 Consolidado registrado! Bora manter esse ritmo!",
                f"✨ Excelente consolidação! Já marquei para você.",
                f"💯 Seu consolidado está guardadinho! 📊",
                f"🔥 Ótimo trabalho! Consolidado anotado!",
                f"🚀 Continuamos avançando! Consolidado salvo, {first_name}! 📌",
            ],
            "closing": [
                f"✅ Excelente! Seu fechamento foi registrado, {first_name}! 🌙",
                f"🎉 Que dia incrível, {first_name}! Fechamento salvo!",
                f"⭐ Adorei ver seu progresso de hoje! Tudo anotado!",
                f"🌟 Dia finalizado com sucesso! Já registrei! 📝",
                f"✨ Perfeito encerramento do dia, {first_name}!",
                f"🏆 Belo dia! Fechamento confirmado! Descansa! 😌",
            ],
            "reflection": [
                f"✅ Obrigado pela reflexão! 🌟 Anotei para você, {first_name}!",
                f"💭 Que reflexão valiosa! Salva com cuidado!",
                f"✨ Autoconhecimento é poder! Sua reflexão está guardada!",
                f"🌱 Ótima análise! Reflexão registrada! 📖",
                f"💡 Insights importantes! Já marquei tudo!",
                f"🎯 Reflexão salva! Continue crescendo, {first_name}! 🚀",
            ],
            "weekend_digest": [
                f"✅ Legal! 🏖️ Seu status de fim de semana foi registrado!",
                f"🌴 Aproveite o fim de semana! Seu status está salvo!",
                f"☀️ Ótimo jeito de encerrar a semana! Registrado!",
                f"🎭 Belo resumo da semana, {first_name}! Anotei!",
                f"✨ Semana encerrada com êxito! Tudo documentado!",
                f"🏡 Aproveite o descanso! Seu digest está seguro! 📋",
            ],
        }

        # Seleciona mensagem aleatória do tipo de checkin
        messages = acknowledgments.get(checkin_type, [
            f"✅ Sua resposta foi registrada, {first_name}!",
            f"📝 Tudo anotado! Obrigado, {first_name}!",
            f"✨ Resposta salva com sucesso!",
            f"👍 Registrado! Continuamos acompanhando!",
        ])

        # Escolhe aleatoriamente uma das variações
        response = random.choice(messages)

        # Adiciona contexto contextual baseado no horário
        next_checkin_hint = self._get_next_checkin_hint(checkin_type, hour)
        if next_checkin_hint:
            response += f"\n{next_checkin_hint}"

        return response

    def _get_next_checkin_hint(self, current_type: str, hour: int) -> Optional[str]:
        """
        Retorna dica sobre o próximo check-in.

        Args:
            current_type: Tipo de checkin atual
            hour: Hora atual

        Returns:
            Mensagem com informação sobre próximo check-in ou None
        """
        # Próximos check-ins por tipo de checkin
        next_checkins = {
            "metas": ("13:30", "planejamento da tarde"),
            "planning": ("15:30", "status da tarde"),
            "status": ("18:00", "fechamento do dia"),
            "consolidado": ("18:00", "reflexão noturna"),
            "closing": ("08:00 de amanhã", "suas metas do novo dia"),
            "reflection": ("08:00 de amanhã", "novo dia trazendo novas metas"),
            "weekend_digest": ("segunda-feira", "uma nova semana cheia de desafios"),
        }

        next_time, next_desc = next_checkins.get(
            current_type,
            ("em breve", "seu próximo check-in")
        )

        hints = [
            f"⏰ Próximo check-in às {next_time} para {next_desc}!",
            f"📅 Nos encontramos às {next_time} com {next_desc}!",
            f"🔔 Aviso: {next_time} teremos seu check-in de {next_desc}!",
        ]

        # 50% de chance de mostrar o hint (não ficar muito repetitivo)
        if random.random() > 0.5:
            return random.choice(hints)

        return None

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
