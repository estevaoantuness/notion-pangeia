"""
Módulo de Analytics de Pessoas.

Gerencia perfis psicológicos, padrões de produtividade
e insights sobre colaboradores.
"""

from .analytics import PeopleAnalytics
from .profile import PersonProfile

__all__ = [
    "PeopleAnalytics",
    "PersonProfile"
]
