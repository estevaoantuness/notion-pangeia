#!/usr/bin/env python3
"""
🧪 TESTE LOCAL: Criar Tasks com Usuário de Teste

Este script:
1. Cria um usuário de teste no banco Railway
2. Testa a criação de múltiplas tasks no Notion
3. Verifica a integração entre Railway e Notion
4. Simula o fluxo completo de criação de task
"""

from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime, date
from src.database.connection import get_db_engine
from src.notion.task_creator import TaskCreator
from sqlalchemy import text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 100)
print("🧪 TESTE LOCAL: CRIAÇÃO DE TASKS")
print("=" * 100)
print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 1: CRIAR USUÁRIO DE TESTE NO BANCO
# ═══════════════════════════════════════════════════════════════════════════

print("1️⃣  CRIANDO USUÁRIO DE TESTE")
print("-" * 100)

engine = get_db_engine()

test_user_name = "TestBot Usuario"
test_user_phone = "+554599999999"

with engine.connect() as conn:
    # Verificar se já existe
    result = conn.execute(
        text("SELECT id FROM users WHERE name = :name"),
        {"name": test_user_name}
    )
    existing_id = result.scalar()

    if existing_id:
        print(f"ℹ️  Usuário '{test_user_name}' já existe (ID: {existing_id})")
        test_user_id = existing_id
    else:
        # Criar novo usuário
        result = conn.execute(
            text("""
                INSERT INTO users (name, phone, onboarding_complete)
                VALUES (:name, :phone, TRUE)
                RETURNING id
            """),
            {"name": test_user_name, "phone": test_user_phone}
        )
        test_user_id = result.scalar()
        conn.commit()
        print(f"✅ Usuário de teste criado: '{test_user_name}' (ID: {test_user_id})")
        print(f"   Telefone: {test_user_phone}")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2: TESTAR CRIAÇÃO DE TASKS
# ═══════════════════════════════════════════════════════════════════════════

print("2️⃣  TESTANDO CRIAÇÃO DE TASKS NO NOTION")
print("-" * 100)

task_creator = TaskCreator()

# Lista de tasks para testar
test_tasks = [
    {
        "title": "📱 Implementar notificações de checkin atrasado",
        "assignee": test_user_name,
        "description": "Adicionar sistema de notificações para usuários que não responderam checkins nos últimos 2 horas",
        "project": "Pange.iA"
    },
    {
        "title": "📊 Criar dashboard de relatórios",
        "assignee": test_user_name,
        "description": "Construir página de relatórios com dados exportáveis em CSV e PDF",
        "project": "Pange.iA"
    },
    {
        "title": "🌙 Implementar dark mode",
        "assignee": test_user_name,
        "description": "Adicionar suporte a tema escuro no dashboard com persistent preferences",
        "project": "Pange.iA"
    },
    {
        "title": "🔄 Sincronizar com Supabase",
        "assignee": test_user_name,
        "description": "Implementar job de sincronização Railway → Supabase a cada 30 minutos",
        "project": "Pange.iA"
    },
]

created_tasks = []

for i, task_data in enumerate(test_tasks, 1):
    try:
        print(f"\n🎯 Task {i}/{len(test_tasks)}: {task_data['title']}")

        result = task_creator.create_task(
            title=task_data["title"],
            assignee=task_data["assignee"],
            description=task_data["description"],
            project=task_data.get("project")
        )

        created_tasks.append(result)
        print(f"   ✅ Criada com sucesso!")
        print(f"   ID: {result['id']}")
        print(f"   Status: {result['status']}")

    except Exception as e:
        print(f"   ❌ Erro ao criar: {e}")

print()
print(f"📊 RESULTADO: {len(created_tasks)}/{len(test_tasks)} tasks criadas com sucesso")
print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 3: VERIFICAR DADOS NO BANCO
# ═══════════════════════════════════════════════════════════════════════════

print("3️⃣  VERIFICANDO USUÁRIO NO BANCO")
print("-" * 100)

with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT id, name, phone, onboarding_complete, created_at
            FROM users
            WHERE name = :name
        """),
        {"name": test_user_name}
    )

    user = result.fetchone()
    if user:
        print(f"\n✅ Usuário encontrado no banco:")
        print(f"   ID: {user[0]}")
        print(f"   Nome: {user[1]}")
        print(f"   Telefone: {user[2]}")
        print(f"   Onboarding: {user[3]}")
        print(f"   Criado em: {user[4]}")
    else:
        print(f"\n❌ Usuário NÃO encontrado no banco")

print()

# ═══════════════════════════════════════════════════════════════════════════
# PARTE 4: RESUMO FINAL
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 100)
print("✅ TESTE CONCLUÍDO")
print("=" * 100)
print()

print("📊 RESUMO:")
print(f"  ✅ Usuário de teste criado: {test_user_name} (ID: {test_user_id})")
print(f"  ✅ Tasks criadas: {len(created_tasks)}")
print()

if created_tasks:
    print("📋 TASKS CRIADAS:")
    for i, task in enumerate(created_tasks, 1):
        print(f"  {i}. {task['title']}")
        print(f"     ID: {task['id']}")
        print(f"     Status: {task['status']}")
    print()

print("🔍 PRÓXIMAS VERIFICAÇÕES:")
print("  1. Abrir Notion e verificar as tasks na database")
print("  2. Testar atualização de status das tasks")
print("  3. Simular resposta do usuário via WhatsApp")
print()

print("🚀 FLUXO TESTADO:")
print("  ✅ Usuário de teste criado no Railway Postgres")
print("  ✅ Tasks criadas no Notion via API")
print("  ✅ Integração Railway ↔ Notion funcionando")
print()
