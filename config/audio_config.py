"""
Audio Configuration - Configuração de Áudio.

Configurações para processamento de áudio, transcrição e síntese de fala.
Pangeia: Primeira Habitante - Fundadora de Novos Costumes de Evolução Humana.
"""

import os
from typing import Optional

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TRANSCRIÇÃO DE ÁUDIO (Speech-to-Text)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# OpenAI Whisper Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "pt")  # Portuguese
WHISPER_RESPONSE_FORMAT = os.getenv("WHISPER_RESPONSE_FORMAT", "json")
WHISPER_TEMPERATURE = float(os.getenv("WHISPER_TEMPERATURE", "0.0"))

# Audio Input Specifications
AUDIO_FORMATS_SUPPORTED = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_AUDIO_FILE_SIZE_MB = int(os.getenv("MAX_AUDIO_FILE_SIZE_MB", "25"))  # Whisper limit
AUDIO_ENCODING = "utf-8"
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))  # 16kHz

# Transcrição Cache
ENABLE_TRANSCRIPTION_CACHE = os.getenv("ENABLE_TRANSCRIPTION_CACHE", "true").lower() == "true"
TRANSCRIPTION_CACHE_DURATION_HOURS = int(os.getenv("TRANSCRIPTION_CACHE_DURATION_HOURS", "24"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SÍNTESE DE FALA (Text-to-Speech)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# TTS Provider Selection
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "groq")  # "groq", "openai", or "elevenlabs"

# GROQ Configuration (llama-3.1-8b for voice)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b")
GROQ_TTS_ENABLED = os.getenv("GROQ_TTS_ENABLED", "true").lower() == "true"

# OpenAI TTS Configuration
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")  # "tts-1" for speed, "tts-1-hd" for quality
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "nova")  # nova, onyx, alloy, echo, fable, shimmer
OPENAI_TTS_SPEED = float(os.getenv("OPENAI_TTS_SPEED", "1.0"))

# Audio Output Format
AUDIO_OUTPUT_FORMAT = os.getenv("AUDIO_OUTPUT_FORMAT", "mp3")  # "mp3", "opus", "aac", "flac"
AUDIO_OUTPUT_BITRATE = os.getenv("AUDIO_OUTPUT_BITRATE", "128k")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROCESSAMENTO DE ÁUDIO (Audio Processing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Audio Processing Pipeline
ENABLE_AUDIO_PROCESSING = os.getenv("ENABLE_AUDIO_PROCESSING", "true").lower() == "true"
AUDIO_COMPRESSION_ENABLED = os.getenv("AUDIO_COMPRESSION_ENABLED", "true").lower() == "true"
AUDIO_NOISE_REDUCTION = os.getenv("AUDIO_NOISE_REDUCTION", "true").lower() == "true"

# Temporary Storage
AUDIO_TEMP_DIR = os.getenv("AUDIO_TEMP_DIR", "/tmp/pangeia_audio")
AUDIO_CLEANUP_HOURS = int(os.getenv("AUDIO_CLEANUP_HOURS", "2"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVOLUTION API ÁUDIO (WhatsApp Audio Integration)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Audio Webhook Handling
AUDIO_WEBHOOK_TIMEOUT = int(os.getenv("AUDIO_WEBHOOK_TIMEOUT", "30"))
MAX_AUDIO_MESSAGES_PER_USER_PER_DAY = int(os.getenv("MAX_AUDIO_MESSAGES_PER_USER_PER_DAY", "50"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUALIDADE E VALIDAÇÃO (Quality & Validation)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Quality Thresholds
MIN_AUDIO_DURATION_SECONDS = float(os.getenv("MIN_AUDIO_DURATION_SECONDS", "0.5"))
MAX_AUDIO_DURATION_SECONDS = float(os.getenv("MAX_AUDIO_DURATION_SECONDS", "600"))  # 10 minutes

# Transcription Quality
MIN_CONFIDENCE_SCORE = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.5"))
ENABLE_QUALITY_CHECK = os.getenv("ENABLE_QUALITY_CHECK", "true").lower() == "true"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PANGEIA AUDIO PERSONA (A Primeira Habitante)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Voice Characteristics for Pangeia
PANGEIA_VOICE_WARMTH = "alta"  # Warmth of voice - alto/médio/baixo
PANGEIA_VOICE_PACE = "natural"  # Speech pace - rápido/natural/lento
PANGEIA_VOICE_EMOTION = "empática"  # Emotional tone - empática/neutra/inspiradora

# Conversational Audio Style
ENABLE_VOICE_EXPRESSIONS = os.getenv("ENABLE_VOICE_EXPRESSIONS", "true").lower() == "true"
VOICE_BREAKS_BETWEEN_THOUGHTS = os.getenv("VOICE_BREAKS_BETWEEN_THOUGHTS", "true").lower() == "true"
NATURAL_PAUSES_ENABLED = os.getenv("NATURAL_PAUSES_ENABLED", "true").lower() == "true"

# Audio as Extension of Psychological Intelligence
AUDIO_REFLECTS_EMOTIONAL_STATE = os.getenv("AUDIO_REFLECTS_EMOTIONAL_STATE", "true").lower() == "true"
VOICE_ADAPTS_TO_USER_TONE = os.getenv("VOICE_ADAPTS_TO_USER_TONE", "true").lower() == "true"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING & ANALYTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOG_AUDIO_INTERACTIONS = os.getenv("LOG_AUDIO_INTERACTIONS", "true").lower() == "true"
TRACK_AUDIO_METRICS = os.getenv("TRACK_AUDIO_METRICS", "true").lower() == "true"

# Audio Metrics to Track
AUDIO_METRICS = [
    "transcription_accuracy",
    "audio_duration",
    "processing_time",
    "tts_latency",
    "user_satisfaction",
    "audio_retry_count"
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COST CONTROL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Pricing (approximate, subject to change)
WHISPER_COST_PER_MINUTE = 0.0001  # $0.01 per 100 minutes
OPENAI_TTS_COST_PER_1K_CHARS = 0.015  # $0.015 per 1K characters
GROQ_COST_PER_REQUEST = 0.0001  # Groq is very cheap

# Cost Tracking
ENABLE_AUDIO_COST_TRACKING = os.getenv("ENABLE_AUDIO_COST_TRACKING", "true").lower() == "true"
MAX_DAILY_AUDIO_COST_USD = float(os.getenv("MAX_DAILY_AUDIO_COST_USD", "5.0"))
