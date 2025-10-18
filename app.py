  """
  Entry point para Render/Railway/Heroku.
  Importa a aplicação Flask de src/webhook/app.py
  """
  from src.webhook.app import app

  if __name__ == '__main__':
      import os
      port = int(os.environ.get('PORT', 5000))
      app.run(host='0.0.0.0', port=port)
