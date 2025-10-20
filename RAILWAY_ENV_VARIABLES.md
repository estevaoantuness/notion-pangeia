# Variáveis de Ambiente - Evolution API (Railway)

## Server Configuration
```
SERVER_URL=https://SEU-APP.up.railway.app
```
**⚠️ IMPORTANTE:** Substitua `SEU-APP` pela URL real que o Railway gerar para você!

---

## Authentication
```
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024
```

---

## Database - PostgreSQL
```
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_URL}}
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=false
DATABASE_SAVE_MESSAGE_UPDATE=false
DATABASE_SAVE_DATA_CONTACTS=false
DATABASE_SAVE_DATA_CHATS=false
```

**📝 Nota:** O Railway vai substituir automaticamente `${{Postgres.DATABASE_URL}}` com a URL do PostgreSQL

---

## Cache - Redis
```
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=${{Redis.REDIS_URL}}
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=false
```

**📝 Nota:** O Railway vai substituir automaticamente `${{Redis.REDIS_URL}}` com a URL do Redis

---

## Logs
```
LOG_LEVEL=ERROR,WARN,INFO
LOG_COLOR=true
```

---

## CORS
```
CORS_ORIGIN=*
CORS_METHODS=GET,POST,PUT,DELETE
CORS_CREDENTIALS=true
```

---

## QR Code
```
QRCODE_LIMIT=30
```

---

## Baileys Configuration
```
CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome
```

---

## Docker Image (se usar Docker no Railway)
```
IMAGE=atendai/evolution-api:v2.1.1
```

---

## ✅ CHECKLIST DE DEPLOY

### Passo 1: Criar Services no Railway
- [ ] Adicionar PostgreSQL
- [ ] Adicionar Redis
- [ ] Criar novo service para Evolution API

### Passo 2: Configurar PostgreSQL
- [ ] Railway cria automaticamente
- [ ] Anote a variável: `DATABASE_URL`

### Passo 3: Configurar Redis
- [ ] Railway cria automaticamente
- [ ] Anote a variável: `REDIS_URL`

### Passo 4: Configurar Evolution API
- [ ] Use a imagem Docker: `atendai/evolution-api:v2.1.1`
- [ ] Adicione TODAS as variáveis acima
- [ ] Substitua `${{Postgres.DATABASE_URL}}` e `${{Redis.REDIS_URL}}`
- [ ] Defina a porta: `8080`

### Passo 5: Após Deploy
- [ ] Aguarde o deploy completar
- [ ] Anote a URL pública (ex: `https://evolution-api-production-XXXX.up.railway.app`)
- [ ] Atualize `SERVER_URL` com essa URL
- [ ] Redesploy

### Passo 6: Testar
```bash
curl https://SEU-APP.up.railway.app/
```

---

## 🔧 Configuração Rápida (copiar/colar)

Se o Railway pedir variáveis de uma vez, use este bloco:

```env
# Server
SERVER_URL=https://SEU-APP.up.railway.app
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024

# Database
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_URL}}
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=false
DATABASE_SAVE_MESSAGE_UPDATE=false
DATABASE_SAVE_DATA_CONTACTS=false
DATABASE_SAVE_DATA_CHATS=false

# Redis
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=${{Redis.REDIS_URL}}
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=false

# Logs
LOG_LEVEL=ERROR,WARN,INFO
LOG_COLOR=true

# CORS
CORS_ORIGIN=*
CORS_METHODS=GET,POST,PUT,DELETE
CORS_CREDENTIALS=true

# QR Code
QRCODE_LIMIT=30

# Baileys
CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome
```

---

## 🆘 Troubleshooting

### Erro: "Redis disconnected"
- Verifique se `CACHE_REDIS_URI` está correto
- Deve usar `${{Redis.REDIS_URL}}` (Railway substitui automaticamente)

### Erro: "Database connection failed"
- Verifique se `DATABASE_CONNECTION_URI` está correto
- Deve usar `${{Postgres.DATABASE_URL}}` (Railway substitui automaticamente)

### Porta incorreta
- Evolution API usa porta `8080` internamente
- Railway faz o mapeamento automático para HTTPS

---

## 📱 Após o Deploy - Gerar QR Code

1. Acesse: `https://SEU-APP.up.railway.app`
2. Crie a instância:
```bash
curl -X POST 'https://SEU-APP.up.railway.app/instance/create' \
  -H 'apikey: pange-bot-secret-key-2024' \
  -H 'Content-Type: application/json' \
  -d '{"instanceName":"pangeia-bot","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'
```

3. Obtenha o QR Code:
```bash
curl 'https://SEU-APP.up.railway.app/instance/connect/pangeia-bot' \
  -H 'apikey: pange-bot-secret-key-2024'
```
