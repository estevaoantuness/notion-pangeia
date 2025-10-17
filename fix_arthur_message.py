"""
Script para corrigir o envio da mensagem - pedir desculpas e enviar para o Arthur correto.
"""

from src.whatsapp.client import WhatsAppClient

def send_messages():
    client = WhatsAppClient()

    # 1. Desculpas para o Arthur errado
    apology = """🙏 Desculpa Arthur!

Mensagem enviada por engano - estava testando o sistema.

Pode ignorar! 😅"""

    print("📤 Enviando desculpas para o Arthur errado (+5548884228246)...")
    response1 = client.send_message("+5548884228246", apology)
    if response1.get("status") == "success":
        print(f"✅ Desculpas enviadas! SID: {response1.get('message_id')}")
    else:
        print(f"❌ Erro: {response1.get('error')}")

    # 2. Mensagem para o Arthur correto
    test_message = """🤖 *Sistema de Tasks - Teste*

Olá Arthur!

O bot de tasks está pronto para testes. Você pode:

✅ *minhas tarefas* - ver suas tasks do dia
✅ *feito N* - marcar task N como concluída
✅ *andamento N* - marcar task N como em andamento
✅ *progresso* - ver seu progresso
✅ *ajuda* - ver todos os comandos

Pode testar à vontade! 🚀

_Sistema desenvolvido por Estevao_"""

    print("\n📤 Enviando mensagem para o Arthur correto (+5548988428246)...")
    response2 = client.send_message("+5548988428246", test_message)
    if response2.get("status") == "success":
        print(f"✅ Mensagem enviada! SID: {response2.get('message_id')}")
    else:
        print(f"❌ Erro: {response2.get('error')}")

if __name__ == "__main__":
    send_messages()
