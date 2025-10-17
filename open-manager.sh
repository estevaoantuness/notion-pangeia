#!/bin/bash

# Script para abrir o Evolution Manager no navegador
# e fornecer instruções de acesso

set -e

API_URL="http://localhost:8080"
MANAGER_URL="http://localhost:8080/manager/"
API_KEY="pange-bot-secret-key-2024"
INSTANCE_NAME="pangeia-bot"

echo "=========================================="
echo "🚀 EVOLUTION API MANAGER"
echo "=========================================="
echo ""

# Verificar se a API está rodando
echo "1️⃣  Verificando se Evolution API está rodando..."
if curl -s -f "$API_URL" > /dev/null 2>&1; then
    echo "✅ API está rodando"
else
    echo "❌ API não está respondendo"
    echo ""
    echo "Por favor, inicie o Docker primeiro:"
    echo "  cd evolution-setup"
    echo "  docker-compose up -d"
    echo ""
    exit 1
fi

echo ""

# Verificar instâncias existentes
echo "2️⃣  Verificando instâncias..."
INSTANCES=$(curl -s -H "apikey: $API_KEY" "$API_URL/instance/fetchInstances" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

if [ "$INSTANCES" -gt 0 ]; then
    echo "✅ Encontrada(s) $INSTANCES instância(s)"

    # Verificar se pangeia-bot existe
    HAS_PANGEIA=$(curl -s -H "apikey: $API_KEY" "$API_URL/instance/fetchInstances" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); print(any(i['name']=='pangeia-bot' for i in data))" 2>/dev/null || echo "False")

    if [ "$HAS_PANGEIA" = "True" ]; then
        echo "✅ Instância 'pangeia-bot' encontrada"
    else
        echo "⚠️  Instância 'pangeia-bot' não encontrada"
        echo ""
        echo "Criando instância..."

        CREATE_RESULT=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -H "apikey: $API_KEY" \
            "$API_URL/instance/create" \
            -d "{
                \"instanceName\": \"$INSTANCE_NAME\",
                \"qrcode\": true,
                \"integration\": \"WHATSAPP-BAILEYS\"
            }")

        if echo "$CREATE_RESULT" | grep -q "$INSTANCE_NAME"; then
            echo "✅ Instância criada com sucesso"
        else
            echo "❌ Erro ao criar instância"
            echo "$CREATE_RESULT"
        fi
    fi
else
    echo "⚠️  Nenhuma instância encontrada"
    echo ""
    echo "Criando instância 'pangeia-bot'..."

    CREATE_RESULT=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "apikey: $API_KEY" \
        "$API_URL/instance/create" \
        -d "{
            \"instanceName\": \"$INSTANCE_NAME\",
            \"qrcode\": true,
            \"integration\": \"WHATSAPP-BAILEYS\"
        }")

    if echo "$CREATE_RESULT" | grep -q "$INSTANCE_NAME"; then
        echo "✅ Instância criada com sucesso"
        echo "⏳ Aguardando 5 segundos para inicialização..."
        sleep 5
    else
        echo "❌ Erro ao criar instância"
        echo "$CREATE_RESULT"
    fi
fi

echo ""
echo "=========================================="
echo "📱 ABRINDO EVOLUTION MANAGER"
echo "=========================================="
echo ""
echo "URL: $MANAGER_URL"
echo ""
echo "📋 CREDENCIAIS:"
echo "   API Key: $API_KEY"
echo ""
echo "🔑 INSTRUÇÕES DE LOGIN:"
echo "   1. Na tela de login, cole a API Key acima"
echo "   2. Clique em 'Login' ou 'Entrar'"
echo ""
echo "📱 COMO CONECTAR O WHATSAPP:"
echo "   1. Procure a instância 'pangeia-bot' na lista"
echo "   2. Clique no botão 'Connect' ou ícone de QR Code"
echo "   3. O QR Code aparecerá na tela"
echo "   4. Abra WhatsApp no celular:"
echo "      → Configurações"
echo "      → Aparelhos conectados"
echo "      → Conectar aparelho"
echo "   5. Escaneie o QR Code exibido no navegador"
echo ""
echo "=========================================="
echo ""

# Aguardar um pouco antes de abrir
sleep 2

# Abrir navegador (funciona no macOS)
if command -v open &> /dev/null; then
    echo "🌐 Abrindo navegador..."
    open "$MANAGER_URL"
    echo "✅ Navegador aberto!"
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Abrindo navegador..."
    xdg-open "$MANAGER_URL"
    echo "✅ Navegador aberto!"
else
    echo "⚠️  Não foi possível abrir o navegador automaticamente"
    echo ""
    echo "Por favor, abra manualmente este link:"
    echo "   $MANAGER_URL"
fi

echo ""
echo "=========================================="
echo "💡 DICAS:"
echo "=========================================="
echo ""
echo "• Se não aparecer QR Code, aguarde 10-15 segundos"
echo "• Se o QR expirar, clique em 'Reconnect'"
echo "• Para verificar conexão: veja se status muda para 'open'"
echo "• Problemas? Execute: docker logs evolution_api"
echo ""
echo "=========================================="
echo "✅ Pronto! Boa sorte!"
echo "=========================================="
echo ""
