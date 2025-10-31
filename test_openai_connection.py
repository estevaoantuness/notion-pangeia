"""
Script para testar conexão com OpenAI API.
Ajuda a diagnosticar problemas com o client retornando None.
"""
import os
import sys

print("=" * 60)
print("🔍 DIAGNÓSTICO: OpenAI Client")
print("=" * 60)

# 1. Verificar variável de ambiente
print("\n1️⃣ Verificando OPENAI_API_KEY...")
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("❌ OPENAI_API_KEY não encontrada nas variáveis de ambiente!")
    print("   Configure com: export OPENAI_API_KEY='sk-proj-...'")
    sys.exit(1)

print(f"✅ OPENAI_API_KEY encontrada")
print(f"   Comprimento: {len(api_key)} caracteres")
print(f"   Prefixo: {api_key[:20]}...")
print(f"   Sufixo: ...{api_key[-10:]}")

# 2. Testar import do OpenAI
print("\n2️⃣ Testando import do OpenAI...")
try:
    from openai import OpenAI
    print("✅ Módulo openai importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar openai: {e}")
    print("   Instale com: pip install openai")
    sys.exit(1)

# 3. Testar inicialização do client
print("\n3️⃣ Testando inicialização do client...")
try:
    client = OpenAI(api_key=api_key)
    print("✅ Client OpenAI inicializado com sucesso")
    print(f"   Tipo: {type(client)}")
    print(f"   Client is None? {client is None}")
except Exception as e:
    print(f"❌ Erro ao inicializar client: {e}")
    sys.exit(1)

# 4. Testar conexão real com API (chamada simples)
print("\n4️⃣ Testando conexão com API (chamada real)...")
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": "Diga apenas 'OK' para confirmar que você está funcionando."}
        ],
        max_tokens=10,
        temperature=0.3
    )

    result = response.choices[0].message.content.strip()
    print(f"✅ API respondeu com sucesso!")
    print(f"   Resposta: '{result}'")
    print(f"   Model usado: {response.model}")
    print(f"   Tokens usados: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ Erro ao chamar API: {e}")
    print(f"   Tipo do erro: {type(e).__name__}")
    sys.exit(1)

# 5. Testar import do config (como o app faz)
print("\n5️⃣ Testando import do config/openai_config.py...")
try:
    from config.openai_config import client as config_client
    print(f"✅ Config importado com sucesso")
    print(f"   Client do config is None? {config_client is None}")

    if config_client is None:
        print("❌ PROBLEMA ENCONTRADO!")
        print("   O client no config/openai_config.py está None!")
        print("   Possíveis causas:")
        print("   - OPENAI_API_KEY não estava setada quando o módulo foi importado")
        print("   - Erro na inicialização que foi capturado silenciosamente")
    else:
        print(f"✅ Client do config está OK (tipo: {type(config_client)})")

except Exception as e:
    print(f"❌ Erro ao importar config: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 60)
