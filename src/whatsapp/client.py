"""
Cliente Evolution API para envio e recebimento de mensagens via WhatsApp.

Este módulo fornece interface para interagir com a Evolution API,
incluindo envio de mensagens com retry logic.
"""

import logging
import time
import requests
from typing import Optional, Tuple

from config.settings import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Cliente para interagir com WhatsApp via Evolution API.

    Gerencia envio de mensagens, validação de números e tratamento de erros.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_name: Optional[str] = None
    ):
        """
        Inicializa o cliente WhatsApp.

        Args:
            api_url: URL base da Evolution API (usa settings se não fornecido)
            api_key: API Key da Evolution API (usa settings se não fornecido)
            instance_name: Nome da instância (usa settings se não fornecido)
        """
        self.api_url = api_url or settings.EVOLUTION_API_URL
        self.api_key = api_key or settings.EVOLUTION_API_KEY
        self.instance_name = instance_name or settings.EVOLUTION_INSTANCE_NAME

        # Headers padrão para todas as requisições
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        logger.info(f"Cliente WhatsApp inicializado: {self.instance_name}")

    def validate_number(self, number: str) -> Tuple[bool, str]:
        """
        Valida formato de número WhatsApp.

        Args:
            number: Número a validar (formato: +55XXXXXXXXXXX ou 55XXXXXXXXXXX)

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        # Remove espaços
        clean_number = number.strip()

        # Aceita formato +55... ou 55...
        if clean_number.startswith("+"):
            if len(clean_number) < 12:  # + + código país (2) + DDD (2) + número (8-9)
                return False, f"Número muito curto: {number}"
        else:
            if len(clean_number) < 11:  # código país (2) + DDD (2) + número (8-9)
                return False, f"Número muito curto: {number}"

        return True, "Número válido"

    def send_message(
        self,
        to_number: str,
        message: str,
        retry_count: int = 0
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem via WhatsApp com retry logic.

        Args:
            to_number: Número de destino (formato: +55XXXXXXXXXXX ou 55XXXXXXXXXXX)
            message: Texto da mensagem
            retry_count: Contador de tentativas (interno)

        Returns:
            Tuple[bool, Optional[str], Optional[str]]:
                (sucesso, message_id, erro)
        """
        # Valida número
        is_valid, validation_msg = self.validate_number(to_number)
        if not is_valid:
            logger.error(validation_msg)
            return False, None, validation_msg

        # Remove prefixo whatsapp: se existir (compatibilidade com código antigo)
        clean_number = to_number.replace("whatsapp:", "")

        # Endpoint da Evolution API
        url = f"{self.api_url}/message/sendText/{self.instance_name}"

        # Payload
        payload = {
            "number": clean_number,
            "text": message
        }

        try:
            # Envia requisição
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            # Verifica status
            if response.status_code == 201:
                data = response.json()
                message_id = data.get("key", {}).get("id", "unknown")

                logger.info(
                    f"✅ Mensagem enviada para {clean_number}. "
                    f"ID: {message_id}"
                )

                return True, message_id, None

            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text}"

                # Tenta fazer retry em alguns casos
                recoverable_codes = [429, 500, 502, 503, 504]
                if response.status_code in recoverable_codes and retry_count < settings.MAX_RETRIES:
                    wait_time = (2 ** retry_count) * 2  # Backoff exponencial
                    logger.warning(
                        f"⚠️ {error_msg}. "
                        f"Tentando novamente em {wait_time}s "
                        f"(tentativa {retry_count + 1}/{settings.MAX_RETRIES})"
                    )
                    time.sleep(wait_time)
                    return self.send_message(to_number, message, retry_count + 1)

                logger.error(f"❌ {error_msg}")
                return False, None, error_msg

        except requests.exceptions.Timeout:
            error_msg = "Timeout ao enviar mensagem"

            # Retry em caso de timeout
            if retry_count < settings.MAX_RETRIES:
                wait_time = (2 ** retry_count) * 2
                logger.warning(
                    f"⚠️ {error_msg}. "
                    f"Tentando novamente em {wait_time}s "
                    f"(tentativa {retry_count + 1}/{settings.MAX_RETRIES})"
                )
                time.sleep(wait_time)
                return self.send_message(to_number, message, retry_count + 1)

            logger.error(f"❌ {error_msg}")
            return False, None, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg

    def send_bulk_messages(
        self,
        recipients: list[tuple[str, str]]
    ) -> dict[str, dict]:
        """
        Envia mensagens para múltiplos destinatários.

        Args:
            recipients: Lista de tuplas (numero, mensagem)

        Returns:
            Dict com resultados: {numero: {success, message_id, error}}
        """
        results = {}

        for to_number, message in recipients:
            success, message_id, error = self.send_message(to_number, message)

            results[to_number] = {
                "success": success,
                "message_id": message_id,
                "error": error
            }

            # Pequena pausa entre mensagens para evitar rate limit
            time.sleep(0.5)

        successful = sum(1 for r in results.values() if r["success"])
        failed = len(results) - successful

        logger.info(
            f"📊 Envio em lote concluído: "
            f"{successful} sucessos, {failed} falhas"
        )

        return results

    def test_connection(self) -> Tuple[bool, str]:
        """
        Testa conexão com Evolution API.

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Tenta buscar informações da instância
            url = f"{self.api_url}/instance/connectionState/{self.instance_name}"

            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                state = data.get("state", "unknown")

                logger.info(f"✅ Conexão com Evolution API OK! Estado: {state}")
                return True, f"Conectado à Evolution API. Estado da instância: {state}"

            else:
                error_msg = f"Erro ao conectar: HTTP {response.status_code}"
                logger.error(f"❌ {error_msg}")
                return False, error_msg

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg

        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg


def format_phone_number(phone: str) -> str:
    """
    Formata número de telefone para formato Evolution API.

    Args:
        phone: Número em qualquer formato (com ou sem +, com ou sem whatsapp:)

    Returns:
        Número formatado: +55XXXXXXXXXXX
    """
    # Remove prefixo whatsapp: se existir
    phone = phone.replace("whatsapp:", "")

    # Remove espaços e caracteres especiais (exceto +)
    clean_phone = phone.strip()

    # Garante que começa com +
    if not clean_phone.startswith('+'):
        # Remove tudo exceto dígitos
        clean_phone = ''.join(filter(str.isdigit, clean_phone))
        clean_phone = '+' + clean_phone

    return clean_phone
