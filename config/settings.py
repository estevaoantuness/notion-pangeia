"""
Configurações centralizadas do sistema Pange.iA Bot.

Este módulo carrega todas as variáveis de ambiente e fornece
configurações para os demais módulos do sistema.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Settings:
    """Configurações gerais do sistema."""

    # Notion Configuration
    NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")
    NOTION_TASKS_DB_ID: str = os.getenv("NOTION_TASKS_DB_ID", "")
    NOTION_USERS_DB_ID: Optional[str] = os.getenv("NOTION_USERS_DB_ID")  # Para onboarding
    NOTION_CHECKINS_DB_ID: Optional[str] = os.getenv("NOTION_CHECKINS_DB_ID")
    NOTION_INSIGHTS_DB_ID: Optional[str] = os.getenv("NOTION_INSIGHTS_DB_ID")

    # Evolution API WhatsApp Configuration
    EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL", "https://pange-evolution-api.u5qiqp.easypanel.host")
    EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_KEY", "429683C4C977415CAAFCCE10F7D57E11")
    EVOLUTION_INSTANCE_NAME: str = os.getenv("EVOLUTION_INSTANCE_NAME", "Pange.IA Bot")

    # Flask Configuration
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/whatsapp/incoming")
    PORT: int = int(os.getenv("PORT", "5000"))

    # Redis Configuration (for conversation memory across workers)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_TTL_HOURS: int = int(os.getenv("REDIS_TTL_HOURS", "24"))

    # Scheduler Configuration
    DAILY_SEND_TIME: str = os.getenv("DAILY_SEND_TIME", "08:00")
    CHECKIN_1_TIME: str = os.getenv("CHECKIN_1_TIME", "13:30")
    CHECKIN_2_TIME: str = os.getenv("CHECKIN_2_TIME", "15:30")
    CHECKIN_3_TIME: str = os.getenv("CHECKIN_3_TIME", "18:00")
    CHECKIN_4_TIME: str = os.getenv("CHECKIN_4_TIME", "22:00")
    TIMEZONE: str = os.getenv("TIMEZONE", "America/Sao_Paulo")

    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CACHE_EXPIRY_HOURS: int = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Psychological Engine
    ENABLE_PSYCHOLOGY: bool = os.getenv("ENABLE_PSYCHOLOGY", "true").lower() == "true"
    ENABLE_MESSAGE_CHUNKING: bool = os.getenv("ENABLE_MESSAGE_CHUNKING", "true").lower() == "true"
    ENABLE_DEDUPLICATION: bool = os.getenv("ENABLE_DEDUPLICATION", "true").lower() == "true"

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Valida se todas as configurações obrigatórias estão presentes.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        if not cls.NOTION_TOKEN:
            errors.append("NOTION_TOKEN não configurado")

        if not cls.NOTION_TASKS_DB_ID:
            errors.append("NOTION_TASKS_DB_ID não configurado")

        if not cls.EVOLUTION_API_URL:
            errors.append("EVOLUTION_API_URL não configurado")

        if not cls.EVOLUTION_API_KEY:
            errors.append("EVOLUTION_API_KEY não configurado")

        if not cls.EVOLUTION_INSTANCE_NAME:
            errors.append("EVOLUTION_INSTANCE_NAME não configurado")

        return len(errors) == 0, errors

    @classmethod
    def setup_logging(cls) -> None:
        """Configura o sistema de logging."""
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)

        # Configuração do formato de log
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True)

        # Configurar logging para arquivo e console
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler('logs/pangeia_bot.log'),
                logging.StreamHandler()
            ]
        )

        # Reduzir verbosidade de bibliotecas externas
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)


# Instância global de configurações
settings = Settings()


def get_settings() -> Settings:
    """
    Retorna a instância de configurações.

    Returns:
        Settings: Instância de configurações do sistema.
    """
    return settings


# Configurar logging ao importar o módulo
settings.setup_logging()
