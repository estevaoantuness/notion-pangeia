"""
Feature Extractor - Extração de Features para ML.

Extrai e prepara features de dados brutos para modelos ML.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extrai features para modelos ML."""

    def __init__(self):
        """Inicializa o extrator."""
        logger.info("FeatureExtractor inicializado")

    def extract_temporal_features(
        self,
        person_name: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Extrai features temporais dos últimos N dias.

        Returns:
            Lista de dicts com métricas por dia
        """
        # Mock - em produção, buscar de database
        historical = []

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            historical.append({
                "date": date.isoformat(),
                "completion_rate": 0.7 - (i * 0.05),  # Simulando declínio
                "energy_level": "medium",
                "cognitive_load": "optimal",
                "tasks_blocked": i,
                "hours_working_today": 8
            })

        return historical

    def prepare_for_prediction(
        self,
        current_metrics: Dict,
        historical_data: List[Dict]
    ) -> Dict:
        """Prepara dados para predição."""
        return {
            "current": current_metrics,
            "history": historical_data,
            "features_extracted": True
        }
