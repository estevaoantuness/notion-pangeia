#!/bin/bash

# Deploy Script para Railway.app
# Sistema: Notion Pangeia com Evolution API + Motor Psicológico

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DEPLOY RAILWAY - NOTION PANGEIA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI não encontrado${NC}"
    echo ""
    echo "Instale com:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Ou visite: https://docs.railway.app/develop/cli"
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI encontrado${NC}"
echo ""

# Login no Railway
echo -e "${BLUE}📝 Fazendo login no Railway...${NC}"
railway login

echo ""
echo -e "${BLUE}📦 Criando projeto no Railway...${NC}"
echo ""
echo "Você será direcionado para o navegador para criar o projeto."
echo "Depois volte aqui para continuar."
echo ""

# Inicializar projeto
railway init

echo ""
echo -e "${GREEN}✅ Projeto criado!${NC}"
echo ""

# Configurar variáveis de ambiente
echo -e "${BLUE}⚙️  Configurando variáveis de ambiente...${NC}"
echo ""

# Ler .env.production
if [ -f ".env.production" ]; then
    echo -e "${YELLOW}Usando .env.production como base${NC}"
    echo ""

    # Adicionar variáveis
    railway variables set -f .env.production

    echo ""
    echo -e "${GREEN}✅ Variáveis configuradas!${NC}"
else
    echo -e "${RED}❌ Arquivo .env.production não encontrado${NC}"
    echo ""
    echo "Configure manualmente com:"
    echo "  railway variables set EVOLUTION_API_URL=..."
    echo ""
    exit 1
fi

echo ""
echo -e "${BLUE}🚀 Fazendo deploy...${NC}"
echo ""

# Deploy
railway up

echo ""
echo -e "${GREEN}✅ Deploy completo!${NC}"
echo ""

# Obter URL
echo -e "${BLUE}📋 Informações do deploy:${NC}"
echo ""

# Mostrar domínio
DOMAIN=$(railway domain 2>/dev/null)

if [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}URL: https://${DOMAIN}${NC}"
    echo -e "${GREEN}Webhook: https://${DOMAIN}/webhook/whatsapp${NC}"
    echo ""

    # Salvar webhook URL
    WEBHOOK_URL="https://${DOMAIN}/webhook/whatsapp"

    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  PRÓXIMO PASSO: Configurar Webhook Evolution${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Execute:"
    echo ""
    echo -e "${BLUE}  ./configure_webhook.sh${NC}"
    echo ""
    echo "Ou manualmente:"
    echo ""
    echo "  curl -X PUT \\"
    echo "    https://pange-evolution-api.u5qiqp.easypanel.host/webhook/48019ee7-c9f5-4409-825c-41888e6b0b27 \\"
    echo "    -H \"apikey: 4487C5C69D4A-4795-8FE8-E1296D76978F\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"url\": \"${WEBHOOK_URL}\", \"events\": [\"MESSAGES_UPSERT\"]}'"
    echo ""
else
    echo -e "${YELLOW}⚠️  Não foi possível obter domínio automaticamente${NC}"
    echo ""
    echo "Acesse: https://railway.app/dashboard"
    echo "E configure o webhook manualmente"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deploy completo!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
