#!/usr/bin/env python3
"""
Script para enviar mensagem de teste para o Saraiva
"""
import requests
import json

# Configurações da Evolution API
EVOLUTION_API_URL = "https://pange-evolution-api.u5qiqp.easypanel.host"
EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE_NAME = "Pange.IA Bot"

# Número do Saraiva (da planilha atualizada)
NUMERO_SARAIVA = "5511991143605"

def send_message(numero: str, mensagem: str):
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "number": numero,
        "text": mensagem
    }

    print(f"📤 Enviando mensagem para {numero}...")
    print(f"💬 Mensagem: {mensagem}")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201 or response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
        print(f"📋 Resposta: {response.json()}")
        return True
    else:
        print(f"❌ Erro ao enviar mensagem: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        return False

if __name__ == "__main__":
    mensagem = """🤖 Olá Saraiva!

Este é um teste do bot Pangeia.

Se você recebeu esta mensagem, significa que a integração com a Evolution API está funcionando perfeitamente! 🎉

- Bot: Pange.IA
- Status: ✅ Online"""

    send_message(NUMERO_SARAIVA, mensagem)
