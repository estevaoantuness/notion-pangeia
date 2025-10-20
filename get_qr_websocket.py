#!/usr/bin/env python3
"""
Captura QR Code via WebSocket da Evolution API
"""

import asyncio
import websockets
import json
import base64
import sys

async def get_qr_code():
    """Conecta ao websocket e captura QR Code"""

    # URL do websocket (Evolution API v2.1.1)
    ws_url = "ws://localhost:8080/instance/events/pangeia-bot"
    headers = {
        "apikey": "pange-bot-secret-key-2024"
    }

    print("🔌 Conectando ao WebSocket da Evolution API...")
    print(f"   URL: {ws_url}")
    print()

    try:
        # Adicionar apikey na URL como query param
        ws_url_with_key = f"{ws_url}?apikey=pange-bot-secret-key-2024"

        async with websockets.connect(
            ws_url_with_key,
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            print("✅ Conectado ao WebSocket!")
            print("⏳ Aguardando QR Code...")
            print()

            # Escutar mensagens
            timeout_counter = 0
            max_timeout = 60  # 60 segundos

            while timeout_counter < max_timeout:
                try:
                    # Aguardar mensagem com timeout de 1 segundo
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)

                    # Parse JSON
                    data = json.loads(message)

                    print(f"📨 Evento recebido: {data.get('event', 'unknown')}")

                    # Verificar se é evento de QR Code
                    if data.get('event') == 'qrcode.updated':
                        qr_data = data.get('data', {})

                        # Verificar se tem código
                        if 'code' in qr_data:
                            print()
                            print("=" * 80)
                            print("✅ QR CODE RECEBIDO!")
                            print("=" * 80)
                            print()
                            print(qr_data['code'])
                            print()
                            print("=" * 80)
                            print()

                            # Salvar em arquivo
                            with open('qrcode.txt', 'w') as f:
                                f.write(qr_data['code'])
                            print("💾 QR Code salvo em: qrcode.txt")

                            return True

                        elif 'base64' in qr_data:
                            print()
                            print("=" * 80)
                            print("✅ QR CODE RECEBIDO (Base64)!")
                            print("=" * 80)
                            print()

                            # Decodificar base64 e salvar imagem
                            img_data = qr_data['base64'].split(',')[1] if ',' in qr_data['base64'] else qr_data['base64']
                            img_bytes = base64.b64decode(img_data)

                            with open('whatsapp-qrcode.png', 'wb') as f:
                                f.write(img_bytes)

                            print("💾 QR Code salvo em: whatsapp-qrcode.png")
                            print()
                            print("📱 Abra a imagem e escaneie com WhatsApp!")
                            print()

                            return True

                    elif data.get('event') == 'connection.update':
                        state = data.get('data', {}).get('state')
                        print(f"   Estado da conexão: {state}")

                        if state == 'open':
                            print()
                            print("🎉 WhatsApp CONECTADO com sucesso!")
                            return True

                except asyncio.TimeoutError:
                    timeout_counter += 1
                    if timeout_counter % 10 == 0:
                        print(f"   Aguardando... ({timeout_counter}s)")
                    continue

                except Exception as e:
                    print(f"❌ Erro ao processar mensagem: {e}")
                    continue

            print()
            print("⚠️ Timeout: QR Code não foi gerado após 60 segundos")
            return False

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Erro de WebSocket: {e}")
        return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal"""
    print()
    print("=" * 80)
    print("🔐 CAPTURADOR DE QR CODE - Evolution API")
    print("=" * 80)
    print()

    success = await get_qr_code()

    if not success:
        print()
        print("=" * 80)
        print("❌ Não foi possível obter o QR Code")
        print("=" * 80)
        print()
        print("💡 Sugestões:")
        print("   1. Verifique se a Evolution API está rodando")
        print("   2. Verifique se a instância 'pangeia-bot' existe")
        print("   3. Tente deletar e recriar a instância")
        print()
        return 1

    return 0


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print("⚠️ Cancelado pelo usuário")
        sys.exit(1)
