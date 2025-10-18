"""
Audio Transcriber - Transcritor de Áudio com Whisper.

Converte áudio em texto usando OpenAI Whisper.
"""

import logging
import os
from typing import Optional, Tuple
from pathlib import Path
import hashlib
import json

import openai

from config.audio_config import (
    WHISPER_MODEL, WHISPER_LANGUAGE, WHISPER_TEMPERATURE,
    MAX_AUDIO_FILE_SIZE_MB, AUDIO_FORMATS_SUPPORTED,
    ENABLE_TRANSCRIPTION_CACHE, TRANSCRIPTION_CACHE_DURATION_HOURS,
    AUDIO_TEMP_DIR, MIN_CONFIDENCE_SCORE
)

logger = logging.getLogger(__name__)

# Criar diretório de cache
CACHE_DIR = Path.home() / ".pangeia" / "transcription_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class AudioTranscriber:
    """Transcreve áudio para texto usando OpenAI Whisper."""

    def __init__(self):
        """Inicializa o transcritor."""
        self.model = WHISPER_MODEL
        self.language = WHISPER_LANGUAGE
        self.temperature = WHISPER_TEMPERATURE
        logger.info(f"AudioTranscriber inicializado com {self.model}")

    def transcribe_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Transcreve um arquivo de áudio.

        Args:
            file_path: Caminho para o arquivo de áudio

        Returns:
            Tuple (sucesso, transcrição_ou_erro)
        """
        try:
            # Validar arquivo
            is_valid, error = self._validate_file(file_path)
            if not is_valid:
                logger.warning(f"Arquivo inválido: {error}")
                return False, error

            # Verificar cache
            if ENABLE_TRANSCRIPTION_CACHE:
                cached = self._get_from_cache(file_path)
                if cached:
                    logger.info(f"Transcrição do cache: {file_path}")
                    return True, cached

            # Transcrever com Whisper
            logger.info(f"Transcrevendo: {file_path}")
            with open(file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model=self.model,
                    file=audio_file,
                    language=self.language,
                    temperature=self.temperature
                )

            text = transcript.get("text", "")

            if not text:
                logger.warning("Transcrição vazia recebida")
                return False, "Não foi possível transcrever o áudio"

            # Guardar em cache
            if ENABLE_TRANSCRIPTION_CACHE:
                self._save_to_cache(file_path, text)

            logger.info(f"✅ Transcrição concluída: {len(text)} caracteres")
            return True, text

        except openai.error.InvalidRequestError as e:
            logger.error(f"Erro de requisição: {e}")
            return False, "Formato de áudio não suportado"

        except openai.error.RateLimitError:
            logger.warning("Rate limit do Whisper atingido")
            return False, "Servidor sobrecarregado, tenta em alguns segundos"

        except Exception as e:
            logger.error(f"Erro ao transcrever: {e}")
            return False, f"Erro na transcrição: {str(e)}"

    def _validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Valida o arquivo de áudio."""
        path = Path(file_path)

        if not path.exists():
            return False, "Arquivo não encontrado"

        # Verificar extensão
        ext = path.suffix.lstrip(".").lower()
        if ext not in AUDIO_FORMATS_SUPPORTED:
            return False, f"Formato não suportado. Use: {', '.join(AUDIO_FORMATS_SUPPORTED)}"

        # Verificar tamanho
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_AUDIO_FILE_SIZE_MB:
            return False, f"Arquivo muito grande ({size_mb:.1f}MB, máximo {MAX_AUDIO_FILE_SIZE_MB}MB)"

        return True, None

    def _get_cache_key(self, file_path: str) -> str:
        """Gera chave de cache baseada no arquivo."""
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash

    def _get_from_cache(self, file_path: str) -> Optional[str]:
        """Recupera transcrição do cache."""
        try:
            cache_key = self._get_cache_key(file_path)
            cache_file = CACHE_DIR / f"{cache_key}.json"

            if not cache_file.exists():
                return None

            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Verificar idade do cache
            from datetime import datetime, timedelta
            created = datetime.fromisoformat(data.get("created", ""))
            if datetime.now() - created > timedelta(hours=TRANSCRIPTION_CACHE_DURATION_HOURS):
                return None

            return data.get("text")

        except Exception as e:
            logger.debug(f"Erro ao acessar cache: {e}")
            return None

    def _save_to_cache(self, file_path: str, text: str) -> None:
        """Salva transcrição em cache."""
        try:
            cache_key = self._get_cache_key(file_path)
            cache_file = CACHE_DIR / f"{cache_key}.json"

            data = {
                "file": file_path,
                "text": text,
                "created": datetime.now().isoformat()
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

        except Exception as e:
            logger.debug(f"Erro ao salvar cache: {e}")

    def estimate_cost(self, audio_duration_minutes: float) -> float:
        """Estima custo da transcrição."""
        from config.audio_config import WHISPER_COST_PER_MINUTE
        return audio_duration_minutes * WHISPER_COST_PER_MINUTE


# Singleton
_transcriber_instance = None


def get_transcriber() -> AudioTranscriber:
    """Obtém instância singleton."""
    global _transcriber_instance
    if _transcriber_instance is None:
        _transcriber_instance = AudioTranscriber()
    return _transcriber_instance
