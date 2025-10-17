#!/usr/bin/env python3
"""
Teste básico do bot (sem WhatsApp conectado)

Testa:
1. Conexão com Notion
2. Leitura de tasks
3. Formatação de mensagens
4. Humanizador
5. Cache de tasks
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.notion.tasks import TasksManager
from src.messaging.formatter import MessageFormatter
from src.messaging.humanizer import get_humanizer
from src.cache.task_mapper import get_task_mapper
from config.colaboradores import get_colaboradores_ativos

def test_notion_connection():
    """Teste 1: Conexão com Notion"""
    print("\n" + "="*60)
    print("TESTE 1: Conexão com Notion")
    print("="*60)

    try:
        tasks_manager = TasksManager()
        print("✅ TasksManager inicializado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Notion: {e}")
        return False

def test_read_tasks():
    """Teste 2: Leitura de tasks"""
    print("\n" + "="*60)
    print("TESTE 2: Leitura de Tasks")
    print("="*60)

    try:
        tasks_manager = TasksManager()

        # Pega primeiro colaborador ativo
        colaboradores = get_colaboradores_ativos()
        if not colaboradores:
            print("❌ Nenhum colaborador ativo encontrado")
            return False

        pessoa = list(colaboradores.keys())[0]
        print(f"📋 Testando com: {pessoa}")

        tasks_grouped = tasks_manager.get_person_tasks(pessoa)

        total = sum(len(tasks) for tasks in tasks_grouped.values())
        print(f"✅ Tasks encontradas: {total}")

        for status, tasks in tasks_grouped.items():
            if tasks:
                print(f"   • {status}: {len(tasks)} tasks")

        return True
    except Exception as e:
        print(f"❌ Erro ao ler tasks: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_formatter():
    """Teste 3: Formatação de mensagens"""
    print("\n" + "="*60)
    print("TESTE 3: Formatação de Mensagens")
    print("="*60)

    try:
        formatter = MessageFormatter()
        colaboradores = get_colaboradores_ativos()
        pessoa = list(colaboradores.keys())[0]

        message, tasks = formatter.format_daily_tasks(pessoa)

        print(f"✅ Mensagem formatada com sucesso")
        print(f"\n📨 Preview da mensagem:")
        print("-" * 60)
        print(message[:500])  # Primeiros 500 caracteres
        if len(message) > 500:
            print("... (mensagem cortada para exibição)")
        print("-" * 60)

        return True
    except Exception as e:
        print(f"❌ Erro ao formatar mensagem: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_humanizer():
    """Teste 4: Sistema de humanização"""
    print("\n" + "="*60)
    print("TESTE 4: Sistema de Humanização")
    print("="*60)

    try:
        humanizer = get_humanizer()

        # Testa diferentes tipos de mensagem
        print("📝 Testando variações de mensagens:\n")

        # 1. Saudação
        saudacao = humanizer.get_greeting("João")
        print(f"   Saudação: {saudacao}")

        # 2. Tarefa concluída
        msg_done = humanizer.get_task_completed_message(
            task_number=1,
            task_title="Implementar feature X",
            is_first=False,
            is_last=False,
            is_high_priority=False
        )
        print(f"   Concluída: {msg_done[:80]}...")

        # 3. Progresso
        msg_progress = humanizer.get_progress_message(
            percent=60,
            done=3,
            total=5
        )
        print(f"   Progresso: {msg_progress[:80]}...")

        print("\n✅ Humanizador funcionando com variações")
        return True
    except Exception as e:
        print(f"❌ Erro no humanizador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_mapper():
    """Teste 5: Cache de tasks"""
    print("\n" + "="*60)
    print("TESTE 5: Cache de Tasks (Task Mapper)")
    print("="*60)

    try:
        mapper = get_task_mapper()
        colaboradores = get_colaboradores_ativos()
        pessoa = list(colaboradores.keys())[0]

        tasks_manager = TasksManager()
        tasks_grouped = tasks_manager.get_person_tasks(pessoa)

        # Atualiza cache
        mapper.update_person_tasks(pessoa, tasks_grouped)

        # Testa busca por número
        task_1 = mapper.get_task(pessoa, 1)
        if task_1:
            print(f"✅ Task #1 encontrada: {task_1['nome'][:50]}")
        else:
            print("⚠️  Nenhuma task encontrada para pessoa")

        # Lista todas
        all_tasks = mapper.get_all_tasks(pessoa)
        print(f"✅ Total de tasks no cache: {len(all_tasks) if all_tasks else 0}")

        return True
    except Exception as e:
        print(f"❌ Erro no task mapper: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🤖 TESTE BÁSICO DO BOT PANGE.IA")
    print("="*60)
    print("(Testa funcionalidades sem WhatsApp conectado)\n")

    tests = [
        ("Conexão Notion", test_notion_connection),
        ("Leitura Tasks", test_read_tasks),
        ("Formatação Mensagens", test_message_formatter),
        ("Humanizador", test_humanizer),
        ("Cache Tasks", test_task_mapper),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO no teste '{name}': {e}")
            results.append((name, False))

    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE TESTES")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    print("="*60)

    if passed == total:
        print("\n🎉 Todos os testes passaram!")
        print("\n📋 Próximos passos:")
        print("   1. Conectar WhatsApp: cd evolution-setup && ./setup-whatsapp.sh")
        print("   2. Testar envio completo: python3 test_bot_whatsapp.py")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("   Verifique os erros acima antes de continuar")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
