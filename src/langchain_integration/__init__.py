"""
LangChain Integration para Pange.IA.

Sistema completo de Agent com Tools, Memory, Caching e Observability.

Usage Básico:
    from src.langchain_integration import PangeiaAgent

    agent = PangeiaAgent(person_name="Saraiva", user_id="5511999999999")
    response = agent.chat("mostra minhas tarefas")

Usage com Caching (Recomendado):
    from src.langchain_integration import get_cached_agent

    agent = get_cached_agent("5511999999999", "Saraiva")
    response = agent.chat("mostra minhas tarefas")
    # 5x mais rápido!

Observability:
    from src.langchain_integration import get_stats

    stats = get_stats()
    print(f"Mensagens: {stats['total_messages']}")
    print(f"Tokens: {stats['total_tokens']}")
    print(f"Custo: {stats['total_cost']}")
"""

from .agent import PangeiaAgent, create_pangeia_agent
from .tools import NotionTaskTool, PsychologyTool, CoordinationTool
from .caching import get_cached_agent, clear_cache, cache_stats
from .callbacks.metrics_callback import get_stats as get_metrics_stats
from .callbacks.error_tracking_callback import get_error_summary

__all__ = [
    # Agent
    'PangeiaAgent',
    'create_pangeia_agent',

    # Tools
    'NotionTaskTool',
    'PsychologyTool',
    'CoordinationTool',

    # Caching
    'get_cached_agent',
    'clear_cache',
    'cache_stats',

    # Observability
    'get_metrics_stats',
    'get_error_summary',
]

# Helper function (alias)
def get_stats():
    """Alias para get_metrics_stats()."""
    return get_metrics_stats()
