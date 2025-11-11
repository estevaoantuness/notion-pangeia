"""
Parser de comandos WhatsApp.

Este módulo analisa mensagens recebidas via WhatsApp e extrai
comandos estruturados para processamento.
"""

import logging
import re
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parse de mensagens em comandos estruturados.

    Identifica e extrai informações de comandos enviados via WhatsApp.
    """

    # Patterns de comandos
    PATTERNS = {
        # Marcar como feito: "feito 1", "concluí 2", "finalizado 3"
        "done": r"^(feito|conclu[ií]|finalizado?|done)\s+(\d+)",

        # Marcar em andamento: "andamento 1", "fazendo 2"
        "in_progress": r"^(andamento|fazendo|working)\s+(\d+)",

        # Marcar bloqueada: "bloqueada 1 - motivo", "problema 2 - descrição"
        "blocked": r"^(bloqueada?|problema|blocked?)\s+(\d+)\s*-\s*(.+)",

        # Listar tasks: "minhas tarefas", "lista", "tasks"
        "list": r"^(minhas\s+tarefas?|lista|tasks?|tarefas?)$",

        # Ver progresso: "progresso", "status"
        "progress": r"^(progresso|status)$",

        # Ajuda: "ajuda", "help", "?"
        "help": r"^(ajuda|help|\?)$",
    }

    @staticmethod
    def parse(message: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Parse uma mensagem em comando estruturado.

        Args:
            message: Mensagem recebida do usuário

        Returns:
            Tuple (command_type, command_data) ou (None, None) se não reconhecido
        """
        # Normaliza mensagem
        message = message.strip().lower()

        logger.info(f"Parseando mensagem: '{message}'")

        # Tenta match com cada pattern
        for command_type, pattern in CommandParser.PATTERNS.items():
            match = re.match(pattern, message, re.IGNORECASE)

            if match:
                command_data = CommandParser._extract_data(command_type, match)
                logger.info(f"Comando reconhecido: {command_type} - {command_data}")
                return command_type, command_data

        logger.info("Comando não reconhecido")
        return None, None

    @staticmethod
    def _extract_data(command_type: str, match: re.Match) -> Dict:
        """
        Extrai dados específicos do comando baseado no tipo.

        Args:
            command_type: Tipo do comando
            match: Match object do regex

        Returns:
            Dict com dados extraídos
        """
        if command_type == "done":
            return {
                "task_number": int(match.group(2))
            }

        elif command_type == "in_progress":
            return {
                "task_number": int(match.group(2))
            }

        elif command_type == "blocked":
            return {
                "task_number": int(match.group(2)),
                "reason": match.group(3).strip()
            }

        elif command_type in ["list", "progress", "help"]:
            return {}

        return {}

    @staticmethod
    def extract_task_number(message: str) -> Optional[int]:
        """
        Extrai número da task de uma mensagem.

        Args:
            message: Mensagem do usuário

        Returns:
            Número da task ou None
        """
        match = re.search(r"\d+", message)
        if match:
            return int(match.group())
        return None

    @staticmethod
    def is_command(message: str) -> bool:
        """
        Verifica se mensagem é um comando válido.

        Args:
            message: Mensagem do usuário

        Returns:
            True se é um comando reconhecido
        """
        command_type, _ = CommandParser.parse(message)
        return command_type is not None
