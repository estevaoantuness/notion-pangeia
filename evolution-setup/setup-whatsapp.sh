#!/bin/bash

# Helper script para configurar WhatsApp na Evolution API
# Usage: ./setup-whatsapp.sh

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "========================================="
echo "Evolution API - Setup WhatsApp"
echo "========================================="
echo ""

# 1. Criar instância
echo "📱 Criando instância WhatsApp..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: $API_KEY" \
  -d "{
    \"instanceName\": \"$INSTANCE_NAME\",
    \"qrcode\": true,
    \"integration\": \"WHATSAPP-BAILEYS\"
  }")

echo "Resposta:"
echo "$CREATE_RESPONSE" | jq '.'
echo ""

# Aguardar um pouco para gerar QR Code
sleep 5

# 2. Obter QR Code
echo "🔲 Obtendo QR Code..."
QR_RESPONSE=$(curl -s "$API_URL/instance/connect/$INSTANCE_NAME" \
  -H "apikey: $API_KEY")

# Extrair código QR (texto)
QR_CODE=$(echo "$QR_RESPONSE" | jq -r '.code')

if [ "$QR_CODE" != "null" ] && [ -n "$QR_CODE" ]; then
    echo ""
    echo "========================================="
    echo "📱 ESCANEIE O QR CODE ABAIXO:"
    echo "========================================="
    echo ""
    echo "$QR_CODE"
    echo ""
    echo "========================================="
    echo ""

    # Salvar QR Code em arquivo
    echo "$QR_CODE" > qrcode.txt
    echo "✅ QR Code salvo em: qrcode.txt"
    echo ""

    # Salvar base64 também
    QR_BASE64=$(echo "$QR_RESPONSE" | jq -r '.base64')
    if [ "$QR_BASE64" != "null" ]; then
        echo "$QR_BASE64" > qrcode_base64.txt
        echo "✅ QR Code (base64) salvo em: qrcode_base64.txt"
    fi
else
    echo "❌ Não foi possível obter o QR Code"
    echo "Resposta completa:"
    echo "$QR_RESPONSE" | jq '.'
fi

echo ""
echo "📋 Próximos passos:"
echo "1. Abra WhatsApp no celular"
echo "2. Vá em 'Aparelhos Conectados'"
echo "3. Clique em 'Conectar um Aparelho'"
echo "4. Escaneie o QR Code acima"
echo ""
echo "⏳ Após escanear, aguarde 10 segundos e execute:"
echo "   ./check-connection.sh"
echo ""
