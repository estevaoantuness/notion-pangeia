"""
Cognitive Load Detector - Detector de Carga Cognitiva em Tempo Real.

Detecta sinais de sobrecarga cognitiva analisando:
- Padrões de resposta (velocidade, tamanho de mensagens)
- Comportamento com tasks (bloqueios, tempo entre ações)
- Linguagem (palavras de stress, confusão)
- Contexto temporal (hora do dia, tempo trabalhando)
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CognitiveLoadLevel(Enum):
    """Níveis de carga cognitiva."""
    VERY_LOW = "very_low"  # Sub-utilizado, pode pegar task mais complexa
    LOW = "low"  # Bom momento para tasks complexas
    OPTIMAL = "optimal"  # Zona ideal de performance
    HIGH = "high"  # Começando a sobrecarregar
    VERY_HIGH = "very_high"  # Sobrecarregado, precisa de pausa
    CRITICAL = "critical"  # Exausto, precisa parar


@dataclass
class CognitiveLoadMetrics:
    """Métricas de carga cognitiva."""

    # Métricas de resposta
    avg_response_time_seconds: float = 0.0
    response_time_trend: str = "stable"  # increasing, decreasing, stable
    message_length_avg: int = 0
    message_length_trend: str = "stable"

    # Métricas de tasks
    tasks_blocked_recently: int = 0
    time_since_last_completion_hours: float = 0.0
    consecutive_failures: int = 0
    task_switching_rate: float = 0.0  # Mudanças de task por hora

    # Métricas de linguagem
    confusion_indicators: int = 0  # "não sei", "confuso", etc
    stress_indicators: int = 0  # "difícil", "impossível", "travado"
    frustration_indicators: int = 0  # "droga", "não consigo", etc

    # Métricas temporais
    hours_working_today: float = 0.0
    time_since_last_break_minutes: float = 0.0

    # Score final
    cognitive_load_level: CognitiveLoadLevel = CognitiveLoadLevel.OPTIMAL
    confidence: float = 0.5  # 0-1


class CognitiveLoadDetector:
    """
    Detector de carga cognitiva em tempo real.

    Analisa múltiplos sinais para determinar se pessoa está sobrecarregada.
    """

    # Palavras que indicam confusão
    CONFUSION_WORDS = {
        "não sei", "não entendo", "confuso", "perdido", "não faço ideia",
        "como", "o que", "qual", "onde", "quando", "por que",
        "help", "ajuda", "não consigo entender", "complicado"
    }

    # Palavras que indicam stress
    STRESS_WORDS = {
        "difícil", "complicado", "impossível", "muito", "demais",
        "sobrecarregado", "estressado", "cansado", "exausto",
        "travado", "bloqueado", "stuck", "não aguento"
    }

    # Palavras que indicam frustração
    FRUSTRATION_WORDS = {
        "droga", "caramba", "porra", "merda", "frustrado",
        "irritado", "chato", "saco", "não consigo", "não dá",
        "desistir", "give up", "quit"
    }

    def __init__(self):
        """Inicializa o detector."""
        self.history: Dict[str, List[Dict]] = {}  # {person_name: [eventos]}
        logger.info("CognitiveLoadDetector inicializado")

    def detect_load(
        self,
        person_name: str,
        recent_messages: List[Dict],
        task_data: Dict,
        context: Optional[Dict] = None
    ) -> CognitiveLoadMetrics:
        """
        Detecta carga cognitiva atual da pessoa.

        Args:
            person_name: Nome da pessoa
            recent_messages: Mensagens recentes (últimas 10)
            task_data: Dados de tasks atuais
            context: Contexto adicional

        Returns:
            Métricas de carga cognitiva
        """
        context = context or {}
        metrics = CognitiveLoadMetrics()

        # Analisar padrões de resposta
        if recent_messages:
            metrics = self._analyze_response_patterns(metrics, recent_messages)

        # Analisar comportamento com tasks
        metrics = self._analyze_task_behavior(metrics, task_data)

        # Analisar linguagem
        if recent_messages:
            metrics = self._analyze_language(metrics, recent_messages)

        # Analisar contexto temporal
        metrics = self._analyze_temporal_context(metrics, person_name)

        # Calcular nível de carga cognitiva
        metrics.cognitive_load_level, metrics.confidence = self._calculate_load_level(metrics)

        # Registrar no histórico
        self._record_measurement(person_name, metrics)

        logger.info(
            f"Carga cognitiva de {person_name}: {metrics.cognitive_load_level.value} "
            f"(confiança: {metrics.confidence * 100:.0f}%)"
        )

        return metrics

    def _analyze_response_patterns(
        self,
        metrics: CognitiveLoadMetrics,
        messages: List[Dict]
    ) -> CognitiveLoadMetrics:
        """Analisa padrões de resposta (velocidade, tamanho)."""

        # Calcular tempo médio de resposta
        response_times = []
        for i in range(1, len(messages)):
            prev_time = datetime.fromisoformat(messages[i-1].get("timestamp", datetime.now().isoformat()))
            curr_time = datetime.fromisoformat(messages[i].get("timestamp", datetime.now().isoformat()))

            delta = (curr_time - prev_time).total_seconds()
            if delta < 600:  # Menos de 10min (mesmo contexto)
                response_times.append(delta)

        if response_times:
            metrics.avg_response_time_seconds = sum(response_times) / len(response_times)

            # Trend: últimos 3 vs primeiros 3
            if len(response_times) >= 6:
                first_half = sum(response_times[:3]) / 3
                second_half = sum(response_times[-3:]) / 3

                if second_half > first_half * 1.5:
                    metrics.response_time_trend = "increasing"  # Ficando mais lento = sobrecarga
                elif second_half < first_half * 0.7:
                    metrics.response_time_trend = "decreasing"
                else:
                    metrics.response_time_trend = "stable"

        # Tamanho das mensagens
        message_lengths = [
            len(msg.get("text", ""))
            for msg in messages
        ]

        if message_lengths:
            metrics.message_length_avg = int(sum(message_lengths) / len(message_lengths))

            # Trend
            if len(message_lengths) >= 6:
                first_half = sum(message_lengths[:3]) / 3
                second_half = sum(message_lengths[-3:]) / 3

                if second_half < first_half * 0.5:
                    metrics.message_length_trend = "decreasing"  # Mensagens curtas = stress
                elif second_half > first_half * 1.5:
                    metrics.message_length_trend = "increasing"
                else:
                    metrics.message_length_trend = "stable"

        return metrics

    def _analyze_task_behavior(
        self,
        metrics: CognitiveLoadMetrics,
        task_data: Dict
    ) -> CognitiveLoadMetrics:
        """Analisa comportamento com tasks."""

        # Tasks bloqueadas recentemente
        metrics.tasks_blocked_recently = task_data.get("tasks_blocked", 0)

        # Tempo desde última conclusão
        last_completion = task_data.get("last_completion_time")
        if last_completion:
            delta = datetime.now() - datetime.fromisoformat(last_completion)
            metrics.time_since_last_completion_hours = delta.total_seconds() / 3600

        # Falhas consecutivas
        metrics.consecutive_failures = task_data.get("consecutive_failures", 0)

        # Taxa de switching
        task_switches = task_data.get("task_switches_last_hour", 0)
        metrics.task_switching_rate = task_switches

        return metrics

    def _analyze_language(
        self,
        metrics: CognitiveLoadMetrics,
        messages: List[Dict]
    ) -> CognitiveLoadMetrics:
        """Analisa linguagem para detectar confusão/stress."""

        # Combinar todas as mensagens
        all_text = " ".join(msg.get("text", "").lower() for msg in messages)

        # Contar indicadores
        metrics.confusion_indicators = sum(
            1 for word in self.CONFUSION_WORDS
            if word in all_text
        )

        metrics.stress_indicators = sum(
            1 for word in self.STRESS_WORDS
            if word in all_text
        )

        metrics.frustration_indicators = sum(
            1 for word in self.FRUSTRATION_WORDS
            if word in all_text
        )

        return metrics

    def _analyze_temporal_context(
        self,
        metrics: CognitiveLoadMetrics,
        person_name: str
    ) -> CognitiveLoadMetrics:
        """Analisa contexto temporal (horas trabalhando, última pausa)."""

        # Buscar histórico da pessoa
        if person_name not in self.history:
            return metrics

        history = self.history[person_name]

        # Calcular horas trabalhando hoje
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_events = [
            event for event in history
            if datetime.fromisoformat(event["timestamp"]) > today_start
        ]

        if today_events:
            first_event = datetime.fromisoformat(today_events[0]["timestamp"])
            hours_working = (datetime.now() - first_event).total_seconds() / 3600
            metrics.hours_working_today = hours_working

        # Tempo desde última pausa (aproximação)
        if history:
            last_event = datetime.fromisoformat(history[-1]["timestamp"])
            minutes_since = (datetime.now() - last_event).total_seconds() / 60
            metrics.time_since_last_break_minutes = minutes_since

        return metrics

    def _calculate_load_level(
        self,
        metrics: CognitiveLoadMetrics
    ) -> tuple[CognitiveLoadLevel, float]:
        """
        Calcula nível de carga cognitiva baseado em métricas.

        Returns:
            (CognitiveLoadLevel, confidence)
        """
        score = 0.0
        weights = []

        # Fator 1: Response time (20%)
        if metrics.avg_response_time_seconds > 0:
            if metrics.avg_response_time_seconds > 60:
                score += 0.8  # Muito lento
                weights.append(0.20)
            elif metrics.avg_response_time_seconds > 30:
                score += 0.6
                weights.append(0.20)
            elif metrics.avg_response_time_seconds < 5:
                score += 0.2  # Muito rápido pode indicar sub-utilização
                weights.append(0.20)
            else:
                score += 0.4  # Optimal
                weights.append(0.20)

        # Fator 2: Response time trend (15%)
        if metrics.response_time_trend == "increasing":
            score += 0.7
            weights.append(0.15)
        elif metrics.response_time_trend == "stable":
            score += 0.4
            weights.append(0.15)

        # Fator 3: Tasks bloqueadas (20%)
        if metrics.tasks_blocked_recently > 3:
            score += 0.9
            weights.append(0.20)
        elif metrics.tasks_blocked_recently > 1:
            score += 0.6
            weights.append(0.20)
        elif metrics.tasks_blocked_recently == 0:
            score += 0.3
            weights.append(0.20)

        # Fator 4: Indicadores de linguagem (25%)
        total_stress = (
            metrics.confusion_indicators +
            metrics.stress_indicators +
            metrics.frustration_indicators
        )

        if total_stress > 5:
            score += 0.9
            weights.append(0.25)
        elif total_stress > 2:
            score += 0.7
            weights.append(0.25)
        elif total_stress > 0:
            score += 0.5
            weights.append(0.25)
        else:
            score += 0.3
            weights.append(0.25)

        # Fator 5: Tempo trabalhando (20%)
        if metrics.hours_working_today > 8:
            score += 0.8
            weights.append(0.20)
        elif metrics.hours_working_today > 5:
            score += 0.6
            weights.append(0.20)
        elif metrics.hours_working_today > 2:
            score += 0.4
            weights.append(0.20)
        else:
            score += 0.2
            weights.append(0.20)

        # Normalizar score
        if weights:
            normalized_score = score / sum(weights)
        else:
            normalized_score = 0.5

        # Mapear para nível
        if normalized_score < 0.25:
            level = CognitiveLoadLevel.VERY_LOW
        elif normalized_score < 0.4:
            level = CognitiveLoadLevel.LOW
        elif normalized_score < 0.6:
            level = CognitiveLoadLevel.OPTIMAL
        elif normalized_score < 0.75:
            level = CognitiveLoadLevel.HIGH
        elif normalized_score < 0.9:
            level = CognitiveLoadLevel.VERY_HIGH
        else:
            level = CognitiveLoadLevel.CRITICAL

        # Confidence baseado em quantidade de dados
        confidence = min(len(weights) / 5.0, 1.0)

        return level, confidence

    def _record_measurement(
        self,
        person_name: str,
        metrics: CognitiveLoadMetrics
    ) -> None:
        """Registra medição no histórico."""
        if person_name not in self.history:
            self.history[person_name] = []

        self.history[person_name].append({
            "timestamp": datetime.now().isoformat(),
            "level": metrics.cognitive_load_level.value,
            "confidence": metrics.confidence
        })

        # Limitar histórico a últimos 100 eventos
        if len(self.history[person_name]) > 100:
            self.history[person_name] = self.history[person_name][-100:]

    def get_load_trend(
        self,
        person_name: str,
        hours: int = 4
    ) -> Dict:
        """
        Retorna tendência de carga cognitiva nas últimas N horas.

        Args:
            person_name: Nome da pessoa
            hours: Número de horas para analisar

        Returns:
            Dict com análise de tendência
        """
        if person_name not in self.history:
            return {"trend": "unknown", "measurements": 0}

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            event for event in self.history[person_name]
            if datetime.fromisoformat(event["timestamp"]) > cutoff
        ]

        if len(recent) < 2:
            return {"trend": "insufficient_data", "measurements": len(recent)}

        # Comparar primeira metade vs segunda metade
        mid = len(recent) // 2
        first_half_avg = sum(
            self._level_to_score(event["level"])
            for event in recent[:mid]
        ) / mid

        second_half_avg = sum(
            self._level_to_score(event["level"])
            for event in recent[mid:]
        ) / (len(recent) - mid)

        if second_half_avg > first_half_avg * 1.2:
            trend = "increasing"  # Piorando
        elif second_half_avg < first_half_avg * 0.8:
            trend = "decreasing"  # Melhorando
        else:
            trend = "stable"

        return {
            "trend": trend,
            "measurements": len(recent),
            "current_avg": second_half_avg,
            "previous_avg": first_half_avg
        }

    def _level_to_score(self, level_str: str) -> float:
        """Converte nível para score numérico."""
        mapping = {
            "very_low": 0.1,
            "low": 0.3,
            "optimal": 0.5,
            "high": 0.7,
            "very_high": 0.85,
            "critical": 1.0
        }
        return mapping.get(level_str, 0.5)
