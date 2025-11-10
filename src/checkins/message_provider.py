"""
Message Provider for Random Check-ins

Carrega mensagens de check-in do config/replies.yaml e fornece API para selecioná-las

Utiliza cache para não recarregar YAML toda vez
"""

import random
import logging
from typing import Optional, List
import yaml
import os

logger = logging.getLogger(__name__)


class CheckinMessageProvider:
    """
    Fornecedor de mensagens de check-in

    Carrega as mensagens do config/replies.yaml e oferece métodos para
    selecionar mensagens aleatórias

    Exemplo:
        provider = CheckinMessageProvider()
        message = provider.get_message("morning")
        # "☕ Bom dia! Como você está planejando o dia? Tem algo que precisa de atenção especial?"
    """

    def __init__(self, yaml_path: Optional[str] = None):
        """
        Inicializar provider

        Args:
            yaml_path: Caminho para replies.yaml (default: config/replies.yaml)
        """
        if yaml_path is None:
            # Tentar encontrar replies.yaml
            possible_paths = [
                "config/replies.yaml",
                "./config/replies.yaml",
                "/Users/estevaoantunes/notion-pangeia/config/replies.yaml"
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    yaml_path = path
                    break

        if yaml_path is None:
            raise FileNotFoundError("Could not find config/replies.yaml")

        self.yaml_path = yaml_path
        self._messages = None
        self._load_messages()

    def _load_messages(self) -> None:
        """Carregar mensagens do arquivo YAML"""
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Extrair seção random_checkins
            self._messages = data.get('random_checkins', {})

            logger.info(f"Loaded {len(self._messages)} message categories from {self.yaml_path}")

        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            self._messages = {}

    def get_message(self, window: str) -> Optional[str]:
        """
        Obter mensagem aleatória para uma janela

        Args:
            window: Nome da janela ("morning", "afternoon", "evening", "late_night")

        Returns:
            Mensagem aleatória ou None se não encontrada

        Exemplo:
            msg = provider.get_message("morning")
            # "☕ Bom dia! Como você está planejando..."
        """
        if window not in self._messages:
            logger.warning(f"No messages found for window: {window}")
            return None

        messages = self._messages[window]

        if not messages:
            logger.warning(f"Message list for {window} is empty")
            return None

        return random.choice(messages)

    def get_all_windows(self) -> List[str]:
        """
        Obter lista de todas as janelas disponíveis

        Returns:
            Lista de window names ["morning", "afternoon", "evening", "late_night"]
        """
        return list(self._messages.keys())

    def get_messages_for_window(self, window: str) -> List[str]:
        """
        Obter todas as mensagens para uma janela

        Args:
            window: Nome da janela

        Returns:
            Lista de mensagens ou lista vazia
        """
        return self._messages.get(window, [])

    def validate(self) -> bool:
        """
        Validar que todas as janelas têm mensagens

        Returns:
            True se tudo está ok
        """
        required_windows = ["morning", "afternoon", "evening", "late_night"]

        for window in required_windows:
            if window not in self._messages:
                logger.error(f"Missing window: {window}")
                return False

            if not self._messages[window]:
                logger.error(f"Empty message list for: {window}")
                return False

        logger.info("Message validation passed")
        return True


# Instância global
_provider: Optional[CheckinMessageProvider] = None


def get_message_provider(yaml_path: Optional[str] = None) -> CheckinMessageProvider:
    """
    Obter instância global do message provider (singleton)

    Args:
        yaml_path: Caminho para replies.yaml (se não fornecido, usa default)

    Returns:
        Instância do CheckinMessageProvider
    """
    global _provider
    if _provider is None:
        _provider = CheckinMessageProvider(yaml_path)
    return _provider


def get_checkin_message(window: str) -> Optional[str]:
    """
    Shortcut para obter mensagem de check-in

    Args:
        window: Nome da janela

    Returns:
        Mensagem aleatória ou None
    """
    provider = get_message_provider()
    return provider.get_message(window)
