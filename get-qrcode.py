#!/usr/bin/env python3
"""
Obtém e exibe QR Code do WhatsApp no terminal
"""

import requests
import time
import sys
import json

API_URL = "http://localhost:8080"
API_KEY = "pange-bot-secret-key-2024"
INSTANCE_NAME = "pangeia-bot"

def get_qr_code():
    """Tenta obter QR Code da instância"""
    headers = {"apikey": API_KEY}

    print("🔄 Tentando obter QR Code...")
    print(f"   Instância: {INSTANCE_NAME}")
    print()

    for attempt in range(1, 16):  # Tenta 15 vezes
        print(f"Tentativa {attempt}/15...", end=" ")

        try:
            # Endpoint para conectar (gera QR Code)
            response = requests.get(
                f"{API_URL}/instance/connect/{INSTANCE_NAME}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                # Tenta diferentes campos onde o QR pode estar
                qr_code = (
                    data.get('code') or
                    data.get('base64') or
                    data.get('qrcode', {}).get('code') or
                    data.get('qrcode', {}).get('base64')
                )

                if qr_code and qr_code != "null":
                    print("✅ QR Code encontrado!")
                    print()
                    print("="*70)
                    print("QR CODE:")
                    print("="*70)
                    print()
                    print(qr_code)
                    print()
                    print("="*70)
                    print()
                    print("📱 Como escanear:")
                    print("   1. Abra WhatsApp no celular")
                    print("   2. Configurações → Aparelhos Conectados")
                    print("   3. Conectar um Aparelho")
                    print("   4. Escaneie o código acima")
                    print()
                    return True
                else:
                    print(f"❌ QR ainda não gerado (count: {data.get('count', 0)})")
            else:
                print(f"❌ Erro HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            print("⏱️ Timeout")
        except Exception as e:
            print(f"❌ Erro: {e}")

        if attempt < 15:
            time.sleep(3)  # Aguarda 3 segundos

    print()
    print("⚠️  QR Code não foi gerado após 15 tentativas")
    print()
    return False

def check_instance():
    """Verifica se instância existe"""
    headers = {"apikey": API_KEY}

    try:
        response = requests.get(
            f"{API_URL}/instance/fetchInstances",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            instances = response.json()
            for inst in instances:
                if inst['name'] == INSTANCE_NAME:
                    print(f"✅ Instância encontrada: {INSTANCE_NAME}")
                    print(f"   Status: {inst['connectionStatus']}")
                    print(f"   Token: {inst['token']}")
                    print()
                    return True

            print(f"❌ Instância '{INSTANCE_NAME}' não encontrada")
            print()
            print("Instâncias disponíveis:")
            for inst in instances:
                print(f"  - {inst['name']} (status: {inst['connectionStatus']})")
            print()
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar instância: {e}")
        return False

def main():
    print()
    print("="*70)
    print("  OBTER QR CODE - WHATSAPP")
    print("="*70)
    print()

    # Verifica instância
    if not check_instance():
        print("💡 Crie a instância primeiro:")
        print("   cd evolution-setup && ./recreate-instance.sh")
        print()
        return False

    # Obtém QR Code
    success = get_qr_code()

    if not success:
        print("📋 Alternativas:")
        print()
        print("1. Acesse o Manager UI:")
        print("   http://localhost:8080/manager")
        print("   Senha: pange-bot-secret-key-2024")
        print()
        print("2. Verifique os logs:")
        print("   docker logs evolution_api --tail 100")
        print()
        print("3. Tente reiniciar o container:")
        print("   cd evolution-setup && docker compose restart")
        print()

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
