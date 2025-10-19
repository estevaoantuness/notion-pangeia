"""
Personalization Engine - Personalização de Nudges por Perfil.

Sistema que adapta nudges ao perfil psicológico único de cada pessoa,
considerando traits, padrões, preferências e histórico de resposta.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.people.profile import PersonProfile, PersonalityTrait, ProductivityPattern, CommunicationStyle
from src.psychology.engine import PsychologicalMetrics, EmotionalState, EnergyLevel
from .nudge_engine import Nudge, NudgeType

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    Motor de personalização de nudges.

    Adapta mensagens e timing baseado no perfil único de cada pessoa.
    """

    def __init__(self):
        """Inicializa motor de personalização."""
        self.response_tracking: Dict[str, Dict[NudgeType, float]] = {}
        logger.info("PersonalizationEngine inicializado")

    def personalize_nudge(
        self,
        nudge: Nudge,
        person_name: str,
        profile: PersonProfile
    ) -> Nudge:
        """
        Personaliza um nudge para uma pessoa específica.

        Args:
            nudge: Nudge original
            person_name: Nome da pessoa
            profile: Perfil da pessoa

        Returns:
            Nudge personalizado
        """
        # Adaptar mensagem ao estilo de comunicação
        message = self._adapt_communication_style(nudge.message, profile.communication_style)

        # Adaptar ao tom preferido
        message = self._adapt_tone(message, profile)

        # Criar novo nudge com mensagem personalizada
        personalized_nudge = Nudge(
            message=message,
            nudge_type=nudge.nudge_type,
            timing=nudge.timing,
            personality_match=nudge.personality_match,
            emotional_state_match=nudge.emotional_state_match,
            energy_level_match=nudge.energy_level_match,
            cooldown_hours=nudge.cooldown_hours,
            priority=nudge.priority
        )

        logger.debug(f"Nudge personalizado para {person_name}")
        return personalized_nudge

    def _adapt_communication_style(
        self,
        message: str,
        style: CommunicationStyle
    ) -> str:
        """Adapta mensagem ao estilo de comunicação preferido."""

        if style == CommunicationStyle.BRIEF:
            # Mensagens mais curtas e diretas
            message = message.split('.')[0] + '.'  # Primeira frase apenas
            message = message.replace('!', '').replace('😊', '')  # Menos entusiasmo

        elif style == CommunicationStyle.FORMAL:
            # Tom mais formal
            replacements = {
                'Você': 'Você',
                'tá': 'está',
                'pra': 'para',
                'né': '',
                '💪': '',
                '🎯': '',
                '🎉': '',
            }
            for old, new in replacements.items():
                message = message.replace(old, new)

        elif style == CommunicationStyle.EMOJI_RICH:
            # Adicionar mais emojis se não tiver
            if message.count('😊') + message.count('💪') + message.count('🎯') < 2:
                message = message + ' ✨'

        return message

    def _adapt_tone(self, message: str, profile: PersonProfile) -> str:
        """Adapta tom da mensagem baseado no perfil."""

        # Para pessoas que precisam de encorajamento, tom mais caloroso
        if profile.has_trait(PersonalityTrait.NEEDS_ENCOURAGEMENT):
            if '!' not in message:
                message = message.replace('.', '! 💙')

        # Para pessoas auto-motivadas, tom mais desafiador
        if profile.has_trait(PersonalityTrait.SELF_MOTIVATED):
            message = message.replace('Você consegue', 'Você vai conseguir')
            message = message.replace('Tenta', 'Vai lá e')

        # Para pessoas colaborativas, mencionar time
        if profile.has_trait(PersonalityTrait.COLLABORATIVE):
            if 'time' not in message.lower() and random.random() < 0.3:
                message = message + ' O time acredita em você!'

        return message

    def should_send_nudge(
        self,
        person_name: str,
        profile: PersonProfile,
        metrics: PsychologicalMetrics,
        nudge_type: NudgeType
    ) -> bool:
        """
        Determina se deve enviar nudge agora baseado em contexto.

        Args:
            person_name: Nome da pessoa
            profile: Perfil da pessoa
            metrics: Métricas atuais
            nudge_type: Tipo de nudge

        Returns:
            True se deve enviar
        """
        # Não enviar se pessoa está em deep work (muito focada)
        if self._is_in_deep_work(metrics):
            logger.debug(f"{person_name} em deep work, pulando nudge")
            return False

        # Não enviar se pessoa está sobrecarregada demais
        if metrics.emotional_state == EmotionalState.BURNED_OUT:
            # Apenas nudges de break ou reset
            if nudge_type not in [NudgeType.BREAK_SUGGESTION, NudgeType.RESET]:
                return False

        # Respeitar padrão de produtividade
        if not self._matches_productivity_pattern(profile.productivity_pattern):
            return False

        # Respeitar preferências de horário
        if not self._matches_time_preference(profile):
            return False

        return True

    def _is_in_deep_work(self, metrics: PsychologicalMetrics) -> bool:
        """Detecta se pessoa está em deep work (não interromper)."""
        # Deep work: alta energia, muito focado, pouquíssimas mensagens
        return (
            metrics.energy_level in [EnergyLevel.HIGH, EnergyLevel.VERY_HIGH]
            and metrics.emotional_state == EmotionalState.MOTIVATED
            and metrics.message_length_avg < 20  # Mensagens curtas = focado
        )

    def _matches_productivity_pattern(self, pattern: ProductivityPattern) -> bool:
        """Verifica se horário atual combina com padrão de produtividade."""
        hour = datetime.now().hour

        if pattern == ProductivityPattern.MORNING_PEAK:
            return 8 <= hour < 12
        elif pattern == ProductivityPattern.AFTERNOON_PEAK:
            return 13 <= hour < 18
        elif pattern == ProductivityPattern.EVENING_PEAK:
            return 18 <= hour < 22
        else:
            # CONSISTENT ou IRREGULAR - qualquer hora
            return True

    def _matches_time_preference(self, profile: PersonProfile) -> bool:
        """Verifica se horário atual respeita preferências."""
        hour = datetime.now().hour

        # Morning person - não enviar tarde da noite
        if profile.has_trait(PersonalityTrait.MORNING_PERSON):
            if hour >= 21 or hour < 6:
                return False

        # Night owl - não enviar cedo demais
        if profile.has_trait(PersonalityTrait.NIGHT_OWL):
            if 6 <= hour < 10:
                return False

        return True

    def track_response(
        self,
        person_name: str,
        nudge_type: NudgeType,
        was_effective: bool
    ) -> None:
        """
        Rastreia efetividade de nudges para aprendizado contínuo.

        Args:
            person_name: Nome da pessoa
            nudge_type: Tipo de nudge enviado
            was_effective: Se foi efetivo
        """
        if person_name not in self.response_tracking:
            self.response_tracking[person_name] = {}

        if nudge_type not in self.response_tracking[person_name]:
            self.response_tracking[person_name][nudge_type] = 0.5  # Neutro

        # Atualizar score com média móvel
        current_score = self.response_tracking[person_name][nudge_type]
        new_value = 1.0 if was_effective else 0.0

        # Média móvel exponencial (alpha=0.3)
        updated_score = 0.7 * current_score + 0.3 * new_value
        self.response_tracking[person_name][nudge_type] = updated_score

        logger.info(
            f"Resposta rastreada: {person_name} + {nudge_type.value} = "
            f"{'efetivo' if was_effective else 'não efetivo'} "
            f"(score: {updated_score:.2f})"
        )

    def get_effectiveness_scores(self, person_name: str) -> Dict[NudgeType, float]:
        """
        Retorna scores de efetividade de cada tipo de nudge.

        Args:
            person_name: Nome da pessoa

        Returns:
            Dict {NudgeType: score (0.0-1.0)}
        """
        return self.response_tracking.get(person_name, {})

    def get_best_nudge_types(
        self,
        person_name: str,
        top_n: int = 3
    ) -> List[NudgeType]:
        """
        Retorna os tipos de nudge mais efetivos para uma pessoa.

        Args:
            person_name: Nome da pessoa
            top_n: Número de tipos a retornar

        Returns:
            Lista de NudgeTypes ordenados por efetividade
        """
        scores = self.get_effectiveness_scores(person_name)

        if not scores:
            return []

        # Ordenar por score
        sorted_types = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [nudge_type for nudge_type, _ in sorted_types[:top_n]]

    def generate_personalization_report(self, person_name: str) -> Dict:
        """
        Gera relatório de personalização para uma pessoa.

        Args:
            person_name: Nome da pessoa

        Returns:
            Dict com insights de personalização
        """
        scores = self.get_effectiveness_scores(person_name)

        if not scores:
            return {
                "person": person_name,
                "has_data": False,
                "message": "Dados insuficientes para personalização"
            }

        best_types = self.get_best_nudge_types(person_name, top_n=3)
        worst_types = sorted(scores.items(), key=lambda x: x[1])[:2]

        return {
            "person": person_name,
            "has_data": True,
            "best_nudge_types": [nt.value for nt in best_types],
            "worst_nudge_types": [nt.value for nt, _ in worst_types],
            "all_scores": {nt.value: score for nt, score in scores.items()},
            "overall_responsiveness": sum(scores.values()) / len(scores) if scores else 0.5
        }


# Importar random para uso no código
import random
