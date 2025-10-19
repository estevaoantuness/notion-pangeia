"""
Leveling System - Sistema de XP e Níveis.

Gerencia progressão de níveis baseado em XP acumulado.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class PlayerLevel:
    """Nível de um jogador."""
    level: int
    current_xp: int
    xp_for_next_level: int
    total_xp: int
    tier: str  # Iniciante, Profissional, Expert, Legend


class LevelingSystem:
    """Sistema de níveis e XP."""

    # XP necessário para cada nível (exponencial)
    XP_CURVE = [
        0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700,  # 1-10
        3300, 4000, 4800, 5700, 6700, 7800, 9000, 10300, 11700, 13200,  # 11-20
        15000, 17000, 19200, 21600, 24200, 27000, 30000, 33200, 36600, 40200,  # 21-30
        44000, 48000, 52200, 56600, 61200, 66000, 71000, 76200, 81600, 87200,  # 31-40
        93000, 99000, 105200, 111600, 118200, 125000, 132000, 139200, 146600, 154200,  # 41-50
    ] + [154200 + i * 10000 for i in range(1, 51)]  # 51-100

    def __init__(self):
        """Inicializa o sistema de níveis."""
        logger.info("LevelingSystem inicializado")

    def calculate_level(self, total_xp: int) -> PlayerLevel:
        """Calcula nível baseado em XP total."""
        level = 1

        for i, xp_required in enumerate(self.XP_CURVE):
            if total_xp >= xp_required:
                level = i + 1
            else:
                break

        # XP atual no nível
        xp_current_level = self.XP_CURVE[level - 1] if level > 1 else 0
        current_xp = total_xp - xp_current_level

        # XP para próximo nível
        if level < len(self.XP_CURVE):
            xp_for_next = self.XP_CURVE[level] - xp_current_level
        else:
            xp_for_next = 10000  # Após nível máximo

        # Tier
        if level < 10:
            tier = "Iniciante"
        elif level < 25:
            tier = "Profissional"
        elif level < 50:
            tier = "Expert"
        else:
            tier = "Legend"

        return PlayerLevel(
            level=level,
            current_xp=current_xp,
            xp_for_next_level=xp_for_next,
            total_xp=total_xp,
            tier=tier
        )

    def format_level_display(self, player_level: PlayerLevel) -> str:
        """Formata display de nível."""
        progress_pct = int((player_level.current_xp / player_level.xp_for_next_level) * 100)
        bar_length = 20
        filled = int((progress_pct / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        return (
            f"🎖️ **Nível {player_level.level}** - {player_level.tier}\n"
            f"💎 XP: {player_level.current_xp}/{player_level.xp_for_next_level}\n"
            f"[{bar}] {progress_pct}%\n"
            f"📊 Total XP: {player_level.total_xp:,}"
        )
