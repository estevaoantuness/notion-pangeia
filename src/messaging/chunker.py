"""
Message Chunker - Quebra inteligente de mensagens.

Divide mensagens longas em chunks humanizados para melhor
experiência no WhatsApp e redução de tokens.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class MessageChunker:
    """Divide mensagens longas em chunks lógicos e humanizados."""

    MAX_CHUNK_SIZE = 1000  # caracteres

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size

    def chunk_message(self, message: str) -> List[str]:
        """
        Divide mensagem em chunks lógicos.

        Estratégia: seções → parágrafos → sentenças → tamanho
        """
        if len(message) <= self.max_size:
            return [message]

        # Tentar quebrar por seções (linhas duplas)
        chunks = re.split(r'\n\n+', message)
        chunks = [s.strip() for s in chunks if s.strip()]

        # Se algum chunk é grande, re-dividir
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.max_size:
                final_chunks.append(chunk)
            else:
                # Dividir por parágrafos
                paragraphs = chunk.split('\n')
                current = ""
                for para in paragraphs:
                    if len(current) + len(para) + 1 <= self.max_size:
                        current += para + "\n"
                    else:
                        if current:
                            final_chunks.append(current.strip())
                        current = para + "\n"
                if current:
                    final_chunks.append(current.strip())

        return final_chunks
