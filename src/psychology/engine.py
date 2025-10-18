"""
Motor Psicológico - Psychological Engine.

Este módulo analisa o estado emocional dos colaboradores baseado em:
- Teoria da Autodeterminação (Autonomia, Competência, Relacionamento)
- Padrões de comportamento e comunicação
- Taxa de conclusão e engajamento
- Indicadores de burnout e sobrecarga

"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EnergyLevel(Enum):
    """Níveis de energia detectados."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EmotionalState(Enum):
    """Estados emocionais possíveis."""
    MOTIVATED = "motivated"
    BALANCED = "balanced"
    STRESSED = "stressed"
    OVERWHELMED = "overwhelmed"
    BURNED_OUT = "burned_out"
    DISENGAGED = "disengaged"


class RiskLevel(Enum):
    """Níveis de risco de burnout."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PsychologicalMetrics:
    """Métricas psicológicas de um colaborador."""

    # Produtividade
    completion_rate: float = 0.0  # Taxa de conclusão (0.0 - 1.0)
    tasks_completed_today: int = 0
    tasks_pending: int = 0
    tasks_blocked: int = 0

    # Engajamento
    response_time_hours: float = 0.0  # Tempo médio de resposta
    last_activity: Optional[datetime] = None
    checkin_participation: float = 0.0  # % de check-ins respondidos

    # Comunicação
    positive_words_count: int = 0
    negative_words_count: int = 0
    message_length_avg: float = 0.0
    emoji_usage: int = 0

    # Estados
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    emotional_state: EmotionalState = EmotionalState.BALANCED
    burnout_risk: RiskLevel = RiskLevel.NONE

    # Padrões
    streak_days: int = 0  # Dias consecutivos produzindo
    last_milestone: Optional[str] = None
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


class PsychologicalEngine:
    """
    Motor que analisa métricas e retorna insights psicológicos.
    """

    # Palavras que indicam sentimentos positivos
    POSITIVE_WORDS = {
        "obrigado", "thanks", "valeu", "ótimo", "excelente", "legal",
        "adorei", "amei", "perfeito", "maravilhoso", "incrível",
        "feliz", "animado", "empolgado", "motivado", "show", "top",
        "sucesso", "conquista", "vitória", "consegui", "fiz"
    }

    # Palavras que indicam sentimentos negativos ou stress
    NEGATIVE_WORDS = {
        "difícil", "complicado", "impossível", "cansado", "exausto",
        "estressado", "frustrado", "travado", "bloqueado", "sobrecarregado",
        "não consigo", "não sei", "confuso", "perdido", "desanimado",
        "desistir", "problema", "erro", "falha", "atrasado"
    }

    def __init__(self):
        """Inicializa o motor psicológico."""
        logger.info("Psychological Engine inicializado")

    def analyze_person(
        self,
        tasks_data: Dict,
        communication_data: Dict,
        history_data: Optional[Dict] = None
    ) -> PsychologicalMetrics:
        """
        Analisa uma pessoa e retorna métricas psicológicas.

        Args:
            tasks_data: Dados de tarefas da pessoa
            communication_data: Dados de comunicação (mensagens)
            history_data: Histórico de atividades (opcional)

        Returns:
            Métricas psicológicas completas
        """
        metrics = PsychologicalMetrics()

        # Analisar produtividade
        metrics = self._analyze_productivity(metrics, tasks_data)

        # Analisar engajamento
        metrics = self._analyze_engagement(metrics, communication_data)

        # Analisar comunicação (sentimentos)
        metrics = self._analyze_communication(metrics, communication_data)

        # Analisar padrões (histórico)
        if history_data:
            metrics = self._analyze_patterns(metrics, history_data)

        # Inferir estado emocional
        metrics.emotional_state = self._infer_emotional_state(metrics)

        # Avaliar risco de burnout
        metrics.burnout_risk = self._assess_burnout_risk(metrics)

        # Determinar nível de energia
        metrics.energy_level = self._determine_energy_level(metrics)

        logger.info(
            f"Análise completa - Estado: {metrics.emotional_state.value}, "
            f"Energia: {metrics.energy_level.value}, "
            f"Risco: {metrics.burnout_risk.value}"
        )

        return metrics

    def _analyze_productivity(
        self,
        metrics: PsychologicalMetrics,
        tasks_data: Dict
    ) -> PsychologicalMetrics:
        """Analisa métricas de produtividade."""

        total_tasks = tasks_data.get("total", 0)
        completed = tasks_data.get("completed", 0)
        pending = tasks_data.get("pending", 0)
        blocked = tasks_data.get("blocked", 0)

        metrics.tasks_completed_today = completed
        metrics.tasks_pending = pending
        metrics.tasks_blocked = blocked

        # Taxa de conclusão
        if total_tasks > 0:
            metrics.completion_rate = completed / total_tasks
        else:
            metrics.completion_rate = 0.0

        return metrics

    def _analyze_engagement(
        self,
        metrics: PsychologicalMetrics,
        communication_data: Dict
    ) -> PsychologicalMetrics:
        """Analisa nível de engajamento."""

        # Tempo de resposta
        response_times = communication_data.get("response_times", [])
        if response_times:
            metrics.response_time_hours = sum(response_times) / len(response_times)

        # Última atividade
        last_activity_str = communication_data.get("last_activity")
        if last_activity_str:
            metrics.last_activity = datetime.fromisoformat(last_activity_str)

        # Participação em check-ins
        checkins_sent = communication_data.get("checkins_sent", 0)
        checkins_answered = communication_data.get("checkins_answered", 0)

        if checkins_sent > 0:
            metrics.checkin_participation = checkins_answered / checkins_sent
        else:
            metrics.checkin_participation = 0.0

        return metrics

    def _analyze_communication(
        self,
        metrics: PsychologicalMetrics,
        communication_data: Dict
    ) -> PsychologicalMetrics:
        """Analisa padrões de comunicação."""

        messages = communication_data.get("recent_messages", [])

        if not messages:
            return metrics

        total_length = 0
        positive_count = 0
        negative_count = 0
        emoji_count = 0

        for message in messages:
            text = message.get("text", "").lower()
            total_length += len(text)

            # Contar palavras positivas
            positive_count += sum(
                1 for word in self.POSITIVE_WORDS
                if word in text
            )

            # Contar palavras negativas
            negative_count += sum(
                1 for word in self.NEGATIVE_WORDS
                if word in text
            )

            # Contar emojis (aproximação)
            emoji_count += text.count("😊") + text.count("😃") + text.count("👍")
            emoji_count += text.count("❤️") + text.count("🎉") + text.count("✨")

        metrics.positive_words_count = positive_count
        metrics.negative_words_count = negative_count
        metrics.emoji_usage = emoji_count

        if len(messages) > 0:
            metrics.message_length_avg = total_length / len(messages)

        return metrics

    def _analyze_patterns(
        self,
        metrics: PsychologicalMetrics,
        history_data: Dict
    ) -> PsychologicalMetrics:
        """Analisa padrões históricos."""

        # Sequência de dias produtivos
        metrics.streak_days = history_data.get("streak_days", 0)

        # Último marco alcançado
        metrics.last_milestone = history_data.get("last_milestone")

        # Áreas de melhoria
        metrics.improvement_areas = history_data.get("improvement_areas", [])

        # Pontos fortes
        metrics.strengths = history_data.get("strengths", [])

        return metrics

    def _infer_emotional_state(
        self,
        metrics: PsychologicalMetrics
    ) -> EmotionalState:
        """
        Infere o estado emocional baseado nas métricas.

        Lógica:
        - BURNED_OUT: Baixa conclusão + Negativas >> Positivas + Baixo engajamento
        - OVERWHELMED: Muitas tarefas pendentes/bloqueadas + Stress
        - STRESSED: Negativas > Positivas
        - MOTIVATED: Alta conclusão + Alta participação + Positivas
        - DISENGAGED: Baixo engajamento + Baixa participação
        - BALANCED: Estado padrão equilibrado
        """

        # Burned out
        if (
            metrics.completion_rate < 0.3
            and metrics.negative_words_count > metrics.positive_words_count * 2
            and metrics.checkin_participation < 0.5
        ):
            return EmotionalState.BURNED_OUT

        # Overwhelmed
        if (
            metrics.tasks_pending > 10
            or metrics.tasks_blocked > 3
        ) and metrics.negative_words_count > 5:
            return EmotionalState.OVERWHELMED

        # Stressed
        if metrics.negative_words_count > metrics.positive_words_count:
            return EmotionalState.STRESSED

        # Disengaged
        if (
            metrics.checkin_participation < 0.4
            and metrics.response_time_hours > 8
        ):
            return EmotionalState.DISENGAGED

        # Motivated
        if (
            metrics.completion_rate > 0.7
            and metrics.checkin_participation > 0.8
            and metrics.positive_words_count > metrics.negative_words_count
        ):
            return EmotionalState.MOTIVATED

        # Balanced (padrão)
        return EmotionalState.BALANCED

    def _assess_burnout_risk(
        self,
        metrics: PsychologicalMetrics
    ) -> RiskLevel:
        """
        Avalia o risco de burnout.

        Indicadores:
        - Taxa de conclusão muito baixa
        - Muitas tarefas bloqueadas
        - Comunicação negativa persistente
        - Baixo engajamento
        - Tempo de resposta muito alto
        """

        risk_score = 0

        # Baixa conclusão
        if metrics.completion_rate < 0.3:
            risk_score += 3
        elif metrics.completion_rate < 0.5:
            risk_score += 1

        # Tarefas bloqueadas
        if metrics.tasks_blocked > 5:
            risk_score += 3
        elif metrics.tasks_blocked > 2:
            risk_score += 1

        # Comunicação negativa
        if metrics.negative_words_count > metrics.positive_words_count * 2:
            risk_score += 2

        # Baixo engajamento
        if metrics.checkin_participation < 0.3:
            risk_score += 2

        # Tempo de resposta alto
        if metrics.response_time_hours > 12:
            risk_score += 2

        # Classificar risco
        if risk_score >= 8:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        elif risk_score >= 1:
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE

    def _determine_energy_level(
        self,
        metrics: PsychologicalMetrics
    ) -> EnergyLevel:
        """
        Determina o nível de energia baseado em múltiplos fatores.
        """

        energy_score = 0

        # Taxa de conclusão afeta energia
        if metrics.completion_rate > 0.8:
            energy_score += 2
        elif metrics.completion_rate > 0.6:
            energy_score += 1
        elif metrics.completion_rate < 0.3:
            energy_score -= 2

        # Engajamento afeta energia
        if metrics.checkin_participation > 0.8:
            energy_score += 1
        elif metrics.checkin_participation < 0.4:
            energy_score -= 1

        # Comunicação positiva indica energia
        if metrics.positive_words_count > metrics.negative_words_count:
            energy_score += 1
        elif metrics.negative_words_count > metrics.positive_words_count:
            energy_score -= 1

        # Emojis indicam energia positiva
        if metrics.emoji_usage > 5:
            energy_score += 1

        # Tempo de resposta
        if metrics.response_time_hours < 2:
            energy_score += 1
        elif metrics.response_time_hours > 8:
            energy_score -= 1

        # Classificar energia
        if energy_score >= 4:
            return EnergyLevel.VERY_HIGH
        elif energy_score >= 2:
            return EnergyLevel.HIGH
        elif energy_score >= -1:
            return EnergyLevel.MEDIUM
        elif energy_score >= -3:
            return EnergyLevel.LOW
        else:
            return EnergyLevel.VERY_LOW

    def should_intervene(self, metrics: PsychologicalMetrics) -> bool:
        """
        Determina se uma intervenção humana/psicológica é necessária.

        Returns:
            True se intervenção é recomendada
        """
        return (
            metrics.burnout_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            or metrics.emotional_state in [EmotionalState.BURNED_OUT, EmotionalState.OVERWHELMED]
        )

    def get_intervention_suggestions(
        self,
        metrics: PsychologicalMetrics
    ) -> List[str]:
        """
        Retorna sugestões de intervenção baseadas no estado da pessoa.

        Args:
            metrics: Métricas psicológicas

        Returns:
            Lista de sugestões de intervenção
        """
        suggestions = []

        if metrics.burnout_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            suggestions.append("Reduzir carga de trabalho imediatamente")
            suggestions.append("Conversa 1:1 com líder recomendada")
            suggestions.append("Considerar dia de descanso")

        if metrics.tasks_blocked > 3:
            suggestions.append("Desbloquear tarefas prioritárias")
            suggestions.append("Pedir ajuda à equipe")

        if metrics.completion_rate < 0.4:
            suggestions.append("Reavaliar complexidade das tarefas")
            suggestions.append("Dividir tarefas em partes menores")

        if metrics.checkin_participation < 0.5:
            suggestions.append("Investigar motivo do baixo engajamento")
            suggestions.append("Ajustar horários dos check-ins")

        if not suggestions:
            suggestions.append("Continuar monitorando")

        return suggestions
