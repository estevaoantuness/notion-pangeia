"""
Servidor Flask para webhook da Evolution API.

Este módulo implementa o servidor web que recebe mensagens do WhatsApp
via webhook da Evolution API e processa comandos dos colaboradores.
"""

import logging
import os
import requests
import tempfile
from pathlib import Path
from flask import Flask, request, Response, jsonify

from src.commands.processor import CommandProcessor  # DEPRECADO - manter para rollback
from src.agents.smart_task_agent import get_smart_task_agent  # DEPRECADO
from src.agents.conversational_agent import get_conversational_agent  # NOVO SISTEMA
from src.scheduler import get_scheduler
from src.audio import get_processor as get_audio_processor
from config.settings import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializa Flask
app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════
# NOVO SISTEMA: Conversational Agent (100% GPT - sem comandos fixos)
# ═══════════════════════════════════════════════════════════════════
conversational_agent = get_conversational_agent()

# DEPRECADO: Mantidos para rollback de emergência
# command_processor = CommandProcessor()  # Desabilitado
# smart_agent = get_smart_task_agent()  # Desabilitado

# Inicializa processador de áudio
audio_processor = get_audio_processor()

# Inicializa scheduler (DESABILITADO - sem disparos automáticos)
# scheduler = get_scheduler()
# scheduler.setup_jobs()
# scheduler.start()
logger.info("⚠️ Scheduler DESABILITADO - sem mensagens automáticas")


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
        "scheduler": "disabled"
    }, 200


@app.route('/scheduler/jobs', methods=['GET'])
def scheduler_jobs():
    """
    Lista todos os jobs agendados.

    Returns:
        JSON com lista de jobs
    """
    return {
        "status": "disabled",
        "message": "Scheduler desabilitado - sem mensagens automáticas"
    }, 200


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
        # NOVO SISTEMA: Processamento 100% Conversacional via GPT-4o-mini
        # ═══════════════════════════════════════════════════════════════════
        # Substitui sistema de 3 camadas (CommandProcessor → SmartTaskAgent → Fallback)
        # por uma única chamada ao ConversationalAgent que entende variações ilimitadas
        try:
            logger.info(f"🤖 [CONVERSATIONAL] Processando via GPT-4o-mini (linguagem natural)...")

            success, response_text = conversational_agent.process(
                user_name=push_name,
                message=message_body
            )

            if success:
                logger.info(f"✅ Resposta gerada pelo Conversational Agent: {response_text[:100]}...")
            else:
                # Fallback se GPT falhar completamente
                logger.warning(f"⚠️ ConversationalAgent retornou erro - usando fallback")
                response_text = "Ops, tive um problema. Tenta de novo?"
                success = True

        except Exception as e:
            logger.error(f"❌ Erro crítico no ConversationalAgent: {e}", exc_info=True)
            success = True
            response_text = "Ops, tive um problema técnico. Pode tentar de novo?"

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ENVIO DE RESPOSTA
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        from src.whatsapp.sender import WhatsAppSender
        sender = WhatsAppSender()

        # Se a mensagem original foi áudio, responder com áudio
        should_respond_with_audio = (message_type == 'audioMessage')

        # Log do resultado com contexto
        if success and response_text:
            logger.info(
                f"✅ Comando processado com sucesso",
                extra={
                    "from_number": from_number,
                    "push_name": push_name,
                    "user_message": message_body[:50] if message_body else "",
                    "success": success,
                    "response_length": len(response_text),
                    "respond_with_audio": should_respond_with_audio
                }
            )
            logger.info(f"Resposta (texto): {response_text[:100]}...")

            # Se foi áudio de entrada, enviar áudio de saída
            if should_respond_with_audio:
                logger.info(f"🎵 Gerando resposta em áudio...")
                try:
                    audio_success, audio_path = audio_processor.generate_audio_response(
                        text=response_text,
                        person_name=push_name
                    )

                    if audio_success and audio_path:
                        logger.info(f"✅ Áudio gerado: {audio_path}")
                        # Enviar áudio
                        send_audio_response(
                            phone_number=from_number,
                            audio_file_path=audio_path,
                            person_name=push_name
                        )
                    else:
                        logger.warning(f"❌ Falha ao gerar áudio: {audio_path}")
                        # Fallback para texto
                        send_success, send_sid, send_error = sender.send_message(
                            person_name=from_number,
                            message=response_text
                        )
                        if not send_success:
                            logger.error(f"❌ Erro ao enviar fallback de texto: {send_error}")

                except Exception as e:
                    logger.error(f"❌ Erro ao gerar resposta em áudio: {e}")
                    # Fallback para texto
                    send_success, send_sid, send_error = sender.send_message(
                        person_name=from_number,
                        message=response_text
                    )
                    if not send_success:
                        logger.error(f"❌ Erro ao enviar fallback de texto: {send_error}")
            else:
                # Resposta de texto normal
                send_success, send_sid, send_error = sender.send_message(
                    person_name=from_number,
                    message=response_text
                )
                if not send_success:
                    logger.error(f"❌ Erro ao enviar resposta: {send_error}")
                else:
                    logger.info(f"✅ Resposta enviada com sucesso. SID: {send_sid}")

        else:
            logger.warning(
                f"⚠️ Processamento incompleto ou sem resposta",
                extra={
                    "from_number": from_number,
                    "push_name": push_name,
                    "user_message": message_body[:50] if message_body else "",
                    "success": success,
                    "response_text": response_text[:50] if response_text else ""
                }
            )
            # Sempre tenta enviar algo, mesmo se falhou
            if response_text:
                send_success, send_sid, send_error = sender.send_message(
                    person_name=from_number,
                    message=response_text
                )
                if not send_success:
                    logger.error(f"❌ Erro ao enviar resposta de erro: {send_error}")

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
