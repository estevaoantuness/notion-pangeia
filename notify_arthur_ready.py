"""
Notificar Arthur que o sistema já está pronto.
"""

from src.whatsapp.client import WhatsAppClient

def notify_arthur():
    client = WhatsAppClient()

    message = """✅ *Pronto, Arthur!*

Seu número foi cadastrado no sistema. Agora você pode usar:

📋 *minhas tarefas* - ver suas tasks
✅ *feito N* - marcar task como concluída
⏳ *andamento N* - marcar como em andamento
📊 *progresso* - ver seu progresso
❓ *ajuda* - todos os comandos

Pode testar! 🚀"""

    print("📤 Enviando notificação para Arthur...")
    success, message_id, error = client.send_message("+554888428246", message)

    if success:
        print(f"✅ Mensagem enviada! SID: {message_id}")
    else:
        print(f"❌ Erro: {error}")

if __name__ == "__main__":
    notify_arthur()
