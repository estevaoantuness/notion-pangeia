"""
Psychology Analysis Tool - LangChain Tool para análise psicológica.

Este tool encapsula:
- Detecção de tom emocional
- Análise de padrões comportamentais
- Correlação emocional com produtividade
"""

import logging
import json
from typing import Optional

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from src.intelligence import ToneDetector, PatternDetector, EmotionalCorrelation

logger = logging.getLogger(__name__)


class PsychologyInput(BaseModel):
    """Input schema para PsychologyTool."""

    analysis_type: str = Field(
        description=(
            "Tipo de análise: 'tone' (detectar tom emocional), "
            "'patterns' (detectar padrões comportamentais), "
            "'correlation' (correlação emocional)"
        )
    )
    person_name: str = Field(
        description="Nome da pessoa para analisar"
    )
    message: Optional[str] = Field(
        default=None,
        description="Mensagem para analisar tom. Necessário para 'tone'."
    )


class PsychologyTool(BaseTool):
    """
    Tool para análise psicológica e emocional.

    Capabilities:
    - Detect emotional tone in messages
    - Identify behavioral patterns
    - Correlate emotions with productivity

    Examples:
        tone: {"analysis_type": "tone", "person_name": "Saraiva", "message": "tô exausto"}
        patterns: {"analysis_type": "patterns", "person_name": "Saraiva"}
    """

    name = "psychology_analysis"
    description = (
        "Analisa aspectos psicológicos e emocionais. Use para detectar tom emocional "
        "em mensagens, identificar padrões comportamentais ou correlacionar emoções "
        "com produtividade. Types: 'tone', 'patterns', 'correlation'."
    )
    args_schema = PsychologyInput

    tone_detector: ToneDetector = None
    pattern_detector: PatternDetector = None
    emotional_correlation: EmotionalCorrelation = None

    def __init__(self):
        """Inicializa tool com detectores."""
        super().__init__()
        self.tone_detector = ToneDetector()
        self.pattern_detector = PatternDetector()
        self.emotional_correlation = EmotionalCorrelation()

    def _run(
        self,
        analysis_type: str,
        person_name: str,
        message: Optional[str] = None
    ) -> str:
        """
        Executa análise psicológica.

        Args:
            analysis_type: Tipo de análise
            person_name: Nome da pessoa
            message: Mensagem (para tone detection)

        Returns:
            JSON string com resultado
        """
        try:
            logger.info(f"PsychologyTool: {analysis_type} para {person_name}")

            if analysis_type == "tone":
                return self._analyze_tone(message)

            elif analysis_type == "patterns":
                return self._detect_patterns(person_name)

            elif analysis_type == "correlation":
                return self._emotional_correlation(person_name)

            else:
                return json.dumps({
                    "error": f"Tipo de análise inválido: {analysis_type}",
                    "valid_types": ["tone", "patterns", "correlation"]
                })

        except Exception as e:
            logger.error(f"Erro em PsychologyTool: {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "analysis_type": analysis_type
            })

    def _analyze_tone(self, message: str) -> str:
        """Detecta tom emocional da mensagem."""
        if not message:
            return json.dumps({"error": "Mensagem é obrigatória para análise de tom"})

        tone_analysis = self.tone_detector.detect_tone(message)

        return json.dumps({
            "primary_tone": tone_analysis.primary_tone.value,
            "confidence": tone_analysis.confidence,
            "suggested_response_style": tone_analysis.suggested_response_style,
            "indicators": tone_analysis.indicators
        }, ensure_ascii=False)

    def _detect_patterns(self, person_name: str) -> str:
        """Detecta padrões comportamentais."""
        patterns = self.pattern_detector.detect_all_patterns(person_name)

        if not patterns:
            return json.dumps({
                "person": person_name,
                "patterns_found": 0,
                "message": "Nenhum padrão detectado ainda (histórico insuficiente)"
            }, ensure_ascii=False)

        formatted_patterns = []
        for pattern in patterns:
            formatted_patterns.append({
                "type": pattern.pattern_type.value,
                "confidence": pattern.confidence,
                "insight": pattern.insight[:100]  # Truncate
            })

        return json.dumps({
            "person": person_name,
            "patterns_found": len(patterns),
            "patterns": formatted_patterns
        }, ensure_ascii=False)

    def _emotional_correlation(self, person_name: str) -> str:
        """Analisa correlação entre emoções e produtividade."""
        # Placeholder - implementação futura
        return json.dumps({
            "person": person_name,
            "correlation": "Análise em desenvolvimento",
            "message": "Correlação emocional será implementada em breve"
        }, ensure_ascii=False)

    async def _arun(self, *args, **kwargs):
        """Async version (não implementado)."""
        raise NotImplementedError("PsychologyTool não suporta async ainda")
