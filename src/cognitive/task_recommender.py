"""
Task Recommender - Recomendador Inteligente de Próxima Tarefa.

Baseado em carga cognitiva, recomenda qual task pegar next.
"""

import logging
from typing import List, Dict, Optional

from .load_detector import CognitiveLoadLevel

logger = logging.getLogger(__name__)


class TaskRecommender:
    """Recomenda próxima task baseado em carga cognitiva."""

    def __init__(self):
        """Inicializa o recomendador."""
        logger.info("TaskRecommender inicializado")

    def recommend_next_task(
        self,
        available_tasks: List[Dict],
        cognitive_load: CognitiveLoadLevel
    ) -> Optional[Dict]:
        """
        Recomenda próxima task baseado em carga cognitiva.

        Args:
            available_tasks: Lista de tasks disponíveis
            cognitive_load: Nível de carga cognitiva atual

        Returns:
            Task recomendada ou None
        """
        if not available_tasks:
            return None

        # Filtrar tasks baseado em carga
        if cognitive_load in [CognitiveLoadLevel.VERY_HIGH, CognitiveLoadLevel.CRITICAL]:
            # Sobrecarregado: apenas tasks fáceis/triviais
            filtered = [
                task for task in available_tasks
                if task.get("complexity", "medium") in ["trivial", "easy"]
            ]

            if not filtered:
                # Se não tem task fácil, sugerir pausa
                return None

            # Retornar a mais fácil
            return min(filtered, key=lambda t: t.get("estimated_minutes", 999))

        elif cognitive_load == CognitiveLoadLevel.HIGH:
            # Alta carga: evitar tasks muito complexas
            filtered = [
                task for task in available_tasks
                if task.get("complexity", "medium") != "very_hard"
            ]

            # Preferir tasks menores
            return min(filtered or available_tasks, key=lambda t: t.get("estimated_minutes", 999))

        elif cognitive_load in [CognitiveLoadLevel.LOW, CognitiveLoadLevel.VERY_LOW]:
            # Baixa carga: pode pegar task complexa
            hard_tasks = [
                task for task in available_tasks
                if task.get("complexity", "medium") in ["hard", "very_hard"]
            ]

            if hard_tasks:
                return hard_tasks[0]

            # Se não tem task difícil, qualquer uma serve
            return available_tasks[0]

        else:  # OPTIMAL
            # Zona ideal: task de complexidade média
            medium_tasks = [
                task for task in available_tasks
                if task.get("complexity", "medium") in ["medium", "easy"]
            ]

            return medium_tasks[0] if medium_tasks else available_tasks[0]

    def suggest_task_reorganization(
        self,
        person_name: str,
        cognitive_load: CognitiveLoadLevel,
        current_tasks: List[Dict]
    ) -> str:
        """
        Sugere reorganização de tasks baseado em carga.

        Returns:
            Mensagem com sugestão
        """
        if cognitive_load in [CognitiveLoadLevel.VERY_HIGH, CognitiveLoadLevel.CRITICAL]:
            return (
                f"Vejo que você está sobrecarregado. "
                f"Que tal fazer uma pausa de 10 minutos? 🧘\n"
                f"Depois, podemos começar com algo mais simples."
            )

        elif cognitive_load == CognitiveLoadLevel.HIGH:
            easy_tasks = [
                task for task in current_tasks
                if task.get("complexity") in ["easy", "trivial"]
            ]

            if easy_tasks:
                return (
                    f"Sinto que você está começando a sobrecarregar. "
                    f"Que tal fazer '{easy_tasks[0]['title']}'? É mais leve. 🌱"
                )

            return (
                f"Você está com muita coisa na cabeça. "
                f"Vamos focar numa task de cada vez? 🎯"
            )

        elif cognitive_load in [CognitiveLoadLevel.LOW, CognitiveLoadLevel.VERY_LOW]:
            hard_tasks = [
                task for task in current_tasks
                if task.get("complexity") in ["hard", "very_hard"]
            ]

            if hard_tasks:
                return (
                    f"Você está com energia! 💪 "
                    f"Bom momento para pegar '{hard_tasks[0]['title']}'."
                )

            return "Você tem capacidade para mais! Quer pegar uma task desafiadora?"

        return "Você está na zona ideal de performance! Continue assim! ✨"
