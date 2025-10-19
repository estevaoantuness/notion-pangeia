#!/usr/bin/env python3
"""
Script rápido para verificar tasks do Saraiva no Notion.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.tasks import TasksManager

def main():
    print("=" * 60)
    print("📋 BUSCANDO TASKS DO SARAIVA NO NOTION")
    print("=" * 60)
    print()

    # Inicializa TasksManager
    tasks_manager = TasksManager()

    # Busca tasks do Saraiva
    person_name = "Saraiva"
    tasks = tasks_manager.get_person_tasks(person_name, include_completed=False)
    progress = tasks_manager.calculate_progress(person_name)

    # Mostra progresso
    print(f"👤 Pessoa: {person_name}")
    print(f"📊 Progresso: {progress.get('concluidas', 0)}/{progress.get('total', 0)} ({progress.get('percentual', 0)}%)")
    print()

    # Tasks A Fazer
    a_fazer = tasks.get("a_fazer", [])
    print(f"📝 A FAZER ({len(a_fazer)} tasks):")
    print("-" * 60)
    if a_fazer:
        for i, task in enumerate(a_fazer, 1):
            title = task.get("title", "Sem título")
            category = task.get("category", "Sem categoria")
            priority = task.get("priority", "Medium")
            due_date = task.get("due_date", "Sem prazo")
            print(f"{i}. {title}")
            print(f"   📂 {category} | ⚡ {priority} | 📅 {due_date}")
            print()
    else:
        print("   (nenhuma)")
        print()

    # Tasks Em Andamento
    em_andamento = tasks.get("em_andamento", [])
    print(f"🔄 EM ANDAMENTO ({len(em_andamento)} tasks):")
    print("-" * 60)
    if em_andamento:
        for i, task in enumerate(em_andamento, 1):
            title = task.get("title", "Sem título")
            category = task.get("category", "Sem categoria")
            priority = task.get("priority", "Medium")
            due_date = task.get("due_date", "Sem prazo")
            print(f"{i}. {title}")
            print(f"   📂 {category} | ⚡ {priority} | 📅 {due_date}")
            print()
    else:
        print("   (nenhuma)")
        print()

    # Total
    total_pendentes = len(a_fazer) + len(em_andamento)
    print("=" * 60)
    print(f"📌 TOTAL PENDENTE: {total_pendentes} tasks")
    print("=" * 60)

if __name__ == "__main__":
    main()
