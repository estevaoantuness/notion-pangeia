#!/bin/bash

# Recria instância do WhatsApp com QR Code

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "========================================="
echo "Recriando instância WhatsApp..."
echo "========================================="
echo ""

# Cria nova instância
echo "📱 Criando instância '$INSTANCE_NAME'..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: $API_KEY" \
  -d "{\"instanceName\": \"$INSTANCE_NAME\", \"qrcode\": true, \"integration\": \"WHATSAPP-BAILEYS\"}")

echo "$CREATE_RESPONSE" | jq '.'

# Aguarda 3 segundos para instância inicializar
echo ""
echo "⏳ Aguardando instância inicializar (3s)..."
sleep 3

# Tenta obter QR Code
echo ""
echo "📱 Obtendo QR Code..."
for i in {1..10}; do
    echo "Tentativa $i/10..."

    QR_RESPONSE=$(curl -s "$API_URL/instance/connect/$INSTANCE_NAME" \
      -H "apikey: $API_KEY")

    QR_CODE=$(echo "$QR_RESPONSE" | jq -r '.code // .base64 // empty')

    if [ -n "$QR_CODE" ] && [ "$QR_CODE" != "null" ]; then
        echo ""
        echo "========================================="
        echo "✅ QR CODE GERADO!"
        echo "========================================="
        echo ""
        echo "$QR_CODE"
        echo ""
        echo "========================================="
        echo ""
        echo "📱 Escaneie o QR Code acima com WhatsApp:"
        echo "   1. Abra WhatsApp no celular"
        echo "   2. Configurações → Aparelhos Conectados"
        echo "   3. Conectar um Aparelho"
        echo "   4. Escaneie o código acima"
        echo ""
        exit 0
    fi

    sleep 2
done

echo ""
echo "⚠️  QR Code não foi gerado automaticamente"
echo ""
echo "📋 Tente acessar o Manager UI:"
echo "   URL: http://localhost:8080/manager"
echo "   Senha: pange-bot-secret-key-2024"
echo ""
echo "Ou verifique os logs:"
echo "   docker logs evolution_api --tail 50"
echo ""
