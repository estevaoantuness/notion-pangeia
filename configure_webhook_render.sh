#!/bin/bash

# Script para configurar webhook Evolution API (Render)

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

# Verificar se tem deploy info
if [ -f ".render_deploy_info" ]; then
    echo -e "${BLUE}📋 Carregando informações do deploy...${NC}"
    echo ""
    source .render_deploy_info

    if [ -n "$SERVICE_URL" ]; then
        BOT_URL="$SERVICE_URL"
        echo -e "${GREEN}✅ URL encontrada: ${BOT_URL}${NC}"
        echo ""
    else
        # Solicitar URL
        echo -e "${BLUE}Digite a URL do seu bot no Render:${NC}"
        echo "(exemplo: https://notion-pangeia-bot.onrender.com)"
        echo ""
        read -p "URL: " BOT_URL
    fi
else
    # Solicitar URL
    echo -e "${BLUE}Digite a URL do seu bot no Render:${NC}"
    echo "(exemplo: https://notion-pangeia-bot.onrender.com)"
    echo ""
    read -p "URL: " BOT_URL
fi

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

# Testar se bot está online primeiro
echo -e "${BLUE}🔍 Testando se bot está online...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BOT_URL}/health" --max-time 10)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Bot está online!${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Bot não respondeu (HTTP ${HTTP_CODE})${NC}"
    echo "Você pode continuar, mas o webhook pode não funcionar até o bot estar online."
    echo ""
    read -p "Deseja continuar? (s/N): " CONTINUE

    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        echo "Abortado."
        exit 1
    fi
    echo ""
fi

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
echo -e "${BLUE}Resposta Evolution API:${NC}"
echo "$RESPONSE"
echo ""

# Verificar se foi sucesso
if echo "$RESPONSE" | grep -q "webhook"; then
    echo -e "${GREEN}✅ Webhook configurado com sucesso!${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📝 PRÓXIMO PASSO: Testar${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1. Envie uma mensagem no WhatsApp: \"oi\""
    echo "2. Verifique os logs no Render:"
    echo "   https://dashboard.render.com/ → Seu serviço → Logs"
    echo "3. Você deve receber uma resposta humanizada do bot"
    echo ""

    # Salvar webhook configurado
    echo "WEBHOOK_CONFIGURED=true" >> .render_deploy_info
    echo "WEBHOOK_URL=${WEBHOOK_URL}" >> .render_deploy_info

else
    echo -e "${RED}❌ Erro ao configurar webhook${NC}"
    echo ""

    # Verificar status da instância
    echo -e "${BLUE}🔍 Verificando status da instância Evolution...${NC}"
    echo ""

    STATUS_RESPONSE=$(curl -s -X GET \
      "${EVOLUTION_URL}/instance/${INSTANCE}/status" \
      -H "apikey: ${API_KEY}")

    echo "Status da instância:"
    echo "$STATUS_RESPONSE"
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
echo ""
echo "Webhook: ${WEBHOOK_URL}"
echo "Bot URL: ${BOT_URL}"
echo "Status: ✅ Configurado"
echo ""
