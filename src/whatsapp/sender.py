"""
Sender de mensagens WhatsApp.

Este módulo gerencia o envio de mensagens formatadas via WhatsApp,
integrando o formatador de mensagens com o cliente Twilio.
"""

import logging
import textwrap
from typing import Optional, Tuple, Dict, List

from src.whatsapp.client import WhatsAppClient
from src.messaging.formatter import MessageFormatter
from src.cache.task_mapper import get_task_mapper
from config.colaboradores import get_phone_by_name, get_colaboradores_ativos

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """
    Gerencia envio de mensagens WhatsApp.

    Integra formatação de mensagens com envio via Twilio.
    """

    def __init__(
        self,
        whatsapp_client: Optional[WhatsAppClient] = None,
        message_formatter: Optional[MessageFormatter] = None
    ):
        """
        Inicializa o sender.

        Args:
            whatsapp_client: Cliente WhatsApp (cria um novo se não fornecido)
            message_formatter: Formatador de mensagens (cria um novo se não fornecido)
        """
        self.whatsapp_client = whatsapp_client or WhatsAppClient()
        self.message_formatter = message_formatter or MessageFormatter()
        logger.info("WhatsAppSender inicializado")

    def _clean_whitespace(self, text: str) -> str:
        """
        Limpa indentação e espaços desnecessários das mensagens.

        Remove:
        - Indentação inicial (textwrap.dedent)
        - Espaços no final de cada linha
        - Linhas vazias no topo e rodapé

        Args:
            text: Texto original

        Returns:
            Texto limpo sem indentação e espaços extras
        """
        # Remove indentação comum
        text = textwrap.dedent(text)

        # Remove espaços no final de cada linha
        lines = [ln.rstrip() for ln in text.splitlines()]

        # Remove linhas vazias no topo
        while lines and not lines[0].strip():
            lines.pop(0)

        # Remove linhas vazias no rodapé
        while lines and not lines[-1].strip():
            lines.pop()

        return "\n".join(lines)

    def send_daily_tasks(
        self,
        person_name: str,
        include_greeting: bool = False
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia tasks diárias para um colaborador.

        Args:
            person_name: Nome completo do colaborador
            include_greeting: Se True, adiciona saudação temporal antes das tasks

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando tasks diárias para {person_name}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Formata mensagem
            message, tasks_grouped = self.message_formatter.format_daily_tasks(person_name)

            # Adiciona saudação temporal se solicitado
            if include_greeting:
                from src.messaging.humanizer import get_humanizer
                humanizer = get_humanizer()
                greeting = humanizer.get_greeting(person_name)
                message = f"{greeting}\n\n{message}"

            # Limpa whitespace antes de enviar
            message = self._clean_whitespace(message)

            # Envia mensagem
            success, sid, error = self.whatsapp_client.send_message(phone, message)

            if success:
                # Cria mapeamento de tasks (número → ID)
                task_mapper = get_task_mapper()
                task_mapper.create_mapping(person_name, tasks_grouped)
                logger.info(f"✅ Tasks enviadas para {person_name}. SID: {sid}")
            else:
                logger.error(f"❌ Falha ao enviar para {person_name}: {error}")

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar tasks para {person_name}: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def send_daily_tasks_to_all(self) -> Dict[str, Dict]:
        """
        Envia tasks diárias para todos os colaboradores ativos.

        Returns:
            Dict com resultados por pessoa:
            {
                "Estevao Antunes": {"success": True, "sid": "...", "error": None},
                ...
            }
        """
        logger.info("Enviando tasks diárias para todos os colaboradores")

        colaboradores = get_colaboradores_ativos()
        results = {}

        for nome in colaboradores.keys():
            success, sid, error = self.send_daily_tasks(nome)

            results[nome] = {
                "success": success,
                "sid": sid,
                "error": error
            }

        # Log de resumo
        successful = sum(1 for r in results.values() if r["success"])
        failed = len(results) - successful

        logger.info(
            f"📊 Envio em lote concluído: "
            f"{successful} sucessos, {failed} falhas"
        )

        return results

    def send_confirmation(
        self,
        person_name: str,
        action: str,
        task_name: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem de confirmação de ação.

        Args:
            person_name: Nome do colaborador
            action: Tipo de ação (done, in_progress, blocked)
            task_name: Nome da task

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando confirmação de {action} para {person_name}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Formata mensagem
            message = self.message_formatter.format_confirmation(
                action=action,
                task_name=task_name,
                person_name=person_name
            )

            # Limpa whitespace
            message = self._clean_whitespace(message)

            # Envia mensagem
            success, sid, error = self.whatsapp_client.send_message(phone, message)

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar confirmação: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def send_help(self, person_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem de ajuda.

        Args:
            person_name: Nome do colaborador

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando ajuda para {person_name}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Formata mensagem
            message = self.message_formatter.format_help()

            # Limpa whitespace
            message = self._clean_whitespace(message)

            # Envia mensagem
            success, sid, error = self.whatsapp_client.send_message(phone, message)

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar ajuda: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def send_error(
        self,
        person_name: str,
        error_type: str = "generic"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem de erro.

        Args:
            person_name: Nome do colaborador
            error_type: Tipo do erro

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando erro '{error_type}' para {person_name}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Formata mensagem
            message = self.message_formatter.format_error(error_type)

            # Limpa whitespace
            message = self._clean_whitespace(message)

            # Envia mensagem
            success, sid, error = self.whatsapp_client.send_message(phone, message)

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar mensagem de erro: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def send_message(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem genérica para um colaborador.

        Args:
            person_name: Nome do colaborador
            message: Texto da mensagem

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando mensagem para {person_name}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Limpa whitespace
            message = self._clean_whitespace(message)

            # Envia mensagem
            success, sid, error = self.whatsapp_client.send_message(phone, message)

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar mensagem: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    # Alias para compatibilidade
    def send_custom_message(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Alias para send_message (compatibilidade)."""
        return self.send_message(person_name, message)

    def send_audio_message(
        self,
        person_name: str,
        audio_file_path: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Envia mensagem de áudio para um colaborador.

        Args:
            person_name: Nome do colaborador
            audio_file_path: Caminho local do arquivo de áudio

        Returns:
            Tuple (sucesso, message_sid, erro)
        """
        logger.info(f"Enviando áudio para {person_name}: {audio_file_path}")

        try:
            # Busca telefone
            phone = get_phone_by_name(person_name)
            if not phone:
                error_msg = f"Telefone não encontrado para {person_name}"
                logger.error(error_msg)
                return False, None, error_msg

            # Envia áudio
            success, sid, error = self.whatsapp_client.send_audio(phone, audio_file_path)

            return success, sid, error

        except Exception as e:
            error_msg = f"Erro ao enviar áudio: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
