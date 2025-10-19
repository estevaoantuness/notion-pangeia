"""
Coordination Module - Sistema de Coordenação Inteligente.

Mapeia TODAS as tasks e TODAS as pessoas para:
- Detectar conexões e colaborações
- Identificar quem pode ajudar quem
- Sugerir formação de times
- Detectar bloqueios e dependências
- Sincronizar visão global entre todos
- Enviar alertas automáticos via WhatsApp
"""

from .team_coordinator import TeamCoordinator, TeamMap
from .connection_detector import ConnectionDetector, Connection
from .collaboration_recommender import CollaborationRecommender, Recommendation
from .message_fragmenter import MessageFragmenter
from .auto_alerter import AutoAlerter

__all__ = [
    'TeamCoordinator',
    'TeamMap',
    'ConnectionDetector',
    'Connection',
    'CollaborationRecommender',
    'Recommendation',
    'MessageFragmenter',
    'AutoAlerter',
]
