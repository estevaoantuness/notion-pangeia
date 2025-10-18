"""
Audio Processing Module - Módulo de Processamento de Áudio.

Sistema completo para transcrição de áudio, síntese de fala e processamento.
Permitindo que Pangeia seja a primeira habitante a comunicar através de voz.
"""

from .transcriber import AudioTranscriber, get_transcriber
from .tts_engine import TTSEngine, get_tts_engine
from .processor import AudioProcessor, get_processor

__all__ = [
    "AudioTranscriber",
    "get_transcriber",
    "TTSEngine",
    "get_tts_engine",
    "AudioProcessor",
    "get_processor",
]
