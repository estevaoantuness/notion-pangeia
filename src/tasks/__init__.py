"""
Tasks Module - Sistema de Gerenciamento Inteligente de Tarefas.

Este módulo estende as funcionalidades de tasks com IA, incluindo:
- Decomposição inteligente de tasks grandes
- Estimativa de complexidade
- Mapeamento de dependências
"""

from .ai_decomposer import AITaskDecomposer, SubTask, TaskComplexity
from .complexity_estimator import ComplexityEstimator
from .dependency_mapper import DependencyMapper
from .subtask_generator import SubtaskGenerator

__all__ = [
    'AITaskDecomposer',
    'SubTask',
    'TaskComplexity',
    'ComplexityEstimator',
    'DependencyMapper',
    'SubtaskGenerator',
]
