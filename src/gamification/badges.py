"""
Badge System - Sistema de Badges e Milestones.

Gerencia badges conquistados e milestones alcançados.
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BadgeRarity(Enum):
    """Raridade de badges."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Badge:
    """Representa um badge."""
    id: str
    name: str
    emoji: str
    description: str
    rarity: BadgeRarity
    earned_at: datetime


class BadgeSystem:
    """Sistema de badges."""

    def __init__(self):
        """Inicializa o sistema de badges."""
        self.player_badges: Dict[str, List[Badge]] = {}
        logger.info("BadgeSystem inicializado")

    def award_badge(
        self,
        person_name: str,
        badge_id: str,
        badge_name: str,
        emoji: str,
        description: str,
        rarity: BadgeRarity
    ) -> Badge:
        """Concede um badge a um jogador."""
        badge = Badge(
            id=badge_id,
            name=badge_name,
            emoji=emoji,
            description=description,
            rarity=rarity,
            earned_at=datetime.now()
        )

        if person_name not in self.player_badges:
            self.player_badges[person_name] = []

        self.player_badges[person_name].append(badge)

        logger.info(f"{emoji} {person_name} ganhou badge: {badge_name}")

        return badge

    def get_player_badges(self, person_name: str) -> List[Badge]:
        """Retorna badges de um jogador."""
        return self.player_badges.get(person_name, [])

    def format_badge_showcase(self, person_name: str) -> str:
        """Formata showcase de badges."""
        badges = self.get_player_badges(person_name)

        if not badges:
            return "🏅 Nenhum badge ainda. Complete conquistas para ganhar!"

        # Agrupar por raridade
        by_rarity = {}
        for badge in badges:
            rarity = badge.rarity.value
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(badge)

        lines = [f"🏅 **Badges de {person_name}** ({len(badges)} total)\n"]

        for rarity in ["legendary", "epic", "rare", "uncommon", "common"]:
            if rarity in by_rarity:
                lines.append(f"\n**{rarity.upper()}:**")
                for badge in by_rarity[rarity]:
                    lines.append(f"{badge.emoji} {badge.name}")

        return "\n".join(lines)
