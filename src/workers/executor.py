#!/usr/bin/env python3
"""
Worker Executor - Agente de Ação (NODE 2)

Responsabilidades:
- Consome mensagens da fila queue:incoming
- Processa comandos via NLP/GPT
- Atualiza Notion com resultados
- Publica resposta na fila queue:responses

Fluxo:
  [Webhook] → queue:incoming → [EXECUTOR] → queue:responses → [Responder]
"""

import logging
import os
import sys
from datetime import datetime
import time

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.queue import RedisQueue
from src.commands.processor import CommandProcessor
from config.colaboradores import get_colaborador_by_phone

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ExecutorWorker:
    """Worker que processa comandos e atualiza Notion."""

    def __init__(self):
        """Inicializa conexões e componentes necessários."""
        try:
            self.queue = RedisQueue()
            self.processor = CommandProcessor()
            logger.info("✅ Executor Worker inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Executor: {e}")
            raise

    def process_message(self, message_data: dict) -> bool:
        """
        Processa uma mensagem individual.

        Args:
            message_data: Dicionário com dados da mensagem

        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            from_number = message_data.get("from_number")
            message = message_data.get("message")
            push_name = message_data.get("push_name", "Usuário")

            if not from_number or not message:
                logger.warning(f"⚠️  Mensagem incompleta: {message_data}")
                return False

            logger.info(f"📥 Processando: {from_number} - {message[:50]}")

            # 1. Identifica usuário pelo telefone
            user_name = get_colaborador_by_phone(from_number)
            if user_name:
                logger.info(f"✅ Usuário identificado: {user_name}")
            else:
                logger.debug(f"⚠️  Usuário não identificado: {from_number}")
                user_name = push_name  # Fallback para push_name

            # 2. Processa comando via NLP/GPT
            success, response_text = self.processor.process(
                from_number=from_number, message=message
            )

            if not success or not response_text:
                logger.error(f"❌ Erro ao processar comando")
                response_text = "Desculpe, tive um erro ao processar sua mensagem. Tente novamente."

            logger.info(f"✅ Comando processado: {response_text[:50]}...")

            # 3. Publica resposta na fila para Respondedor enviar
            response_data = {
                "to_number": from_number,
                "text": response_text,
                "user_name": user_name,
                "timestamp": datetime.now().isoformat(),
            }

            if self.queue.publish_response(response_data):
                logger.info(f"✅ Resposta enfileirada para {user_name}")
                return True
            else:
                logger.error(f"❌ Falha ao enfileirar resposta")
                return False

        except Exception as e:
            logger.error(f"💥 Erro ao processar mensagem: {e}", exc_info=True)
            return False

    def run(self):
        """
        Loop principal do worker.

        Continua rodando indefinidamente, aguardando mensagens na fila.
        """
        logger.info("🚀 Executor Worker iniciado - aguardando mensagens...")
        logger.info(f"   Redis URL: {os.getenv('REDIS_URL', 'não configurado')[:30]}...")

        error_count = 0
        max_consecutive_errors = 5

        while True:
            try:
                # Consome mensagem da fila (blocking com timeout de 5s)
                message_data = self.queue.consume_incoming(timeout=5)

                if message_data:
                    # Reseta contador de erros se processou com sucesso
                    if self.process_message(message_data):
                        error_count = 0
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
                    # Nenhuma mensagem (timeout) - continua aguardando
                    pass

            except KeyboardInterrupt:
                logger.info("⏸️  Executor Worker parado pelo usuário")
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
        worker = ExecutorWorker()
        worker.run()
    except Exception as e:
        logger.critical(f"❌ Falha crítica: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
