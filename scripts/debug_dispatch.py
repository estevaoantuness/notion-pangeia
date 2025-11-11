#!/usr/bin/env python3
"""
Debug Dispatch System

Verifica qual é a lista de usuários que o bot está usando para disparos.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("=" * 80)
    print("🔍 DEBUG: SISTEMA DE DISPAROS")
    print("=" * 80)
    print()

    # 1. Verificar colaboradores carregados
    print("1️⃣  COLABORADORES CARREGADOS:")
    print("-" * 80)
    try:
        from config.colaboradores import COLABORADORES, get_colaboradores_ativos

        print(f"Total na config: {len(COLABORADORES)}")
        print(f"Ativos: {len(get_colaboradores_ativos())}\n")

        print("Status de cada colaborador:")
        for nome, info in COLABORADORES.items():
            status = "✅ ATIVO" if info.get("ativo") else "❌ INATIVO"
            phone = info.get("telefone", "N/A")
            print(f"  {status:12} | {nome:20} | {phone}")

        print("\n✓ Colaboradores ativos que receberão disparos:")
        for nome in get_colaboradores_ativos().keys():
            print(f"  → {nome}")

    except Exception as e:
        print(f"✗ Erro ao carregar colaboradores: {e}")
        return 1

    # 2. Verificar variáveis de ambiente
    print("\n" + "=" * 80)
    print("2️⃣  VARIÁVEIS DE AMBIENTE:")
    print("-" * 80)

    vars_to_check = [
        "ENABLE_RANDOM_CHECKINS",
        "ENABLE_LATE_NIGHT_CHECKINS",
        "ENVIRONMENT",
        "SCHEDULER_ENABLED",
    ]

    for var in vars_to_check:
        value = os.getenv(var, "NÃO CONFIGURADO")
        print(f"  {var:30} = {value}")

    # 3. Verificar se scheduler está habilitado
    print("\n" + "=" * 80)
    print("3️⃣  SCHEDULER:")
    print("-" * 80)

    scheduler_enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    print(f"  Scheduler habilitado: {'✅ SIM' if scheduler_enabled else '❌ NÃO'}")

    if scheduler_enabled:
        print("  Status: Bot ESTÁ enviando mensagens")
    else:
        print("  Status: Bot NÃO está enviando mensagens")

    # 4. Verificar se há fallback de Google Sheets
    print("\n" + "=" * 80)
    print("4️⃣  FALLBACK (Google Sheets):")
    print("-" * 80)

    sheets_url = os.getenv("GOOGLE_SHEETS_URL")
    if sheets_url:
        print(f"  ⚠️  Google Sheets configurada: {sheets_url[:50]}...")
        print("  Isso PODE estar sobrescrevendo a config de colaboradores!")
    else:
        print("  ✓ Google Sheets NÃO configurada")
        print("  Usando apenas config/colaboradores.py")

    # 5. Recomendação
    print("\n" + "=" * 80)
    print("5️⃣  DIAGNÓSTICO:")
    print("-" * 80)

    active_collab = get_colaboradores_ativos()

    if len(active_collab) == 1 and "Estevao" in list(active_collab.keys())[0]:
        print("✅ CONFIG CORRETA!")
        print("   → Apenas Estevão configurado para receber")
        print("   → Se outros estão recebendo, é problema de:")
        print("      1. Cache no Railway (deploy antigo)")
        print("      2. Google Sheets sobrescrevendo config")
        print("      3. Bot rodando versão antiga do código")
    else:
        print("❌ PROBLEMA DETECTADO!")
        print(f"   → {len(active_collab)} usuários ativos")
        print("   → Apenas Estevão deveria estar ativo")

    print("\n" + "=" * 80)
    print("AÇÃO RECOMENDADA:")
    print("-" * 80)
    print("1. Se estão recebendo: Fazer novo redeploy no Railway")
    print("2. Se problema persistir: Checar Google Sheets URL")
    print("3. Se ainda não resolver: Verificar logs do Railway")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
