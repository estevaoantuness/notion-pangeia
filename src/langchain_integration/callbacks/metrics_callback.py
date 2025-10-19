"""
Metrics Callback - Tracking de métricas do Agent.

Tracks:
- Latência de respostas
- Tokens usados (input + output)
- Custo estimado
- Tools utilizados
- Taxa de sucesso
"""

import logging
import time
from typing import Any, Dict, List
from datetime import datetime

from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)


class MetricsCallback(BaseCallbackHandler):
    """
    Callback para tracking de métricas.

    Usage:
        agent = PangeiaAgent(
            ...
            callbacks=[MetricsCallback()]
        )
    """

    def __init__(self):
        """Inicializa callback."""
        super().__init__()

        # Métricas acumuladas
        self.total_messages = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.tool_usage = {}  # {tool_name: count}
        self.errors = 0
        self.start_times = {}  # {run_id: timestamp}

        # Métricas da conversação atual
        self.current_tokens = 0
        self.current_tools = []
        self.current_latency = 0.0

        logger.info("MetricsCallback inicializado")

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """LLM começou a processar."""
        run_id = kwargs.get("run_id")
        if run_id:
            self.start_times[run_id] = time.time()

        logger.debug(f"LLM started: {len(prompts)} prompts")

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """LLM terminou processamento."""
        run_id = kwargs.get("run_id")

        # Calcula latência
        if run_id and run_id in self.start_times:
            latency = time.time() - self.start_times[run_id]
            self.current_latency = latency
            del self.start_times[run_id]

            logger.debug(f"LLM finished: {latency*1000:.0f}ms")

        # Extrai tokens (se disponível)
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            if token_usage:
                total_tokens = token_usage.get("total_tokens", 0)
                self.current_tokens += total_tokens
                self.total_tokens += total_tokens

                # Calcula custo (GPT-4o-mini pricing)
                # $0.15 / 1M input tokens, $0.60 / 1M output tokens
                input_tokens = token_usage.get("prompt_tokens", 0)
                output_tokens = token_usage.get("completion_tokens", 0)

                cost = (input_tokens * 0.15 / 1_000_000) + \
                       (output_tokens * 0.60 / 1_000_000)

                self.total_cost += cost

                logger.debug(f"Tokens: {total_tokens} (${cost:.4f})")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any
    ) -> None:
        """Tool começou execução."""
        tool_name = serialized.get("name", "unknown")
        self.current_tools.append(tool_name)

        # Incrementa contador
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1

        logger.debug(f"Tool started: {tool_name}")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Tool terminou execução."""
        logger.debug(f"Tool finished: output_len={len(output)}")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Erro em tool."""
        self.errors += 1
        logger.error(f"Tool error: {error}")

    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Agent terminou processamento."""
        self.total_messages += 1

        logger.info(
            f"Agent finished: {self.current_latency*1000:.0f}ms, "
            f"{self.current_tokens} tokens, "
            f"{len(self.current_tools)} tools"
        )

        # Reset métricas da conversação atual
        self.current_tokens = 0
        self.current_tools = []
        self.current_latency = 0.0

    def get_stats(self) -> Dict:
        """
        Retorna estatísticas acumuladas.

        Returns:
            Dict com todas as métricas
        """
        return {
            "total_messages": self.total_messages,
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
            "avg_tokens_per_message": self.total_tokens // max(self.total_messages, 1),
            "tool_usage": self.tool_usage,
            "errors": self.errors,
            "most_used_tool": max(self.tool_usage.items(), key=lambda x: x[1])[0] if self.tool_usage else None
        }

    def reset_stats(self):
        """Reseta todas as estatísticas."""
        self.total_messages = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.tool_usage = {}
        self.errors = 0
        logger.info("Métricas resetadas")


# Instância global (singleton)
_global_metrics = MetricsCallback()


def get_metrics_callback() -> MetricsCallback:
    """Retorna instância global de metrics callback."""
    return _global_metrics


def get_stats() -> Dict:
    """Retorna estatísticas globais."""
    return _global_metrics.get_stats()
