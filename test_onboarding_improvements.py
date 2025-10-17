#!/usr/bin/env python3
"""
Teste das melhorias de onboarding.

Verifica se:
1. Sinônimos expandidos ('s', 'n', emojis) funcionam
2. Normalização preserva emojis e números
3. Persistência funciona (se configurada)
"""

import logging
from src.onboarding.manager import OnboardingManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_normalization():
    """Testa se normalização preserva emojis e números"""
    print("\n" + "="*60)
    print("TESTE 1: Normalização de Respostas")
    print("="*60)

    manager = OnboardingManager()

    test_cases = [
        # (input, expected_output)
        ("Sim!", "sim"),
        ("s", "s"),
        ("S", "s"),
        ("sim.", "sim"),
        ("não!", "nao"),
        ("n", "n"),
        ("👍", "👍"),
        ("✅", "✅"),
        ("1", "1"),
        ("2", "2"),
    ]

    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = manager.normalize_text(input_text)
        if result == expected:
            print(f"✅ '{input_text}' → '{result}'")
            passed += 1
        else:
            print(f"❌ '{input_text}' → '{result}' (esperado: '{expected}')")
            failed += 1

    print(f"\nResultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_synonyms():
    """Testa se sinônimos expandidos funcionam"""
    print("\n" + "="*60)
    print("TESTE 2: Sinônimos de Confirmação")
    print("="*60)

    manager = OnboardingManager()

    # Testa sinônimos de SIM
    yes_cases = ['s', 'si', 'ss', '1', '👍', '✅', 'sim', 'ok']

    print("\n🟢 Sinônimos de SIM:")
    for text in yes_cases:
        processed, response = manager.handle_onboarding_response("Test User", text)
        is_yes = "tutorial" in response.lower() or "comandos" in response.lower()
        if is_yes:
            print(f"  ✅ '{text}' reconhecido como SIM")
        else:
            print(f"  ❌ '{text}' NÃO reconhecido como SIM")
            print(f"     Resposta: {response[:50]}...")

    # Testa sinônimos de NÃO
    no_cases = ['n', 'nn', '2', '👎', '❌', 'não', 'nao']

    print("\n🔴 Sinônimos de NÃO:")
    for text in no_cases:
        processed, response = manager.handle_onboarding_response("Test User", text)
        is_no = "comandos básicos" in response.lower() or "vamos começar" in response.lower()
        if is_no:
            print(f"  ✅ '{text}' reconhecido como NÃO")
        else:
            print(f"  ❌ '{text}' NÃO reconhecido como NÃO")
            print(f"     Resposta: {response[:50]}...")


def test_persistence():
    """Testa se persistência está configurada"""
    print("\n" + "="*60)
    print("TESTE 3: Persistência de Onboarding")
    print("="*60)

    from src.onboarding.persistence import get_persistence

    persistence = get_persistence()

    if persistence.is_enabled():
        print("✅ Persistência HABILITADA")
        print(f"   Database ID: {persistence.database_id[:10]}...")

        # Testa se consegue verificar usuário
        try:
            has_completed = persistence.has_completed_onboarding("Test User")
            print(f"   Teste de leitura: OK (resultado: {has_completed})")
        except Exception as e:
            print(f"   ⚠️ Erro ao testar leitura: {e}")
    else:
        print("⚠️ Persistência DESABILITADA")
        print("   Motivo: NOTION_USERS_DB_ID não configurado")
        print("   Impacto: Estado será perdido ao reiniciar")
        print("   Solução: Configure NOTION_USERS_DB_ID no .env")


def test_full_flow():
    """Testa fluxo completo de onboarding"""
    print("\n" + "="*60)
    print("TESTE 4: Fluxo Completo de Onboarding")
    print("="*60)

    manager = OnboardingManager()
    test_user = "Test Flow User"

    # 1. Verifica se é primeira vez
    is_first = manager.is_first_time_user(test_user)
    print(f"1. is_first_time_user: {is_first}")

    # 2. Inicia onboarding
    intro_message = manager.start_onboarding(test_user)
    print(f"2. Mensagem de boas-vindas: {intro_message[:50]}...")

    # 3. Verifica se está aguardando resposta
    is_waiting = manager.is_waiting_onboarding_answer(test_user)
    print(f"3. is_waiting_onboarding_answer: {is_waiting}")

    # 4. Testa resposta com 's' (deve funcionar!)
    processed, response = manager.handle_onboarding_response(test_user, "s")
    print(f"4. Resposta com 's': processed={processed}")
    print(f"   Conteúdo: {response[:50]}...")

    # 5. Verifica se completou
    is_first_after = manager.is_first_time_user(test_user)
    print(f"5. is_first_time_user (após): {is_first_after}")

    if is_first_after == False:
        print("✅ Onboarding marcado como completo!")
    else:
        print("⚠️ Onboarding NÃO foi marcado como completo")


def main():
    """Executa todos os testes"""
    print("\n🧪 TESTES DE MELHORIAS DE ONBOARDING")
    print("="*60)

    try:
        # Teste 1: Normalização
        test_normalization()

        # Teste 2: Sinônimos
        test_synonyms()

        # Teste 3: Persistência
        test_persistence()

        # Teste 4: Fluxo completo
        test_full_flow()

        print("\n" + "="*60)
        print("✅ TESTES CONCLUÍDOS")
        print("="*60)
        print("\n📋 Próximos passos:")
        print("1. Se persistência estiver desabilitada, configure NOTION_USERS_DB_ID")
        print("2. Teste com mensagens reais no WhatsApp")
        print("3. Envie 's' em resposta à pergunta de tutorial")
        print("4. Reinicie o bot e verifique se ele lembra do onboarding")

    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
