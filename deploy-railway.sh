#!/bin/bash
# Script para deploy automatizado no Railway

echo "🚀 Iniciando deployment no Railway..."

# Criar serviço via Railway API se não existir
# Como o CLI tem problemas com TTY, vamos usar a abordagem de commit e deixar
# o Railway detectar automaticamente

echo "✅ Código já está no GitHub (main branch)"
echo "📋 Próximos passos:"
echo ""
echo "1. Acesse: https://railway.app/project/notion-pangeia"
echo "2. Clique em '+ New Service'"
echo "3. Selecione 'GitHub Repo'"
echo "4. Escolha: estevaoantuness/notion-pangeia"
echo "5. O Railway vai detectar automaticamente:"
echo "   - Dockerfile ✅"
echo "   - railway.toml ✅"
echo "   - requirements.txt ✅"
echo ""
echo "6. Após criar, vá em 'Variables' e adicione:"
echo "   (Use o arquivo RAILWAY_BOT_ENV.md como referência)"
echo ""
echo "7. Vá em 'Settings' → 'Networking' → 'Generate Domain'"
echo ""
echo "Ou... deixe-me tentar fazer via CLI:"
read -p "Tentar via CLI? (s/n): " choice

if [ "$choice" = "s" ]; then
    echo "Tentando deployment via CLI..."
    railway up --detach 2>&1 || echo "❌ CLI falhou (esperado devido ao TTY)"
fi

echo ""
echo "📝 Alternativa: Use o Dashboard Web do Railway"
echo "É mais rápido e evita problemas de CLI!"
