"""
Servidor Flask para webhook da Evolution API.

Este módulo implementa o servidor web que recebe mensagens do WhatsApp
via webhook da Evolution API e processa comandos dos colaboradores.
"""

import logging
from flask import Flask, request, Response, jsonify

from src.commands.processor import CommandProcessor
from src.scheduler import get_scheduler
from src.whatsapp.psychological_sender import PsychologicalSender
from src.psychology.engine import PsychologicalEngine
from config.settings import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializa Flask
app = Flask(__name__)

# Inicializa componentes psicológicos
psych_engine = PsychologicalEngine()
psychological_sender = PsychologicalSender()

# Inicializa processador de comandos
command_processor = CommandProcessor()

# Inicializa e configura scheduler
scheduler = get_scheduler()
scheduler.setup_jobs()
scheduler.start()


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check.

    Returns:
        JSON com status do serviço
    """
    return {
        "status": "healthy",
        "service": "notion-pangeia-webhook",
        "version": "1.0.0",
        "scheduler": "running" if scheduler.scheduler.running else "stopped"
    }, 200


@app.route('/scheduler/jobs', methods=['GET'])
def scheduler_jobs():
    """
    Lista todos os jobs agendados.

    Returns:
        JSON com lista de jobs
    """
    try:
        jobs = scheduler.scheduler.get_jobs()
        jobs_data = []

        for job in jobs:
            next_run = job.next_run_time
            jobs_data.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_run.isoformat() if next_run else None,
                "trigger": str(job.trigger)
            })

        return {
            "status": "success",
            "total_jobs": len(jobs_data),
            "jobs": jobs_data
        }, 200

    except Exception as e:
        logger.error(f"Erro ao listar jobs: {e}")
        return {
            "status": "error",
            "message": str(e)
        }, 500


@app.route('/scheduler/run/<job_id>', methods=['POST'])
def scheduler_run_job(job_id: str):
    """
    Executa um job manualmente (para testes).

    Args:
        job_id: ID do job a executar

    Returns:
        JSON com resultado
    """
    try:
        success = scheduler.run_job_now(job_id)

        if success:
            return {
                "status": "success",
                "message": f"Job '{job_id}' executado com sucesso"
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Job '{job_id}' não encontrado"
            }, 404

    except Exception as e:
        logger.error(f"Erro ao executar job: {e}")
        return {
            "status": "error",
            "message": str(e)
        }, 500


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook principal para receber mensagens do WhatsApp via Evolution API.

    Recebe mensagens em formato JSON, processa comandos e retorna resposta JSON.

    Returns:
        JSON response
    """
    try:
        # Log da requisição
        logger.info("=" * 60)
        logger.info("📨 MENSAGEM RECEBIDA VIA WEBHOOK")
        logger.info("=" * 60)

        # Validação de API Key (temporariamente desabilitada para debugging)
        api_key = request.headers.get('apikey', '')
        logger.info(f"API Key recebida: {api_key[:10]}... (esperada: {settings.EVOLUTION_API_KEY[:10]}...)")
        # if api_key != settings.EVOLUTION_API_KEY:
        #     logger.warning("⚠️ API Key inválida")
        #     return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Extrai dados do payload JSON
        payload = request.json

        if not payload:
            logger.warning("Payload vazio")
            return jsonify({"status": "error", "message": "Empty payload"}), 400

        # Estrutura do payload Evolution API:
        # {
        #   "event": "messages.upsert",
        #   "instance": "instance_name",
        #   "data": {
        #     "key": {
        #       "remoteJid": "5511999999999@s.whatsapp.net",
        #       "fromMe": false,
        #       "id": "message_id"
        #     },
        #     "message": {
        #       "conversation": "texto da mensagem"
        #     },
        #     "messageType": "conversation",
        #     "pushName": "Nome do Contato"
        #   }
        # }

        event = payload.get('event', '')
        data = payload.get('data', {})

        # Ignora mensagens que não são do tipo messages.upsert
        if event != 'messages.upsert':
            logger.info(f"Evento ignorado: {event}")
            return jsonify({"status": "success", "message": "Event ignored"}), 200

        # Análise psicológica da mensagem recebida
        psychological_context = psych_engine.analyze_message_sentiment(data.get('message', {}).get('conversation', ''))
        logger.info(f"Contexto psicológico: {psychological_context}")

        # Extrai informações da mensagem
        key = data.get('key', {})
        message_data = data.get('message', {})

        # Ignora mensagens enviadas pelo próprio bot
        if key.get('fromMe', False):
            logger.info("Mensagem do próprio bot - ignorada")
            return jsonify({"status": "success", "message": "Own message ignored"}), 200

        # Extrai número do remetente
        remote_jid = key.get('remoteJid', '')
        from_number = remote_jid.replace('@s.whatsapp.net', '').replace('@g.us', '')

        # Adiciona + se não tiver
        if not from_number.startswith('+'):
            from_number = '+' + from_number

        # Extrai texto da mensagem
        message_body = message_data.get('conversation', '')

        # Tenta outros campos se conversation estiver vazio
        if not message_body:
            # Tenta extendedTextMessage
            extended = message_data.get('extendedTextMessage', {})
            message_body = extended.get('text', '')

        message_body = message_body.strip()

        # Extrai nome do contato
        push_name = data.get('pushName', 'Desconhecido')

        logger.info(f"From: {from_number} ({push_name})")
        logger.info(f"Message: {message_body}")
        logger.info(f"Event: {event}")

        # Valida que temos os dados necessários
        if not from_number or not message_body:
            logger.warning("Mensagem sem dados necessários")
            return jsonify({"status": "error", "message": "Invalid message"}), 400

        # Processa comando
        success, response_text = command_processor.process(
            from_number=from_number,
            message=message_body
        )

        # Log do resultado com contexto
        if success:
            logger.info(
                f"✅ Comando processado com sucesso",
                extra={
                    "from_number": from_number,
                    "push_name": push_name,
                    "user_message": message_body,
                    "success": success,
                    "response_length": len(response_text) if response_text else 0
                }
            )
            if response_text:
                logger.info(f"Resposta: {response_text[:100]}...")
                # Envia resposta via WhatsApp
                from src.whatsapp.sender import WhatsAppSender
                sender = WhatsAppSender()
                sender.send_message(person_name=push_name, message=response_text)
        else:
            logger.warning(
                f"❌ Falha ao processar comando",
                extra={
                    "from_number": from_number,
                    "push_name": push_name,
                    "user_message": message_body,
                    "success": success
                }
            )
            if response_text:
                logger.warning(f"Erro: {response_text}")
                # Envia mensagem de erro via WhatsApp
                from src.whatsapp.sender import WhatsAppSender
                sender = WhatsAppSender()
                sender.send_message(person_name=push_name, message=response_text)

        # Retorna sucesso
        # Com Evolution API, não retornamos mensagens no webhook
        # As respostas são enviadas via API diretamente
        return jsonify({
            "status": "success",
            "processed": success,
            "message": "Command processed"
        }), 200

    except Exception as e:
        logger.exception(
            f"💥 Erro ao processar webhook",
            extra={
                "payload": payload if 'payload' in locals() else None,
                "error": str(e)
            }
        )

        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@app.route('/webhook/whatsapp/status', methods=['POST'])
def whatsapp_status_callback():
    """
    Callback de status de mensagens (delivery, read, etc).

    Returns:
        JSON response
    """
    try:
        payload = request.json

        event = payload.get('event', '')
        data = payload.get('data', {})

        logger.info(f"📊 Status callback - Event: {event}")

        # Aqui você pode implementar lógica para rastrear status de mensagens
        # Por exemplo, atualizar um banco de dados com o status de entrega

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Erro no status callback: {e}")
        return jsonify({"status": "success"}), 200  # Sempre retorna 200 para não causar retries


def validate_api_key() -> bool:
    """
    Valida que a requisição tem API Key válida.

    Returns:
        True se válida, False caso contrário
    """
    try:
        api_key = request.headers.get('apikey', '')

        is_valid = (api_key == settings.EVOLUTION_API_KEY)

        if not is_valid:
            logger.warning("⚠️ API Key inválida!")

        return is_valid

    except Exception as e:
        logger.error(f"Erro ao validar API Key: {e}")
        return False


if __name__ == '__main__':
    """
    Execução direta do servidor (desenvolvimento).

    Para produção, use gunicorn ou similar:
    gunicorn -w 4 -b 0.0.0.0:5000 src.webhook.app:app
    """
    PORT = 5001  # Mudado para 5001 (porta 5000 usada pelo AirPlay no macOS)

    logger.info("=" * 60)
    logger.info("🚀 SERVIDOR WEBHOOK INICIANDO")
    logger.info("=" * 60)
    logger.info(f"Porta: {PORT}")
    logger.info(f"Endpoint: http://localhost:{PORT}/webhook/whatsapp")
    logger.info(f"Health: http://localhost:{PORT}/health")
    logger.info("=" * 60)

    # Executa servidor
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=settings.DEBUG if hasattr(settings, 'DEBUG') else False
    )
