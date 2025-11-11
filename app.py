"""
Entry point para Render/Railway/Heroku.
Importa a aplicacao Flask de src/webhook/app.py
"""
import logging

print("DEBUG: /app.py is being imported", flush=True)
logging.info("DEBUG: /app.py entry point starting")

from src.webhook.app import app, initialize_scheduler

print("DEBUG: About to initialize scheduler", flush=True)

# Inicializa scheduler na importação do app
# Isso garante que o scheduler é inicializado exatamente uma vez,
# independentemente se rodando via Gunicorn, Flask dev server, ou outro WSGI server
initialize_scheduler()

print("DEBUG: Scheduler initialization complete", flush=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
