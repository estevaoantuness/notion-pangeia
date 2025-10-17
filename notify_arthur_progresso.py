"""
Notificar Arthur sobre o novo comando progresso.
"""

from src.whatsapp.client import WhatsAppClient

def notify():
    client = WhatsAppClient()

    message = """✨ *Novidade: Comando "progresso"*

Agora você pode ver um relatório visual completo do seu dia!

Digite: *progresso*

Vai mostrar:
✅ Tasks concluídas
🔵 Em andamento
⚪ Pendentes
📈 Estatísticas completas

Experimente! 🚀"""

    print("📤 Enviando notificação para Arthur...")
    success, message_id, error = client.send_message("+554888428246", message)

    if success:
        print(f"✅ Mensagem enviada! SID: {message_id}")
    else:
        print(f"❌ Erro: {error}")

if __name__ == "__main__":
    notify()
