"""
Achievement Engine - Motor de Conquistas.

Sistema que rastreia ações e desbloqueia conquistas automaticamente,
recompensando jogadores com XP e badges.
"""

import logging
import yaml
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AchievementCategory(Enum):
    """Categorias de conquistas."""
    PRODUCTIVITY = "productivity"
    STREAK = "streak"
    TEAM = "team"
    WELLNESS = "wellness"
    CHALLENGE = "challenge"
    GROWTH = "growth"
    SPECIAL = "special"
    MILESTONE = "milestone"


class AchievementRarity(Enum):
    """Raridade das conquistas."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Representa uma conquista."""
    id: str
    name: str
    description: str
    category: AchievementCategory
    xp_reward: int
    rarity: AchievementRarity
    criteria: Dict
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100%


@dataclass
class PlayerProgress:
    """Progresso de um jogador."""
    person_name: str
    achievements_unlocked: List[str] = field(default_factory=list)
    achievements_progress: Dict[str, float] = field(default_factory=dict)
    total_xp: int = 0
    stats: Dict = field(default_factory=dict)


class AchievementEngine:
    """
    Motor de conquistas que rastreia ações e desbloqueia achievements.
    """

    def __init__(self, achievements_config_path: Optional[str] = None):
        """
        Inicializa o motor de conquistas.

        Args:
            achievements_config_path: Caminho para config de conquistas
        """
        if achievements_config_path is None:
            achievements_config_path = Path(__file__).parent.parent.parent / "config" / "achievements.yaml"

        self.config_path = Path(achievements_config_path)
        self.achievements: Dict[str, Achievement] = {}
        self.player_progress: Dict[str, PlayerProgress] = {}

        self._load_achievements()
        logger.info(f"AchievementEngine inicializado com {len(self.achievements)} conquistas")

    def _load_achievements(self) -> None:
        """Carrega conquistas do arquivo YAML."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            for ach_data in config.get("achievements", []):
                achievement = Achievement(
                    id=ach_data["id"],
                    name=ach_data["name"],
                    description=ach_data["description"],
                    category=AchievementCategory(ach_data["category"]),
                    xp_reward=ach_data["xp_reward"],
                    rarity=AchievementRarity(ach_data["rarity"]),
                    criteria=ach_data["criteria"]
                )
                self.achievements[achievement.id] = achievement

            logger.info(f"Carregadas {len(self.achievements)} conquistas")

        except Exception as e:
            logger.error(f"Erro ao carregar conquistas: {e}")

    def track_event(
        self,
        person_name: str,
        event_type: str,
        event_data: Dict
    ) -> List[Achievement]:
        """
        Rastreia um evento e verifica conquistas desbloqueadas.

        Args:
            person_name: Nome da pessoa
            event_type: Tipo do evento (task_completion, collaboration, etc.)
            event_data: Dados do evento

        Returns:
            Lista de conquistas desbloqueadas neste evento
        """
        # Criar progresso se não existir
        if person_name not in self.player_progress:
            self.player_progress[person_name] = PlayerProgress(person_name=person_name)

        progress = self.player_progress[person_name]

        # Atualizar stats
        self._update_stats(progress, event_type, event_data)

        # Verificar conquistas
        newly_unlocked = []

        for achievement in self.achievements.values():
            # Já desbloqueada?
            if achievement.id in progress.achievements_unlocked:
                continue

            # Verificar se critério foi atingido
            if self._check_criteria(achievement, progress, event_type, event_data):
                # Desbloquear!
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
                achievement.progress = 100.0

                progress.achievements_unlocked.append(achievement.id)
                progress.total_xp += achievement.xp_reward

                newly_unlocked.append(achievement)

                logger.info(
                    f"🎉 {person_name} desbloqueou: {achievement.name} "
                    f"(+{achievement.xp_reward} XP)"
                )

            else:
                # Atualizar progresso
                progress_pct = self._calculate_progress(achievement, progress)
                progress.achievements_progress[achievement.id] = progress_pct

        return newly_unlocked

    def _update_stats(
        self,
        progress: PlayerProgress,
        event_type: str,
        event_data: Dict
    ) -> None:
        """Atualiza estatísticas do jogador."""
        stats = progress.stats

        # Task completion
        if event_type == "task_completion":
            stats["tasks_completed"] = stats.get("tasks_completed", 0) + 1

            # Por complexidade
            complexity = event_data.get("complexity", "medium")
            key = f"tasks_{complexity}"
            stats[key] = stats.get(key, 0) + 1

            # Por hora
            hour = datetime.now().hour
            if hour < 7:
                stats["tasks_before_7"] = stats.get("tasks_before_7", 0) + 1
            elif hour >= 22:
                stats["tasks_after_22"] = stats.get("tasks_after_22", 0) + 1

            # Streak
            self._update_streak(stats)

        # Collaboration
        elif event_type == "collaboration":
            stats["collaborations"] = stats.get("collaborations", 0) + 1

            helped_person = event_data.get("person_name")
            if helped_person:
                if "people_helped" not in stats:
                    stats["people_helped"] = {}
                stats["people_helped"][helped_person] = stats["people_helped"].get(helped_person, 0) + 1

        # Break taken
        elif event_type == "break_taken":
            if event_data.get("was_suggested"):
                stats["breaks_when_suggested"] = stats.get("breaks_when_suggested", 0) + 1

        # Perfect day
        elif event_type == "perfect_day":
            stats["perfect_days"] = stats.get("perfect_days", 0) + 1
            stats["last_perfect_day"] = datetime.now().isoformat()

        # Burnout risk reduced
        elif event_type == "cognitive_load_recovery":
            stats["cognitive_recoveries"] = stats.get("cognitive_recoveries", 0) + 1

    def _update_streak(self, stats: Dict) -> None:
        """Atualiza streak de dias consecutivos."""
        today = datetime.now().date().isoformat()
        last_day = stats.get("last_completion_day")

        if last_day:
            last_date = datetime.fromisoformat(last_day).date()
            today_date = datetime.now().date()

            if (today_date - last_date).days == 1:
                # Continuou streak
                stats["current_streak"] = stats.get("current_streak", 0) + 1
            elif (today_date - last_date).days > 1:
                # Quebrou streak
                stats["current_streak"] = 1
        else:
            stats["current_streak"] = 1

        stats["last_completion_day"] = today

        # Max streak
        current = stats.get("current_streak", 0)
        max_streak = stats.get("max_streak", 0)
        if current > max_streak:
            stats["max_streak"] = current

    def _check_criteria(
        self,
        achievement: Achievement,
        progress: PlayerProgress,
        event_type: str,
        event_data: Dict
    ) -> bool:
        """Verifica se critério da conquista foi atingido."""
        criteria = achievement.criteria
        criterion_type = criteria.get("type")
        stats = progress.stats

        # Task completion
        if criterion_type == "task_completion":
            return stats.get("tasks_completed", 0) >= criteria.get("count", 0)

        # Consecutive days
        elif criterion_type == "consecutive_days":
            return stats.get("current_streak", 0) >= criteria.get("days", 0)

        # Perfect day
        elif criterion_type == "perfect_day":
            if event_type != "perfect_day":
                return False
            return event_data.get("tasks_completed", 0) >= criteria.get("min_tasks", 3)

        # Tasks by complexity
        elif criterion_type == "tasks_by_complexity":
            complexities = criteria.get("complexity", [])
            count = sum(
                stats.get(f"tasks_{comp}", 0)
                for comp in complexities
            )
            return count >= criteria.get("count", 0)

        # Unique people helped
        elif criterion_type == "unique_people_helped":
            people_helped = stats.get("people_helped", {})
            return len(people_helped) >= criteria.get("count", 0)

        # Collaborations
        elif criterion_type == "collaborations":
            return stats.get("collaborations", 0) >= criteria.get("count", 0)

        # Days no burnout
        elif criterion_type == "days_no_burnout_risk":
            return stats.get("days_no_burnout", 0) >= criteria.get("days", 0)

        # Breaks when suggested
        elif criterion_type == "breaks_taken_when_suggested":
            return stats.get("breaks_when_suggested", 0) >= criteria.get("count", 0)

        # Cognitive load recoveries
        elif criterion_type == "cognitive_load_recoveries":
            return stats.get("cognitive_recoveries", 0) >= criteria.get("count", 0)

        # Tasks before/after hour
        elif criterion_type == "task_completion_before_hour":
            hour = criteria.get("hour", 7)
            return stats.get(f"tasks_before_{hour}", 0) >= criteria.get("count", 0)

        elif criterion_type == "task_completion_after_hour":
            hour = criteria.get("hour", 22)
            return stats.get(f"tasks_after_{hour}", 0) >= criteria.get("count", 0)

        # Level reached
        elif criterion_type == "level_reached":
            # Implementado pelo LevelingSystem
            return False

        # Total XP
        elif criterion_type == "total_xp":
            return progress.total_xp >= criteria.get("xp", 0)

        # Default: não atingido
        return False

    def _calculate_progress(
        self,
        achievement: Achievement,
        progress: PlayerProgress
    ) -> float:
        """Calcula progresso em direção a uma conquista (0-100)."""
        criteria = achievement.criteria
        criterion_type = criteria.get("type")
        stats = progress.stats

        if criterion_type == "task_completion":
            current = stats.get("tasks_completed", 0)
            target = criteria.get("count", 1)
            return min(100.0, (current / target) * 100)

        elif criterion_type == "consecutive_days":
            current = stats.get("current_streak", 0)
            target = criteria.get("days", 1)
            return min(100.0, (current / target) * 100)

        elif criterion_type == "tasks_by_complexity":
            complexities = criteria.get("complexity", [])
            current = sum(
                stats.get(f"tasks_{comp}", 0)
                for comp in complexities
            )
            target = criteria.get("count", 1)
            return min(100.0, (current / target) * 100)

        # Default: 0%
        return 0.0

    def get_player_achievements(
        self,
        person_name: str
    ) -> Dict:
        """
        Retorna conquistas do jogador.

        Returns:
            Dict com conquistas desbloqueadas e em progresso
        """
        if person_name not in self.player_progress:
            return {
                "unlocked": [],
                "in_progress": [],
                "total_xp": 0
            }

        progress = self.player_progress[person_name]

        unlocked = [
            {
                "id": ach_id,
                "name": self.achievements[ach_id].name,
                "description": self.achievements[ach_id].description,
                "category": self.achievements[ach_id].category.value,
                "rarity": self.achievements[ach_id].rarity.value,
                "xp_reward": self.achievements[ach_id].xp_reward
            }
            for ach_id in progress.achievements_unlocked
            if ach_id in self.achievements
        ]

        # Em progresso (>0% e <100%)
        in_progress = [
            {
                "id": ach_id,
                "name": self.achievements[ach_id].name,
                "description": self.achievements[ach_id].description,
                "progress": pct,
                "category": self.achievements[ach_id].category.value,
                "rarity": self.achievements[ach_id].rarity.value
            }
            for ach_id, pct in progress.achievements_progress.items()
            if 0 < pct < 100 and ach_id in self.achievements
        ]

        # Ordenar por progresso (maior primeiro)
        in_progress.sort(key=lambda x: x["progress"], reverse=True)

        return {
            "unlocked": unlocked,
            "in_progress": in_progress[:10],  # Top 10
            "total_xp": progress.total_xp,
            "total_unlocked": len(unlocked)
        }

    def format_achievement_notification(
        self,
        achievement: Achievement
    ) -> str:
        """Formata mensagem de conquista desbloqueada."""
        rarity_emoji = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟠"
        }

        emoji = rarity_emoji.get(achievement.rarity.value, "⚪")

        return (
            f"🎉 **CONQUISTA DESBLOQUEADA!** 🎉\n\n"
            f"{emoji} {achievement.name}\n"
            f"_{achievement.description}_\n\n"
            f"💰 +{achievement.xp_reward} XP\n"
            f"🏷️ Raridade: {achievement.rarity.value.upper()}"
        )
