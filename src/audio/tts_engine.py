"""
Text-to-Speech Engine - Motor de Síntese de Fala.

Converte texto em áudio usando GROQ ou OpenAI.
Pangeia fala com voz empática e humanizada.
"""

import logging
import os
from typing import Optional, Tuple
from pathlib import Path
import hashlib

import openai

from config.audio_config import (
    TTS_PROVIDER, GROQ_API_KEY, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE,
    OPENAI_TTS_SPEED, AUDIO_OUTPUT_FORMAT, AUDIO_TEMP_DIR,
    PANGEIA_VOICE_WARMTH, ENABLE_VOICE_EXPRESSIONS
)

logger = logging.getLogger(__name__)


class TTSEngine:
    """Motor de síntese de fala com suporte a múltiplos provedores."""

    def __init__(self):
        """Inicializa o TTS engine."""
        self.provider = TTS_PROVIDER
        self.output_format = AUDIO_OUTPUT_FORMAT

        # Criar diretório temporário
        Path(AUDIO_TEMP_DIR).mkdir(parents=True, exist_ok=True)

        logger.info(f"TTSEngine inicializado com provider: {self.provider}")

    def synthesize(self, text: str, voice: Optional[str] = None) -> Tuple[bool, str]:
        """
        Sintetiza texto em áudio.

        Args:
            text: Texto a sintetizar
            voice: Voz opcional (padrão: Pangeia)

        Returns:
            Tuple (sucesso, caminho_do_arquivo_ou_erro)
        """
        try:
            if not text:
                return False, "Texto vazio"

            if len(text) > 4000:
                logger.warning(f"Texto muito longo ({len(text)} chars), truncando")
                text = text[:4000]

            # Usar voz padrão da Pangeia
            if voice is None:
                voice = OPENAI_TTS_VOICE

            if self.provider == "openai":
                return self._synthesize_openai(text, voice)
            elif self.provider == "groq":
                return self._synthesize_groq(text, voice)
            else:
                return False, f"Provider desconhecido: {self.provider}"

        except Exception as e:
            logger.error(f"Erro ao sintetizar: {e}")
            return False, str(e)

    def _synthesize_openai(self, text: str, voice: str) -> Tuple[bool, str]:
        """Sintetiza usando OpenAI TTS."""
        try:
            logger.info(f"Sintetizando com OpenAI: {len(text)} chars")

            response = openai.Audio.create(
                model=OPENAI_TTS_MODEL,
                text=text,
                voice=voice,
                response_format=self.output_format,
                speed=OPENAI_TTS_SPEED
            )

            # Salvar arquivo
            file_path = self._save_audio(response)
            logger.info(f"✅ Áudio gerado: {file_path}")
            return True, file_path

        except Exception as e:
            logger.error(f"Erro OpenAI TTS: {e}")
            return False, str(e)

    def _synthesize_groq(self, text: str, voice: str) -> Tuple[bool, str]:
        """Sintetiza usando GROQ (quando disponível)."""
        try:
            logger.info(f"Sintetizando com GROQ: {len(text)} chars")
            # GROQ TTS será integrado quando disponível
            logger.warning("GROQ TTS ainda não implementado, usando fallback OpenAI")
            return self._synthesize_openai(text, voice)

        except Exception as e:
            logger.error(f"Erro GROQ TTS: {e}")
            return False, str(e)

    def _save_audio(self, audio_data) -> str:
        """Salva dados de áudio em arquivo."""
        try:
            # Gerar nome único
            file_hash = hashlib.md5(str(audio_data).encode()).hexdigest()[:8]
            file_path = Path(AUDIO_TEMP_DIR) / f"pangeia_{file_hash}.{self.output_format}"

            # Salvar
            if hasattr(audio_data, 'write'):
                with open(file_path, "wb") as f:
                    f.write(audio_data)
            else:
                with open(file_path, "wb") as f:
                    f.write(audio_data)

            return str(file_path)

        except Exception as e:
            logger.error(f"Erro ao salvar áudio: {e}")
            raise


# Singleton
_tts_instance = None


def get_tts_engine() -> TTSEngine:
    """Obtém instância singleton."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSEngine()
    return _tts_instance
