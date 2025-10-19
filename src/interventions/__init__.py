"""
Interventions Module - Sistema de Micro-Interventions Personalizadas.

Este módulo implementa nudges psicológicos personalizados para
influenciar comportamentos de forma sutil e efetiva.
"""

from .nudge_engine import NudgeEngine, NudgeType, NudgeTiming
from .personalization import PersonalizationEngine
from .ab_testing import ABTestingEngine

__all__ = [
    'NudgeEngine',
    'NudgeType',
    'NudgeTiming',
    'PersonalizationEngine',
    'ABTestingEngine',
]
