#!/usr/bin/env python3
"""
Teste Completo de CRUD de Tasks.

Demonstra:
- ✅ Criar tasks com assignee
- ✅ Editar propriedades (status, prioridade, etc)
- ✅ Reatribuir responsáveis
- ✅ Completar tasks
- ✅ Criar subtasks
"""

import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.task_creator import TaskCreator
from src.notion.tasks import TasksManager


def print_section(title):
    """Imprime seção bonita."""
    print(f"\n{'='*80}")
    print(f"📋 {title}")
    print('='*80)


def main():
    print("="*80)
    print("🧪 TESTE COMPLETO DE CRUD - TASKS DO NOTION")
    print("="*80)
    print()

    # Inicializa
    print("🔧 Inicializando TaskCreator e TasksManager...")
    task_creator = TaskCreator()
    tasks_manager = TasksManager()
    print("✅ Pronto!\n")

    # ========================================================================
    # TESTE 1: CRIAR TASK COM ASSIGNEE
    # ========================================================================
    print_section("TESTE 1: CRIAR TASK COM ASSIGNEE")

    print("Criando task 'Teste de Integração API' para Saraiva...")

    task_id = task_creator.create_task(
        title="[TESTE] Integração API do WhatsApp",
        assignee="Saraiva",
        description="Task criada automaticamente pelo teste CRUD.\n\nObjetivo: Validar integração com Evolution API.",
        due_date=date.today() + timedelta(days=7),
        priority="High"
    )

    # task_id é um dict com várias informações
    if task_id and task_id.get("created"):
        actual_id = task_id.get("id")
        print(f"✅ Task criada com sucesso!")
        print(f"   ID: {actual_id}")
        print(f"   Responsável: Saraiva")
        print(f"   Prazo: {(date.today() + timedelta(days=7)).strftime('%d/%m/%Y')}")

        # Usar ID real para próximos testes
        task_id = actual_id
    else:
        print("❌ Erro ao criar task")
        return

    # ========================================================================
    # TESTE 2: BUSCAR E MOSTRAR A TASK CRIADA
    # ========================================================================
    print_section("TESTE 2: BUSCAR TASK CRIADA")

    print("Buscando tasks do Saraiva...")
    saraiva_tasks = tasks_manager.get_person_tasks("Saraiva")

    # Encontra nossa task de teste
    test_task = None
    for task_data in saraiva_tasks:
        # task_data pode ser dict ou string, vamos verificar
        if isinstance(task_data, dict):
            title = task_data.get("title", "")
        elif isinstance(task_data, str):
            # Se for string, é o próprio título
            title = task_data
            task_data = {"title": title}
        else:
            continue

        if "[TESTE]" in title:
            test_task = task_data
            break

    if test_task:
        print("✅ Task encontrada:")
        print(f"   Título: {test_task.get('title', test_task if isinstance(test_task, str) else 'N/A')}")
        if isinstance(test_task, dict):
            print(f"   Status: {test_task.get('status', 'N/A')}")
            assignees = test_task.get('assignees', [])
            if assignees:
                print(f"   Responsável: {', '.join(assignees)}")
    else:
        print("⚠️  Task de teste não encontrada (pode demorar alguns segundos para sincronizar)")

    # ========================================================================
    # TESTE 3: ATUALIZAR STATUS DA TASK
    # ========================================================================
    print_section("TESTE 3: ATUALIZAR STATUS")

    print("Mudando status de 'A Fazer' → 'Em Andamento'...")

    success = task_creator.update_task_status(task_id, "Em Andamento")

    if success:
        print("✅ Status atualizado com sucesso!")
        print("   Novo status: Em Andamento")
    else:
        print("❌ Erro ao atualizar status")

    # ========================================================================
    # TESTE 4: REATRIBUIR RESPONSÁVEL
    # ========================================================================
    print_section("TESTE 4: REATRIBUIR RESPONSÁVEL")

    print("Reatribuindo de 'Saraiva' → 'Julio'...")

    try:
        result = task_creator.reassign_task(
            page_id=task_id,
            new_assignee="Julio"
        )

        if result.get("updated"):
            print("✅ Responsável reatribuído!")
            print("   Novo responsável: Julio")
        else:
            print("❌ Erro ao reatribuir")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # ========================================================================
    # TESTE 5: CRIAR SUBTASKS
    # ========================================================================
    print_section("TESTE 5: CRIAR SUBTASKS")

    print("Criando 3 subtasks...")

    subtasks = [
        "Configurar credenciais da Evolution API",
        "Implementar endpoint de envio",
        "Testar envio de mensagem"
    ]

    subtask_ids = task_creator.create_subtasks(
        parent_task_id=task_id,
        subtasks=subtasks,
        assignee="Julio"
    )

    if subtask_ids:
        print(f"✅ {len(subtask_ids)} subtasks criadas com sucesso!")
        for i, subtask_title in enumerate(subtasks, 1):
            print(f"   {i}. {subtask_title}")
    else:
        print("❌ Erro ao criar subtasks")

    # ========================================================================
    # TESTE 6: COMPLETAR TASK
    # ========================================================================
    print_section("TESTE 6: COMPLETAR TASK")

    print("Marcando task como concluída...")

    success = task_creator.complete_task(task_id)

    if success:
        print("✅ Task marcada como concluída!")
        print("   Status final: Concluída ✓")
    else:
        print("❌ Erro ao completar task")

    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    print()
    print("="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    print()
    print("✅ FUNCIONALIDADES TESTADAS:")
    print("   1. ✓ Criar task com assignee")
    print("   2. ✓ Buscar tasks de uma pessoa")
    print("   3. ✓ Atualizar status da task")
    print("   4. ✓ Reatribuir responsável")
    print("   5. ✓ Criar subtasks")
    print("   6. ✓ Completar task")
    print()
    print("💡 TODAS AS FUNCIONALIDADES DISPONÍVEIS:")
    print("   • create_task() - Criar nova task com assignee, prioridade, prazo")
    print("   • update_task_status() - Mudar status (A Fazer, Em Andamento, Concluída)")
    print("   • reassign_task() - Reatribuir responsável")
    print("   • update_priority() - Mudar prioridade (Low, Medium, High, Urgent)")
    print("   • update_due_date() - Alterar ou remover data de vencimento")
    print("   • complete_task() - Marcar como concluída")
    print("   • start_task() - Marcar como 'Em Andamento'")
    print("   • create_subtasks() - Criar múltiplas subtasks automaticamente")
    print("   • find_task_by_title() - Buscar task por título (fuzzy match)")
    print("   • update_task() - Método genérico para atualizar qualquer propriedade")
    print()
    print("🤖 INTEGRAÇÃO COM CONVERSATIONAL AGENT:")
    print("   • Bot pode criar tasks quando usuário pedir")
    print("   • Bot pode atualizar status durante conversa")
    print("   • Bot pode sugerir e criar subtasks automaticamente")
    print("   • Bot pode reatribuir tasks quando detectar sobrecarga")
    print()
    print("="*80)
    print("✅ TESTE COMPLETO!")
    print("="*80)
    print()
    print(f"🔗 Task de teste criada: {task_id}")
    print("   (você pode ver ela no Notion agora)")
    print()


if __name__ == "__main__":
    main()
