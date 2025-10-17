"""
Script para testar fluxo de onboarding.
"""

from src.commands.processor import CommandProcessor

def test_onboarding():
    """Testa o fluxo de onboarding completo."""
    processor = CommandProcessor()

    # Simular novo usuário (Estevão será tratado como novo)
    test_user = "Estevão Antunes"
    test_user2 = "João Silva"  # Outro usuário fictício

    print("=" * 60)
    print("TESTE 1: Primeira interação (deve iniciar onboarding)")
    print("=" * 60)
    success, response = processor.process_by_name(test_user, "Olá")
    print(f"\n📨 Usuário (Estevão): Olá")
    print(f"🤖 Bot:\n{response}\n")

    print("=" * 60)
    print("TESTE 2: Resposta SIM (deve enviar tutorial completo)")
    print("=" * 60)
    success, response = processor.process_by_name(test_user, "sim")
    print(f"\n📨 Usuário (Estevão): sim")
    print(f"🤖 Bot:\n{response[:200]}...\n")  # Mostrar só início do tutorial

    print("=" * 60)
    print("TESTE 3: Segunda interação João - responde NÃO")
    print("=" * 60)
    success, response = processor.process_by_name(test_user2, "oi")
    print(f"\n📨 Usuário (João): oi")
    print(f"🤖 Bot:\n{response}\n")

    success, response = processor.process_by_name(test_user2, "não")
    print(f"\n📨 Usuário (João): não")
    print(f"🤖 Bot:\n{response}\n")

    print("=" * 60)
    print("TESTE 4: Comando ajuda de usuário já onboarded")
    print("=" * 60)
    success, response = processor.process_by_name(test_user, "ajuda")
    print(f"\n📨 Usuário (Estevão já fez onboarding): ajuda")
    print(f"🤖 Bot:\n{response}\n")

    print("=" * 60)
    print("TESTE 5: Resposta 'básico' (deve enviar explicação rápida)")
    print("=" * 60)
    success, response = processor.process_by_name(test_user, "básico")
    print(f"\n📨 Usuário (Estevão): básico")
    print(f"🤖 Bot:\n{response}\n")

if __name__ == "__main__":
    test_onboarding()
