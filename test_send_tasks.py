"""
Script de teste para enviar tasks via WhatsApp.

Este script testa o fluxo completo:
1. Busca tasks no Notion
2. Formata mensagem
3. Envia via WhatsApp
"""

import sys
from src.whatsapp.sender import WhatsAppSender

def main():
    print("=" * 60)
    print("📱 TESTE DE ENVIO DE TASKS VIA WHATSAPP")
    print("=" * 60)
    print()

    # Nome do colaborador para testar
    person_name = "Estevao Antunes"  # Você pode mudar para outro colaborador

    print(f"👤 Colaborador: {person_name}")
    print()
    print("🔄 Processando...")
    print()

    try:
        # Cria sender
        sender = WhatsAppSender()

        # Envia tasks diárias
        success, sid, error = sender.send_daily_tasks(person_name)

        if success:
            print("=" * 60)
            print("✅ MENSAGEM ENVIADA COM SUCESSO!")
            print("=" * 60)
            print()
            print(f"📨 Message SID: {sid}")
            print()
            print("📱 Verifique seu WhatsApp para ver a mensagem!")
            print()
            print("💡 Dica: A mensagem foi enviada para o número cadastrado")
            print("   em config/colaboradores.py")
            print()
        else:
            print("=" * 60)
            print("❌ FALHA AO ENVIAR MENSAGEM")
            print("=" * 60)
            print()
            print(f"Erro: {error}")
            print()
            print("💡 Possíveis causas:")
            print("   - WhatsApp Sandbox não ativado")
            print("   - Número não verificado no Twilio")
            print("   - Credenciais incorretas")
            print()

    except Exception as e:
        print("=" * 60)
        print("❌ ERRO DURANTE EXECUÇÃO")
        print("=" * 60)
        print()
        print(f"Erro: {str(e)}")
        print()
        import traceback
        traceback.print_exc()

    print("=" * 60)

if __name__ == "__main__":
    main()
