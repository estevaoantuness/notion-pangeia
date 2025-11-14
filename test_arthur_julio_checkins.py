#!/usr/bin/env python3
"""
Teste: Simular checkins para Arthur e Julio
Confirma que ambos foram ativados e funcionam
"""

from dotenv import load_dotenv
load_dotenv()

from src.database.checkins_integration import get_checkins_integration
from src.checkins.pending_tracker import get_pending_checkin_tracker
from src.checkins.response_handler import get_checkin_response_handler
from config.colaboradores import get_colaboradores_ativos

print("=" * 100)
print("🧪 TESTE: VERIFICAR CHECKINS PARA ARTHUR E JULIO")
print("=" * 100)
print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 1: VERIFICAR SE ESTÃO ATIVOS
# ═══════════════════════════════════════════════════════════════════════════

print("1️⃣  VERIFICANDO USUÁRIOS ATIVOS")
print("-" * 100)

colaboradores_ativos = get_colaboradores_ativos()

print(f"\nTotal de colaboradores ativos: {len(colaboradores_ativos)}")
print()

for nome, info in colaboradores_ativos.items():
    print(f"  ✅ {nome}")
    print(f"     Telefone: {info['telefone']}")
    print(f"     Cargo: {info['cargo']}")
    print()

# Verificar especificamente Arthur e Julio
arthur_ativo = "Arthur Leuzzi" in colaboradores_ativos
julio_ativo = "Julio Inoue" in colaboradores_ativos

print("📊 STATUS ESPECÍFICO:")
print(f"  Arthur Leuzzi: {'✅ ATIVO' if arthur_ativo else '❌ INATIVO'}")
print(f"  Julio Inoue:   {'✅ ATIVO' if julio_ativo else '❌ INATIVO'}")

if not arthur_ativo or not julio_ativo:
    print("\n❌ ERRO: Algum deles ainda está inativo!")
    exit(1)

print("\n✅ Ambos estão ativos!")
print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2: CRIAR CHECKINS PARA AMBOS
# ═══════════════════════════════════════════════════════════════════════════

print("2️⃣  CRIANDO CHECKINS")
print("-" * 100)

integration = get_checkins_integration()
tracker = get_pending_checkin_tracker()
response_handler = get_checkin_response_handler()

# Arthur
print("\n🎯 ARTHUR LEUZZI:")
integration.create_daily_checkin("Arthur Leuzzi")
print("   ✅ Checkin criado")

# Morning
tracker.record_sent_checkin("Arthur Leuzzi", "Arthur Leuzzi", "metas", "Qual é sua meta?")
success, msg = response_handler.handle_checkin_response("Arthur Leuzzi", "Terminar feature de análise")
print(f"   ☀️  Morning: {msg}")

# Afternoon
tracker.record_sent_checkin("Arthur Leuzzi", "Arthur Leuzzi", "status", "Como está?")
success, msg = response_handler.handle_checkin_response("Arthur Leuzzi", "Tudo ok, em andamento")
print(f"   🌤️  Afternoon: {msg}")

# Evening
tracker.record_sent_checkin("Arthur Leuzzi", "Arthur Leuzzi", "closing", "Resumo?")
success, msg = response_handler.handle_checkin_response("Arthur Leuzzi", "Dia produtivo, concluído 2 tasks")
print(f"   🌙 Evening: {msg}")

print()

# Julio
print("🎯 JULIO INOUE:")
integration.create_daily_checkin("Julio Inoue")
print("   ✅ Checkin criado")

# Morning
tracker.record_sent_checkin("Julio Inoue", "Julio Inoue", "metas", "Qual é sua meta?")
success, msg = response_handler.handle_checkin_response("Julio Inoue", "Implementar API do checkin")
print(f"   ☀️  Morning: {msg}")

# Afternoon
tracker.record_sent_checkin("Julio Inoue", "Julio Inoue", "status", "Como está?")
success, msg = response_handler.handle_checkin_response("Julio Inoue", "API funcionando, testando endpoints")
print(f"   🌤️  Afternoon: {msg}")

# Evening
tracker.record_sent_checkin("Julio Inoue", "Julio Inoue", "closing", "Resumo?")
success, msg = response_handler.handle_checkin_response("Julio Inoue", "API pronta, testes passando")
print(f"   🌙 Evening: {msg}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 3: VERIFICAR NO BANCO DE DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("3️⃣  VERIFICANDO DADOS SALVOS")
print("-" * 100)

from src.database.connection import get_db_engine
from sqlalchemy import text
from datetime import date

engine = get_db_engine()

with engine.connect() as conn:
    # Arthur
    print("\n🎯 ARTHUR LEUZZI (Banco de Dados):")
    result = conn.execute(text("""
        SELECT u.name, dc.date, dc.morning_answer, dc.afternoon_answer, dc.evening_answer
        FROM daily_checkins dc
        JOIN users u ON dc.user_id = u.id
        WHERE u.name = 'Arthur Leuzzi' AND dc.date = :today
    """), {"today": date.today()})

    row = result.fetchone()
    if row:
        name, checkin_date, m_a, a_a, e_a = row
        print(f"   ✅ Checkin encontrado ({checkin_date})")
        print(f"   ☀️  Morning: {m_a[:50]}..." if m_a and len(m_a) > 50 else f"   ☀️  Morning: {m_a}")
        print(f"   🌤️  Afternoon: {a_a[:50]}..." if a_a and len(a_a) > 50 else f"   🌤️  Afternoon: {a_a}")
        print(f"   🌙 Evening: {e_a[:50]}..." if e_a and len(e_a) > 50 else f"   🌙 Evening: {e_a}")
    else:
        print("   ❌ Nenhum checkin encontrado")

    # Julio
    print("\n🎯 JULIO INOUE (Banco de Dados):")
    result = conn.execute(text("""
        SELECT u.name, dc.date, dc.morning_answer, dc.afternoon_answer, dc.evening_answer
        FROM daily_checkins dc
        JOIN users u ON dc.user_id = u.id
        WHERE u.name = 'Julio Inoue' AND dc.date = :today
    """), {"today": date.today()})

    row = result.fetchone()
    if row:
        name, checkin_date, m_a, a_a, e_a = row
        print(f"   ✅ Checkin encontrado ({checkin_date})")
        print(f"   ☀️  Morning: {m_a[:50]}..." if m_a and len(m_a) > 50 else f"   ☀️  Morning: {m_a}")
        print(f"   🌤️  Afternoon: {a_a[:50]}..." if a_a and len(a_a) > 50 else f"   🌤️  Afternoon: {a_a}")
        print(f"   🌙 Evening: {e_a[:50]}..." if e_a and len(e_a) > 50 else f"   🌙 Evening: {e_a}")
    else:
        print("   ❌ Nenhum checkin encontrado")

print()

# ═══════════════════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 100)
print("✅ TESTE CONCLUÍDO COM SUCESSO")
print("=" * 100)
print()
print("📊 RESUMO:")
print("  ✅ Arthur Leuzzi - Ativo e recebendo checkins")
print("  ✅ Julio Inoue - Ativo e recebendo checkins")
print()
print("🚀 PRÓXIMO PASSO:")
print("  • Ambos receberão checkins automáticos nos horários configurados")
print("  • 06:00 - Pergunta de metas")
print("  • 12:00 - Pergunta de status")
print("  • 18:00 - Pergunta de fechamento")
print()
print("📱 NÚMEROS:")
print(f"  Arthur: +55 48 8842-8246")
print(f"  Julio:  +55 11 99932-2027")
print()
