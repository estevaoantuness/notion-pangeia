"""
Gamification Module - Sistema de Gamificação e Conquistas.

Transforma trabalho em jornada gamificada com conquistas, níveis,
badges e recompensas para aumentar motivação e engajamento.
"""

from .achievement_engine import AchievementEngine, Achievement, AchievementCategory
from .leveling_system import LevelingSystem, PlayerLevel
from .badges import BadgeSystem, Badge, BadgeRarity
from .leaderboards import Leaderboard, LeaderboardPeriod

__all__ = [
    'AchievementEngine',
    'Achievement',
    'AchievementCategory',
    'LevelingSystem',
    'PlayerLevel',
    'BadgeSystem',
    'Badge',
    'BadgeRarity',
    'Leaderboard',
    'LeaderboardPeriod',
]
