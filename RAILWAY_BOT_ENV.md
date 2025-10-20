# Variáveis de Ambiente para Bot Python (Railway)

## ⚙️ Configuração do Bot no Railway

Copie e cole estas variáveis no Railway Dashboard:

```env
# Notion API
NOTION_TOKEN=[REDACTED - See .env file]
NOTION_TASKS_DB_ID=[REDACTED - See .env file]

# Evolution API (Easypanel)
EVOLUTION_API_URL=https://pange-evolution-api.u5qiqp.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=Pange.IA Bot

# Flask Configuration
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
WEBHOOK_PATH=/whatsapp/incoming
PORT=5000

# Scheduler Configuration
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo

# Application Settings
LOG_LEVEL=INFO
CACHE_EXPIRY_HOURS=24
MAX_RETRIES=3
ENVIRONMENT=production
```

## 📋 Passos para Deploy:

1. **Acesse**: https://railway.app/
2. **Selecione projeto**: notion-pangeia
3. **New Service** → **GitHub Repo** → `estevaoantuness/notion-pangeia`
4. **Settings** → **Environment Variables** → Cole as variáveis acima
5. **Settings** → **Networking** → **Generate Domain**
6. **Aguarde o deploy** (~3-5 minutos)
7. **Copie a URL** gerada (ex: `https://notion-pangeia-production-xxxx.up.railway.app`)

## ✅ Após o Deploy:

Teste o health endpoint:
```bash
curl https://SEU-BOT-URL.up.railway.app/health
```

Resultado esperado:
```json
{
  "status": "healthy",
  "service": "notion-pangeia-webhook",
  "version": "1.0.0",
  "scheduler": "running"
}
```

## 🔗 Configurar Webhook na Evolution API:

Depois que o bot estiver deployado, configure o webhook:

```bash
curl -X POST 'https://pange-evolution-api.u5qiqp.easypanel.host/webhook/set/Pange.IA%20Bot' \
  -H 'apikey: 429683C4C977415CAAFCCE10F7D57E11' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://SEU-BOT-URL.up.railway.app/webhook/whatsapp",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "QRCODE_UPDATED",
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "SEND_MESSAGE",
      "CONNECTION_UPDATE"
    ]
  }'
```

Substitua `SEU-BOT-URL` pela URL que o Railway gerar!
