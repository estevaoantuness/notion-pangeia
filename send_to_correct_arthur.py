"""
Enviar mensagem para o Arthur correto.
"""

from src.whatsapp.client import WhatsAppClient

def send_to_correct_arthur():
    client = WhatsAppClient()

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

    print("📤 Enviando mensagem para o Arthur correto (+5548988428246)...")
    # send_message retorna uma tupla (success, message_id, error)
    success, message_id, error = client.send_message("+5548988428246", test_message)

    if success:
        print(f"✅ Mensagem enviada! SID: {message_id}")
    else:
        print(f"❌ Erro: {error}")

if __name__ == "__main__":
    send_to_correct_arthur()
