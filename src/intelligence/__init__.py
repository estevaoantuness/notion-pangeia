"""
Intelligence Module - Inteligência Proativa e Detecção de Padrões.

Módulo revolucionário que transforma Pange.IA em Terapeuta Produtivo:
- Detecta padrões comportamentais
- Correlaciona emoções com produtividade
- Proatividade inteligente (insights automáticos)
- Conversação natural e contextual
"""

from .pattern_detector import PatternDetector, DetectedPattern, PatternType
from .proactive_engine import ProactiveEngine, ProactiveInsight, TriggerType
from .conversation_memory import ConversationMemory, get_conversation_memory
from .tone_detector import ToneDetector, ToneAnalysis, EmotionalTone
from .emotional_correlation import EmotionalCorrelation, EmotionalCorrelationInsight

__all__ = [
    # Pattern Detection
    'PatternDetector',
    'DetectedPattern',
    'PatternType',

    # Proactive Engine
    'ProactiveEngine',
    'ProactiveInsight',
    'TriggerType',

    # Conversation Memory
    'ConversationMemory',
    'get_conversation_memory',

    # Tone Detection
    'ToneDetector',
    'ToneAnalysis',
    'EmotionalTone',

    # Emotional Correlation
    'EmotionalCorrelation',
    'EmotionalCorrelationInsight',
]
