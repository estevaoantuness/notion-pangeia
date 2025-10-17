#!/usr/bin/env python3
"""
Gera e exibe QR Code visual da Evolution API
"""

import requests
import qrcode
from PIL import Image

# Configurações
API_URL = "https://pange-evolution-api.u5qiqp.easypanel.host"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE = "pangeia-bot"

print("=" * 60)
print("🔍 OBTENDO QR CODE DA EVOLUTION API")
print("=" * 60)
print()

# Buscar QR Code
response = requests.get(
    f"{API_URL}/instance/connect/{INSTANCE}",
    headers={"apikey": API_KEY},
    timeout=10
)

data = response.json()

if data.get('code'):
    qr_text = data['code']
    print(f"✅ QR Code obtido! (Count: {data.get('count', 0)})")
    print()

    # Gerar imagem do QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Salvar imagem
    filename = "whatsapp-qrcode.png"
    img.save(filename)

    print(f"📱 QR Code salvo em: {filename}")
    print()
    print("=" * 60)
    print("ABRINDO QR CODE...")
    print("=" * 60)
    print()
    print("📱 Como escanear:")
    print("  1. Abra WhatsApp no celular")
    print("  2. Toque em Configurações")
    print("  3. Toque em Aparelhos conectados")
    print("  4. Toque em Conectar aparelho")
    print("  5. Escaneie o QR Code que acabou de abrir")
    print()
    print("=" * 60)

    # Abrir imagem
    import subprocess
    subprocess.run(['open', filename])

else:
    print(f"❌ QR Code não disponível (Count: {data.get('count', 0)})")
    print("Aguarde alguns segundos e tente novamente.")
