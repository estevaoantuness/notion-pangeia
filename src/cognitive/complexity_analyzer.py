"""
Task Complexity Analyzer - Analisador de Complexidade de Tarefas.

Analisa tasks e classifica complexidade para matching com carga cognitiva.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class TaskComplexityAnalyzer:
    """Analisa complexidade de tasks."""

    def __init__(self):
        """Inicializa o analisador."""
        logger.info("TaskComplexityAnalyzer inicializado")

    def analyze_task_complexity(
        self,
        task_description: str,
        estimated_hours: float = 0.0
    ) -> str:
        """
        Analisa e classifica complexidade de uma task.

        Args:
            task_description: Descrição da task
            estimated_hours: Estimativa de horas (opcional)

        Returns:
            Complexidade: trivial, easy, medium, hard, very_hard
        """
        text = task_description.lower()

        # Heurística baseada em estimativa de tempo
        if estimated_hours > 0:
            if estimated_hours < 0.25:
                return "trivial"
            elif estimated_hours < 1:
                return "easy"
            elif estimated_hours < 4:
                return "medium"
            elif estimated_hours < 8:
                return "hard"
            else:
                return "very_hard"

        # Heurística baseada em palavras-chave
        complex_indicators = [
            "arquitetura", "design", "sistema", "completo",
            "integração", "refatoração", "otimização",
            "pesquisa", "investigação", "análise"
        ]

        easy_indicators = [
            "simples", "rápido", "pequeno", "ajuste",
            "fix", "correção", "update", "atualizar"
        ]

        complex_count = sum(1 for word in complex_indicators if word in text)
        easy_count = sum(1 for word in easy_indicators if word in text)

        if complex_count > easy_count:
            return "hard" if complex_count > 2 else "medium"

        if easy_count > 0:
            return "easy"

        # Default
        return "medium"

    def estimate_cognitive_cost(
        self,
        task: Dict
    ) -> float:
        """
        Estima custo cognitivo de uma task (0-1).

        Args:
            task: Dict com info da task

        Returns:
            Score de custo cognitivo
        """
        complexity = task.get("complexity", "medium")

        mapping = {
            "trivial": 0.1,
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.75,
            "very_hard": 0.95
        }

        return mapping.get(complexity, 0.5)
