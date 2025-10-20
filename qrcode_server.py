#!/usr/bin/env python3
"""
Servidor HTTPS para exibir QR Code da Evolution API
Atualiza automaticamente a cada 3 segundos
"""

import requests
import json
import time
from flask import Flask, render_template_string
import ssl
import threading

app = Flask(__name__)

# Configurações da Evolution API
EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "pange-bot-secret-key-2024"
INSTANCE_NAME = "pangeia-bot"

# Cache do QR Code
qr_data = {
    "base64": None,
    "code": None,
    "count": 0,
    "status": "Aguardando...",
    "last_update": None
}

def fetch_qr_code():
    """Busca o QR Code da Evolution API"""
    global qr_data

    while True:
        try:
            # Tentar obter QR Code
            response = requests.get(
                f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}",
                headers={"apikey": EVOLUTION_API_KEY},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if "base64" in data and data["base64"]:
                    qr_data["base64"] = data["base64"]
                    qr_data["code"] = data.get("code", "")
                    qr_data["count"] = data.get("count", 0)
                    qr_data["status"] = "QR Code disponível"
                    qr_data["last_update"] = time.strftime("%H:%M:%S")
                    print(f"✅ QR Code obtido! Count: {qr_data['count']}")
                else:
                    # Verificar status da instância
                    status_response = requests.get(
                        f"{EVOLUTION_API_URL}/instance/connectionState/{INSTANCE_NAME}",
                        headers={"apikey": EVOLUTION_API_KEY},
                        timeout=10
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        state = status_data.get("state", "unknown")

                        if state == "open":
                            qr_data["status"] = "✅ WhatsApp Conectado!"
                            print("✅ WhatsApp já está conectado!")
                        elif state == "close":
                            qr_data["status"] = "⏳ Aguardando QR Code..."
                        else:
                            qr_data["status"] = f"Status: {state}"
                    else:
                        qr_data["status"] = "⏳ Gerando QR Code..."

            else:
                qr_data["status"] = f"❌ Erro: HTTP {response.status_code}"
                print(f"❌ Erro ao obter QR Code: {response.status_code}")

        except Exception as e:
            qr_data["status"] = f"❌ Erro: {str(e)}"
            print(f"❌ Erro: {e}")

        # Aguardar 3 segundos antes de tentar novamente
        time.sleep(3)

# HTML Template com auto-refresh
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code - Pangeia WhatsApp</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .status {
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: 600;
            font-size: 16px;
        }

        .status.loading {
            background: #fff3cd;
            color: #856404;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
        }

        .qr-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
        }

        .qr-code {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .placeholder {
            padding: 60px 20px;
            color: #999;
            font-size: 18px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .instructions {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-top: 20px;
            text-align: left;
            border-radius: 5px;
        }

        .instructions h3 {
            color: #1976D2;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .instructions ol {
            margin-left: 20px;
            color: #555;
        }

        .instructions li {
            margin: 8px 0;
            font-size: 14px;
        }

        .info {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 12px;
            color: #666;
        }

        .info strong {
            color: #333;
        }

        .update-time {
            color: #999;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
    <script>
        // Auto-refresh a cada 3 segundos
        setTimeout(function() {
            location.reload();
        }, 3000);
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 Pangeia Bot</h1>
        <p class="subtitle">Conecte seu WhatsApp</p>

        {% if qr_data.status == "✅ WhatsApp Conectado!" %}
            <div class="status success">{{ qr_data.status }}</div>
        {% elif "❌" in qr_data.status %}
            <div class="status error">{{ qr_data.status }}</div>
        {% else %}
            <div class="status loading">{{ qr_data.status }}</div>
        {% endif %}

        <div class="qr-container">
            {% if qr_data.base64 %}
                <img src="data:image/png;base64,{{ qr_data.base64 }}"
                     alt="QR Code"
                     class="qr-code">
                <p class="update-time">
                    Atualizado: {{ qr_data.last_update }}<br>
                    Tentativa: {{ qr_data.count }}
                </p>
            {% elif qr_data.status == "✅ WhatsApp Conectado!" %}
                <div class="placeholder">
                    <h2 style="color: #28a745;">✅</h2>
                    <p style="margin-top: 20px; color: #28a745; font-weight: 600;">
                        WhatsApp conectado com sucesso!
                    </p>
                </div>
            {% else %}
                <div class="placeholder">
                    <div class="spinner"></div>
                    <p>Aguardando QR Code...</p>
                </div>
            {% endif %}
        </div>

        {% if qr_data.base64 %}
        <div class="instructions">
            <h3>📱 Como conectar:</h3>
            <ol>
                <li>Abra o <strong>WhatsApp</strong> no seu celular</li>
                <li>Toque em <strong>Menu (⋮)</strong> ou <strong>Configurações</strong></li>
                <li>Toque em <strong>Aparelhos conectados</strong></li>
                <li>Toque em <strong>Conectar um aparelho</strong></li>
                <li>Aponte a câmera para o <strong>QR Code acima</strong></li>
            </ol>
        </div>
        {% endif %}

        <div class="info">
            <strong>🌐 API:</strong> notion-pangeia-production.up.railway.app<br>
            <strong>📱 Instância:</strong> pangeia<br>
            <strong>🔄 Auto-refresh:</strong> 3 segundos
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal com QR Code"""
    return render_template_string(HTML_TEMPLATE, qr_data=qr_data)

@app.route('/api/qr')
def api_qr():
    """API endpoint para obter dados do QR Code"""
    return json.dumps(qr_data, indent=2)

@app.route('/health')
def health():
    """Health check"""
    return {"status": "ok", "qr_status": qr_data["status"]}

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor QR Code - Pangeia WhatsApp Bot")
    print("=" * 60)
    print(f"📡 Evolution API: {EVOLUTION_API_URL}")
    print(f"📱 Instância: {INSTANCE_NAME}")
    print("=" * 60)

    # Iniciar thread para buscar QR Code
    qr_thread = threading.Thread(target=fetch_qr_code, daemon=True)
    qr_thread.start()
    print("✅ Thread de atualização do QR Code iniciada")

    # Verificar se os certificados existem
    import os
    cert_path = "/Users/estevaoantunes/notion-pangeia/cert.pem"
    key_path = "/Users/estevaoantunes/notion-pangeia/key.pem"

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("🔒 Certificados SSL encontrados")
        print("=" * 60)
        print("🌐 Acesse: https://localhost:5002")
        print("=" * 60)

        # Criar contexto SSL
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)

        # Iniciar servidor HTTPS
        app.run(
            host='0.0.0.0',
            port=5002,
            ssl_context=ssl_context,
            debug=False
        )
    else:
        print("⚠️  Certificados SSL não encontrados")
        print("=" * 60)
        print("🌐 Acesse: http://localhost:5002")
        print("=" * 60)

        # Iniciar servidor HTTP
        app.run(
            host='0.0.0.0',
            port=5002,
            debug=False
        )
