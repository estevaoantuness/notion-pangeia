#!/bin/bash

# Script para resolver problemas de QR Code no Evolution API
# Diagnostica e corrige problemas comuns

set -e

API_URL="http://localhost:8080"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "======================================"
echo "🔧 FIX QR CODE - Evolution API"
echo "======================================"
echo ""

# Função auxiliar para colorir output
print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "ℹ️  $1"
}

print_warning() {
    echo "⚠️  $1"
}

# 1. Verificar se a API está respondendo
echo "1️⃣  Verificando Evolution API..."
if curl -s -f "$API_URL" > /dev/null 2>&1; then
    print_success "API está respondendo"
else
    print_error "API não está respondendo"
    print_info "Execute: cd evolution-setup && docker-compose up -d"
    exit 1
fi

echo ""

# 2. Deletar instância antiga (se existir)
echo "2️⃣  Limpando instância antiga..."
DELETE_RESPONSE=$(curl -s -X DELETE \
    -H "apikey: $API_KEY" \
    "$API_URL/instance/delete/$INSTANCE_NAME" 2>&1)

if echo "$DELETE_RESPONSE" | grep -q "SUCCESS\|deleted\|not found"; then
    print_success "Instância antiga removida"
else
    print_warning "Nenhuma instância antiga encontrada (isso é OK)"
fi

echo ""

# 3. Aguardar um pouco
echo "3️⃣  Aguardando limpeza do banco..."
sleep 3
print_success "Pronto"

echo ""

# 4. Criar nova instância
echo "4️⃣  Criando nova instância '$INSTANCE_NAME'..."
CREATE_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "apikey: $API_KEY" \
    "$API_URL/instance/create" \
    -d "{
        \"instanceName\": \"$INSTANCE_NAME\",
        \"qrcode\": true,
        \"integration\": \"WHATSAPP-BAILEYS\"
    }")

if echo "$CREATE_RESPONSE" | grep -q "$INSTANCE_NAME"; then
    print_success "Instância criada com sucesso"
else
    print_error "Erro ao criar instância"
    echo "$CREATE_RESPONSE"
    exit 1
fi

echo ""

# 5. Aguardar inicialização
echo "5️⃣  Aguardando inicialização do WhatsApp (15 segundos)..."
for i in {15..1}; do
    echo -ne "   Aguardando... $i segundos\r"
    sleep 1
done
echo ""
print_success "Inicialização completa"

echo ""

# 6. Verificar estado da conexão
echo "6️⃣  Verificando estado da instância..."
STATE_RESPONSE=$(curl -s -H "apikey: $API_KEY" \
    "$API_URL/instance/connectionState/$INSTANCE_NAME")

STATE=$(echo "$STATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['instance']['state'])" 2>/dev/null || echo "unknown")

if [ "$STATE" = "connecting" ] || [ "$STATE" = "close" ]; then
    print_success "Estado: $STATE (pronto para QR Code)"
elif [ "$STATE" = "open" ]; then
    print_warning "Já conectado! Não precisa de QR Code"
    exit 0
else
    print_warning "Estado: $STATE"
fi

echo ""

# 7. Tentar obter QR Code (até 3 tentativas)
echo "7️⃣  Obtendo QR Code..."

MAX_ATTEMPTS=5
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo ""
    print_info "Tentativa $ATTEMPT de $MAX_ATTEMPTS..."

    QR_RESPONSE=$(curl -s -H "apikey: $API_KEY" \
        "$API_URL/instance/connect/$INSTANCE_NAME")

    # Verificar se tem QR code
    QR_CODE=$(echo "$QR_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('code', ''))" 2>/dev/null || echo "")
    QR_BASE64=$(echo "$QR_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('base64', ''))" 2>/dev/null || echo "")

    if [ -n "$QR_CODE" ] && [ "$QR_CODE" != "None" ]; then
        print_success "QR Code obtido com sucesso!"
        echo ""
        echo "======================================"
        echo "📱 ESCANEIE O QR CODE ABAIXO:"
        echo "======================================"
        echo ""
        echo "$QR_CODE"
        echo ""
        echo "======================================"

        # Salvar base64 se disponível
        if [ -n "$QR_BASE64" ] && [ "$QR_BASE64" != "None" ]; then
            echo "$QR_BASE64" | base64 -d > qrcode.png 2>/dev/null && \
                print_success "QR Code salvo em: qrcode.png" || \
                print_warning "Não foi possível salvar o QR Code em arquivo"
        fi

        echo ""
        print_info "Abra o WhatsApp:"
        print_info "  → Configurações"
        print_info "  → Aparelhos conectados"
        print_info "  → Conectar aparelho"
        print_info "  → Escaneie o código acima"
        echo ""

        # Aguardar conexão
        echo "⏳ Aguardando conexão..."
        for i in {30..1}; do
            sleep 2
            CONN_STATE=$(curl -s -H "apikey: $API_KEY" \
                "$API_URL/instance/connectionState/$INSTANCE_NAME" | \
                python3 -c "import sys, json; print(json.load(sys.stdin)['instance']['state'])" 2>/dev/null || echo "unknown")

            if [ "$CONN_STATE" = "open" ]; then
                echo ""
                print_success "🎉 CONECTADO COM SUCESSO!"
                echo ""
                echo "======================================"
                echo "✅ Tudo pronto para usar!"
                echo "======================================"
                exit 0
            fi

            echo -ne "   Verificando conexão... ${i}x   \r"
        done

        echo ""
        print_warning "QR Code expirou. Gerando novo..."
        ATTEMPT=$((ATTEMPT + 1))
    else
        print_warning "QR Code ainda não disponível"
        print_info "Aguardando 5 segundos..."
        sleep 5
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo ""
print_error "Não foi possível obter o QR Code após $MAX_ATTEMPTS tentativas"
print_info "Possíveis soluções:"
echo "  1. Reiniciar o Docker: cd evolution-setup && docker-compose restart"
echo "  2. Ver logs: docker logs evolution_api --tail 100"
echo "  3. Verificar se a porta 8080 está acessível"
echo ""

exit 1
