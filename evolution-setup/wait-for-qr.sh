#!/bin/bash

# Script que aguarda até o QR Code ser gerado

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "⏳ Aguardando QR Code ser gerado..."
echo "Tentando a cada 5 segundos (máximo 60 segundos)..."
echo ""

for i in {1..12}; do
    echo "Tentativa $i/12..."

    QR_CODE=$(curl -s "$API_URL/instance/connect/$INSTANCE_NAME" \
      -H "apikey: $API_KEY" | jq -r '.code')

    if [ "$QR_CODE" != "null" ] && [ -n "$QR_CODE" ] && [ "$QR_CODE" != "" ]; then
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

    sleep 5
done

echo ""
echo "⚠️  QR Code não foi gerado após 60 segundos"
echo ""
echo "📋 Opções:"
echo "   1. Acesse o Manager UI: http://localhost:8080/manager"
echo "   2. Veja os logs: docker logs evolution_api --tail 50"
echo "   3. Tente deletar e recriar a instância"
echo ""
