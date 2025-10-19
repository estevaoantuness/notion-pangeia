#!/usr/bin/env python3
"""
Debug - Ver dados brutos das tasks do Saraiva.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.notion.tasks import TasksManager

def main():
    tasks_manager = TasksManager()

    # Busca tasks raw
    results = tasks_manager.notion_client.query_database(
        database_id="2f0e4657-54d4-44c8-8ee4-93ca30b1ea36"
    )

    print("=" * 80)
    print("BUSCANDO TASKS DO SARAIVA (DADOS BRUTOS)")
    print("=" * 80)
    print()

    saraiva_tasks = []

    for task in results:
        assignees_prop = task.get("properties", {}).get("Assignees", {})
        assignees = assignees_prop.get("multi_select", [])

        # Check se é do Saraiva
        for assignee in assignees:
            if "saraiva" in assignee.get("name", "").lower():
                saraiva_tasks.append(task)
                break

    print(f"Encontradas {len(saraiva_tasks)} tasks do Saraiva\n")

    for i, task in enumerate(saraiva_tasks, 1):
        print(f"\n{'='*80}")
        print(f"TASK {i}")
        print('='*80)

        # Properties
        props = task.get("properties", {})

        # Mostra todos os campos
        for key, value in props.items():
            print(f"\n{key}:")
            print(f"  Type: {value.get('type')}")

            if value.get('type') == 'title':
                titles = value.get('title', [])
                if titles:
                    print(f"  Content: {titles[0].get('plain_text', 'N/A')}")
                else:
                    print(f"  Content: (vazio)")

            elif value.get('type') == 'status':
                status = value.get('status', {})
                print(f"  Content: {status.get('name', 'N/A')}")

            elif value.get('type') == 'multi_select':
                items = value.get('multi_select', [])
                names = [item.get('name') for item in items]
                print(f"  Content: {', '.join(names) if names else '(vazio)'}")

            elif value.get('type') == 'rich_text':
                texts = value.get('rich_text', [])
                if texts:
                    print(f"  Content: {texts[0].get('plain_text', 'N/A')}")
                else:
                    print(f"  Content: (vazio)")

            elif value.get('type') == 'url':
                print(f"  Content: {value.get('url', 'N/A')}")

if __name__ == "__main__":
    main()
