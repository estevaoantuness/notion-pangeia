"""
Agentes Inteligentes - Intelligent Agents Module.

Módulo que contém agentes baseados em LLM para processamento conversacional.
"""

from .conversational_agent import ConversationalAgent, get_conversational_agent

__all__ = [
    "ConversationalAgent",
    "get_conversational_agent",
]
