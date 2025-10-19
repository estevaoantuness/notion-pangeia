"""
Error Tracking Callback - Rastreamento de erros do Agent.

Tracks:
- Erros de LLM
- Erros de tools
- Erros de parsing
- Stack traces
- Recovery attempts
"""

import logging
from typing import Any, Dict, List
from datetime import datetime
import traceback

from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)


class ErrorTrackingCallback(BaseCallbackHandler):
    """
    Callback para tracking de erros.

    Usage:
        agent = PangeiaAgent(
            ...
            callbacks=[ErrorTrackingCallback()]
        )
    """

    def __init__(self):
        """Inicializa callback."""
        super().__init__()

        # Erros rastreados
        self.errors: List[Dict] = []
        self.error_count = 0

        logger.info("ErrorTrackingCallback inicializado")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Erro no LLM."""
        self._track_error(
            error_type="LLM Error",
            error=error,
            context=kwargs
        )

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Erro em tool."""
        tool_name = kwargs.get("name", "unknown")
        self._track_error(
            error_type=f"Tool Error ({tool_name})",
            error=error,
            context=kwargs
        )

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Erro em chain."""
        self._track_error(
            error_type="Chain Error",
            error=error,
            context=kwargs
        )

    def on_agent_action(self, action, **kwargs: Any) -> None:
        """Agent executou ação (para debugging)."""
        logger.debug(f"Agent action: {action.tool} with input: {action.tool_input}")

    def _track_error(
        self,
        error_type: str,
        error: Exception,
        context: Dict
    ):
        """Rastreia erro completo."""
        self.error_count += 1

        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": self._sanitize_context(context)
        }

        self.errors.append(error_data)

        # Log error
        logger.error(
            f"{error_type}: {error.__class__.__name__}: {error}",
            exc_info=True
        )

        # Mantém só últimos 100 erros (evita memory leak)
        if len(self.errors) > 100:
            self.errors = self.errors[-100:]

    def _sanitize_context(self, context: Dict) -> Dict:
        """Remove informações sensíveis do context."""
        sanitized = {}
        for key, value in context.items():
            # Skip valores muito grandes
            if isinstance(value, str) and len(value) > 500:
                sanitized[key] = f"{value[:500]}... (truncated)"
            # Skip objetos complexos
            elif hasattr(value, "__dict__"):
                sanitized[key] = str(type(value))
            else:
                sanitized[key] = value

        return sanitized

    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """
        Retorna erros recentes.

        Args:
            limit: Número de erros a retornar

        Returns:
            Lista de erros recentes
        """
        return self.errors[-limit:]

    def get_error_summary(self) -> Dict:
        """
        Retorna resumo de erros.

        Returns:
            Dict com estatísticas de erros
        """
        if not self.errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "recent_errors": []
            }

        # Conta por tipo
        error_types = {}
        for error in self.errors:
            error_type = error["type"]
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1

        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            "recent_errors": self.get_recent_errors(5)
        }

    def clear_errors(self):
        """Limpa histórico de erros."""
        self.errors = []
        self.error_count = 0
        logger.info("Histórico de erros limpo")


# Instância global (singleton)
_global_error_tracker = ErrorTrackingCallback()


def get_error_tracking_callback() -> ErrorTrackingCallback:
    """Retorna instância global de error tracking callback."""
    return _global_error_tracker


def get_error_summary() -> Dict:
    """Retorna resumo de erros global."""
    return _global_error_tracker.get_error_summary()
