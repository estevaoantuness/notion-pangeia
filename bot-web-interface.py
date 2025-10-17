#!/usr/bin/env python3
"""
Interface Web Completa - Pangeia Bot
Com abas: QR Code | Chat Bot | Logs
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json
from datetime import datetime
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.commands.processor import CommandProcessor
from config.colaboradores import COLABORADORES

# Configurações Evolution API
API_URL = "https://pange-evolution-api.u5qiqp.easypanel.host"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE = "pangeia-bot"

# Processador de comandos
command_processor = CommandProcessor()

class BotHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))

        elif self.path == '/api/qr':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            try:
                r = requests.get(
                    f"{API_URL}/instance/connect/{INSTANCE}",
                    headers={"apikey": API_KEY},
                    timeout=5
                )
                data = r.json()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "code": data.get("code", ""),
                    "count": data.get("count", 0)
                }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": str(e)
                }).encode())

        elif self.path == '/api/colaboradores':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Lista de colaboradores para o dropdown
            colabs = [{"name": name, "phone": phone}
                     for phone, name in COLABORADORES.items()]
            self.wfile.write(json.dumps(colabs).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            person_name = data.get('person_name')
            message = data.get('message')

            if not person_name or not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": "person_name e message são obrigatórios"
                }).encode())
                return

            # Processar comando
            try:
                success, response = command_processor.process_by_name(
                    person_name=person_name,
                    message=message
                )

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "success": success,
                    "response": response
                }).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": str(e)
                }).encode())

        else:
            self.send_response(404)
            self.end_headers()


HTML = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pangeia Bot - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 20px 20px 0 0;
            padding: 30px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .tabs {
            display: flex;
            background: white;
            border-bottom: 2px solid #f0f0f0;
        }

        .tab {
            flex: 1;
            padding: 15px 20px;
            background: #f5f5f5;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }

        .tab:hover {
            background: #e8e8e8;
        }

        .tab.active {
            background: white;
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }

        .tab-content {
            display: none;
            background: white;
            padding: 40px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            min-height: 500px;
        }

        .tab-content.active {
            display: block;
        }

        /* QR Code Tab */
        #qr-container {
            text-align: center;
            padding: 20px;
        }

        #qr-display {
            background: #f9f9f9;
            padding: 30px;
            border-radius: 12px;
            min-height: 350px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
        }

        /* Chat Tab */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 600px;
        }

        .chat-header {
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
        }

        .person-selector {
            margin-bottom: 15px;
        }

        .person-selector select {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        .person-selector select option {
            color: #333;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
        }

        .message.user {
            justify-content: flex-end;
        }

        .message.bot {
            justify-content: flex-start;
        }

        .message-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }

        .message.user .message-bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.bot .message-bubble {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }

        .message-time {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
        }

        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-radius: 0 0 12px 12px;
            border-top: 1px solid #e0e0e0;
        }

        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 24px;
            font-size: 15px;
            outline: none;
        }

        .chat-input input:focus {
            border-color: #667eea;
        }

        .chat-input button {
            margin-left: 10px;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: background 0.3s;
        }

        .chat-input button:hover {
            background: #5568d3;
        }

        .chat-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        /* Botões */
        .btn {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            margin: 5px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .btn-secondary {
            background: #6c757d;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        /* Spinner */
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .timer {
            font-size: 14px;
            color: #666;
            margin: 15px 0;
        }

        .quick-commands {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        .quick-commands h4 {
            margin-bottom: 10px;
            color: #333;
        }

        .quick-cmd {
            display: inline-block;
            padding: 8px 12px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 16px;
            margin: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .quick-cmd:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>

    <!-- QRCode.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Pangeia Bot Dashboard</h1>
            <p>Gerenciador de WhatsApp + Notion | Evolution API Cloud</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab(0)">📱 QR Code</button>
            <button class="tab" onclick="switchTab(1)">💬 Testar Bot</button>
            <button class="tab" onclick="switchTab(2)">ℹ️ Ajuda</button>
        </div>

        <!-- Tab 1: QR Code -->
        <div class="tab-content active" id="tab-qr">
            <div id="qr-container">
                <h2>Conectar WhatsApp</h2>
                <div id="qr-display">
                    <div>
                        <div class="spinner"></div>
                        <p style="color: #999;">Carregando QR Code...</p>
                    </div>
                </div>
                <div class="timer" id="qr-timer">Atualiza em: 30s</div>
                <button class="btn" onclick="refreshQR()">🔄 Atualizar Agora</button>
                <button class="btn btn-secondary" onclick="recreateInstance()">🔄 Gerar QR Novo</button>
            </div>
        </div>

        <!-- Tab 2: Chat Bot -->
        <div class="tab-content" id="tab-chat">
            <div class="chat-container">
                <div class="chat-header">
                    <h3>💬 Testar Bot Localmente</h3>
                    <div class="person-selector">
                        <select id="person-select">
                            <option value="">Selecione seu nome...</option>
                        </select>
                    </div>
                </div>

                <div class="quick-commands">
                    <h4>⚡ Comandos Rápidos:</h4>
                    <span class="quick-cmd" onclick="sendQuick('minhas tarefas')">📋 minhas tarefas</span>
                    <span class="quick-cmd" onclick="sendQuick('feito 1')">✅ feito 1</span>
                    <span class="quick-cmd" onclick="sendQuick('andamento 1')">🔄 andamento 1</span>
                    <span class="quick-cmd" onclick="sendQuick('bloqueada 1 aguardando api')">🚫 bloqueada 1</span>
                    <span class="quick-cmd" onclick="sendQuick('progresso')">📊 progresso</span>
                    <span class="quick-cmd" onclick="sendQuick('ajuda')">❓ ajuda</span>
                </div>

                <div class="chat-messages" id="chat-messages">
                    <div class="message bot">
                        <div>
                            <div class="message-bubble">
                                Olá! 👋<br><br>
                                Selecione seu nome acima e digite um comando para testar o bot!
                            </div>
                        </div>
                    </div>
                </div>

                <div class="chat-input">
                    <input type="text" id="message-input" placeholder="Digite um comando..."
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()" id="send-btn">Enviar</button>
                </div>
            </div>
        </div>

        <!-- Tab 3: Ajuda -->
        <div class="tab-content" id="tab-help">
            <h2>📚 Guia de Uso</h2>
            <br>
            <h3>🔐 Conectar WhatsApp:</h3>
            <ol style="line-height: 2; margin-left: 20px;">
                <li>Vá para aba "📱 QR Code"</li>
                <li>Aguarde o QR Code aparecer</li>
                <li>Abra WhatsApp → Configurações → Aparelhos conectados</li>
                <li>Clique em "Conectar aparelho"</li>
                <li>Escaneie o QR Code</li>
            </ol>
            <br>
            <h3>💬 Testar Bot:</h3>
            <ol style="line-height: 2; margin-left: 20px;">
                <li>Vá para aba "💬 Testar Bot"</li>
                <li>Selecione seu nome no dropdown</li>
                <li>Digite comandos como: "minhas tarefas", "feito 1", etc</li>
                <li>Veja as respostas do bot em tempo real!</li>
            </ol>
            <br>
            <h3>⚡ Comandos Disponíveis:</h3>
            <ul style="line-height: 2; margin-left: 20px;">
                <li><strong>minhas tarefas</strong> - Lista suas tasks do Notion</li>
                <li><strong>feito [número]</strong> - Marca task como concluída</li>
                <li><strong>andamento [número]</strong> - Marca task como em andamento</li>
                <li><strong>bloqueada [número] [motivo]</strong> - Marca task como bloqueada</li>
                <li><strong>progresso</strong> - Mostra seu progresso</li>
                <li><strong>ajuda</strong> - Lista todos os comandos</li>
            </ul>
        </div>
    </div>

    <script>
        let qrCountdown = 30;
        let currentPerson = '';

        // Carregar colaboradores
        fetch('/api/colaboradores')
            .then(r => r.json())
            .then(data => {
                const select = document.getElementById('person-select');
                data.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.name;
                    opt.textContent = c.name;
                    select.appendChild(opt);
                });
            });

        // Trocar abas
        function switchTab(index) {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');

            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tabs[index].classList.add('active');
            contents[index].classList.add('active');
        }

        // QR Code
        async function loadQR() {
            const res = await fetch('/api/qr');
            const data = await res.json();
            const div = document.getElementById('qr-display');

            if (data.ok && data.code) {
                div.innerHTML = '';
                new QRCode(div, {
                    text: data.code,
                    width: 300,
                    height: 300,
                    colorDark: "#000000",
                    colorLight: "#ffffff",
                    correctLevel: QRCode.CorrectLevel.L
                });
                const info = document.createElement('p');
                info.style.fontSize = '12px';
                info.style.color = '#666';
                info.style.marginTop = '10px';
                info.textContent = `Tentativa ${data.count || 1} de 30`;
                div.appendChild(info);
            } else if (data.count === 0) {
                div.innerHTML = '<div><div class="spinner"></div><p style="color:#999;">Aguardando QR Code...</p></div>';
            } else {
                div.innerHTML = '<p style="color:#e74c3c;">❌ ' + (data.error || 'Erro ao carregar QR Code') + '</p>';
            }
        }

        function refreshQR() {
            qrCountdown = 30;
            loadQR();
        }

        function updateQRTimer() {
            qrCountdown--;
            document.getElementById('qr-timer').textContent = 'Atualiza em: ' + qrCountdown + 's';
            if (qrCountdown <= 0) {
                qrCountdown = 30;
                loadQR();
            }
        }

        function recreateInstance() {
            if (confirm('Isso vai deletar a instância atual e criar uma nova. Continuar?')) {
                alert('Função em desenvolvimento. Use o script Python: python3 show-qrcode.py');
            }
        }

        // Chat Bot
        function addMessage(text, isUser) {
            const container = document.getElementById('chat-messages');
            const msg = document.createElement('div');
            msg.className = 'message ' + (isUser ? 'user' : 'bot');

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = text;

            msg.appendChild(document.createElement('div'));
            msg.firstChild.appendChild(bubble);

            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('message-input');
            const select = document.getElementById('person-select');
            const btn = document.getElementById('send-btn');

            const message = input.value.trim();
            const person = select.value;

            if (!person) {
                alert('Selecione seu nome primeiro!');
                return;
            }

            if (!message) return;

            // Adicionar mensagem do usuário
            addMessage(message, true);
            input.value = '';
            btn.disabled = true;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({person_name: person, message: message})
                });

                const data = await res.json();

                if (data.ok) {
                    addMessage(data.response, false);
                } else {
                    addMessage('❌ Erro: ' + data.error, false);
                }
            } catch (e) {
                addMessage('❌ Erro de conexão: ' + e.message, false);
            }

            btn.disabled = false;
            input.focus();
        }

        function sendQuick(cmd) {
            document.getElementById('message-input').value = cmd;
            sendMessage();
        }

        // Iniciar
        loadQR();
        setInterval(loadQR, 30000);
        setInterval(updateQRTimer, 1000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 PANGEIA BOT - WEB DASHBOARD")
    print("=" * 70)
    print()
    print("📱 Acesse: http://localhost:8000")
    print()
    print("Funcionalidades:")
    print("  ✅ QR Code WhatsApp (atualização automática)")
    print("  ✅ Chat para testar bot localmente")
    print("  ✅ Guia de uso completo")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 70)
    print()

    try:
        HTTPServer(('', 8000), BotHandler).serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado")
