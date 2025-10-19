"""
LangChain Integration para Pange.IA.

Sistema completo de Agent com Tools, Memory e Prompts.

Usage:
    from src.langchain_integration import PangeiaAgent

    agent = PangeiaAgent(person_name="Saraiva", user_id="5511999999999")
    response = agent.chat("mostra minhas tarefas")
"""

from .agent import PangeiaAgent, create_pangeia_agent
from .tools import NotionTaskTool, PsychologyTool

__all__ = [
    'PangeiaAgent',
    'create_pangeia_agent',
    'NotionTaskTool',
    'PsychologyTool',
]
