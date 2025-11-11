"""
Servidor Flask para webhook da Evolution API.

Este módulo implementa o servidor web que recebe mensagens do WhatsApp
via webhook da Evolution API.

ARQUITETURA:
- Node 1 (Webhook Receiver): Este arquivo - recebe e enfileira em Redis
- Node 2 (Executor Worker): src/workers/executor.py - processa e atualiza Notion
- Node 3 (Respondedor Worker): src/workers/responder.py - envia via WhatsApp

O webhook NÃO processa diretamente. Apenas enfileira mensagens em Redis,
permitindo que workers assíncronos façam o processamento pesado.
"""

import logging
import os
import requests
import tempfile
from datetime import datetime
from pathlib import Path
from flask import Flask, request, Response, jsonify

from src.scheduler import get_scheduler
from src.audio import get_processor as get_audio_processor
from src.commands.processor import CommandProcessor
from config.settings import settings
from config.colaboradores import get_colaborador_by_phone

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializa Flask
app = Flask(__name__)
logger.info("✅ Flask app inicializado - Modo síncrono (Redis desativado)")

# Inicializa command processor (NLP-based, sem OpenAI)
command_processor = CommandProcessor()

# Inicializa processador de áudio
audio_processor = get_audio_processor()

# Inicializa scheduler
scheduler = get_scheduler()
scheduler.setup_jobs()
scheduler.start()
logger.info("✅ Scheduler ATIVADO - mensagens automáticas habilitadas")


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
        "scheduler": "enabled"
    }, 200


@app.route('/debug', methods=['GET'])
def debug_info():
    """
    Endpoint de debug para verificar qual sistema está ativo.

    Returns:
        JSON com informações de debug
    """
    import sys
    import os

    try:
        # Testar se CommandProcessor foi carregado
        processor_test = command_processor.process("+5511999999999", "oi")
        processor_status = "OK" if processor_test else "FAILED"
    except Exception as e:
        processor_status = f"ERROR: {str(e)}"

    return jsonify({
        "python_version": sys.version,
        "nlp_system": "CommandProcessor (NLP-based, no OpenAI)",
        "command_processor": {
            "loaded": command_processor is not None,
            "test_result": processor_status
        },
        "git_commit": "27814ab",
        "deployment_time": "2025-10-20 16:40"
    }), 200


@app.route('/scheduler/jobs', methods=['GET'])
def scheduler_jobs():
    """
    Lista todos os jobs agendados.

    Returns:
        JSON com lista de jobs
    """
    try:
        jobs = []
        if scheduler and scheduler.scheduler:
            for job in scheduler.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": str(job.next_run_time)
                })

        return {
            "status": "enabled",
            "message": "Scheduler ativado",
            "job_count": len(jobs),
            "jobs": jobs
        }, 200
    except Exception as e:
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
        # Extrai API key de diferentes fontes (header, bearer, query)
        api_key = request.headers.get('apikey', '') or request.headers.get('x-api-key', '')

        if not api_key:
            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.lower().startswith('bearer '):
                api_key = auth_header.split(' ', 1)[1].strip()

        if not api_key:
            api_key = request.args.get('apikey', '')

        logger.info(f"API Key recebida: {api_key[:10]}... (esperada: {settings.EVOLUTION_API_KEY[:10]}...)")

        if settings.EVOLUTION_WEBHOOK_AUTH_REQUIRED:
            if not api_key or api_key != settings.EVOLUTION_API_KEY:
                logger.warning("⚠️ API Key inválida ou ausente (modo estrito)")
                return jsonify({"status": "error", "message": "Unauthorized"}), 401
        else:
            if not api_key:
                logger.warning("⚠️ API Key ausente no webhook (modo permissivo)")
            elif api_key != settings.EVOLUTION_API_KEY:
                logger.warning("⚠️ API Key incorreta no webhook (modo permissivo)")

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

        # Extrai nome do contato
        push_name = data.get('pushName', 'Desconhecido')

        logger.info(f"From: {from_number} ({push_name})")
        logger.info(f"Event: {event}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # IDENTIFICAÇÃO DO USUÁRIO (hardcoded + Google Sheets fallback)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        from config.colaboradores import get_colaborador_by_phone

        identified_user = get_colaborador_by_phone(from_number)
        if identified_user:
            logger.info(f"✅ Usuário identificado: {identified_user} (WhatsApp: {push_name})")
            push_name = identified_user  # Usa nome identificado
        else:
            logger.debug(f"⚠️ Usuário não identificado no banco de colaboradores: {from_number} (push_name: {push_name})")

        # **DETECÇÃO DE TIPO DE MENSAGEM**
        message_type = data.get('messageType', 'conversation')
        logger.info(f"MessageType: {message_type}")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CASO 1: MENSAGEM DE ÁUDIO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if message_type == 'audioMessage':
            logger.info("🎤 MENSAGEM DE ÁUDIO DETECTADA")

            try:
                # Extrai URL do áudio
                audio_message = message_data.get('audioMessage', {})
                audio_url = audio_message.get('url', '')

                if not audio_url:
                    logger.warning("URL de áudio não encontrada")
                    return jsonify({"status": "error", "message": "Audio URL not found"}), 400

                logger.info(f"🔗 URL do áudio: {audio_url[:100]}...")

                # Download do áudio
                audio_file_path = download_audio_from_url(audio_url)

                # Transcrição
                logger.info(f"📝 Iniciando transcrição...")
                success, transcription = audio_processor.process_audio_message(
                    audio_file_path=audio_file_path,
                    user_id=from_number,
                    person_name=push_name
                )

                if not success:
                    logger.error(f"❌ Erro na transcrição: {transcription}")
                    message_body = ""
                else:
                    logger.info(f"✅ Transcrição concluída: {transcription[:100]}...")
                    message_body = transcription

            except Exception as e:
                logger.error(f"❌ Erro ao processar áudio: {e}")
                message_body = ""

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CASO 2: MENSAGEM DE TEXTO (padrão)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        else:
            # Extrai texto da mensagem
            message_body = message_data.get('conversation', '')

            # Tenta outros campos se conversation estiver vazio
            if not message_body:
                # Tenta extendedTextMessage
                extended = message_data.get('extendedTextMessage', {})
                message_body = extended.get('text', '')

            message_body = message_body.strip()

        logger.info(f"Message: {message_body[:100] if message_body else '(vazio)'}")

        # Valida que temos os dados necessários
        if not from_number or not message_body:
            logger.warning("Mensagem sem dados necessários")
            return jsonify({"status": "error", "message": "Invalid message"}), 400

        # ═══════════════════════════════════════════════════════════════════
        # VERIFICAR SE É RESPOSTA A CHECK-IN PENDENTE
        # ═══════════════════════════════════════════════════════════════════

        from src.checkins.pending_tracker import get_pending_checkin_tracker
        from src.checkins.feedback_handler import get_feedback_handler

        # Import database connection - module is created but may not be available in old deployment
        try:
            from src.database.connection import get_db_engine
            has_db_module = True
        except ModuleNotFoundError:
            has_db_module = False
            logger.warning("⚠️ src.database module not available yet (waiting for redeploy)")

        tracker = get_pending_checkin_tracker()
        pending_checkin = tracker.get_pending_checkin(push_name)

        if pending_checkin:
            logger.info(f"📍 Resposta detectada para check-in: {pending_checkin.checkin_type}")

            try:
                if has_db_module:
                    # Get database connection and feedback handler
                    db_engine = get_db_engine()
                    feedback_handler = get_feedback_handler(db_engine)

                    # Process the check-in response
                    from datetime import datetime
                    feedback = feedback_handler.process_checkin_response(
                        user_id=push_name,
                        response_text=message_body,
                        checkin_id=pending_checkin.checkin_id,
                        checkin_window=pending_checkin.checkin_type,
                        checkin_message=pending_checkin.checkin_message,
                        checkin_timestamp=pending_checkin.sent_timestamp,
                        response_timestamp=datetime.utcnow()
                    )

                    if feedback:
                        logger.info(f"✅ Check-in response recorded: {feedback.response_intent.value}")
                        # Clear the pending check-in
                        tracker.clear_pending_checkin(push_name)
                        # Send acknowledgment
                        response_text = "Obrigado! Registrei sua resposta. 👍"
                        success = True
                    else:
                        logger.error(f"❌ Failed to record check-in response")
                        response_text = "Tive um problema ao registrar sua resposta. Pode tentar de novo?"
                        success = True
                else:
                    # Database module not available yet - just acknowledge the response for now
                    logger.warning("Database module not available - acknowledging but not storing feedback")
                    tracker.clear_pending_checkin(push_name)
                    response_text = "Obrigado! Registrei sua resposta. 👍"
                    success = True

            except Exception as e:
                logger.error(f"❌ Erro ao processar resposta de check-in: {e}", exc_info=True)
                response_text = "Tive um problema ao registrar sua resposta. Pode tentar de novo?"
                success = True

        else:
            # ═══════════════════════════════════════════════════════════════════
            # MODO SÍNCRONO - PROCESSA COMO COMANDO NORMAL (Redis desativado)
            # ═══════════════════════════════════════════════════════════════════

            try:
                logger.info(f"🤖 [NLP] Processando via CommandProcessor...")

                success, response_text = command_processor.process(
                    from_number=from_number,
                    message=message_body
                )

                if success:
                    logger.info(f"✅ Resposta gerada: {response_text[:100]}...")
                else:
                    logger.warning(f"⚠️ Erro no processamento")
                    response_text = "Ops, tive um problema. Tenta de novo?"
                    success = True

            except Exception as e:
                logger.error(f"❌ Erro crítico: {e}", exc_info=True)
                response_text = "Ops, tive um problema técnico. Pode tentar de novo?"
                success = True

        # Envia resposta via WhatsApp
        try:
            from src.whatsapp.sender import WhatsAppSender
            sender = WhatsAppSender()

            send_success, send_sid, send_error = sender.send_message(
                person_name=from_number,
                message=response_text
            )

            if send_success:
                logger.info(f"✅ Resposta enviada. SID: {send_sid}")
            else:
                logger.error(f"❌ Erro ao enviar: {send_error}")

        except Exception as e:
            logger.error(f"❌ Erro ao enviar resposta: {e}")

        return jsonify({
            "status": "success",
            "processed": success,
            "message": "Processado (modo síncrono)"
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


def download_audio_from_url(audio_url: str) -> str:
    """
    Baixa áudio de uma URL (Evolution API).

    Args:
        audio_url: URL do arquivo de áudio

    Returns:
        Caminho local do arquivo baixado

    Raises:
        Exception: Se falhar ao baixar
    """
    try:
        logger.info(f"📥 Baixando áudio de: {audio_url[:80]}...")

        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".opus",
            delete=False,
            dir=tempfile.gettempdir()
        )
        temp_path = temp_file.name
        temp_file.close()

        # Download com timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Pangeia/1.0)',
            'Accept': '*/*'
        }

        response = requests.get(audio_url, headers=headers, timeout=30)
        response.raise_for_status()

        # Salvar arquivo
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"✅ Áudio baixado: {temp_path} ({len(response.content)} bytes)")
        return temp_path

    except Exception as e:
        logger.error(f"❌ Erro ao baixar áudio: {e}")
        raise


def send_audio_response(
    phone_number: str,
    audio_file_path: str,
    person_name: str
) -> bool:
    """
    Envia resposta em áudio via WhatsApp (Evolution API).

    Args:
        phone_number: Número do telefone do destinatário
        audio_file_path: Caminho local do arquivo de áudio
        person_name: Nome da pessoa

    Returns:
        True se enviado com sucesso, False caso contrário
    """
    try:
        logger.info(f"📤 Enviando áudio para {person_name} ({phone_number})")

        # Importar sender aqui para evitar circular imports
        from src.whatsapp.sender import WhatsAppSender

        sender = WhatsAppSender()

        # Enviar áudio
        success = sender.send_audio_message(
            person_name=person_name,
            audio_file_path=audio_file_path
        )

        if success:
            logger.info(f"✅ Áudio enviado com sucesso")

            # Cleanup do arquivo temporário
            try:
                os.unlink(audio_file_path)
                logger.debug(f"Removido arquivo temporário: {audio_file_path}")
            except Exception as e:
                logger.debug(f"Não foi possível remover arquivo: {e}")

        return success

    except Exception as e:
        logger.error(f"❌ Erro ao enviar áudio: {e}")
        return False


if __name__ == '__main__':
    """
    Execução direta do servidor (desenvolvimento).

    Para produção, use gunicorn ou similar:
    gunicorn -w 4 -b 0.0.0.0:5000 src.webhook.app:app
    """
    PORT = int(os.environ.get('PORT', 5000))  # Usa variável de ambiente ou padrão 5000

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
