"""
Entry point para Render/Railway/Heroku.
Importa a aplicacao Flask de src/webhook/app.py
"""
from src.webhook.app import app, initialize_scheduler

# Inicializa scheduler na importação do app
# Isso garante que o scheduler é inicializado exatamente uma vez,
# independentemente se rodando via Gunicorn, Flask dev server, ou outro WSGI server
# (Força redeploy com timestamp: 2025-11-11 21:30)
initialize_scheduler()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
