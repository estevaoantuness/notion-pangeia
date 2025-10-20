"""
Agentes - Agents Module.

Módulo contendo agentes especializados para o bot.
"""

from .task_manager_agent import TaskManagerAgent
from .smart_task_agent import get_smart_task_agent

__all__ = [
    "TaskManagerAgent",
    "get_smart_task_agent",
]
