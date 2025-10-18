#!/bin/bash

# Deploy Script para Render.com
# Sistema: Notion Pangeia com Evolution API + Motor Psicológico

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DEPLOY RENDER - NOTION PANGEIA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Render API Config
RENDER_API_KEY="rnd_SvZVnQCt6aIdNBmwaspZJiBlErNV"
RENDER_API_URL="https://api.render.com/v1"

# Verificar se .env.production existe
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Arquivo .env.production não encontrado${NC}"
    echo ""
    echo "Crie o arquivo .env.production com suas credenciais."
    exit 1
fi

echo -e "${GREEN}✅ .env.production encontrado${NC}"
echo ""

# Carregar variáveis do .env.production
export $(cat .env.production | grep -v '^#' | xargs)

# Verificar credenciais Notion
if [ "$NOTION_TOKEN" = "secret_xxxxx" ] || [ -z "$NOTION_TOKEN" ]; then
    echo -e "${RED}❌ NOTION_TOKEN não configurado em .env.production${NC}"
    echo ""
    echo "Edite .env.production e adicione suas credenciais Notion."
    exit 1
fi

echo -e "${GREEN}✅ Credenciais Notion configuradas${NC}"
echo ""

# GitHub repo
GITHUB_REPO="estevaoantuness/notion-pangeia"
SERVICE_NAME="notion-pangeia-bot"

echo -e "${BLUE}📦 Criando web service no Render...${NC}"
echo ""

# Obter owner ID
echo -e "${BLUE}🔍 Obtendo informações da conta...${NC}"
OWNERS_RESPONSE=$(curl -s -X GET "${RENDER_API_URL}/owners" \
  -H "Authorization: Bearer ${RENDER_API_KEY}")

OWNER_ID=$(echo "$OWNERS_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$OWNER_ID" ]; then
    echo -e "${RED}❌ Erro ao obter owner ID${NC}"
    echo ""
    echo "Resposta da API:"
    echo "$OWNERS_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Owner ID: ${OWNER_ID}${NC}"
echo ""

# Criar payload JSON para criar serviço
PAYLOAD=$(cat <<EOF
{
  "type": "web_service",
  "name": "${SERVICE_NAME}",
  "ownerId": "${OWNER_ID}",
  "repo": "https://github.com/${GITHUB_REPO}",
  "autoDeploy": "yes",
  "branch": "main",
  "serviceDetails": {
    "env": "python",
    "plan": "starter",
    "envSpecificDetails": {
      "buildCommand": "pip install -r requirements.txt",
      "startCommand": "gunicorn -w 4 -b 0.0.0.0:\$PORT app:app"
    }
  },
  "envVars": [
    {"key": "NOTION_TOKEN", "value": "${NOTION_TOKEN}"},
    {"key": "NOTION_TASKS_DB_ID", "value": "${NOTION_TASKS_DB_ID}"},
    {"key": "NOTION_USERS_DB_ID", "value": "${NOTION_USERS_DB_ID:-}"},
    {"key": "NOTION_CHECKINS_DB_ID", "value": "${NOTION_CHECKINS_DB_ID:-}"},
    {"key": "EVOLUTION_API_URL", "value": "${EVOLUTION_API_URL}"},
    {"key": "EVOLUTION_API_KEY", "value": "${EVOLUTION_API_KEY}"},
    {"key": "EVOLUTION_INSTANCE_NAME", "value": "${EVOLUTION_INSTANCE_NAME}"},
    {"key": "FLASK_SECRET_KEY", "value": "${FLASK_SECRET_KEY:-production-secret-key}"},
    {"key": "LOG_LEVEL", "value": "${LOG_LEVEL:-INFO}"},
    {"key": "ENVIRONMENT", "value": "${ENVIRONMENT:-production}"},
    {"key": "ENABLE_PSYCHOLOGY", "value": "${ENABLE_PSYCHOLOGY:-true}"},
    {"key": "ENABLE_MESSAGE_CHUNKING", "value": "${ENABLE_MESSAGE_CHUNKING:-true}"},
    {"key": "ENABLE_DEDUPLICATION", "value": "${ENABLE_DEDUPLICATION:-true}"},
    {"key": "DAILY_SEND_TIME", "value": "${DAILY_SEND_TIME:-08:00}"},
    {"key": "CHECKIN_1_TIME", "value": "${CHECKIN_1_TIME:-13:30}"},
    {"key": "CHECKIN_2_TIME", "value": "${CHECKIN_2_TIME:-15:30}"},
    {"key": "CHECKIN_3_TIME", "value": "${CHECKIN_3_TIME:-18:00}"},
    {"key": "CHECKIN_4_TIME", "value": "${CHECKIN_4_TIME:-22:00}"},
    {"key": "TIMEZONE", "value": "${TIMEZONE:-America/Sao_Paulo}"}
  ]
}
EOF
)

# Criar serviço
RESPONSE=$(curl -s -X POST "${RENDER_API_URL}/services" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")

# Verificar se criou com sucesso
if echo "$RESPONSE" | grep -q '"id"'; then
    echo -e "${GREEN}✅ Serviço criado com sucesso!${NC}"
    echo ""

    # Extrair service ID e URL
    SERVICE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    SERVICE_URL=$(echo "$RESPONSE" | grep -o '"serviceUrl":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$SERVICE_URL" ]; then
        # Tentar construir URL do service name
        SERVICE_URL="https://${SERVICE_NAME}.onrender.com"
    fi

    echo -e "${BLUE}Service ID: ${SERVICE_ID}${NC}"
    echo -e "${BLUE}Service URL: ${SERVICE_URL}${NC}"
    echo ""

    # Salvar informações
    echo "SERVICE_ID=${SERVICE_ID}" > .render_deploy_info
    echo "SERVICE_URL=${SERVICE_URL}" >> .render_deploy_info

    echo -e "${YELLOW}⏳ Aguardando deploy inicial...${NC}"
    echo ""
    echo "Isso pode levar de 5-10 minutos."
    echo "Você pode acompanhar em: https://dashboard.render.com/"
    echo ""

    # Aguardar um pouco
    echo -e "${BLUE}Aguardando 30 segundos...${NC}"
    sleep 30

    echo ""
    echo -e "${GREEN}✅ Deploy iniciado!${NC}"
    echo ""

    # Webhook URL
    WEBHOOK_URL="${SERVICE_URL}/webhook/whatsapp"

    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  PRÓXIMO PASSO: Configurar Webhook Evolution${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Aguarde o deploy completar (verifique em dashboard.render.com)"
    echo "Depois execute:"
    echo ""
    echo -e "${BLUE}  ./configure_webhook_render.sh${NC}"
    echo ""

else
    echo -e "${RED}❌ Erro ao criar serviço${NC}"
    echo ""
    echo "Resposta da API:"
    echo "$RESPONSE"
    echo ""

    # Verificar se serviço já existe
    if echo "$RESPONSE" | grep -q "already exists"; then
        echo -e "${YELLOW}⚠️  Serviço já existe. Listando serviços...${NC}"
        echo ""

        # Listar serviços
        SERVICES=$(curl -s -X GET "${RENDER_API_URL}/services" \
          -H "Authorization: Bearer ${RENDER_API_KEY}")

        echo "$SERVICES" | grep -o '"name":"[^"]*"' | head -5
        echo ""
        echo "Acesse https://dashboard.render.com/ para gerenciar"
    fi

    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deploy Render iniciado!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Dashboard: https://dashboard.render.com/"
echo "Service URL: ${SERVICE_URL}"
echo "Webhook URL: ${WEBHOOK_URL}"
echo ""
