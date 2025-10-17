"""
Script para testar conexões com Notion e Twilio.
"""

import sys
from src.notion.client import NotionClient
from src.whatsapp.client import WhatsAppClient
from config.settings import settings

def main():
    print("=" * 60)
    print("🧪 TESTE DE CONEXÕES - Pange.iA Bot")
    print("=" * 60)
    print()

    # Validar configurações
    print("📋 Validando configurações...")
    is_valid, errors = settings.validate()

    if not is_valid:
        print("❌ Erro nas configurações:")
        for error in errors:
            print(f"   - {error}")
        print()
        print("💡 Dica: Adicione o TWILIO_AUTH_TOKEN no arquivo .env")
        sys.exit(1)

    print("✅ Configurações válidas!")
    print()

    # Teste Notion
    print("-" * 60)
    print("🧪 Testando conexão com Notion...")
    print("-" * 60)

    try:
        notion = NotionClient()
        success, msg = notion.test_connection()

        if success:
            print(f"✅ {msg}")
        else:
            print(f"❌ {msg}")
    except Exception as e:
        print(f"❌ Erro ao testar Notion: {e}")

    print()

    # Teste Twilio
    print("-" * 60)
    print("🧪 Testando conexão com Twilio...")
    print("-" * 60)

    try:
        whatsapp = WhatsAppClient()
        success, msg = whatsapp.test_connection()

        if success:
            print(f"✅ {msg}")
        else:
            print(f"❌ {msg}")
    except Exception as e:
        print(f"❌ Erro ao testar Twilio: {e}")

    print()
    print("=" * 60)
    print("🎉 Testes concluídos!")
    print("=" * 60)

if __name__ == "__main__":
    main()
