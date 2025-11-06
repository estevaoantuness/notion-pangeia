#!/usr/bin/env python3
"""
Worker Respondedor - Agente de Comunicação (NODE 3)

Responsabilidades:
- Consome respostas da fila queue:responses
- Humaniza mensagens
- Envia via WhatsApp (Evolution API)
- Gera áudio TTS (se aplicável)

Fluxo:
  [Webhook] → queue:incoming → [Executor] → queue:responses → [RESPONDEDOR]
"""

import logging
import os
import sys
from datetime import datetime
import time

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.queue import RedisQueue
from src.whatsapp.sender import WhatsAppSender
from src.messaging.humanizer import get_humanizer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ResponderWorker:
    """Worker que envia respostas via WhatsApp."""

    def __init__(self):
        """Inicializa conexões e componentes necessários."""
        try:
            self.queue = RedisQueue()
            self.sender = WhatsAppSender()
            self.humanizer = get_humanizer()
            logger.info("✅ Responder Worker inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Responder: {e}")
            raise

    def send_response(self, response_data: dict) -> bool:
        """
        Envia uma resposta via WhatsApp.

        Args:
            response_data: Dicionário com dados da resposta

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            to_number = response_data.get("to_number")
            text = response_data.get("text", "")
            user_name = response_data.get("user_name", "Usuário")

            if not to_number or not text:
                logger.warning(f"⚠️  Resposta incompleta: {response_data}")
                return False

            logger.info(f"📤 Enviando para {user_name} ({to_number})")

            # 1. Humaniza a mensagem (remove whitespace extra, etc)
            humanized_text = self.humanizer.humanize(text)

            logger.debug(f"   Original: {text[:50]}...")
            logger.debug(f"   Humanized: {humanized_text[:50]}...")

            # 2. Envia via WhatsApp
            success, sid, error = self.sender.send_message(
                person_name=to_number, message=humanized_text
            )

            if success:
                logger.info(f"✅ Mensagem enviada. SID: {sid}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar: {error}")
                return False

        except Exception as e:
            logger.error(f"💥 Erro ao enviar resposta: {e}", exc_info=True)
            return False

    def run(self):
        """
        Loop principal do worker.

        Continua rodando indefinidamente, aguardando respostas na fila.
        """
        logger.info("🚀 Responder Worker iniciado - aguardando respostas...")
        logger.info(
            f"   Redis URL: {os.getenv('REDIS_URL', 'não configurado')[:30]}..."
        )

        error_count = 0
        max_consecutive_errors = 5

        while True:
            try:
                # Consome resposta da fila (blocking com timeout de 5s)
                response_data = self.queue.consume_response(timeout=5)

                if response_data:
                    # Tenta enviar
                    if self.send_response(response_data):
                        error_count = 0  # Reseta contador de erros
                    else:
                        error_count += 1

                    # Se muitos erros consecutivos, aguarda mais tempo
                    if error_count >= max_consecutive_errors:
                        logger.warning(
                            f"⚠️  {error_count} erros consecutivos. Aguardando 10s..."
                        )
                        time.sleep(10)
                        error_count = 0

                else:
                    # Nenhuma resposta (timeout) - continua aguardando
                    pass

            except KeyboardInterrupt:
                logger.info("⏸️  Responder Worker parado pelo usuário")
                break

            except Exception as e:
                logger.error(f"💥 Erro no loop principal: {e}", exc_info=True)
                error_count += 1

                if error_count >= max_consecutive_errors:
                    logger.critical(
                        f"❌ Muitos erros consecutivos ({error_count}). Reinicie o worker."
                    )
                    time.sleep(30)
                    error_count = 0


def main():
    """Entry point do script."""
    try:
        worker = ResponderWorker()
        worker.run()
    except Exception as e:
        logger.critical(f"❌ Falha crítica: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
