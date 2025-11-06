"""
Redis Queue Client - Comunicação assíncrona entre agentes.

Este módulo implementa um cliente Redis para pub/sub, permitindo que os
agentes (Executor e Respondedor) se comuniquem de forma assíncrona através
de filas (listas Redis com LPUSH/BRPOP).

Arquitetura:
- Node 1 (Webhook): Publica em queue:incoming
- Node 2 (Executor): Consome de queue:incoming, publica em queue:responses
- Node 3 (Respondedor): Consome de queue:responses
"""

import redis
import json
import os
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisQueue:
    """
    Cliente Redis para comunicação entre agentes via filas (pub/sub).

    Usa listas Redis (LPUSH/BRPOP) para criar filas persistentes.
    Suporta múltiplos workers consumindo da mesma fila simultaneamente.
    """

    # Nomes das filas
    QUEUE_INCOMING = "queue:incoming"  # Mensagens recebidas do WhatsApp
    QUEUE_RESPONSES = "queue:responses"  # Respostas a enviar

    def __init__(self):
        """Inicializa conexão com Redis."""
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("REDIS_URL environment variable not configured")

        try:
            self.redis = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
            # Test connection
            self.redis.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    def publish_incoming(self, message_data: Dict) -> bool:
        """
        Publica mensagem na fila de entrada (para Node 2 - Executor).

        Args:
            message_data: Dicionário com dados da mensagem
                {
                    'from_number': '+5541...',
                    'message': 'texto da mensagem',
                    'push_name': 'Nome WhatsApp',
                    'message_type': 'conversation|audioMessage',
                    'timestamp': '2025-11-06T...'
                }

        Returns:
            True se publicado com sucesso, False caso contrário
        """
        try:
            json_data = json.dumps(message_data)
            self.redis.lpush(self.QUEUE_INCOMING, json_data)
            logger.debug(f"📤 Mensagem enfileirada em {self.QUEUE_INCOMING}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao publicar em Redis: {e}")
            return False

    def publish_response(self, response_data: Dict) -> bool:
        """
        Publica resposta na fila de saída (para Node 3 - Respondedor).

        Args:
            response_data: Dicionário com dados da resposta
                {
                    'to_number': '+5541...',
                    'text': 'texto da resposta',
                    'user_name': 'Estevão',
                    'timestamp': '2025-11-06T...'
                }

        Returns:
            True se publicado com sucesso, False caso contrário
        """
        try:
            json_data = json.dumps(response_data)
            self.redis.lpush(self.QUEUE_RESPONSES, json_data)
            logger.debug(f"📤 Resposta enfileirada em {self.QUEUE_RESPONSES}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao publicar resposta: {e}")
            return False

    def consume_incoming(self, timeout: int = 5) -> Optional[Dict]:
        """
        Consome mensagem da fila de entrada (usado por Node 2 - Executor).

        Args:
            timeout: Tempo máximo de espera em segundos (0 = sem timeout)

        Returns:
            Dicionário com dados da mensagem ou None se timeout
        """
        try:
            # BRPOP: Blocking Right Pop (aguarda com timeout)
            result = self.redis.brpop(self.QUEUE_INCOMING, timeout=timeout)

            if result:
                # result = (queue_name, json_data)
                json_data = result[1]
                message_data = json.loads(json_data)
                logger.debug(f"📥 Mensagem consumida de {self.QUEUE_INCOMING}")
                return message_data

            return None

        except Exception as e:
            logger.error(f"❌ Erro ao consumir de Redis: {e}")
            return None

    def consume_response(self, timeout: int = 5) -> Optional[Dict]:
        """
        Consome resposta da fila de saída (usado por Node 3 - Respondedor).

        Args:
            timeout: Tempo máximo de espera em segundos (0 = sem timeout)

        Returns:
            Dicionário com dados da resposta ou None se timeout
        """
        try:
            result = self.redis.brpop(self.QUEUE_RESPONSES, timeout=timeout)

            if result:
                json_data = result[1]
                response_data = json.loads(json_data)
                logger.debug(f"📥 Resposta consumida de {self.QUEUE_RESPONSES}")
                return response_data

            return None

        except Exception as e:
            logger.error(f"❌ Erro ao consumir resposta: {e}")
            return None

    def get_queue_lengths(self) -> Dict[str, int]:
        """
        Retorna tamanho de ambas as filas (útil para monitoramento).

        Returns:
            {'queue:incoming': 5, 'queue:responses': 2}
        """
        try:
            return {
                self.QUEUE_INCOMING: self.redis.llen(self.QUEUE_INCOMING),
                self.QUEUE_RESPONSES: self.redis.llen(self.QUEUE_RESPONSES),
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter tamanho das filas: {e}")
            return {}

    def clear_queues(self) -> bool:
        """
        Limpa ambas as filas (cuidado: remove todas as mensagens pendentes).

        Returns:
            True se limpas com sucesso
        """
        try:
            self.redis.delete(self.QUEUE_INCOMING, self.QUEUE_RESPONSES)
            logger.warning("⚠️  Filas limpas")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao limpar filas: {e}")
            return False

    def health_check(self) -> bool:
        """
        Verifica se conexão com Redis está ok.

        Returns:
            True se conectado e respondendo
        """
        try:
            self.redis.ping()
            return True
        except Exception:
            return False
