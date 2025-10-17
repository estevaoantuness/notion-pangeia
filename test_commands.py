"""
Script de teste para comandos.

Testa o fluxo completo:
1. Envia tasks
2. Cria mapeamento
3. Testa comando para atualizar task
"""

import sys
from src.whatsapp.sender import WhatsAppSender
from src.cache.task_mapper import get_task_mapper
from src.commands.processor import CommandProcessor

def main():
    print("=" * 60)
    print("🧪 TESTE DE COMANDOS - Sistema de Tasks")
    print("=" * 60)
    print()

    person_name = "Estevao Antunes"

    print(f"👤 Testando com: {person_name}")
    print()

    try:
        # Passo 1: Enviar tasks e criar mapeamento
        print("━" * 60)
        print("PASSO 1: Enviando tasks e criando mapeamento")
        print("━" * 60)

        sender = WhatsAppSender()
        task_mapper = get_task_mapper()

        # Envia tasks (isso cria o mapeamento automático)
        success, sid, error = sender.send_daily_tasks(person_name)

        if not success:
            print(f"❌ Falha ao enviar tasks: {error}")
            sys.exit(1)

        print(f"✅ Tasks enviadas! SID: {sid}")
        print()

        # Verifica se tem mapeamento
        if not task_mapper.has_mapping(person_name):
            print("❌ Nenhum mapeamento criado")
            sys.exit(1)

        # Mostra mapeamento
        mapping = task_mapper.get_all_tasks(person_name)
        print(f"📋 Mapeamento criado: {len(mapping)} tasks")

        for numero, task_info in mapping.items():
            print(f"   {numero}. {task_info['nome'][:50]}...")

        print()

        # Passo 2: Testar comandos
        print("━" * 60)
        print("PASSO 2: Testando comandos")
        print("━" * 60)
        print()

        processor = CommandProcessor()

        # Lista de comandos para testar
        test_commands = [
            ("minhas tarefas", "Listar tasks"),
            ("progresso", "Ver progresso"),
            ("ajuda", "Ver ajuda"),
        ]

        for command, description in test_commands:
            print(f"🧪 Testando: {description}")
            print(f"   Comando: '{command}'")

            success, response = processor.process_by_name(person_name, command)

            if success:
                print(f"   ✅ Sucesso!")
                if response:
                    print(f"   Resposta: {response[:100]}...")
            else:
                print(f"   ❌ Falha: {response}")

            print()

        # Passo 3: Teste de atualização (se houver tasks)
        if len(mapping) > 0:
            print("━" * 60)
            print("PASSO 3: Testando atualização de task")
            print("━" * 60)
            print()

            # Pega primeira task
            first_task_number = min(mapping.keys())
            first_task = mapping[first_task_number]

            print(f"🎯 Vamos testar com a task {first_task_number}:")
            print(f"   {first_task['nome']}")
            print()

            # Teste 1: Marcar em andamento
            print("🧪 Teste: Marcar como 'em andamento'")
            command = f"andamento {first_task_number}"
            success, response = processor.process_by_name(person_name, command)

            if success:
                print("   ✅ Task marcada como em andamento!")
            else:
                print(f"   ❌ Falha: {response}")

            print()

            # Aguarda input do usuário
            print("⚠️  ATENÇÃO: A task foi atualizada no Notion!")
            print("   Verifique no Notion se o status mudou para 'Em Andamento'")
            print()

            continuar = input("   Deseja continuar e marcar como concluída? (s/n): ")

            if continuar.lower() == 's':
                print()
                print("🧪 Teste: Marcar como 'concluída'")
                command = f"feito {first_task_number}"
                success, response = processor.process_by_name(person_name, command)

                if success:
                    print("   ✅ Task marcada como concluída!")
                    print()
                    print("   Verifique no Notion se foi marcada como concluída!")
                else:
                    print(f"   ❌ Falha: {response}")

        print()
        print("=" * 60)
        print("✅ TESTES CONCLUÍDOS!")
        print("=" * 60)
        print()
        print("📱 Verifique seu WhatsApp e o Notion para ver os resultados!")

    except Exception as e:
        print("=" * 60)
        print("❌ ERRO DURANTE TESTES")
        print("=" * 60)
        print()
        print(f"Erro: {str(e)}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
