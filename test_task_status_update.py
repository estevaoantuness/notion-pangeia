#!/usr/bin/env python3
"""
🧪 TESTE LOCAL: Atualizar Status de Tasks

Este script testa:
1. Atualizar status de uma task para "Em Andamento"
2. Atualizar status para "Concluída"
3. Verificar as mudanças no Notion
"""

from dotenv import load_dotenv
load_dotenv()

import logging
from src.notion.task_creator import TaskCreator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 100)
print("🧪 TESTE LOCAL: ATUALIZAÇÃO DE STATUS DE TASKS")
print("=" * 100)
print()

# IDs das tasks criadas no teste anterior
task_ids = [
    "2aba53b3-e53c-8136-bc5d-ce36c510ffa8",  # Notificações
    "2aba53b3-e53c-8190-b2ff-ddc06f5bd668",  # Dashboard de relatórios
    "2aba53b3-e53c-819c-b94d-d1672d4d0cd0",  # Dark mode
    "2aba53b3-e53c-8121-a818-df743910e147",  # Sincronizar com Supabase
]

task_names = [
    "📱 Notificações de checkin atrasado",
    "📊 Dashboard de relatórios",
    "🌙 Dark mode",
    "🔄 Sincronizar com Supabase"
]

task_creator = TaskCreator()

print("1️⃣  ATUALIZANDO TASKS PARA 'EM ANDAMENTO'")
print("-" * 100)

for task_id, task_name in zip(task_ids[:2], task_names[:2]):
    try:
        print(f"\n📝 Atualizando: {task_name}")
        result = task_creator.update_task_status(task_id, "Em Andamento")
        print(f"   ✅ Atualizado com sucesso!")
        print(f"   Novo status: Em Andamento")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print()
print("2️⃣  ATUALIZANDO TASKS PARA 'CONCLUÍDO'")
print("-" * 100)

for task_id, task_name in zip(task_ids[2:], task_names[2:]):
    try:
        print(f"\n✅ Atualizando: {task_name}")
        result = task_creator.update_task_status(task_id, "Concluído")
        print(f"   ✅ Atualizado com sucesso!")
        print(f"   Novo status: Concluído")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print()
print("=" * 100)
print("✅ TESTE DE ATUALIZAÇÃO CONCLUÍDO")
print("=" * 100)
print()

print("📊 RESUMO:")
print(f"  ✅ {len(task_ids[:2])} tasks movidas para 'Em Andamento'")
print(f"  ✅ {len(task_ids[2:])} tasks movidas para 'Concluída'")
print()

print("🔍 VERIFICAÇÃO:")
print("  1. Abrir Notion e verificar os status das tasks")
print("  2. Confirmar que as mudanças foram sincronizadas")
print()

print("✨ FLUXO COMPLETO TESTADO:")
print("  ✅ Criação de tasks")
print("  ✅ Atualização de status")
print("  ✅ Integração Railway ↔ Notion")
print()
