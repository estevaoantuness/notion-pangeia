"""
Middleware de Enriquecimento Psicológico.

Este módulo processa respostas para adicionar camadas psicológicas
antes de enviar para o usuário.
"""

import logging
from typing import Optional, Tuple
from src.psychology.engine import PsychologicalEngine, EmotionalState
from src.psychology.communicator import EmpatheticCommunicator
from src.people.analytics import PeopleAnalytics

logger = logging.getLogger(__name__)


class PsychologicalEnrichmentMiddleware:
    """Enriquece respostas com inteligência psicológica."""

    def __init__(self):
        """Inicializa o middleware."""
        self.psych_engine = PsychologicalEngine()
        self.communicator = EmpatheticCommunicator()
        self.analytics = PeopleAnalytics()
        logger.info("PsychologicalEnrichmentMiddleware inicializado")

    def enrich_response(
        self,
        response: str,
        person_name: str,
        context: Optional[dict] = None
    ) -> str:
        """
        Enriquece resposta com elementos psicológicos.

        Adiciona:
        - Validação emocional (OARS)
        - Reforço positivo
        - Variação nas respostas
        - Emojis contextuais
        - Senso de pertencimento

        Args:
            response: Resposta original
            person_name: Nome da pessoa
            context: Contexto adicional

        Returns:
            Resposta enriquecida
        """
        try:
            # Análise do perfil da pessoa
            profile = self.analytics.get_or_create_profile(person_name)

            # Detecta estado emocional baseado no histórico
            if context and "emotional_state" in context:
                emotional_state = context["emotional_state"]
            else:
                emotional_state = EmotionalState.BALANCED

            # Adapta tom baseado no perfil
            enriched = response

            # Adiciona validação emocional se pessoa está estressada
            if emotional_state in [EmotionalState.STRESSED, EmotionalState.OVERWHELMED]:
                enriched = f"Entendo que tá pesado...\n\n{response}\n\nVocê não está sozinho. Vou ajudar. 🤝"

            # Adiciona reforço se pessoa está progredindo bem
            elif emotional_state == EmotionalState.MOTIVATED:
                enriched = f"{response}\n\n✨ Você está indo MUITO bem! Continue assim!"

            # Adiciona sensação de pertencimento
            if not enriched.endswith("🤝") and person_name:
                enriched += f"\n\nEstou aqui contigo, {person_name}! 💪"

            logger.info(f"Resposta enriquecida para {person_name}")
            return enriched

        except Exception as e:
            logger.error(f"Erro ao enriquecer resposta: {e}")
            return response

    def detect_burnout_risk(self, person_name: str) -> Tuple[bool, Optional[str]]:
        """
        Detecta risco de burnout e sugere intervenção.

        Returns:
            Tuple (tem_risco, mensagem_sugestão)
        """
        try:
            metrics = self.psych_engine.analyze_user(person_name)

            if metrics.burnout_risk.value in ["high", "critical"]:
                intervention = (
                    f"🚨 Detectei que você pode estar sobrecarregado.\n\n"
                    f"Vamos priorizar apenas o essencial hoje?\n\n"
                    f"Foco > Volume. Você merece descanso. 🌟"
                )
                return True, intervention

            return False, None

        except Exception as e:
            logger.error(f"Erro ao detectar burnout: {e}")
            return False, None
