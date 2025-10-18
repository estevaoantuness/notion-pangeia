"""
Detector de Burnout - Burnout Detection System.

Sistema proativo que monitora sinais de esgotamento mental
e oferece suporte psicológico preventivo.
"""

import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta

from src.psychology.engine import PsychologicalEngine, RiskLevel
from src.people.analytics import PeopleAnalytics
from src.psychology.communicator import EmpatheticCommunicator

logger = logging.getLogger(__name__)


class BurnoutDetector:
    """Detecta e previne burnout através de monitoramento contínuo."""

    def __init__(self):
        """Inicializa o detector de burnout."""
        self.psych_engine = PsychologicalEngine()
        self.analytics = PeopleAnalytics()
        self.communicator = EmpatheticCommunicator()
        logger.info("BurnoutDetector inicializado")

    def check_and_intervene(self, person_name: str) -> Optional[str]:
        """
        Verifica risco de burnout e oferece intervenção se necessário.

        Args:
            person_name: Nome da pessoa

        Returns:
            Mensagem de intervenção ou None
        """
        try:
            # Analisa métricas psicológicas
            metrics = self.psych_engine.analyze_user(person_name)

            if not metrics:
                return None

            # Define mensagens por nível de risco
            interventions = {
                RiskLevel.CRITICAL: (
                    "🚨 *ATENÇÃO URGENTE* 🚨\n\n"
                    f"{person_name}, você está em risco crítico de esgotamento.\n\n"
                    "Vamos fazer uma pausa AGORA:\n"
                    "• Desligue por 30 minutos\n"
                    "• Respire fundo 5 vezes\n"
                    "• Beba água\n"
                    "• Estique o corpo\n\n"
                    "Você é mais importante que qualquer tarefa. 💙"
                ),
                RiskLevel.HIGH: (
                    "⚠️ Você está sobrecarregado\n\n"
                    "Percebi que tem muita coisa acontecendo.\n"
                    "Vamos priorizar APENAS o essencial hoje?\n\n"
                    "Foco em 3 tarefas máximo.\n"
                    "O resto pode esperar. 🌟"
                ),
                RiskLevel.MEDIUM: (
                    "💭 Dica de bem-estar\n\n"
                    "Você está indo bem, mas vejo que está um pouco acelerado.\n"
                    "Que tal tirar 5 minutos para você antes de continuar?"
                ),
            }

            risk_level = metrics.burnout_risk

            if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM]:
                message = interventions.get(risk_level)
                if message:
                    logger.warning(f"Intervenção de burnout para {person_name}: {risk_level.value}")
                    return message

            return None

        except Exception as e:
            logger.error(f"Erro ao verificar burnout: {e}")
            return None

    def get_recovery_plan(self, person_name: str) -> str:
        """
        Gera plano de recuperação para pessoa em risco.

        Args:
            person_name: Nome da pessoa

        Returns:
            Plano de recuperação personalizado
        """
        try:
            profile = self.analytics.get_or_create_profile(person_name)

            recovery_plan = f"""
📋 *Plano de Recuperação para {person_name}*

**Semana 1: Restauração**
• Durma 8h por noite
• 30min movimento físico diário
• Uma refeição sem pressa diária

**Semana 2: Reorganização**
• Revise prioridades com perspectiva fresca
• Delegue ou negocie prazos
• Estabeleça limites de horário

**Semana 3: Reengajamento**
• Volte com carga gradual
• Celebre pequenas vitórias diariamente
• Mantenha auto-compaixão

🌟 Você vai se recuperar. Estou aqui te apoiando.
            """
            return recovery_plan

        except Exception as e:
            logger.error(f"Erro ao gerar plano de recuperação: {e}")
            return "Vamos conversar sobre como apoiá-lo melhor. 🤝"
