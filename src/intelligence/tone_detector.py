"""
Tone Detector - Detecção de Tom Emocional.

Analisa o tom das mensagens do usuário para entender estado emocional:
- Frustração/raiva
- Cansaço/burnout
- Ansiedade/estresse
- Felicidade/satisfação
- Confusão/sobrecarga

Permite respostas mais empáticas e contextuais.
"""

import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionalTone(Enum):
    """Tons emocionais detectáveis."""
    FRUSTRATED = "frustrated"  # Frustrado/irritado
    EXHAUSTED = "exhausted"  # Cansado/esgotado
    ANXIOUS = "anxious"  # Ansioso/estressado
    HAPPY = "happy"  # Feliz/satisfeito
    CONFUSED = "confused"  # Confuso/sobrecarregado
    NEUTRAL = "neutral"  # Neutro


@dataclass
class ToneAnalysis:
    """Resultado da análise de tom."""
    primary_tone: EmotionalTone
    confidence: float  # 0-1
    indicators: List[str]  # Palavras/padrões que indicaram o tom
    suggested_response_style: str  # Como responder


class ToneDetector:
    """
    Detector de tom emocional nas mensagens.

    Usa análise de padrões linguísticos para identificar
    o estado emocional do usuário e sugerir estilo de resposta.
    """

    def __init__(self):
        """Inicializa detector de tom."""
        # Padrões linguísticos por tom emocional
        self.tone_patterns = {
            EmotionalTone.FRUSTRATED: [
                r"(?i)pqp|porra|droga|saco|odeio|cansei de|tá foda",
                r"(?i)não aguento|não dá mais|que merda|tá difícil demais",
                r"(?i)não funciona|bugado|travando|problema|erro",
                r"(?i)por que (sempre|nunca|todo|tudo)",
            ],
            EmotionalTone.EXHAUSTED: [
                r"(?i)cansado|exausto|esgotado|sem energia|não aguento",
                r"(?i)não consigo mais|tô morto|acabado|destruído",
                r"(?i)dormir|descansar|parar|preciso de um tempo",
                r"(?i)muita coisa|sobrecarga|muito|demais|não dou conta",
            ],
            EmotionalTone.ANXIOUS: [
                r"(?i)ansioso|preocupado|nervoso|estressado|tenso",
                r"(?i)vai dar ruim|e se|medo de|inseguro|aflito",
                r"(?i)prazo|urgente|rápido|atrasado|não vai dar tempo",
                r"(?i)pressão|cobrança|expectativa|responsabilidade",
            ],
            EmotionalTone.HAPPY: [
                r"(?i)feliz|animado|empolgado|ótimo|massa|show|top",
                r"(?i)consegui|funcionou|deu certo|bom demais|adorei",
                r"(?i)obrigado|valeu|ajudou muito|salvou|perfeito",
                r"(?i)😊|😄|🎉|✨|❤️|👏",
            ],
            EmotionalTone.CONFUSED: [
                r"(?i)confuso|perdido|não entendi|como assim|não sei",
                r"(?i)complicado|difícil de entender|não tá claro",
                r"(?i)o que|como|por que|qual|onde começo",
                r"(?i)muita informação|muita coisa|não sei por onde",
            ],
        }

        # Respostas sugeridas por tom
        self.response_styles = {
            EmotionalTone.FRUSTRATED: (
                "Empático e validador. Reconhecer frustração. "
                "Oferecer solução prática imediata. Não minimizar."
            ),
            EmotionalTone.EXHAUSTED: (
                "Acolhedor e protetor. Priorizar CUIDAR acima de tudo. "
                "Sugerir redução de carga. Dar permissão para parar."
            ),
            EmotionalTone.ANXIOUS: (
                "Calmo e estruturante. Quebrar em passos pequenos. "
                "Reduzir incerteza. Focar no próximo passo simples."
            ),
            EmotionalTone.HAPPY: (
                "Celebratório mas genuíno. Validar conquista. "
                "Evitar quebrar o momento com novas demandas."
            ),
            EmotionalTone.CONFUSED: (
                "Clarificador e paciente. Simplificar ao máximo. "
                "Fazer uma pergunta de cada vez. Guiar suavemente."
            ),
            EmotionalTone.NEUTRAL: (
                "Direto e informativo. Responder objetivamente. "
                "Manter tom natural sem forçar empatia."
            ),
        }

        logger.info("ToneDetector inicializado")

    def detect_tone(self, message: str) -> ToneAnalysis:
        """
        Detecta o tom emocional de uma mensagem.

        Args:
            message: Mensagem do usuário

        Returns:
            Análise de tom com tom primário e confiança
        """
        # Detecta todos os tons
        tone_scores = {}
        tone_indicators = {}

        for tone, patterns in self.tone_patterns.items():
            matches = []
            score = 0

            for pattern in patterns:
                found = re.findall(pattern, message)
                if found:
                    matches.extend(found)
                    score += len(found)

            if score > 0:
                tone_scores[tone] = score
                tone_indicators[tone] = matches

        # Nenhum tom detectado = neutro
        if not tone_scores:
            return ToneAnalysis(
                primary_tone=EmotionalTone.NEUTRAL,
                confidence=1.0,
                indicators=[],
                suggested_response_style=self.response_styles[EmotionalTone.NEUTRAL]
            )

        # Tom com maior score
        primary_tone = max(tone_scores, key=tone_scores.get)
        max_score = tone_scores[primary_tone]

        # Confiança baseada em score (normalizada)
        # 1 match = 0.5, 2+ matches = 0.8+
        confidence = min(1.0, 0.3 + (max_score * 0.25))

        return ToneAnalysis(
            primary_tone=primary_tone,
            confidence=confidence,
            indicators=tone_indicators[primary_tone],
            suggested_response_style=self.response_styles[primary_tone]
        )

    def detect_energy_level(self, message: str) -> str:
        """
        Detecta nível de energia baseado em linguagem.

        Returns:
            "very_low", "low", "medium", "high", "very_high"
        """
        message_lower = message.lower()

        # Very Low: exaustão explícita
        very_low_indicators = [
            "não aguento", "esgotado", "exausto", "destruído",
            "não consigo mais", "acabado", "sem energia"
        ]
        if any(ind in message_lower for ind in very_low_indicators):
            return "very_low"

        # Low: cansaço, fadiga
        low_indicators = [
            "cansado", "cansaço", "descansar", "dormir",
            "muita coisa", "sobrecarga", "demais"
        ]
        if any(ind in message_lower for ind in low_indicators):
            return "low"

        # High: animação, motivação
        high_indicators = [
            "animado", "empolgado", "bora", "vamo", "consegui",
            "deu certo", "show", "top", "massa"
        ]
        if any(ind in message_lower for ind in high_indicators):
            return "high"

        # Very High: euforia
        very_high_indicators = [
            "demais", "incrível", "perfeito", "muito bom",
            "adorei", "salvou", "🎉", "❤️"
        ]
        if any(ind in message_lower for ind in very_high_indicators):
            return "very_high"

        # Neutro = medium
        return "medium"

    def should_back_off(self, message: str) -> bool:
        """
        Detecta se o bot deve recuar e dar espaço.

        Returns:
            True se usuário quer espaço/pausa
        """
        back_off_patterns = [
            r"(?i)deixa eu (em paz|pensar|ver|respirar)",
            r"(?i)(para|pare) de (perguntar|falar|mandar)",
            r"(?i)não (quero|vou) (falar|responder|fazer) (agora|hoje)",
            r"(?i)depois|mais tarde|amanhã eu",
            r"(?i)preciso de (espaço|tempo|paz)",
        ]

        for pattern in back_off_patterns:
            if re.search(pattern, message):
                return True

        return False

    def detect_urgency(self, message: str) -> str:
        """
        Detecta nível de urgência na mensagem.

        Returns:
            "critical", "urgent", "normal", "low"
        """
        message_lower = message.lower()

        # Critical: emergência
        critical_indicators = [
            "urgente", "URGENTE", "AGORA", "emergência",
            "crítico", "problema sério", "tá quebrado"
        ]
        if any(ind in message for ind in critical_indicators):
            return "critical"

        # Urgent: prazo apertado
        urgent_indicators = [
            "hoje", "já", "rápido", "prazo", "atrasado",
            "vai dar ruim", "preciso resolver"
        ]
        if any(ind in message_lower for ind in urgent_indicators):
            return "urgent"

        # Low: sem pressa
        low_indicators = [
            "quando der", "sem pressa", "qualquer hora",
            "se puder", "eventualmente"
        ]
        if any(ind in message_lower for ind in low_indicators):
            return "low"

        return "normal"
