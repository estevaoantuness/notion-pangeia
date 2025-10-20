#!/usr/bin/env python3
"""
Monitor QR Code endpoint até aparecer o QR Code
"""

import requests
import time
import json
import sys

API_URL = "http://localhost:8080"
API_KEY = "pange-bot-secret-key-2024"
INSTANCE = "pangeia-bot"

headers = {"apikey": API_KEY}

print("🔍 Monitorando QR Code...")
print(f"   Instância: {INSTANCE}")
print(f"   Endpoint: {API_URL}/instance/connect/{INSTANCE}")
print()

for i in range(1, 31):  # 30 tentativas
    try:
        response = requests.get(
            f"{API_URL}/instance/connect/{INSTANCE}",
            headers=headers,
            timeout=5
        )

        data = response.json()

        print(f"[{i}/30] ", end="")

        if "code" in str(data) or "base64" in str(data):
            print("✅ QR CODE ENCONTRADO!")
            print()
            print(json.dumps(data, indent=2))
            sys.exit(0)
        else:
            count = data.get("count", 0)
            print(f"Aguardando... (count: {count})")

    except Exception as e:
        print(f"[{i}/30] ❌ Erro: {e}")

    time.sleep(3)

print()
print("❌ Timeout: QR Code não foi gerado após 90 segundos")
sys.exit(1)
