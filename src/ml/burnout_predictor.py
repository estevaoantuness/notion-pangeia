"""
Burnout Predictor - Preditor de Burnout com 7 Dias de Antecedência.

Usa ML simples para prever burnout baseado em séries temporais de métricas.
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Níveis de risco de burnout."""
    NONE = "none"  # <10% chance
    LOW = "low"  # 10-30%
    MEDIUM = "medium"  # 30-50%
    HIGH = "high"  # 50-70%
    CRITICAL = "critical"  # >70%


@dataclass
class BurnoutPrediction:
    """Predição de burnout."""
    person_name: str
    risk_level: RiskLevel
    probability: float  # 0-100%
    days_until_burnout: int  # Estimativa
    confidence: float  # 0-1
    risk_factors: List[str]
    protective_factors: List[str]
    recommendations: List[str]


class BurnoutPredictor:
    """
    Preditor de burnout com 7 dias de antecedência.

    Analisa séries temporais de:
    - Completion rate (7 dias)
    - Energy level (7 dias)
    - Carga cognitiva (7 dias)
    - Tasks bloqueadas
    - Padrões de sono/trabalho
    """

    def __init__(self):
        """Inicializa o preditor."""
        self.history: Dict[str, List[Dict]] = {}
        logger.info("BurnoutPredictor inicializado")

    def predict_burnout(
        self,
        person_name: str,
        current_metrics: Dict,
        historical_data: List[Dict]
    ) -> BurnoutPrediction:
        """
        Prediz risco de burnout nos próximos 7 dias.

        Args:
            person_name: Nome da pessoa
            current_metrics: Métricas atuais
            historical_data: Últimos 7-14 dias de dados

        Returns:
            Predição de burnout
        """
        # Extrair features
        features = self._extract_features(current_metrics, historical_data)

        # Calcular score de risco
        risk_score = self._calculate_risk_score(features)

        # Classificar risco
        risk_level, probability = self._classify_risk(risk_score)

        # Calcular dias até burnout
        days_until = self._estimate_days_until_burnout(features, risk_score)

        # Identificar fatores de risco
        risk_factors = self._identify_risk_factors(features)

        # Identificar fatores protetivos
        protective_factors = self._identify_protective_factors(features)

        # Gerar recomendações
        recommendations = self._generate_recommendations(risk_level, risk_factors)

        # Calcular confiança
        confidence = self._calculate_confidence(historical_data)

        prediction = BurnoutPrediction(
            person_name=person_name,
            risk_level=risk_level,
            probability=probability,
            days_until_burnout=days_until,
            confidence=confidence,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            recommendations=recommendations
        )

        logger.info(
            f"Predição para {person_name}: {risk_level.value} "
            f"({probability:.0f}% em {days_until} dias)"
        )

        return prediction

    def _extract_features(
        self,
        current: Dict,
        history: List[Dict]
    ) -> Dict:
        """Extrai features para predição."""
        features = {}

        # Feature 1: Tendência de completion_rate
        if history:
            completion_rates = [d.get("completion_rate", 0.5) for d in history]
            features["completion_trend"] = self._calculate_trend(completion_rates)
            features["completion_variance"] = self._calculate_variance(completion_rates)
            features["completion_current"] = current.get("completion_rate", 0.5)

        # Feature 2: Tendência de energia
        if history:
            energy_scores = [self._energy_to_score(d.get("energy_level", "medium")) for d in history]
            features["energy_trend"] = self._calculate_trend(energy_scores)
            features["energy_current"] = self._energy_to_score(current.get("energy_level", "medium"))

        # Feature 3: Carga cognitiva
        if history:
            cognitive_scores = [self._cognitive_to_score(d.get("cognitive_load", "optimal")) for d in history]
            features["cognitive_trend"] = self._calculate_trend(cognitive_scores)
            features["cognitive_current"] = self._cognitive_to_score(current.get("cognitive_load", "optimal"))

        # Feature 4: Tasks bloqueadas (crescendo?)
        features["tasks_blocked_current"] = current.get("tasks_blocked", 0)

        if history:
            blocked_counts = [d.get("tasks_blocked", 0) for d in history]
            features["blocked_trend"] = self._calculate_trend(blocked_counts)

        # Feature 5: Horas trabalhando
        features["hours_working"] = current.get("hours_working_today", 0)

        # Feature 6: Dias consecutivos sem pausa
        features["days_no_break"] = current.get("days_without_rest", 0)

        # Feature 7: Streak atual (proteção)
        features["current_streak"] = current.get("streak_days", 0)

        return features

    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calcula tendência (positiva ou negativa).

        Returns:
            -1.0 (declinando forte) a +1.0 (crescendo forte)
        """
        if len(values) < 2:
            return 0.0

        # Regressão linear simples
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalizar para -1 a +1
        return max(-1.0, min(1.0, slope * 10))

    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula variância (instabilidade)."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance

    def _energy_to_score(self, level: str) -> float:
        """Converte nível de energia para score."""
        mapping = {
            "very_low": 0.1,
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "very_high": 0.9
        }
        return mapping.get(level, 0.5)

    def _cognitive_to_score(self, load: str) -> float:
        """Converte carga cognitiva para score (menor = pior)."""
        mapping = {
            "critical": 0.0,
            "very_high": 0.2,
            "high": 0.4,
            "optimal": 0.8,
            "low": 0.9,
            "very_low": 1.0
        }
        return mapping.get(load, 0.5)

    def _calculate_risk_score(self, features: Dict) -> float:
        """
        Calcula score de risco (0-100).

        Maior = mais risco de burnout.
        """
        score = 0.0

        # Fator 1: Completion rate declinando (peso 25%)
        if "completion_trend" in features:
            if features["completion_trend"] < -0.3:  # Declinando
                score += 25
            elif features["completion_trend"] < 0:
                score += 15

        # Completion rate atual baixa
        if features.get("completion_current", 1.0) < 0.4:
            score += 10

        # Fator 2: Energia declinando (peso 20%)
        if "energy_trend" in features:
            if features["energy_trend"] < -0.3:
                score += 20
            elif features["energy_trend"] < 0:
                score += 10

        if features.get("energy_current", 0.5) < 0.3:
            score += 10

        # Fator 3: Carga cognitiva crescendo (peso 20%)
        if "cognitive_trend" in features:
            if features["cognitive_trend"] < -0.3:  # Piorando (score baixo = alta carga)
                score += 20
            elif features["cognitive_trend"] < 0:
                score += 10

        if features.get("cognitive_current", 0.5) < 0.3:
            score += 10

        # Fator 4: Tasks bloqueadas crescendo (peso 15%)
        if features.get("tasks_blocked_current", 0) > 3:
            score += 10

        if features.get("blocked_trend", 0) > 0.3:
            score += 5

        # Fator 5: Horas trabalhando excessivas (peso 10%)
        hours = features.get("hours_working", 0)
        if hours > 10:
            score += 10
        elif hours > 8:
            score += 5

        # Fator 6: Dias sem pausa (peso 10%)
        days_no_break = features.get("days_no_break", 0)
        if days_no_break > 7:
            score += 10
        elif days_no_break > 3:
            score += 5

        # Fatores protetivos (reduzem risco)
        streak = features.get("current_streak", 0)
        if streak > 7:
            score -= 10  # Streak forte = proteção
        elif streak > 3:
            score -= 5

        return max(0, min(100, score))

    def _classify_risk(self, score: float) -> Tuple[RiskLevel, float]:
        """Classifica risco baseado em score."""
        if score < 20:
            return RiskLevel.NONE, score
        elif score < 40:
            return RiskLevel.LOW, score
        elif score < 60:
            return RiskLevel.MEDIUM, score
        elif score < 80:
            return RiskLevel.HIGH, score
        else:
            return RiskLevel.CRITICAL, score

    def _estimate_days_until_burnout(self, features: Dict, risk_score: float) -> int:
        """Estima dias até burnout."""
        if risk_score < 20:
            return 14  # Baixo risco, ~2 semanas
        elif risk_score < 40:
            return 10
        elif risk_score < 60:
            return 7
        elif risk_score < 80:
            return 3
        else:
            return 1  # Crítico, iminente

    def _identify_risk_factors(self, features: Dict) -> List[str]:
        """Identifica fatores de risco."""
        factors = []

        if features.get("completion_trend", 0) < -0.3:
            factors.append("📉 Taxa de conclusão caindo consistentemente")

        if features.get("energy_trend", 0) < -0.3:
            factors.append("⚡ Energia declinando nos últimos dias")

        if features.get("cognitive_current", 0.5) < 0.3:
            factors.append("🧠 Sobrecarga cognitiva crítica")

        if features.get("tasks_blocked_current", 0) > 3:
            factors.append("🚫 Múltiplas tasks bloqueadas")

        if features.get("hours_working", 0) > 10:
            factors.append("⏰ Horas de trabalho excessivas")

        if features.get("days_no_break", 0) > 7:
            factors.append("😰 Sem pausas há mais de 1 semana")

        return factors

    def _identify_protective_factors(self, features: Dict) -> List[str]:
        """Identifica fatores protetivos."""
        factors = []

        if features.get("current_streak", 0) > 7:
            factors.append("🔥 Streak forte indica resiliência")

        if features.get("completion_current", 0) > 0.7:
            factors.append("✅ Alta taxa de conclusão atual")

        if features.get("energy_current", 0.5) > 0.7:
            factors.append("⚡ Boa energia atual")

        if features.get("cognitive_current", 0.5) > 0.7:
            factors.append("🧠 Carga cognitiva saudável")

        return factors

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[str]
    ) -> List[str]:
        """Gera recomendações baseadas em risco."""
        recs = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recs.append("🚨 URGENTE: Reduzir carga de trabalho IMEDIATAMENTE")
            recs.append("💬 Conversa 1:1 com líder recomendada HOJE")
            recs.append("🏖️ Considerar dia de descanso nos próximos 2 dias")

        elif risk_level == RiskLevel.MEDIUM:
            recs.append("⚠️ Atenção: Monitorar de perto nos próximos dias")
            recs.append("☕ Aumentar frequência de pausas")
            recs.append("📅 Reavaliar prioridades e reduzir tasks não-essenciais")

        elif risk_level == RiskLevel.LOW:
            recs.append("👀 Acompanhar tendências")
            recs.append("🧘 Manter práticas de autocuidado")

        # Recomendações específicas por fator
        for factor in risk_factors:
            if "conclusão caindo" in factor:
                recs.append("📊 Investigar causa da queda de produtividade")
            elif "bloqueadas" in factor:
                recs.append("🔓 Priorizar desbloquear tasks")
            elif "horas excessivas" in factor:
                recs.append("⏰ Limitar jornada a 8h por dia")

        return recs

    def _calculate_confidence(self, history: List[Dict]) -> float:
        """Calcula confiança da predição."""
        if len(history) < 3:
            return 0.3  # Dados insuficientes
        elif len(history) < 7:
            return 0.6
        else:
            return 0.9  # Dados completos

    def format_prediction(self, prediction: BurnoutPrediction) -> str:
        """Formata predição para display."""
        risk_emoji = {
            "none": "✅",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "🚨"
        }

        emoji = risk_emoji.get(prediction.risk_level.value, "⚠️")

        lines = [
            f"{emoji} **PREDIÇÃO DE BURNOUT - {prediction.person_name}**\n",
            f"📊 Risco: **{prediction.risk_level.value.upper()}** ({prediction.probability:.0f}%)",
            f"⏰ Estimativa: **{prediction.days_until_burnout} dias**",
            f"🎯 Confiança: {int(prediction.confidence * 100)}%\n"
        ]

        if prediction.risk_factors:
            lines.append("⚠️ **Fatores de Risco:**")
            for factor in prediction.risk_factors:
                lines.append(f"  • {factor}")
            lines.append("")

        if prediction.protective_factors:
            lines.append("💪 **Fatores Protetivos:**")
            for factor in prediction.protective_factors:
                lines.append(f"  • {factor}")
            lines.append("")

        if prediction.recommendations:
            lines.append("💡 **Recomendações:**")
            for rec in prediction.recommendations:
                lines.append(f"  • {rec}")

        return "\n".join(lines)
