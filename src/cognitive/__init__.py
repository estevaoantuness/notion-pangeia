"""
Cognitive Module - Sistema de Detecção e Gestão de Carga Cognitiva.

Este módulo detecta sobrecarga cognitiva em tempo real e adapta
o sistema para reduzir estresse e melhorar performance.
"""

from .load_detector import CognitiveLoadDetector, CognitiveLoadLevel
from .task_recommender import TaskRecommender
from .break_scheduler import BreakScheduler
from .complexity_analyzer import TaskComplexityAnalyzer

__all__ = [
    'CognitiveLoadDetector',
    'CognitiveLoadLevel',
    'TaskRecommender',
    'BreakScheduler',
    'TaskComplexityAnalyzer',
]
