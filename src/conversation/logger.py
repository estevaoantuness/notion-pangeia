"""
Conversation Logger - Registro de Conversas.

Sistema para registrar e analisar conversas para melhorar o sistema.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Registra conversas para análise e melhoria contínua."""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Inicializa o logger de conversas.

        Args:
            storage_dir: Diretório para armazenar logs
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".pangeia" / "conversations"
        else:
            storage_dir = Path(storage_dir)

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ConversationLogger inicializado em {self.storage_dir}")

    def log_conversation(
        self,
        user_id: str,
        person_name: str,
        user_message: str,
        bot_response: str,
        tokens_used: int = 0,
        response_time_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra uma interação conversacional.

        Args:
            user_id: ID único do usuário
            person_name: Nome da pessoa
            user_message: Mensagem do usuário
            bot_response: Resposta do bot
            tokens_used: Tokens utilizados na geração
            response_time_ms: Tempo de resposta em ms
            metadata: Metadados adicionais
        """
        try:
            # Diretório por pessoa
            person_dir = self.storage_dir / person_name.replace(" ", "_")
            person_dir.mkdir(parents=True, exist_ok=True)

            # Arquivo por data
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = person_dir / f"{today}.jsonl"

            # Cria registro
            record = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "person_name": person_name,
                "user_message": user_message,
                "bot_response": bot_response,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms,
                "metadata": metadata or {}
            }

            # Escreve no arquivo (append)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            logger.debug(f"Conversa registrada para {person_name}")

        except Exception as e:
            logger.error(f"Erro ao registrar conversa: {e}")

    def analyze_patterns(self, person_name: str) -> Dict[str, Any]:
        """
        Analisa padrões de conversa de uma pessoa.

        Args:
            person_name: Nome da pessoa

        Returns:
            Dicionário com padrões identificados
        """
        try:
            person_dir = self.storage_dir / person_name.replace(" ", "_")

            if not person_dir.exists():
                return {}

            all_messages = []
            total_tokens = 0
            total_time = 0.0
            interaction_count = 0

            # Lê todos os logs da pessoa
            for log_file in person_dir.glob("*.jsonl"):
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            record = json.loads(line)
                            all_messages.append(record)
                            total_tokens += record.get("tokens_used", 0)
                            total_time += record.get("response_time_ms", 0)
                            interaction_count += 1
                        except json.JSONDecodeError:
                            pass

            if interaction_count == 0:
                return {}

            # Calcula estatísticas
            avg_time = total_time / interaction_count
            avg_tokens = total_tokens / interaction_count

            return {
                "person_name": person_name,
                "total_interactions": interaction_count,
                "total_tokens_used": total_tokens,
                "average_response_time_ms": avg_time,
                "average_tokens_per_response": avg_tokens,
                "recent_messages": all_messages[-10:]  # Últimas 10
            }

        except Exception as e:
            logger.error(f"Erro ao analisar padrões: {e}")
            return {}


# Singleton
_logger_instance = None


def get_conversation_logger() -> ConversationLogger:
    """Obtém instância singleton do logger."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ConversationLogger()
    return _logger_instance
