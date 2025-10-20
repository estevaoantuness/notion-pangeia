#!/bin/bash
# Script para obter QR Code da Evolution API

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE="pangeia-bot"

echo "🔄 Deletando instância antiga..."
curl -s -X DELETE "${API_URL}/instance/delete/${INSTANCE}" -H "apikey: ${API_KEY}"
echo ""
echo ""

echo "✨ Criando nova instância..."
curl -s -X POST "${API_URL}/instance/create" \
  -H "apikey: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"instanceName\":\"${INSTANCE}\",\"qrcode\":true,\"integration\":\"WHATSAPP-BAILEYS\"}" | python3 -m json.tool
echo ""
echo ""

echo "⏳ Aguardando 10 segundos para gerar QR Code..."
sleep 10

echo "📲 Tentando obter QR Code..."
for i in {1..10}; do
  echo "   Tentativa $i/10..."
  RESPONSE=$(curl -s -X GET "${API_URL}/instance/connect/${INSTANCE}" -H "apikey: ${API_KEY}")
  echo "   Resposta: $RESPONSE"

  # Verificar se há QR code
  if echo "$RESPONSE" | grep -q "code"; then
    echo ""
    echo "✅ QR CODE ENCONTRADO!"
    echo "$RESPONSE" | python3 -m json.tool
    exit 0
  fi

  sleep 3
done

echo ""
echo "❌ Não foi possível obter QR Code após 10 tentativas"
