"""
Audio Processor - Processador de Áudio.

Pipeline completo de processamento de áudio para WhatsApp.
"""

import logging
from typing import Optional, Tuple
from pathlib import Path
import tempfile
import shutil

from config.audio_config import (
    ENABLE_AUDIO_PROCESSING, AUDIO_COMPRESSION_ENABLED,
    AUDIO_NOISE_REDUCTION, AUDIO_TEMP_DIR, AUDIO_CLEANUP_HOURS,
    MIN_AUDIO_DURATION_SECONDS, MAX_AUDIO_DURATION_SECONDS
)
from .transcriber import get_transcriber
from .tts_engine import get_tts_engine

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processa áudio end-to-end."""

    def __init__(self):
        """Inicializa o processador."""
        self.transcriber = get_transcriber()
        self.tts_engine = get_tts_engine()

        # Criar diretórios
        Path(AUDIO_TEMP_DIR).mkdir(parents=True, exist_ok=True)

        logger.info("AudioProcessor inicializado")

    def process_audio_message(
        self,
        audio_file_path: str,
        user_id: str,
        person_name: str
    ) -> Tuple[bool, str]:
        """
        Processa mensagem de áudio: download → transcrição → processamento.

        Args:
            audio_file_path: Caminho do arquivo de áudio
            user_id: ID do usuário
            person_name: Nome da pessoa

        Returns:
            Tuple (sucesso, transcrição_ou_erro)
        """
        try:
            logger.info(f"🎤 Processando áudio de {person_name}")

            # Validar duração
            is_valid, error = self._validate_audio_duration(audio_file_path)
            if not is_valid:
                logger.warning(f"Áudio inválido: {error}")
                return False, error

            # Processar áudio (compressão, noise reduction, etc)
            if ENABLE_AUDIO_PROCESSING:
                audio_file_path = self._process_audio(audio_file_path)

            # Transcrever
            success, transcription = self.transcriber.transcribe_file(audio_file_path)

            if success:
                logger.info(f"✅ Áudio transcrito: {len(transcription)} chars")
                return True, transcription
            else:
                return False, transcription

        except Exception as e:
            logger.error(f"Erro ao processar áudio: {e}")
            return False, "Erro no processamento do áudio"

    def generate_audio_response(
        self,
        text: str,
        person_name: str,
        voice: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Gera resposta em áudio.

        Args:
            text: Texto a converter em áudio
            person_name: Nome da pessoa
            voice: Voz (opcional)

        Returns:
            Tuple (sucesso, caminho_do_arquivo_ou_erro)
        """
        try:
            logger.info(f"🎵 Gerando áudio para {person_name}")

            success, audio_path = self.tts_engine.synthesize(text, voice)

            if success:
                logger.info(f"✅ Áudio gerado: {audio_path}")
                return True, audio_path
            else:
                logger.error(f"Erro ao gerar áudio: {audio_path}")
                return False, audio_path

        except Exception as e:
            logger.error(f"Erro ao gerar resposta em áudio: {e}")
            return False, str(e)

    def _validate_audio_duration(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Valida duração do áudio."""
        try:
            import wave

            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)

            if duration < MIN_AUDIO_DURATION_SECONDS:
                return False, "Áudio muito curto"

            if duration > MAX_AUDIO_DURATION_SECONDS:
                return False, f"Áudio muito longo (máximo {MAX_AUDIO_DURATION_SECONDS}s)"

            return True, None

        except Exception as e:
            logger.debug(f"Erro ao validar duração: {e}")
            # Se não conseguir validar, permitir (pode ser formato diferente)
            return True, None

    def _process_audio(self, file_path: str) -> str:
        """Processa áudio (compressão, noise reduction)."""
        try:
            if not ENABLE_AUDIO_PROCESSING:
                return file_path

            logger.info(f"Processando áudio: {file_path}")

            # Aqui iríamos usar librosa, pydub ou similar
            # Por enquanto, retorna o arquivo original
            # Implementar quando tiver librosa disponível

            return file_path

        except Exception as e:
            logger.warning(f"Erro ao processar áudio: {e}")
            return file_path

    def cleanup_old_files(self) -> None:
        """Remove arquivos de áudio antigos."""
        try:
            from datetime import datetime, timedelta

            cutoff = datetime.now() - timedelta(hours=AUDIO_CLEANUP_HOURS)
            temp_dir = Path(AUDIO_TEMP_DIR)

            if not temp_dir.exists():
                return

            for file_path in temp_dir.glob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff:
                        file_path.unlink()
                        logger.debug(f"Removido: {file_path}")

        except Exception as e:
            logger.warning(f"Erro ao limpar arquivos: {e}")


# Singleton
_processor_instance = None


def get_processor() -> AudioProcessor:
    """Obtém instância singleton."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = AudioProcessor()
    return _processor_instance
