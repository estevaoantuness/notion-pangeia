#!/bin/bash

# Script para configurar webhook Evolution API

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 CONFIGURAR WEBHOOK EVOLUTION API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Evolution API Config
EVOLUTION_URL="https://pange-evolution-api.u5qiqp.easypanel.host"
API_KEY="4487C5C69D4A-4795-8FE8-E1296D76978F"
INSTANCE="48019ee7-c9f5-4409-825c-41888e6b0b27"

# Solicitar URL do webhook
echo -e "${BLUE}Digite a URL do seu bot no Railway:${NC}"
echo "(exemplo: https://notion-pangeia-production.up.railway.app)"
echo ""
read -p "URL: " BOT_URL

if [ -z "$BOT_URL" ]; then
    echo -e "${RED}❌ URL não pode ser vazia${NC}"
    exit 1
fi

# Construir webhook URL
WEBHOOK_URL="${BOT_URL}/webhook/whatsapp"

echo ""
echo -e "${BLUE}📡 Configurando webhook...${NC}"
echo ""
echo "Webhook URL: $WEBHOOK_URL"
echo ""

# Configurar webhook
RESPONSE=$(curl -s -X PUT \
  "${EVOLUTION_URL}/webhook/${INSTANCE}" \
  -H "apikey: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"webhook_by_events\": false,
    \"events\": [\"MESSAGES_UPSERT\"]
  }")

echo ""
echo -e "${BLUE}Resposta:${NC}"
echo "$RESPONSE"
echo ""

# Verificar se foi sucesso
if echo "$RESPONSE" | grep -q "\"webhook\""; then
    echo -e "${GREEN}✅ Webhook configurado com sucesso!${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📝 PRÓXIMO PASSO: Testar${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1. Envie uma mensagem no WhatsApp: \"oi\""
    echo "2. Verifique os logs no Railway: railway logs"
    echo "3. Você deve receber uma resposta do bot"
    echo ""
else
    echo -e "${RED}❌ Erro ao configurar webhook${NC}"
    echo ""
    echo "Tente manualmente:"
    echo ""
    echo "curl -X PUT \\"
    echo "  ${EVOLUTION_URL}/webhook/${INSTANCE} \\"
    echo "  -H \"apikey: ${API_KEY}\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"url\": \"${WEBHOOK_URL}\", \"events\": [\"MESSAGES_UPSERT\"]}'"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Configuração completa!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
