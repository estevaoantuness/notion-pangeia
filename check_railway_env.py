"""
Script para verificar variáveis de ambiente no Railway.
Adicione um endpoint /check-env no app.py temporariamente para debug.
"""
import os

print("=" * 60)
print("🔍 VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
print("=" * 60)

# Lista de variáveis críticas
critical_vars = [
    "OPENAI_API_KEY",
    "NOTION_TOKEN",
    "NOTION_TASKS_DB_ID",
    "EVOLUTION_API_URL",
    "EVOLUTION_API_KEY",
    "EVOLUTION_INSTANCE_NAME",
]

for var in critical_vars:
    value = os.getenv(var, "")
    if value:
        # Mascara valores sensíveis
        if len(value) > 20:
            masked = f"{value[:10]}...{value[-10:]}"
        else:
            masked = f"{value[:5]}..."
        print(f"✅ {var}: {masked} ({len(value)} chars)")
    else:
        print(f"❌ {var}: NÃO CONFIGURADA!")

print("=" * 60)
