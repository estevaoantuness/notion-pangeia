#!/bin/bash

# Script para iniciar o servidor de QR Code

echo "=========================================="
echo "🚀 QR CODE SERVER - Evolution API"
echo "=========================================="
echo ""
echo "Iniciando servidor..."
echo ""

# Matar processo anterior se existir
pkill -f "qrcode-server.py" 2>/dev/null

# Iniciar servidor
python3 /Users/estevaoantunes/notion-pangeia/qrcode-server.py &

# Aguardar um pouco
sleep 3

# Abrir navegador
echo "Abrindo navegador..."
open http://localhost:8000

echo ""
echo "=========================================="
echo "✅ Servidor iniciado!"
echo "=========================================="
echo ""
echo "📱 Acesse: http://localhost:8000"
echo ""
echo "🔄 O QR Code atualiza automaticamente a cada 30 segundos"
echo ""
echo "⚠️  Para parar o servidor:"
echo "   pkill -f qrcode-server.py"
echo ""
echo "=========================================="
