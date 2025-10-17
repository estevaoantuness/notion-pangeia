#!/bin/bash

# Check WhatsApp connection status
# Usage: ./check-connection.sh

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "========================================="
echo "Verificando conexão WhatsApp..."
echo "========================================="
echo ""

# Obter estado da conexão
CONN_RESPONSE=$(curl -s "$API_URL/instance/connectionState/$INSTANCE_NAME" \
  -H "apikey: $API_KEY")

echo "Status da Conexão:"
echo "$CONN_RESPONSE" | jq '.'
echo ""

STATE=$(echo "$CONN_RESPONSE" | jq -r '.state')

if [ "$STATE" == "open" ]; then
    echo "✅ WhatsApp conectado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Configurar webhook: ./setup-webhook.sh"
    echo "2. Testar envio: ./test-send.sh +5511999999999"
    echo "3. Atualizar .env do projeto com as credenciais"
elif [ "$STATE" == "connecting" ]; then
    echo "⏳ Conectando... Aguarde e execute este script novamente."
elif [ "$STATE" == "close" ]; then
    echo "❌ Desconectado. Execute: ./setup-whatsapp.sh para gerar novo QR Code"
else
    echo "⚠️  Estado: $STATE"
fi

echo ""
