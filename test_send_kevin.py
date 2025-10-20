#!/usr/bin/env python3
"""
Teste de envio para Kevin.

Envia mensagem informando sobre os novos comandos de tutoriais.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.whatsapp.sender import WhatsAppSender

def main():
    """Envia mensagem de teste para Kevin"""

    sender = WhatsAppSender()

    message = """👋 Olá, Kevin! Sou o Pangeia Bot (versão atualizada)!

🎉 *NOVIDADES IMPLEMENTADAS:*

1. ✅ Comandos diretos de tutoriais
   • Digite "tutorial" → recebe tutorial completo
   • Digite "básico" → recebe resumo rápido
   • Digite "exemplos" → vê exemplos práticos
   • Digite "dicas" → recebe dicas de uso
   • Digite "começar" → tutorial + primeiro passo

2. ✅ Sinônimos expandidos
   • Pode responder apenas "s" para sim
   • Ou "n" para não
   • Emojis funcionam: 👍 ✅ 👎 ❌
   • Números também: 1 = sim, 2 = não

3. ✅ Bot tem memória!
   • Lembra das conversas anteriores
   • Não repete tutorial se você já fez
   • Funciona mesmo após reiniciar

━━━━━━━━━━━━━━━━━━━━━━

*🧪 TESTE AGORA:*

Experimente os novos comandos:
• tutorial
• básico
• exemplos
• dicas
• começar

E também tente:
• s (em vez de sim)
• n (em vez de não)
• 👍 ou ✅ para confirmar

━━━━━━━━━━━━━━━━━━━━━━

Qualquer problema, me avise! 😊"""

    print(f"📤 Enviando mensagem para Kevin...")

    success, sid, error = sender.send_message("Kevin", message)

    if success:
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   SID: {sid}")
    else:
        print(f"❌ Erro ao enviar mensagem:")
        print(f"   {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
