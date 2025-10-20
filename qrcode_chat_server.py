#!/usr/bin/env python3
"""
Servidor HTTPS para exibir QR Code e Chat de testes
"""

from flask import Flask, render_template_string, request, jsonify
import ssl
import requests
import os

app = Flask(__name__)

API_URL = "http://localhost:8080"
API_KEY = "pange-bot-secret-key-2024"
INSTANCE = "pangeia-bot"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pangeia Bot - QR Code & Chat</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1200px;
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            overflow: hidden;
        }

        .qr-section {
            padding: 40px;
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .chat-section {
            padding: 40px;
            display: flex;
            flex-direction: column;
        }

        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            text-align: center;
            font-size: 14px;
        }

        #qrcode {
            width: 280px;
            height: 280px;
            background: white;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        #qrcode img {
            max-width: 100%;
            max-height: 100%;
            border-radius: 10px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .status {
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 14px;
            text-align: center;
            margin-top: 15px;
        }

        .status.connecting {
            background: #fff3cd;
            color: #856404;
        }

        .status.connected {
            background: #d4edda;
            color: #155724;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
        }

        .chat-header {
            margin-bottom: 20px;
        }

        .chat-header h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 5px;
        }

        .chat-header p {
            color: #666;
            font-size: 14px;
        }

        .chat-messages {
            flex: 1;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            max-height: 300px;
            overflow-y: auto;
        }

        .message {
            background: white;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .message-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
            color: #999;
        }

        .message-text {
            color: #333;
            line-height: 1.5;
        }

        .chat-input-form {
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }

        .chat-input:focus {
            border-color: #667eea;
        }

        .send-btn {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }

        .send-btn:hover {
            background: #5568d3;
        }

        .send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }

            .qr-section {
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="qr-section">
            <h1>🤖 Pangeia Bot</h1>
            <p class="subtitle">Escaneie o QR Code com WhatsApp</p>

            <div id="qrcode">
                <div class="spinner"></div>
            </div>

            <div id="status" class="status connecting">
                Aguardando QR Code...
            </div>
        </div>

        <div class="chat-section">
            <div class="chat-header">
                <h2>💬 Chat de Teste</h2>
                <p>Teste comandos do bot aqui após conectar</p>
            </div>

            <div class="chat-messages" id="messages">
                <div class="message">
                    <div class="message-info">
                        <span><strong>Sistema</strong></span>
                        <span>Agora</span>
                    </div>
                    <div class="message-text">
                        👋 Bem-vindo! Após escanear o QR Code, você poderá testar os comandos do bot aqui.
                    </div>
                </div>
            </div>

            <form class="chat-input-form" id="chatForm">
                <input
                    type="text"
                    class="chat-input"
                    id="messageInput"
                    placeholder="Digite /ajuda para ver os comandos..."
                    disabled
                >
                <button type="submit" class="send-btn" id="sendBtn" disabled>
                    Enviar
                </button>
            </form>
        </div>
    </div>

    <script>
        const API_URL = '/api';
        let pollInterval;
        let isConnected = false;

        // Polling para QR Code
        function pollQRCode() {
            fetch(`${API_URL}/qrcode`)
                .then(res => res.json())
                .then(data => {
                    if (data.qrcode) {
                        document.getElementById('qrcode').innerHTML =
                            `<img src="${data.qrcode}" alt="QR Code">`;
                        document.getElementById('status').textContent =
                            '📱 Escaneie com WhatsApp';
                        document.getElementById('status').className = 'status connecting';
                    } else if (data.status === 'connected') {
                        clearInterval(pollInterval);
                        document.getElementById('qrcode').innerHTML =
                            '<div style="font-size: 80px;">✅</div>';
                        document.getElementById('status').textContent =
                            '✅ Conectado!';
                        document.getElementById('status').className = 'status connected';
                        isConnected = true;

                        // Habilitar chat
                        document.getElementById('messageInput').disabled = false;
                        document.getElementById('sendBtn').disabled = false;

                        addSystemMessage('✅ WhatsApp conectado! Agora você pode enviar mensagens.');
                    } else if (data.error) {
                        document.getElementById('status').textContent =
                            `❌ Erro: ${data.error}`;
                        document.getElementById('status').className = 'status error';
                    }
                })
                .catch(err => {
                    console.error('Erro ao buscar QR Code:', err);
                });
        }

        // Adicionar mensagem do sistema
        function addSystemMessage(text) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            messageDiv.innerHTML = `
                <div class="message-info">
                    <span><strong>Sistema</strong></span>
                    <span>${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-text">${text}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Adicionar mensagem do usuário
        function addUserMessage(text) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            messageDiv.innerHTML = `
                <div class="message-info">
                    <span><strong>Você</strong></span>
                    <span>${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-text">${text}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Adicionar mensagem do bot
        function addBotMessage(text) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            messageDiv.innerHTML = `
                <div class="message-info">
                    <span><strong>🤖 Bot</strong></span>
                    <span>${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message-text">${text}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Enviar mensagem
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();

            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message || !isConnected) return;

            addUserMessage(message);
            input.value = '';

            // Enviar para API
            fetch(`${API_URL}/send`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    addBotMessage(data.response || '✅ Mensagem enviada!');
                } else {
                    addSystemMessage(`❌ Erro: ${data.error}`);
                }
            })
            .catch(err => {
                addSystemMessage(`❌ Erro ao enviar: ${err.message}`);
            });
        });

        // Iniciar polling
        pollInterval = setInterval(pollQRCode, 3000);
        pollQRCode(); // Primeira chamada imediata
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/qrcode')
def get_qrcode():
    """Retorna QR Code ou status da conexão"""
    try:
        response = requests.get(
            f"{API_URL}/instance/connect/{INSTANCE}",
            headers={"apikey": API_KEY},
            timeout=5
        )
        data = response.json()

        # Verificar se tem QR Code
        if "code" in str(data) or "base64" in str(data):
            # Extrair QR Code base64
            qrcode = data.get("code") or data.get("base64") or data.get("qrcode", {}).get("code")
            return jsonify({"qrcode": qrcode})

        # Verificar se está conectado
        if data.get("instance", {}).get("state") == "open":
            return jsonify({"status": "connected"})

        # Ainda conectando
        return jsonify({"status": "connecting", "count": data.get("count", 0)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send', methods=['POST'])
def send_message():
    """Envia mensagem de teste (simulação)"""
    try:
        data = request.json
        message = data.get("message", "")

        # Simular resposta do bot baseado no comando
        if message.startswith("/"):
            if "/ajuda" in message or "/help" in message:
                response = """
📚 *Comandos Disponíveis:*

/ajuda - Mostra esta mensagem
/status - Status do bot
/tutorial - Tutorial de onboarding
/tarefas - Listar tarefas
/criar - Criar nova tarefa
                """.strip()
            elif "/status" in message:
                response = "✅ Bot online e funcionando!"
            elif "/tutorial" in message:
                response = "👋 Iniciando tutorial de onboarding..."
            elif "/tarefas" in message:
                response = "📋 Lista de tarefas:\n1. Tarefa exemplo 1\n2. Tarefa exemplo 2"
            else:
                response = f"❓ Comando '{message}' não reconhecido. Digite /ajuda"
        else:
            response = "💬 Mensagem recebida! Use /ajuda para ver os comandos."

        return jsonify({"success": True, "response": response})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Criar contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')

    print("=" * 60)
    print("🚀 Servidor HTTPS iniciado!")
    print("=" * 60)
    print()
    print("📱 Acesse no PC:")
    print("   https://localhost:8443")
    print()
    print("🔒 Se aparecer aviso de segurança:")
    print("   Chrome: Digite 'thisisunsafe' na página")
    print("   Safari: Clique em 'Prosseguir'")
    print()
    print("=" * 60)

    app.run(host='0.0.0.0', port=8443, ssl_context=context, debug=False)
