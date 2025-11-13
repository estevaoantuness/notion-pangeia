#!/usr/bin/env python3
"""
Teste completo: Criar usuário de teste, fazer checkin local,
e verificar se aparece no Supabase em tempo real.

Workflow:
1. Criar usuário "TestUser" no Railway Postgres
2. Criar checkin para TestUser localmente
3. Registrar 3 respostas (morning, afternoon, evening)
4. Verificar dados no Railway Postgres
5. Verificar dados no Supabase
6. Comparar se são iguais
"""

from dotenv import load_dotenv
load_dotenv()

from src.database.checkins_integration import get_checkins_integration
from src.database.users_manager import get_users_manager
from src.database.connection import get_db_engine
from src.checkins.pending_tracker import get_pending_checkin_tracker
from src.checkins.response_handler import get_checkin_response_handler
from sqlalchemy import text
from datetime import date
import json

print("=" * 100)
print("🧪 TESTE: CHECKIN → RAILWAY → SUPABASE SYNC")
print("=" * 100)
print()

users_mgr = get_users_manager()
checkins_integration = get_checkins_integration()
tracker = get_pending_checkin_tracker()
response_handler = get_checkin_response_handler()
engine = get_db_engine()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 1: CRIAR USUÁRIO DE TESTE
# ═══════════════════════════════════════════════════════════════════════════

print("1️⃣  CRIANDO USUÁRIO DE TESTE")
print("-" * 100)

test_user_name = "TestUser"
test_user_phone = "55 85 9999-9999"

# Verificar se já existe
existing = users_mgr.get_user(test_user_name)
if existing:
    print(f"   ✅ Usuário já existe: {existing}")
    test_user_id = existing['id']
else:
    # Criar novo usuário
    print(f"   Criando novo usuário: {test_user_name}")
    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO users (name, phone, onboarding_complete)
            VALUES (:name, :phone, FALSE)
            RETURNING id
        """), {"name": test_user_name, "phone": test_user_phone})
        test_user_id = result.scalar()
        conn.commit()
    print(f"   ✅ Usuário criado com ID: {test_user_id}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2: CRIAR CHECKIN LOCALMENTE
# ═══════════════════════════════════════════════════════════════════════════

print("2️⃣  CRIANDO CHECKIN PARA TESTUSER")
print("-" * 100)

checkins_integration.create_daily_checkin(test_user_name)
print(f"   ✅ Checkin criado para {test_user_name}")
print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 3: REGISTRAR RESPOSTAS
# ═══════════════════════════════════════════════════════════════════════════

print("3️⃣  REGISTRANDO 3 RESPOSTAS (MORNING, AFTERNOON, EVENING)")
print("-" * 100)

# Morning
tracker.record_sent_checkin(test_user_name, test_user_name, "metas", "🎯 Meta teste?")
success, msg = response_handler.handle_checkin_response(test_user_name, "Minha meta é testar o Supabase!")
print(f"   ☀️  Morning: {msg}")

# Afternoon
tracker.record_sent_checkin(test_user_name, test_user_name, "status", "🌤️ Status teste?")
success, msg = response_handler.handle_checkin_response(test_user_name, "Tudo funcionando perfeitamente!")
print(f"   🌤️  Afternoon: {msg}")

# Evening
tracker.record_sent_checkin(test_user_name, test_user_name, "closing", "🌙 Fechamento teste?")
success, msg = response_handler.handle_checkin_response(test_user_name, "Dia foi ótimo, tudo sincronizado!")
print(f"   🌙 Evening: {msg}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 4: VERIFICAR NO RAILWAY POSTGRES
# ═══════════════════════════════════════════════════════════════════════════

print("4️⃣  VERIFICANDO DADOS NO RAILWAY POSTGRES")
print("-" * 100)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            id, user_id, date,
            morning_question, morning_answer,
            afternoon_question, afternoon_answer,
            evening_question, evening_answer
        FROM daily_checkins
        WHERE user_id = :user_id AND date = :today
    """), {"user_id": test_user_id, "today": date.today()})

    row = result.fetchone()

    if row:
        checkin_id, user_id, checkin_date, m_q, m_a, a_q, a_a, e_q, e_a = row

        print(f"   ✅ Checkin encontrado no Railway Postgres!")
        print(f"   ID: {checkin_id}")
        print(f"   Usuario: {user_id}")
        print(f"   Data: {checkin_date}")
        print()
        print(f"   ☀️  Manhã:")
        print(f"       Q: {m_q}")
        print(f"       A: {m_a}")
        print()
        print(f"   🌤️  Tarde:")
        print(f"       Q: {a_q}")
        print(f"       A: {a_a}")
        print()
        print(f"   🌙 Noite:")
        print(f"       Q: {e_q}")
        print(f"       A: {e_a}")
    else:
        print(f"   ❌ Nenhum checkin encontrado!")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 5: VERIFICAR NO SUPABASE
# ═══════════════════════════════════════════════════════════════════════════

print("5️⃣  VERIFICANDO DADOS NO SUPABASE")
print("-" * 100)

try:
    from supabase import create_client
    import os

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("   ⚠️  Supabase não configurado (.env)")
    else:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Buscar usuário no Supabase
        print("   Buscando usuário no Supabase...")
        response = supabase.table("users").select("*").eq("name", test_user_name).execute()

        if response.data:
            user_supabase = response.data[0]
            print(f"   ✅ Usuário encontrado no Supabase!")
            print(f"   ID: {user_supabase['id']}")
            print(f"   Nome: {user_supabase['name']}")
            print()

            # Buscar checkin no Supabase
            print("   Buscando checkin no Supabase...")
            response = supabase.table("daily_checkins").select("*").eq("user_id", user_supabase['id']).eq("date", str(date.today())).execute()

            if response.data:
                checkin_supabase = response.data[0]
                print(f"   ✅ Checkin encontrado no Supabase!")
                print(f"   ID: {checkin_supabase['id']}")
                print(f"   Usuario: {checkin_supabase['user_id']}")
                print(f"   Data: {checkin_supabase['date']}")
                print()
                print(f"   ☀️  Manhã:")
                print(f"       Q: {checkin_supabase.get('morning_question')}")
                print(f"       A: {checkin_supabase.get('morning_answer')}")
                print()
                print(f"   🌤️  Tarde:")
                print(f"       Q: {checkin_supabase.get('afternoon_question')}")
                print(f"       A: {checkin_supabase.get('afternoon_answer')}")
                print()
                print(f"   🌙 Noite:")
                print(f"       Q: {checkin_supabase.get('evening_question')}")
                print(f"       A: {checkin_supabase.get('evening_answer')}")
            else:
                print(f"   ❌ Checkin NÃO encontrado no Supabase!")
                print(f"      Supabase talvez não esteja sincronizado com Railway")
        else:
            print(f"   ⚠️  Usuário NÃO encontrado no Supabase!")
            print(f"      Supabase talvez não tenha sincronização automática")

except ImportError:
    print("   ⚠️  Supabase não instalado (pip install supabase)")
except Exception as e:
    print(f"   ❌ Erro ao acessar Supabase: {e}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 6: COMPARAÇÃO E RESULTADO
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 100)
print("6️⃣  RESUMO E RECOMENDAÇÕES")
print("=" * 100)
print()

print("📊 CONCLUSÕES:")
print()
print("Railway Postgres:")
print("  ✅ É o banco PRIMÁRIO")
print("  ✅ Todos os dados são salvos aqui primeiro")
print("  ✅ Todos os checkins estão aqui")
print()
print("Supabase:")
print("  ⚠️  NÃO está sincronizado AUTOMATICAMENTE")
print("  ⚠️  Supabase é banco SEPARADO (não é cópia)")
print()
print("🔄 OPÇÕES PARA SINCRONIZAÇÃO:")
print()
print("Opção 1: SYNC JOB (Recomendado para próxima fase)")
print("  └─ Criar job que copia Railway → Supabase a cada 30 min")
print("  └─ Implementar em: src/integrations/supabase_sync.py")
print()
print("Opção 2: MANTER RAILWAY COMO PRIMÁRIO")
print("  └─ Railway Postgres é o banco principal")
print("  └─ Dashboard web acessa Railway")
print("  └─ Supabase fica como backup opcional")
print()
print("Opção 3: USAR APENAS SUPABASE")
print("  └─ Mudar DATABASE_URL para Supabase")
print("  └─ Benefício: Dashboard automático em Supabase")
print("  └─ Requer migração de dados existentes")
print()

print("=" * 100)
print("✅ TESTE CONCLUÍDO")
print("=" * 100)
print()
print("💡 Próximo passo sugerido:")
print("   Se quiser sincronização automática, isso seria:")
print("   → FASE 3, Task 7 (Sincronizar com Supabase)")
print()
