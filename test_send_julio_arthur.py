#!/usr/bin/env python3
"""
Envia mensagem de teste para Julio e Arthur.
"""

import logging
from src.whatsapp.sender import WhatsAppSender

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    sender = WhatsAppSender()

    message = """👋 Olá! Sou o Pangeia Bot (versão atualizada)!

🎉 *NOVIDADES IMPLEMENTADAS:*

1. ✅ Sinônimos expandidos
   • Agora você pode responder apenas "s" para sim
   • Ou "n" para não
   • Emojis funcionam: 👍 ✅ 👎 ❌
   • Números também: 1 = sim, 2 = não

2. ✅ Bot tem memória!
   • Lembra das conversas anteriores
   • Não repete tutorial se você já fez
   • Funciona mesmo após reiniciar

🧪 *TESTE AGORA:*

Digite qualquer coisa para testar! Por exemplo:
• "oi"
• "tarefas"
• "s" (quando perguntar se quer tutorial)
• "👍" (também funciona!)

Pode testar à vontade! 🚀"""

    print("\n" + "="*60)
    print("📱 ENVIANDO MENSAGENS DE TESTE")
    print("="*60)

    # Julio
    print("\n📤 Enviando para Julio Inoue...")
    success, sid, error = sender.send_message("Julio Inoue", message)
    if success:
        print(f"✅ Enviado! SID: {sid}")
    else:
        print(f"❌ Erro: {error}")

    # Arthur
    print("\n📤 Enviando para Arthur Leuzzi...")
    success, sid, error = sender.send_message("Arthur Leuzzi", message)
    if success:
        print(f"✅ Enviado! SID: {sid}")
    else:
        print(f"❌ Erro: {error}")

    print("\n" + "="*60)
    print("✅ MENSAGENS ENVIADAS")
    print("="*60)
    print("\n📋 Próximos passos:")
    print("1. Julio e Arthur devem receber a mensagem")
    print("2. Eles podem testar respondendo 's' ou emojis")
    print("3. Verificar logs em /tmp/webhook.log")
    print("4. Testar comandos: 'tarefas', 'progresso', etc")

if __name__ == "__main__":
    main()
