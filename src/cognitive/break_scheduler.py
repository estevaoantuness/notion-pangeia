"""
Break Scheduler - Agendador Inteligente de Pausas.

Sugere pausas baseado em carga cognitiva e tempo trabalhando.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from .load_detector import CognitiveLoadLevel

logger = logging.getLogger(__name__)


class BreakScheduler:
    """Agenda pausas inteligentemente."""

    def __init__(self):
        """Inicializa o agendador."""
        self.last_break_suggested = {}
        logger.info("BreakScheduler inicializado")

    def should_suggest_break(
        self,
        person_name: str,
        cognitive_load: CognitiveLoadLevel,
        hours_working: float,
        time_since_last_break_minutes: float
    ) -> bool:
        """
        Determina se deve sugerir pausa.

        Args:
            person_name: Nome da pessoa
            cognitive_load: Nível de carga cognitiva
            hours_working: Horas trabalhando hoje
            time_since_last_break_minutes: Minutos desde última pausa

        Returns:
            True se deve sugerir
        """
        # Não sugerir se já sugeriu recentemente
        if person_name in self.last_break_suggested:
            last_suggested = self.last_break_suggested[person_name]
            if (datetime.now() - last_suggested).total_seconds() < 1800:  # 30min
                return False

        # Critérios para sugerir pausa
        if cognitive_load in [CognitiveLoadLevel.VERY_HIGH, CognitiveLoadLevel.CRITICAL]:
            # Sobrecarregado: sugerir imediatamente
            return True

        if time_since_last_break_minutes > 120:  # 2h sem pausa
            return True

        if hours_working > 4 and time_since_last_break_minutes > 60:
            return True

        return False

    def suggest_break_message(
        self,
        person_name: str,
        cognitive_load: CognitiveLoadLevel
    ) -> str:
        """Gera mensagem de sugestão de pausa."""
        self.last_break_suggested[person_name] = datetime.now()

        if cognitive_load == CognitiveLoadLevel.CRITICAL:
            return (
                "⚠️ Você está exausto! PARE AGORA.\n"
                "Sério, sua saúde é mais importante. 30 minutos de pausa. 🧘"
            )

        elif cognitive_load == CognitiveLoadLevel.VERY_HIGH:
            return (
                "Você está muito sobrecarregado. 😰\n"
                "15 minutos de pausa? Seu cérebro precisa! ☕"
            )

        elif cognitive_load == CognitiveLoadLevel.HIGH:
            return (
                "Sinto que você tá precisando de um break.\n"
                "10 minutos longe da tela? 🚶"
            )

        return (
            "Que tal um break de 5 minutos?\n"
            "Esticar as pernas, tomar água... 💧"
        )
