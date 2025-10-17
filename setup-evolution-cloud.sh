#!/bin/bash

# Script interativo para configurar Evolution Cloud

set -e

echo "=========================================="
echo "🚀 EVOLUTION CLOUD - SETUP WIZARD"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[PASSO $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Passo 1: Informações
print_step "1" "Bem-vindo ao Setup Wizard"
echo ""
echo "Este script irá ajudá-lo a configurar o Evolution Cloud."
echo ""
echo "Você precisará:"
echo "  1. Criar uma conta no Evolution Cloud"
echo "  2. Criar uma instância WhatsApp"
echo "  3. Copiar as credenciais"
echo ""
read -p "Pressione ENTER para continuar..."

# Passo 2: Abrir navegador
print_step "2" "Criando conta no Evolution Cloud"
echo ""
echo "Opções de provedor:"
echo "  1. Evolution API Official (Recomendado)"
echo "  2. Railway (Self-hosted - Free tier)"
echo "  3. DigitalOcean (Self-hosted)"
echo ""
read -p "Escolha uma opção (1-3): " provider_choice

case $provider_choice in
    1)
        echo ""
        echo "Abrindo Evolution API Official..."
        open "https://evolution-api.com" 2>/dev/null || echo "Abra manualmente: https://evolution-api.com"
        ;;
    2)
        echo ""
        echo "Abrindo Railway..."
        open "https://railway.app/template/evolution-api" 2>/dev/null || echo "Abra manualmente: https://railway.app"
        ;;
    3)
        echo ""
        echo "Para DigitalOcean, você precisará:"
        echo "  1. Criar um Droplet Ubuntu"
        echo "  2. Instalar Docker"
        echo "  3. Deploy Evolution API via Docker Compose"
        echo ""
        echo "Tutorial: https://doc.evolution-api.com/install/docker"
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "Após criar sua conta e instância, volte aqui!"
echo ""
read -p "Pressione ENTER quando tiver criado a conta e instância..."

# Passo 3: Coletar credenciais
print_step "3" "Configurando credenciais"
echo ""

read -p "Cole a URL da API (ex: https://api.evolution.com): " EVOLUTION_URL
read -p "Cole a API Key: " EVOLUTION_KEY
read -p "Nome da instância (padrão: pangeia-bot): " EVOLUTION_INSTANCE
EVOLUTION_INSTANCE=${EVOLUTION_INSTANCE:-pangeia-bot}

# Validar URL
if [[ ! $EVOLUTION_URL =~ ^https?:// ]]; then
    print_error "URL inválida. Deve começar com http:// ou https://"
    exit 1
fi

# Remover trailing slash da URL
EVOLUTION_URL=${EVOLUTION_URL%/}

echo ""
print_success "Credenciais coletadas:"
echo "  URL: $EVOLUTION_URL"
echo "  API Key: ${EVOLUTION_KEY:0:20}..."
echo "  Instância: $EVOLUTION_INSTANCE"
echo ""

# Passo 4: Atualizar .env
print_step "4" "Atualizando arquivo .env"
echo ""

ENV_FILE=".env"

# Backup do .env atual
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Backup criado: ${ENV_FILE}.backup.*"
fi

# Atualizar ou criar .env
if [ -f "$ENV_FILE" ]; then
    # Atualizar valores existentes
    sed -i.tmp "s|^EVOLUTION_API_URL=.*|EVOLUTION_API_URL=$EVOLUTION_URL|" "$ENV_FILE"
    sed -i.tmp "s|^EVOLUTION_API_KEY=.*|EVOLUTION_API_KEY=$EVOLUTION_KEY|" "$ENV_FILE"
    sed -i.tmp "s|^EVOLUTION_INSTANCE_NAME=.*|EVOLUTION_INSTANCE_NAME=$EVOLUTION_INSTANCE|" "$ENV_FILE"
    rm "${ENV_FILE}.tmp"
else
    # Criar novo .env
    cat > "$ENV_FILE" <<EOF
# Evolution API WhatsApp Configuration
EVOLUTION_API_URL=$EVOLUTION_URL
EVOLUTION_API_KEY=$EVOLUTION_KEY
EVOLUTION_INSTANCE_NAME=$EVOLUTION_INSTANCE

# Notion Configuration
NOTION_TOKEN=secret_your_token_here
NOTION_TASKS_DB_ID=your_database_id_here

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
WEBHOOK_PATH=/whatsapp/incoming
PORT=5000

# Scheduler Configuration
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo

# Application Settings
LOG_LEVEL=INFO
CACHE_EXPIRY_HOURS=24
MAX_RETRIES=3
ENVIRONMENT=development
EOF
fi

print_success "Arquivo .env atualizado"

# Passo 5: Testar conexão
print_step "5" "Testando conexão com Evolution Cloud"
echo ""

echo "Testando conectividade..."

# Teste básico com curl
RESPONSE=$(curl -s -w "\n%{http_code}" "$EVOLUTION_URL" || echo "000")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    print_success "API está acessível (HTTP $HTTP_CODE)"
else
    print_error "API não está acessível (HTTP $HTTP_CODE)"
    echo "Verifique se a URL está correta"
    exit 1
fi

# Teste com API Key
echo ""
echo "Testando autenticação..."

INSTANCES_RESPONSE=$(curl -s -H "apikey: $EVOLUTION_KEY" "$EVOLUTION_URL/instance/fetchInstances" || echo "error")

if echo "$INSTANCES_RESPONSE" | grep -q "$EVOLUTION_INSTANCE"; then
    print_success "Instância '$EVOLUTION_INSTANCE' encontrada!"
elif echo "$INSTANCES_RESPONSE" | grep -q "\["; then
    print_warning "API Key válida, mas instância '$EVOLUTION_INSTANCE' não encontrada"
    echo "Instâncias disponíveis:"
    echo "$INSTANCES_RESPONSE" | python3 -m json.tool 2>/dev/null | grep '"name"' || echo "Nenhuma"
else
    print_error "Erro ao autenticar. Verifique a API Key"
    exit 1
fi

# Passo 6: Obter QR Code
print_step "6" "Obtendo QR Code"
echo ""

echo "Iniciando servidor web local para exibir QR Code..."
echo ""

# Matar servidor anterior se existir
pkill -f "qr-web.py" 2>/dev/null || true

# Iniciar servidor
python3 qr-web.py > /dev/null 2>&1 &
SERVER_PID=$!

sleep 3

# Abrir navegador
open "http://localhost:8000"

echo ""
print_success "Servidor QR Code iniciado!"
echo ""
echo "=========================================="
echo "📱 PRÓXIMOS PASSOS:"
echo "=========================================="
echo ""
echo "1. O navegador deve abrir automaticamente"
echo "   URL: http://localhost:8000"
echo ""
echo "2. Aguarde o QR Code aparecer (10-15 segundos)"
echo ""
echo "3. Abra WhatsApp no celular:"
echo "   → Configurações"
echo "   → Aparelhos conectados"
echo "   → Conectar aparelho"
echo "   → Escaneie o QR Code"
echo ""
echo "4. Aguarde a conexão"
echo ""
echo "=========================================="
echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Para parar o servidor:"
echo "  kill $SERVER_PID"
echo ""
echo "Para testar o bot:"
echo "  python3 test_connections.py"
echo ""
echo "=========================================="
