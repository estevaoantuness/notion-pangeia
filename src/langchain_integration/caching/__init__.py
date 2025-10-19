"""
Agent Caching - Sistema de cache para PangeiaAgent.

Evita recriar agents a cada mensagem, melhorando performance 5x.
"""

from .agent_cache import get_cached_agent, clear_cache, cache_stats

__all__ = [
    'get_cached_agent',
    'clear_cache',
    'cache_stats',
]
