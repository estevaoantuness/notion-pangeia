"""
NLP Performance Monitor - Tracks NLP accuracy and collects feedback in production

Este módulo fornece tracking de performance do NLP em produção, permitindo:
- Monitoramento de confiança média por intent
- Coleta de feedback do usuário
- Identificação de padrões de falha
- Otimização contínua baseada em dados reais
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class NLPMetric:
    """Representa uma métrica de NLP registrada"""
    timestamp: float
    text: str
    intent: str
    confidence: float
    user_confirmed: Optional[bool] = None  # True: correto, False: incorreto, None: não confirmado
    corrected_intent: Optional[str] = None  # Intent correto se user_confirmed = False
    user_id: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))


class NLPMonitor:
    """
    Monitor de performance NLP com Redis backend

    Armazena métricas em Redis para análise posterior:
    - nlp_metrics:{intent} → lista de métricas por intent
    - nlp_feedback → fila de feedback do usuário
    - nlp_stats → estatísticas agregadas

    Uso:
        monitor = NLPMonitor()

        # Registrar parsing
        monitor.log_parse_result(
            text="vou criar uma tarefa",
            intent="create_task",
            confidence=0.88,
            user_id="user123"
        )

        # Registrar feedback do usuário
        monitor.log_feedback(
            text="vou criar uma tarefa",
            detected_intent="create_task",
            user_confirmed=True,
            user_id="user123"
        )
    """

    def __init__(self, redis_client: Optional[Any] = None, debug: bool = False):
        """
        Inicializar monitor

        Args:
            redis_client: Cliente Redis (se None, tenta conectar automaticamente)
            debug: Se True, log em console (não persiste em Redis)
        """
        self.redis_client = redis_client
        self.debug = debug

        # Tentar conectar ao Redis se não fornecido
        if self.redis_client is None and not self.debug and HAS_REDIS:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando modo debug.")
                self.debug = True
        elif not HAS_REDIS:
            logger.info("Redis não disponível. Usando modo debug.")
            self.debug = True

        self.metrics_cache: List[Dict[str, Any]] = []

    def log_parse_result(
        self,
        text: str,
        intent: str,
        confidence: float,
        user_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Registrar resultado de parsing

        Args:
            text: Texto original
            intent: Intent detectado
            confidence: Confiança (0-1)
            user_id: ID do usuário
            **kwargs: Dados adicionais
        """
        metric = NLPMetric(
            timestamp=datetime.now().timestamp(),
            text=text,
            intent=intent,
            confidence=confidence,
            user_id=user_id
        )

        if self.debug:
            logger.info(f"[NLP] {intent} (conf: {confidence:.2f}) → {text[:50]}")
            self.metrics_cache.append(asdict(metric))
        else:
            try:
                # Armazenar em Redis
                key = f"nlp_metrics:{intent}"
                self.redis_client.lpush(key, metric.to_json())

                # Limitar tamanho da lista (manter últimos 1000)
                self.redis_client.ltrim(key, 0, 999)

                # Atualizar stats agregadas
                self._update_stats(intent, confidence)
            except Exception as e:
                logger.error(f"Erro ao registrar métrica em Redis: {e}")

    def log_feedback(
        self,
        text: str,
        detected_intent: str,
        user_confirmed: bool,
        user_id: Optional[str] = None,
        corrected_intent: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Registrar feedback do usuário sobre parsing

        Args:
            text: Texto original
            detected_intent: Intent que foi detectado
            user_confirmed: Se o usuário confirmou que estava correto
            user_id: ID do usuário
            corrected_intent: Se confirmação=False, qual era o intent correto
        """
        metric = NLPMetric(
            timestamp=datetime.now().timestamp(),
            text=text,
            intent=detected_intent,
            confidence=0.0,  # Será preenchido depois
            user_confirmed=user_confirmed,
            corrected_intent=corrected_intent,
            user_id=user_id
        )

        if self.debug:
            status = "✓" if user_confirmed else "✗"
            correction = f" → {corrected_intent}" if corrected_intent else ""
            logger.info(f"[FEEDBACK] {status} {detected_intent}{correction}: {text[:50]}")
        else:
            try:
                # Armazenar feedback em fila separada
                self.redis_client.lpush("nlp_feedback", metric.to_json())
                self.redis_client.ltrim("nlp_feedback", 0, 999)

                # Se feedback negativo, registrar como erro
                if not user_confirmed and corrected_intent:
                    error_key = f"nlp_errors:{detected_intent}→{corrected_intent}"
                    self.redis_client.incr(error_key)
            except Exception as e:
                logger.error(f"Erro ao registrar feedback: {e}")

    def _update_stats(self, intent: str, confidence: float) -> None:
        """Atualizar estatísticas agregadas no Redis"""
        try:
            stats_key = f"nlp_stats:{intent}"
            pipe = self.redis_client.pipeline()

            # Incrementar contadores
            pipe.incr(f"{stats_key}:count")
            pipe.incr(f"{stats_key}:conf_sum")

            # Manter min/max
            # Note: Redis não tem estrutura eficiente para isso, seria melhor usar sorted sets

            pipe.execute()
        except Exception as e:
            logger.error(f"Erro ao atualizar stats: {e}")

    def get_stats(self, intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Obter estatísticas de NLP

        Args:
            intent: Se None, retorna stats de todos os intents

        Returns:
            Dict com estatísticas
        """
        if self.debug:
            return self._get_stats_from_cache(intent)

        try:
            if intent:
                # Stats para um intent específico
                key = f"nlp_stats:{intent}"
                count = int(self.redis_client.get(f"{key}:count") or 0)
                conf_sum = float(self.redis_client.get(f"{key}:conf_sum") or 0)

                return {
                    "intent": intent,
                    "count": count,
                    "avg_confidence": conf_sum / count if count > 0 else 0,
                }
            else:
                # Stats agregadas
                # Encontrar todos os intents
                keys = self.redis_client.keys("nlp_stats:*:count")
                intents = set()
                for key in keys:
                    intent_name = key.replace("nlp_stats:", "").replace(":count", "")
                    intents.add(intent_name)

                stats = {}
                for i in intents:
                    stats[i] = self.get_stats(i)

                return stats
        except Exception as e:
            logger.error(f"Erro ao obter stats: {e}")
            return {}

    def _get_stats_from_cache(self, intent: Optional[str] = None) -> Dict[str, Any]:
        """Obter stats do cache em memória (modo debug)"""
        if not self.metrics_cache:
            return {}

        if intent:
            metrics = [m for m in self.metrics_cache if m.get("intent") == intent]
        else:
            metrics = self.metrics_cache

        if not metrics:
            return {}

        confidences = [m["confidence"] for m in metrics if m.get("confidence")]

        return {
            "count": len(metrics),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "intent": intent
        }

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Obter resumo de feedback do usuário"""
        if self.debug:
            return {
                "total_feedback": len([m for m in self.metrics_cache if m.get("user_confirmed") is not None]),
                "correct": len([m for m in self.metrics_cache if m.get("user_confirmed") is True]),
                "incorrect": len([m for m in self.metrics_cache if m.get("user_confirmed") is False]),
            }

        try:
            feedback = self.redis_client.lrange("nlp_feedback", 0, -1)
            total = len(feedback)
            correct = sum(1 for f in feedback if NLPMetric.from_json(f).user_confirmed is True)
            incorrect = total - correct

            return {
                "total_feedback": total,
                "correct": correct,
                "incorrect": incorrect,
                "accuracy": correct / total * 100 if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Erro ao obter resumo de feedback: {e}")
            return {}


# Instância global para uso facilitado
_monitor: Optional[NLPMonitor] = None


def get_monitor(debug: bool = False) -> NLPMonitor:
    """Obter instância global do monitor"""
    global _monitor
    if _monitor is None:
        _monitor = NLPMonitor(debug=debug)
    return _monitor


def log_parse(text: str, intent: str, confidence: float, user_id: Optional[str] = None) -> None:
    """Shortcut para log_parse_result"""
    get_monitor().log_parse_result(text, intent, confidence, user_id)


def log_feedback(
    text: str,
    detected_intent: str,
    user_confirmed: bool,
    user_id: Optional[str] = None,
    corrected_intent: Optional[str] = None
) -> None:
    """Shortcut para log_feedback"""
    get_monitor().log_feedback(text, detected_intent, user_confirmed, user_id, corrected_intent)
