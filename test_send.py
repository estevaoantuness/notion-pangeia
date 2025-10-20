#!/usr/bin/env python3
"""
Teste de envio de mensagem via Evolution API
"""
import requests
import json

# Configurações
EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "pange-bot-secret-key-2024"
INSTANCE_NAME = "pangeia-bot"

# Número do Estevão (formato internacional sem +)
# Ajuste o número aqui:
NUMERO_ESTEVAO = "5511999999999"  # Coloque o número real aqui

def enviar_mensagem(numero, texto):
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"

    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }

    data = {
        "number": numero,
        "text": texto
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200 or response.status_code == 201:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Teste de Envio - Pangeia Bot")
    print("=" * 60)

    # Verificar se a instância existe
    print("\n1. Verificando instância...")
    try:
        check_url = f"{EVOLUTION_API_URL}/instance/fetchInstances"
        headers = {"apikey": EVOLUTION_API_KEY}
        response = requests.get(check_url, headers=headers, timeout=10)

        if response.status_code == 200:
            instances = response.json()
            if instances:
                print(f"✅ Encontradas {len(instances)} instância(s)")
                for inst in instances:
                    print(f"   - {inst['name']}: {inst.get('connectionStatus', 'unknown')}")
            else:
                print("⚠️  Nenhuma instância encontrada")
        else:
            print(f"❌ Erro ao verificar instâncias: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    # Enviar mensagem
    print("\n2. Enviando mensagem de teste...")
    mensagem = """🤖 *Teste Pangeia Bot*

Olá! Este é um teste de envio via Evolution API.

Se você recebeu esta mensagem, significa que a integração está funcionando! ✅"""

    enviar_mensagem(NUMERO_ESTEVAO, mensagem)

    print("\n" + "=" * 60)
