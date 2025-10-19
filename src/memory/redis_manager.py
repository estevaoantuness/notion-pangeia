"""
Redis Memory Manager - Gerenciamento de Memória Persistente.

Gerencia conversas usando Redis para compartilhamento entre workers.
"""

import logging
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Tentar importar Redis
try:
    import redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️  Redis não instalado - usando memória local (não persiste entre workers)")


class RedisMemoryManager:
    """
    Gerencia memória de conversas usando Redis.

    Permite que múltiplos workers Gunicorn compartilhem histórico de conversas.
    Fallback para memória local se Redis não estiver disponível.
    """

    def __init__(self, redis_url: Optional[str] = None, ttl_hours: int = 24):
        """
        Inicializa o gerenciador de memória.

        Args:
            redis_url: URL do Redis (default: variável de ambiente REDIS_URL)
            ttl_hours: Tempo de vida dos dados em horas (default: 24h)
        """
        self.ttl_seconds = ttl_hours * 3600
        self.redis_client = None
        self.local_fallback: Dict[str, List[Dict]] = {}

        # Tentar conectar ao Redis
        if REDIS_AVAILABLE:
            redis_url = redis_url or os.getenv("REDIS_URL")

            if redis_url:
                try:
                    self.redis_client = redis.from_url(
                        redis_url,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    # Test connection
                    self.redis_client.ping()
                    logger.info("✅ Redis conectado com sucesso")
                except Exception as e:
                    logger.error(f"❌ Erro ao conectar Redis: {e}")
                    self.redis_client = None
            else:
                logger.warning("⚠️  REDIS_URL não configurada - usando memória local")
        else:
            logger.warning("⚠️  Redis não disponível - usando memória local")

    def _get_key(self, user_id: str) -> str:
        """Gera chave Redis para usuário."""
        return f"conversation:{user_id}"

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        max_messages: int = 20
    ) -> None:
        """
        Adiciona mensagem ao histórico.

        Args:
            user_id: ID do usuário
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
            max_messages: Máximo de mensagens a manter
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        # Tentar usar Redis
        if self.redis_client:
            try:
                key = self._get_key(user_id)

                # Buscar histórico atual
                history_json = self.redis_client.get(key)
                history = json.loads(history_json) if history_json else []

                # Adicionar nova mensagem
                history.append(message)

                # Manter apenas as últimas N mensagens
                if len(history) > max_messages:
                    history = history[-max_messages:]

                # Salvar de volta no Redis com TTL
                self.redis_client.setex(
                    key,
                    self.ttl_seconds,
                    json.dumps(history)
                )

                logger.debug(f"Mensagem salva no Redis para {user_id}")
                return

            except (RedisError, RedisConnectionError) as e:
                logger.error(f"Erro ao salvar mensagem no Redis: {e}")
                # Continua para fallback

        # Fallback: memória local
        if user_id not in self.local_fallback:
            self.local_fallback[user_id] = []

        self.local_fallback[user_id].append(message)

        # Limitar tamanho
        if len(self.local_fallback[user_id]) > max_messages:
            self.local_fallback[user_id] = self.local_fallback[user_id][-max_messages:]

        logger.debug(f"Mensagem salva em memória local para {user_id}")

    def get_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtém histórico de conversa.

        Args:
            user_id: ID do usuário
            limit: Limitar número de mensagens retornadas

        Returns:
            Lista de mensagens: [{"role": "user", "content": "...", "timestamp": "..."}]
        """
        # Tentar usar Redis
        if self.redis_client:
            try:
                key = self._get_key(user_id)
                history_json = self.redis_client.get(key)

                if history_json:
                    history = json.loads(history_json)

                    if limit:
                        history = history[-limit:]

                    logger.debug(f"Histórico recuperado do Redis para {user_id}: {len(history)} msgs")
                    return history

            except (RedisError, RedisConnectionError) as e:
                logger.error(f"Erro ao recuperar histórico do Redis: {e}")
                # Continua para fallback

        # Fallback: memória local
        history = self.local_fallback.get(user_id, [])

        if limit:
            history = history[-limit:]

        logger.debug(f"Histórico recuperado da memória local para {user_id}: {len(history)} msgs")
        return history

    def clear_history(self, user_id: str) -> None:
        """
        Limpa histórico de um usuário.

        Args:
            user_id: ID do usuário
        """
        # Tentar usar Redis
        if self.redis_client:
            try:
                key = self._get_key(user_id)
                self.redis_client.delete(key)
                logger.info(f"Histórico limpo no Redis para {user_id}")
                return
            except (RedisError, RedisConnectionError) as e:
                logger.error(f"Erro ao limpar histórico no Redis: {e}")
                # Continua para fallback

        # Fallback: memória local
        if user_id in self.local_fallback:
            del self.local_fallback[user_id]
            logger.info(f"Histórico limpo na memória local para {user_id}")

    def get_all_user_ids(self) -> List[str]:
        """
        Retorna lista de todos os user_ids com histórico.

        Returns:
            Lista de user_ids
        """
        # Tentar usar Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys("conversation:*")
                user_ids = [key.replace("conversation:", "") for key in keys]
                return user_ids
            except (RedisError, RedisConnectionError) as e:
                logger.error(f"Erro ao buscar user_ids no Redis: {e}")
                # Continua para fallback

        # Fallback: memória local
        return list(self.local_fallback.keys())

    def cleanup_old_conversations(self, max_age_hours: int = 48) -> int:
        """
        Remove conversas antigas.

        Args:
            max_age_hours: Idade máxima em horas

        Returns:
            Número de conversas removidas
        """
        removed = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Redis tem TTL automático, então apenas limpamos memória local
        for user_id in list(self.local_fallback.keys()):
            history = self.local_fallback[user_id]

            # Filtrar mensagens antigas
            filtered = [
                msg for msg in history
                if datetime.fromisoformat(msg["timestamp"]) > cutoff_time
            ]

            if len(filtered) == 0:
                del self.local_fallback[user_id]
                removed += 1
            else:
                self.local_fallback[user_id] = filtered

        if removed > 0:
            logger.info(f"Limpeza: {removed} conversas antigas removidas")

        return removed

    def is_redis_available(self) -> bool:
        """
        Verifica se Redis está disponível e funcionando.

        Returns:
            True se Redis está conectado e respondendo
        """
        if not self.redis_client:
            return False

        try:
            return self.redis_client.ping()
        except Exception:
            return False

    def get_stats(self) -> Dict:
        """
        Retorna estatísticas de uso.

        Returns:
            Dict com estatísticas
        """
        stats = {
            "redis_available": self.is_redis_available(),
            "total_conversations": 0,
            "total_messages": 0,
            "storage": "redis" if self.is_redis_available() else "local"
        }

        # Contar conversas
        if self.redis_client and self.is_redis_available():
            try:
                keys = self.redis_client.keys("conversation:*")
                stats["total_conversations"] = len(keys)

                # Contar mensagens aproximadas
                for key in keys[:100]:  # Amostra de 100 para performance
                    history_json = self.redis_client.get(key)
                    if history_json:
                        history = json.loads(history_json)
                        stats["total_messages"] += len(history)

            except Exception as e:
                logger.error(f"Erro ao coletar stats do Redis: {e}")
        else:
            # Stats da memória local
            stats["total_conversations"] = len(self.local_fallback)
            stats["total_messages"] = sum(len(h) for h in self.local_fallback.values())

        return stats


# Singleton
_memory_instance = None


def get_memory_manager() -> RedisMemoryManager:
    """Obtém instância singleton do gerenciador de memória."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = RedisMemoryManager()
    return _memory_instance
