# Evolution API - Deploy Railway

## Passo 1: Criar PostgreSQL no Railway

1. Acesse: https://railway.app
2. Crie um novo projeto: **"pangeia-evolution"**
3. Adicione PostgreSQL:
   - Clique em **"+ New"**
   - Selecione **"Database" > "PostgreSQL"**
   - Aguarde deploy (anote as credenciais)

## Passo 2: Criar Redis no Railway

1. No mesmo projeto, clique em **"+ New"**
2. Selecione **"Database" > "Redis"**
3. Aguarde deploy

## Passo 3: Deploy Evolution API

### Via GitHub (Recomendado):

1. Faça commit deste código:
```bash
cd ~/notion-pangeia
git add evolution-api-railway/
git commit -m "Add Evolution API Railway config"
git push
```

2. No Railway:
   - Clique em **"+ New" > "GitHub Repo"**
   - Selecione o repositório `notion-pangeia`
   - Em **"Root Directory"**, coloque: `evolution-api-railway`
   - Railway vai detectar o Dockerfile automaticamente

### Ou via CLI:

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link projeto
cd ~/notion-pangeia/evolution-api-railway
railway link

# Deploy
railway up
```

## Passo 4: Configurar Variáveis de Ambiente

No painel do Railway, adicione as seguintes variáveis para o serviço Evolution API:

```bash
# Server
SERVER_URL=${{RAILWAY_PUBLIC_DOMAIN}}
PORT=8080

# Authentication
AUTHENTICATION_API_KEY=4487C5C69D4A-4795-8FE8-E1296D76978F

# Database - PostgreSQL (use a reference do Railway)
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_URL}}?schema=public
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=false
DATABASE_SAVE_MESSAGE_UPDATE=false
DATABASE_SAVE_DATA_CONTACTS=false
DATABASE_SAVE_DATA_CHATS=false

# Cache - Redis (use a reference do Railway)
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

# Baileys Config
CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome
```

## Passo 5: Gerar Domínio Público

1. No serviço Evolution API, vá em **"Settings"**
2. Em **"Networking"**, clique em **"Generate Domain"**
3. Anote a URL (ex: `https://pangeia-evolution-production.up.railway.app`)

## Passo 6: Atualizar .env Local

Atualize o arquivo `~/notion-pangeia/.env`:

```bash
EVOLUTION_API_URL=https://sua-url.up.railway.app
EVOLUTION_API_KEY=4487C5C69D4A-4795-8FE8-E1296D76978F
EVOLUTION_INSTANCE_NAME=pangeia
```

## Passo 7: Criar Instância e Conectar

```bash
# Criar instância
curl -X POST https://sua-url.up.railway.app/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: 4487C5C69D4A-4795-8FE8-E1296D76978F" \
  -d '{
    "instanceName": "pangeia",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

# Obter QR Code
curl https://sua-url.up.railway.app/instance/connect/pangeia \
  -H "apikey: 4487C5C69D4A-4795-8FE8-E1296D76978F"
```

## Troubleshooting

### Logs do serviço:
```bash
railway logs
```

### Verificar saúde:
```bash
curl https://sua-url.up.railway.app
```

### Redeploy:
```bash
railway up --detach
```
