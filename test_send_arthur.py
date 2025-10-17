"""
Script para enviar mensagem de teste para o Arthur.
"""

from src.whatsapp.sender import WhatsAppSender

def send_test_message():
    sender = WhatsAppSender()

    message = """🤖 *Sistema de Tasks - Teste*

Olá Arthur!

O bot de tasks está pronto para testes. Você pode:

✅ *minhas tarefas* - ver suas tasks do dia
✅ *feito N* - marcar task N como concluída
✅ *andamento N* - marcar task N como em andamento
✅ *progresso* - ver seu progresso
✅ *ajuda* - ver todos os comandos

Pode testar à vontade! 🚀

_Sistema desenvolvido por Estevao_"""

    success, sid, error = sender.send_message("Arthur Pangeia", message)

    if success:
        print(f"✅ Mensagem enviada para Arthur! SID: {sid}")
    else:
        print(f"❌ Erro ao enviar: {error}")

if __name__ == "__main__":
    send_test_message()
