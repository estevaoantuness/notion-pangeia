#!/usr/bin/env python3
"""
Servidor web simples para exibir QR Code
Atualiza a cada 30 segundos
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json
from datetime import datetime

API_URL = "https://pange-evolution-api.u5qiqp.easypanel.host"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE = "pangeia-bot"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/qr':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            try:
                r = requests.get(f"{API_URL}/instance/connect/{INSTANCE}",
                               headers={"apikey": API_KEY}, timeout=5)
                data = r.json()
                self.wfile.write(json.dumps({
                    "ok": True,
                    "code": data.get("code", ""),
                    "count": data.get("count", 0)
                }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>QR Code WhatsApp</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial;
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 700px;
            margin: 0 auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 20px; }
        #qr {
            background: #f9f9f9;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        pre {
            font-size: 8px;
            line-height: 8px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            display: inline-block;
        }
        .timer {
            font-size: 14px;
            color: #666;
            margin-top: 15px;
        }
        .instructions {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin-top: 20px;
            text-align: left;
            border-radius: 8px;
        }
        .instructions h3 { color: #1976d2; margin: 0 0 10px 0; }
        .instructions ol { margin: 10px 0 0 20px; line-height: 1.8; }
        .loading { color: #999; }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin: 10px 5px;
        }
        .btn:hover { background: #5568d3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 QR Code WhatsApp</h1>
        <p style="color: #666;">Evolution API - Pangeia Bot</p>

        <div id="qr">
            <div>
                <div class="spinner"></div>
                <p class="loading">Carregando...</p>
            </div>
        </div>

        <div class="timer" id="timer">Atualiza em: 30s</div>

        <button class="btn" onclick="refresh()">🔄 Atualizar Agora</button>
        <button class="btn" onclick="window.open('whatsapp-qrcode.png')">📥 Baixar PNG</button>

        <div class="instructions">
            <h3>📱 Como conectar:</h3>
            <ol>
                <li>Abra o <b>WhatsApp</b> no celular</li>
                <li>Toque em <b>Configurações</b></li>
                <li>Toque em <b>Aparelhos conectados</b></li>
                <li>Toque em <b>Conectar aparelho</b></li>
                <li><b>Escaneie o QR Code</b> acima</li>
            </ol>
        </div>

        <p style="color: #999; font-size: 12px; margin-top: 20px;">
            Atualização automática a cada 30 segundos
        </p>
    </div>

    <!-- Biblioteca QRCode.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>

    <script>
        let countdown = 30;
        let currentQRCode = null;

        async function loadQR() {
            try {
                const res = await fetch('/qr');
                const data = await res.json();
                const div = document.getElementById('qr');

                if (data.ok && data.code) {
                    // Limpar QR anterior
                    div.innerHTML = '';

                    // Criar novo QR Code visual
                    currentQRCode = new QRCode(div, {
                        text: data.code,
                        width: 300,
                        height: 300,
                        colorDark : "#000000",
                        colorLight : "#ffffff",
                        correctLevel : QRCode.CorrectLevel.L
                    });

                    // Adicionar info
                    const info = document.createElement('p');
                    info.style.fontSize = '12px';
                    info.style.color = '#666';
                    info.style.marginTop = '10px';
                    info.textContent = `Tentativa ${data.count || 1} de 30`;
                    div.appendChild(info);

                } else if (data.count === 0) {
                    div.innerHTML = '<div><div class="spinner"></div><p class="loading">Aguardando QR Code...</p></div>';
                } else {
                    div.innerHTML = '<p class="loading">❌ ' + (data.error || 'Erro') + '</p>';
                }
            } catch(e) {
                document.getElementById('qr').innerHTML = '<p class="loading">❌ Erro: ' + e.message + '</p>';
            }
        }

        function updateTimer() {
            countdown--;
            document.getElementById('timer').textContent = 'Atualiza em: ' + countdown + 's';
            if (countdown <= 0) {
                countdown = 30;
                loadQR();
            }
        }

        function refresh() {
            countdown = 30;
            loadQR();
        }

        // Iniciar
        loadQR();
        setInterval(loadQR, 30000);
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 QR CODE SERVER")
    print("=" * 60)
    print()
    print("📱 Acesse: http://localhost:8000")
    print("🔄 Atualização automática a cada 30 segundos")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    print()

    try:
        HTTPServer(('', 8000), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado")
