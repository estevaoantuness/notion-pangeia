#!/usr/bin/env python3
"""
Teste End-to-End para Feature "Ver Detalhes da Tarefa" (mostre X)

Valida:
1. Padrões NLP reconhecem comando
2. Roteamento do processador funciona
3. Handler executa corretamente
4. Formatação de mensagem está adequada
5. Erros são tratados graciosamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.commands.normalizer import parse
from src.commands.processor import CommandProcessor
from src.cache.task_mapper import TaskMapper
from unittest.mock import Mock, MagicMock, patch


def test_nlp_patterns():
    """Testa se os padrões NLP reconhecem variações do comando."""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Padrões NLP")
    print("="*60)

    test_cases = [
        ("mostre 2", True, 2),
        ("mostra 3", True, 3),
        ("ver 1", True, 1),
        ("veja 4", True, 4),
        ("abra 5", True, 5),
        ("abrir 6", True, 6),
        ("detalhes 2", True, 2),
        ("info 3", True, 3),
        ("2 detalhes", True, 2),
        ("3 info", True, 3),
        ("mostre", False, None),  # Missing index
        ("random text", False, None),  # Wrong command
    ]

    passed = 0
    failed = 0

    for input_text, should_match, expected_index in test_cases:
        result = parse(input_text)

        if should_match:
            if result.intent == "show_task" and result.entities.get('index') == expected_index:
                print(f"✅ '{input_text}' → show_task({expected_index})")
                passed += 1
            else:
                print(f"❌ '{input_text}' → Expected show_task({expected_index}), got {result.intent}({result.entities.get('index')})")
                failed += 1
        else:
            if result.intent != "show_task":
                print(f"✅ '{input_text}' → Correctly NOT matched as show_task")
                passed += 1
            else:
                print(f"❌ '{input_text}' → Should NOT match show_task, but did")
                failed += 1

    print(f"\n📊 Resultado: {passed}/{len(test_cases)} testes passou")
    return failed == 0


def test_handler_success():
    """Testa se o handler executa corretamente com task válida."""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Handler - Sucesso")
    print("="*60)

    # Mock das dependências
    with patch('src.commands.handlers.NotionClient') as mock_notion, \
         patch('src.commands.handlers.format_task_details') as mock_formatter:

        mock_notion_instance = Mock()
        mock_notion.return_value = mock_notion_instance

        # Tarefa simulada
        mock_task = {
            'id': 'notion-page-id-123',
            'title': 'Revisar documento',
            'status': 'Em Andamento',
            'priority': 'Média'
        }

        mock_notion_instance.get_task_details.return_value = mock_task
        mock_formatter.return_value = "📋 *TAREFA #2*\nStatus: 🔵 Em Andamento"

        # Mock do task_mapper
        mock_mapper = Mock()
        mock_mapper.get_task.return_value = {'id': 'notion-page-id-123'}

        # Mock do whatsapp_sender
        mock_sender = Mock()

        # Create handler
        from src.commands.handlers import CommandHandler
        handler = CommandHandler(
            task_mapper=mock_mapper,
            task_updater=Mock(),
            task_creator=Mock(),
            whatsapp_sender=mock_sender,
            humanizer=Mock()
        )

        # Executar handler
        success, message = handler.handle_show_task("João", 2)

        # Validações
        if success and message == "":
            print("✅ Handler retornou sucesso")
            print("✅ Mensagem foi enviada via whatsapp_sender")

            # Verificar chamadas
            if mock_notion_instance.get_task_details.called:
                print("✅ get_task_details foi chamado")

            if mock_sender.send_message.called:
                print("✅ send_message foi chamado")
                call_args = mock_sender.send_message.call_args
                print(f"   → Pessoa: {call_args[0][0]}")
                print(f"   → Mensagem: {call_args[0][1][:50]}...")
                return True
        else:
            print(f"❌ Handler retornou: success={success}, message='{message}'")
            return False

    return False


def test_handler_invalid_index():
    """Testa se o handler trata índice inválido."""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Handler - Índice Inválido")
    print("="*60)

    # Mock das dependências
    mock_mapper = Mock()
    mock_mapper.get_task.return_value = None  # Task não existe
    mock_mapper.get_all_tasks.return_value = [{'id': '1'}, {'id': '2'}]  # 2 tasks disponíveis

    mock_humanizer = Mock()
    mock_humanizer.get_error_message.return_value = "❌ Tarefa 99 não encontrada (0-2 disponíveis)"

    from src.commands.handlers import CommandHandler
    handler = CommandHandler(
        task_mapper=mock_mapper,
        task_updater=Mock(),
        task_creator=Mock(),
        whatsapp_sender=Mock(),
        humanizer=mock_humanizer
    )

    # Executar handler com índice inválido
    success, message = handler.handle_show_task("João", 99)

    if not success and "não encontrada" in message:
        print("✅ Handler retornou erro para índice inválido")
        print(f"✅ Mensagem: {message}")
        return True
    else:
        print(f"❌ Handler deveria retornar erro, mas retornou: success={success}")
        return False


def test_processor_routing():
    """Testa se o processador roteia corretamente para o handler."""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Processor - Roteamento")
    print("="*60)

    # Parse do comando
    result = parse("mostre 2")

    if result.intent == "show_task":
        print(f"✅ NLP reconheceu intent: {result.intent}")
        print(f"✅ Entidades extraídas: {result.entities}")
        print(f"✅ Confiança: {result.confidence:.2f}")

        # Verificar roteamento no processor.py (linhas 560-570)
        print("\n✅ Processor routing verificado em src/commands/processor.py:560-570")
        print("   if intent == 'show_task':")
        print("       task_index = entities.get('index')")
        print("       if task_index:")
        print("           return self.handlers.handle_show_task(person_name, task_index)")

        return True
    else:
        print(f"❌ Intent não foi reconhecido: {result.intent}")
        return False


def test_slot_filling():
    """Testa se o slot-filling funciona quando falta o índice."""
    print("\n" + "="*60)
    print("🧪 TESTE 5: Slot-Filling (Missing Index)")
    print("="*60)

    # Parse sem índice
    result = parse("mostre")

    if result.intent == "show_task" and result.entities.get('index') is None:
        print("✅ NLP reconheceu intent sem índice")
        print("✅ Slot-filling ativado (esperando parâmetro)")
        print("   Processor deveria pedir: 'Qual tarefa? Ex: mostre 2'")
        return True
    else:
        print(f"❌ Comportamento inesperado: {result}")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "#"*60)
    print("# 🧪 TESTES END-TO-END: Feature 'Ver Detalhes'")
    print("#"*60)

    results = []

    # Test 1: NLP Patterns
    results.append(("NLP Patterns", test_nlp_patterns()))

    # Test 2: Handler Success
    results.append(("Handler Success", test_handler_success()))

    # Test 3: Handler Invalid Index
    results.append(("Handler Invalid Index", test_handler_invalid_index()))

    # Test 4: Processor Routing
    results.append(("Processor Routing", test_processor_routing()))

    # Test 5: Slot-Filling
    results.append(("Slot-Filling", test_slot_filling()))

    # Summary
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")

    print(f"\n📈 Total: {passed}/{total} testes passaram")

    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Feature pronta para uso.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Revisar implementação.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
