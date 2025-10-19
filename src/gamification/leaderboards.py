"""
Leaderboard System - Rankings e Competições.

Sistema de rankings time-wise para motivação saudável.
"""

import logging
from enum import Enum
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LeaderboardPeriod(Enum):
    """Períodos de leaderboard."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class Leaderboard:
    """Sistema de leaderboards."""

    def __init__(self):
        """Inicializa o sistema de leaderboards."""
        self.scores: Dict[str, Dict[str, int]] = {}
        logger.info("Leaderboard inicializado")

    def update_score(
        self,
        person_name: str,
        metric: str,
        value: int,
        period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME
    ) -> None:
        """Atualiza score de um jogador."""
        key = f"{period.value}:{metric}"

        if key not in self.scores:
            self.scores[key] = {}

        if person_name not in self.scores[key]:
            self.scores[key][person_name] = 0

        self.scores[key][person_name] += value

    def get_leaderboard(
        self,
        metric: str,
        period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME,
        limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Retorna leaderboard ordenado.

        Returns:
            Lista de (person_name, score) ordenada
        """
        key = f"{period.value}:{metric}"

        if key not in self.scores:
            return []

        # Ordenar por score (maior primeiro)
        sorted_scores = sorted(
            self.scores[key].items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_scores[:limit]

    def get_player_rank(
        self,
        person_name: str,
        metric: str,
        period: LeaderboardPeriod = LeaderboardPeriod.ALL_TIME
    ) -> Tuple[int, int]:
        """
        Retorna posição e score do jogador.

        Returns:
            (rank, score)
        """
        leaderboard = self.get_leaderboard(metric, period, limit=1000)

        for idx, (name, score) in enumerate(leaderboard, 1):
            if name == person_name:
                return idx, score

        return 0, 0  # Não encontrado

    def format_leaderboard(
        self,
        metric: str,
        period: LeaderboardPeriod = LeaderboardPeriod.WEEKLY,
        limit: int = 10
    ) -> str:
        """Formata leaderboard para display."""
        leaderboard = self.get_leaderboard(metric, period, limit)

        if not leaderboard:
            return f"📊 Leaderboard ({metric}) - Nenhum dado ainda"

        period_name = {
            "daily": "Hoje",
            "weekly": "Esta Semana",
            "monthly": "Este Mês",
            "all_time": "Todos os Tempos"
        }.get(period.value, period.value)

        lines = [f"🏆 **Top {limit} - {metric.title()}** ({period_name})\n"]

        medals = ["🥇", "🥈", "🥉"]

        for idx, (name, score) in enumerate(leaderboard, 1):
            medal = medals[idx - 1] if idx <= 3 else f"{idx}."
            lines.append(f"{medal} **{name}** - {score:,} pontos")

        return "\n".join(lines)

    def reset_period(self, period: LeaderboardPeriod) -> None:
        """Reseta scores de um período."""
        keys_to_reset = [
            key for key in self.scores.keys()
            if key.startswith(f"{period.value}:")
        ]

        for key in keys_to_reset:
            self.scores[key] = {}

        logger.info(f"Leaderboard resetado: {period.value}")
