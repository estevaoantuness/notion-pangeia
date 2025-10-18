"""
Cliente WAHA (WhatsApp HTTP API) para comunicação com WhatsApp.

Este módulo substitui a Evolution API e fornece uma interface
simplificada para enviar e receber mensagens via WAHA.
"""

import requests
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class WAHAConfig:
    """Configuração do WAHA."""
    api_url: str = "https://pange-waha.u5qiqp.easypanel.host"
    api_key: str = "460cf6f80f8c4599a6276acbf1cabc71"
    session: str = "default"


class WAHAClient:
    """Cliente para interagir com WAHA API."""

    def __init__(self, config: Optional[WAHAConfig] = None):
        """
        Inicializa o cliente WAHA.

        Args:
            config: Configuração WAHA. Se None, usa valores padrão.
        """
        self.config = config or WAHAConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": self.config.api_key,
            "Content-Type": "application/json"
        })
        logger.info(f"WAHA Client inicializado: {self.config.api_url}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Faz requisição para WAHA API.

        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            data: Dados para enviar no body
            params: Parâmetros de query string

        Returns:
            Resposta da API

        Raises:
            requests.RequestException: Se falhar
        """
        url = f"{self.config.api_url}/api/{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.RequestException as e:
            logger.error(f"Erro na requisição WAHA: {e}")
            raise

    def send_text(
        self,
        chat_id: str,
        text: str,
        session: Optional[str] = None
    ) -> Dict:
        """
        Envia mensagem de texto.

        Args:
            chat_id: ID do chat (número com @s.whatsapp.net ou @g.us para grupos)
            text: Texto da mensagem
            session: Nome da sessão (usa config.session se None)

        Returns:
            Resposta da API com ID da mensagem

        Example:
            >>> client.send_text("5511999999999@s.whatsapp.net", "Olá!")
        """
        session = session or self.config.session

        payload = {
            "session": session,
            "chatId": chat_id,
            "text": text
        }

        logger.info(f"Enviando texto para {chat_id}: {text[:50]}...")
        return self._make_request("POST", "sendText", data=payload)

    def send_message(
        self,
        phone: str,
        message: str,
        session: Optional[str] = None
    ) -> Dict:
        """
        Envia mensagem para um número de telefone.

        Args:
            phone: Número de telefone (formato: +5511999999999)
            message: Mensagem a enviar
            session: Nome da sessão

        Returns:
            Resposta da API
        """
        # Converter número para formato WhatsApp
        chat_id = self._format_phone_to_chat_id(phone)
        return self.send_text(chat_id, message, session)

    def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: Optional[str] = None,
        session: Optional[str] = None
    ) -> Dict:
        """
        Envia imagem.

        Args:
            chat_id: ID do chat
            image_url: URL da imagem
            caption: Legenda opcional
            session: Nome da sessão

        Returns:
            Resposta da API
        """
        session = session or self.config.session

        payload = {
            "session": session,
            "chatId": chat_id,
            "file": {
                "url": image_url
            }
        }

        if caption:
            payload["file"]["caption"] = caption

        logger.info(f"Enviando imagem para {chat_id}")
        return self._make_request("POST", "sendImage", data=payload)

    def send_file(
        self,
        chat_id: str,
        file_url: str,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        session: Optional[str] = None
    ) -> Dict:
        """
        Envia arquivo.

        Args:
            chat_id: ID do chat
            file_url: URL do arquivo
            filename: Nome do arquivo
            caption: Legenda opcional
            session: Nome da sessão

        Returns:
            Resposta da API
        """
        session = session or self.config.session

        payload = {
            "session": session,
            "chatId": chat_id,
            "file": {
                "url": file_url
            }
        }

        if filename:
            payload["file"]["filename"] = filename
        if caption:
            payload["file"]["caption"] = caption

        logger.info(f"Enviando arquivo para {chat_id}")
        return self._make_request("POST", "sendFile", data=payload)

    def send_seen(
        self,
        chat_id: str,
        message_id: str,
        session: Optional[str] = None
    ) -> Dict:
        """
        Marca mensagem como vista.

        Args:
            chat_id: ID do chat
            message_id: ID da mensagem
            session: Nome da sessão

        Returns:
            Resposta da API
        """
        session = session or self.config.session

        payload = {
            "session": session,
            "chatId": chat_id,
            "messageId": message_id
        }

        return self._make_request("POST", "sendSeen", data=payload)

    def get_messages(
        self,
        chat_id: str,
        limit: int = 100,
        session: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém mensagens de um chat.

        Args:
            chat_id: ID do chat
            limit: Número máximo de mensagens
            session: Nome da sessão

        Returns:
            Lista de mensagens
        """
        session = session or self.config.session

        params = {
            "session": session,
            "chatId": chat_id,
            "limit": limit
        }

        return self._make_request("GET", "messages", params=params)

    def get_chats(
        self,
        session: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém lista de chats.

        Args:
            session: Nome da sessão

        Returns:
            Lista de chats
        """
        session = session or self.config.session

        params = {"session": session}
        return self._make_request("GET", "chats", params=params)

    def get_contacts(
        self,
        session: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém lista de contatos.

        Args:
            session: Nome da sessão

        Returns:
            Lista de contatos
        """
        session = session or self.config.session

        params = {"session": session}
        return self._make_request("GET", "contacts", params=params)

    def check_number_exists(
        self,
        phone: str,
        session: Optional[str] = None
    ) -> bool:
        """
        Verifica se número existe no WhatsApp.

        Args:
            phone: Número de telefone
            session: Nome da sessão

        Returns:
            True se número existe
        """
        session = session or self.config.session

        payload = {
            "session": session,
            "phone": phone
        }

        try:
            result = self._make_request("POST", "checkNumberStatus", data=payload)
            return result.get("exists", False)
        except Exception as e:
            logger.error(f"Erro ao verificar número {phone}: {e}")
            return False

    def get_session_status(
        self,
        session: Optional[str] = None
    ) -> Dict:
        """
        Obtém status da sessão.

        Args:
            session: Nome da sessão

        Returns:
            Status da sessão
        """
        session = session or self.config.session

        params = {"session": session}
        return self._make_request("GET", f"sessions/{session}", params=params)

    def start_session(
        self,
        session: Optional[str] = None
    ) -> Dict:
        """
        Inicia uma sessão.

        Args:
            session: Nome da sessão

        Returns:
            Informações da sessão
        """
        session = session or self.config.session

        payload = {
            "name": session,
            "config": {
                "webhooks": []
            }
        }

        return self._make_request("POST", "sessions", data=payload)

    def logout_session(
        self,
        session: Optional[str] = None
    ) -> Dict:
        """
        Faz logout de uma sessão.

        Args:
            session: Nome da sessão

        Returns:
            Confirmação
        """
        session = session or self.config.session

        return self._make_request("DELETE", f"sessions/{session}/logout")

    def set_webhook(
        self,
        webhook_url: str,
        events: Optional[List[str]] = None,
        session: Optional[str] = None
    ) -> Dict:
        """
        Configura webhook para receber eventos.

        Args:
            webhook_url: URL do webhook
            events: Lista de eventos (None = todos)
            session: Nome da sessão

        Returns:
            Confirmação
        """
        session = session or self.config.session

        if events is None:
            events = [
                "message",
                "message.ack",
                "message.reaction",
                "state.change"
            ]

        payload = {
            "session": session,
            "webhooks": [
                {
                    "url": webhook_url,
                    "events": events
                }
            ]
        }

        return self._make_request("PUT", f"sessions/{session}", data=payload)

    @staticmethod
    def _format_phone_to_chat_id(phone: str) -> str:
        """
        Converte número de telefone para formato chat_id do WhatsApp.

        Args:
            phone: Número (formato: +5511999999999 ou 5511999999999)

        Returns:
            Chat ID (formato: 5511999999999@s.whatsapp.net)
        """
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))

        # Adiciona sufixo do WhatsApp
        return f"{clean_phone}@s.whatsapp.net"

    @staticmethod
    def _format_chat_id_to_phone(chat_id: str) -> str:
        """
        Converte chat_id para número de telefone.

        Args:
            chat_id: Chat ID (formato: 5511999999999@s.whatsapp.net)

        Returns:
            Número (formato: +5511999999999)
        """
        # Remove sufixo do WhatsApp
        phone = chat_id.split("@")[0]

        # Adiciona + no início
        return f"+{phone}" if not phone.startswith("+") else phone


# Instância global
waha_client = WAHAClient()


def get_waha_client() -> WAHAClient:
    """
    Retorna instância global do cliente WAHA.

    Returns:
        Cliente WAHA
    """
    return waha_client
