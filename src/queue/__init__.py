"""
Message Queue Module - Comunicação entre agentes via Redis.

Exports:
- RedisQueue: Client para pub/sub em Redis
"""

from .redis_client import RedisQueue

__all__ = ["RedisQueue"]
