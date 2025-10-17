#!/usr/bin/env python3
"""
Servidor HTTPS local para exibir QR Code da Evolution API
Atualiza automaticamente a cada 30 segundos
"""

import os
import sys
import json
import time
import requests
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
from datetime import datetime

# Configurações
API_URL = "http://localhost:8080"
API_KEY = "pange-bot-secret-key-2024"
INSTANCE_NAME = "pangeia-bot"
SERVER_PORT = 8443  # Porta HTTPS


class QRCodeHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servir o QR Code"""

    def log_message(self, format, *args):
        """Override para customizar logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

    def do_GET(self):
        """Handle GET requests"""

        if self.path == '/':
            # Página principal com QR Code
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            html = self.generate_html()
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/api/qrcode':
            # API endpoint para obter QR Code (JSON)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            qr_data = self.get_qrcode()
            self.wfile.write(json.dumps(qr_data).encode('utf-8'))

        elif self.path == '/status':
            # Status da conexão
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            status = self.get_connection_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def get_qrcode(self):
        """Obtém QR Code da Evolution API"""
        try:
            response = requests.get(
                f"{API_URL}/instance/connect/{INSTANCE_NAME}",
                headers={"apikey": API_KEY},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                return {
                    "success": True,
                    "code": data.get("code", ""),
                    "base64": data.get("base64", ""),
                    "count": data.get("count", 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_connection_status(self):
        """Verifica status da conexão"""
        try:
            response = requests.get(
                f"{API_URL}/instance/connectionState/{INSTANCE_NAME}",
                headers={"apikey": API_KEY},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "state": data.get("instance", {}).get("state", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_html(self):
        """Gera HTML da página com QR Code"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code - Evolution API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
            padding: 40px;
            max-width: 600px;
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
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 20px;
        }

        .status.connecting {
            background: #fef3c7;
            color: #92400e;
        }

        .status.open {
            background: #d1fae5;
            color: #065f46;
        }

        .status.close {
            background: #fee2e2;
            color: #991b1b;
        }

        .qr-container {
            background: #f9fafb;
            border: 2px dashed #e5e7eb;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        #qrcode {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .qr-text {
            font-family: 'Courier New', monospace;
            font-size: 10px;
            line-height: 10px;
            white-space: pre;
            color: #000;
            background: white;
            padding: 10px;
            border-radius: 4px;
            max-width: 100%;
            overflow: auto;
        }

        .loading {
            font-size: 14px;
            color: #666;
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

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .timer {
            font-size: 12px;
            color: #666;
            margin-top: 15px;
        }

        .instructions {
            background: #f0f9ff;
            border-left: 4px solid #0284c7;
            padding: 15px;
            margin-top: 20px;
            text-align: left;
            border-radius: 4px;
        }

        .instructions h3 {
            color: #0284c7;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .instructions ol {
            margin-left: 20px;
            font-size: 13px;
            color: #334155;
            line-height: 1.8;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 13px;
        }

        .footer {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #9ca3af;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 WhatsApp QR Code</h1>
        <p class="subtitle">Evolution API - Pangeia Bot</p>

        <div id="status-badge" class="status connecting">
            🔄 Verificando conexão...
        </div>

        <div class="qr-container">
            <div id="qrcode">
                <div class="spinner"></div>
                <p class="loading">Carregando QR Code...</p>
            </div>
            <div class="timer" id="timer">
                Atualiza em: 30s
            </div>
        </div>

        <button class="btn" onclick="forceRefresh()">🔄 Atualizar Agora</button>

        <div class="instructions">
            <h3>📱 Como conectar:</h3>
            <ol>
                <li>Abra o <strong>WhatsApp</strong> no celular</li>
                <li>Toque em <strong>Configurações</strong> (ou ⋮ Mais opções)</li>
                <li>Toque em <strong>Aparelhos conectados</strong></li>
                <li>Toque em <strong>Conectar um aparelho</strong></li>
                <li><strong>Escaneie o QR Code</strong> acima</li>
            </ol>
        </div>

        <div class="footer">
            <p>🤖 Notion Pangeia Bot v1.0</p>
            <p>Atualização automática a cada 30 segundos</p>
        </div>
    </div>

    <script>
        let countdown = 30;
        let countdownInterval;
        let refreshInterval;

        // Função para buscar status da conexão
        async function fetchStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();

                const badge = document.getElementById('status-badge');

                if (data.success) {
                    const state = data.state;

                    if (state === 'open') {
                        badge.className = 'status open';
                        badge.innerHTML = '✅ Conectado';

                        // Se conectado, mostrar mensagem de sucesso
                        document.getElementById('qrcode').innerHTML = `
                            <div style="padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 20px;">🎉</div>
                                <h2 style="color: #059669; margin-bottom: 10px;">Conectado com sucesso!</h2>
                                <p style="color: #666;">Seu WhatsApp está conectado e pronto para uso.</p>
                            </div>
                        `;

                        // Para de atualizar quando conectado
                        clearInterval(refreshInterval);
                        clearInterval(countdownInterval);

                    } else if (state === 'connecting') {
                        badge.className = 'status connecting';
                        badge.innerHTML = '🔄 Conectando...';
                    } else {
                        badge.className = 'status close';
                        badge.innerHTML = '❌ Desconectado';
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar status:', error);
            }
        }

        // Função para buscar QR Code
        async function fetchQRCode() {
            try {
                const response = await fetch('/api/qrcode');
                const data = await response.json();

                const qrcodeDiv = document.getElementById('qrcode');

                if (data.success && data.code) {
                    // Se tem código ASCII
                    qrcodeDiv.innerHTML = `<pre class="qr-text">${data.code}</pre>`;
                } else if (data.success && data.base64) {
                    // Se tem imagem base64
                    qrcodeDiv.innerHTML = `<img src="${data.base64}" alt="QR Code" style="max-width: 300px;">`;
                } else if (data.count === 0) {
                    // QR Code ainda não disponível
                    qrcodeDiv.innerHTML = `
                        <div class="spinner"></div>
                        <p class="loading">Aguardando QR Code...</p>
                        <p style="font-size: 12px; color: #999; margin-top: 10px;">
                            Pode levar até 30 segundos
                        </p>
                    `;
                } else {
                    // Erro
                    qrcodeDiv.innerHTML = `
                        <div class="error">
                            ⚠️ Erro ao obter QR Code<br>
                            ${data.error || 'Erro desconhecido'}
                        </div>
                    `;
                }

                // Atualizar status também
                fetchStatus();

            } catch (error) {
                document.getElementById('qrcode').innerHTML = `
                    <div class="error">
                        ❌ Erro de conexão<br>
                        ${error.message}
                    </div>
                `;
            }
        }

        // Função para atualizar contador
        function updateTimer() {
            countdown--;
            document.getElementById('timer').textContent = `Atualiza em: ${countdown}s`;

            if (countdown <= 0) {
                countdown = 30;
                fetchQRCode();
            }
        }

        // Função para forçar atualização
        function forceRefresh() {
            countdown = 30;
            fetchQRCode();
        }

        // Inicializar
        window.onload = function() {
            // Buscar QR Code imediatamente
            fetchQRCode();

            // Atualizar a cada 30 segundos
            refreshInterval = setInterval(fetchQRCode, 30000);

            // Atualizar contador a cada segundo
            countdownInterval = setInterval(updateTimer, 1000);
        };
    </script>
</body>
</html>
        """


def generate_self_signed_cert():
    """Gera certificado SSL auto-assinado"""
    import subprocess

    cert_file = "server.crt"
    key_file = "server.key"

    # Verifica se já existe
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ Certificados SSL encontrados")
        return cert_file, key_file

    print("🔐 Gerando certificado SSL auto-assinado...")

    try:
        # Gerar certificado usando OpenSSL
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', key_file, '-out', cert_file,
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ], check=True, capture_output=True)

        print("✅ Certificado SSL gerado com sucesso")
        return cert_file, key_file

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar certificado: {e}")
        print("Usando HTTP ao invés de HTTPS...")
        return None, None
    except FileNotFoundError:
        print("⚠️  OpenSSL não encontrado. Usando HTTP ao invés de HTTPS...")
        return None, None


def main():
    """Inicia o servidor"""
    print("=" * 60)
    print("🚀 QR CODE SERVER - Evolution API")
    print("=" * 60)
    print()

    # Verificar se Evolution API está acessível
    print("1️⃣  Verificando Evolution API...")
    try:
        response = requests.get(API_URL, timeout=5)
        print(f"✅ Evolution API está respondendo (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Erro ao conectar com Evolution API: {e}")
        print()
        print("Por favor, inicie o Docker primeiro:")
        print("  cd evolution-setup")
        print("  docker-compose up -d")
        print()
        return 1

    print()

    # Gerar certificados SSL
    cert_file, key_file = generate_self_signed_cert()

    print()
    print("2️⃣  Iniciando servidor...")

    # Criar servidor HTTP/HTTPS
    server_address = ('', SERVER_PORT if cert_file else 8000)
    httpd = HTTPServer(server_address, QRCodeHandler)

    # Configurar SSL se certificados foram gerados
    if cert_file and key_file:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        protocol = "https"
        port = SERVER_PORT
        print(f"✅ Servidor HTTPS iniciado")
    else:
        protocol = "http"
        port = 8000
        print(f"✅ Servidor HTTP iniciado")

    print()
    print("=" * 60)
    print("🌐 SERVIDOR RODANDO")
    print("=" * 60)
    print()
    print(f"📱 Acesse no navegador:")
    print(f"   {protocol}://localhost:{port}")
    print()

    if protocol == "https":
        print("⚠️  IMPORTANTE:")
        print("   Como o certificado é auto-assinado, você verá um aviso")
        print("   de segurança no navegador. É seguro prosseguir.")
        print("   Clique em 'Avançado' → 'Continuar para localhost'")
        print()

    print("📋 Configuração:")
    print(f"   API URL: {API_URL}")
    print(f"   Instância: {INSTANCE_NAME}")
    print(f"   Atualização: a cada 30 segundos")
    print()
    print("=" * 60)
    print()
    print("💡 Pressione Ctrl+C para parar o servidor")
    print()

    # Abrir navegador automaticamente
    try:
        import webbrowser
        time.sleep(1)
        webbrowser.open(f"{protocol}://localhost:{port}")
        print("✅ Navegador aberto automaticamente")
        print()
    except:
        pass

    # Iniciar servidor
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("👋 Servidor parado")
        print("=" * 60)
        return 0


if __name__ == '__main__':
    sys.exit(main())
