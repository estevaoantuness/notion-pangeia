# 🔧 FIX DEFINITIVO - Railway Database Connection

## 🎯 PROBLEMA IDENTIFICADO

A Evolution API roda `prisma migrate deploy` **durante o BUILD**, não no runtime.

Nessa fase, as variáveis de referência `${{Postgres.DATABASE_URL}}` **NÃO funcionam** porque os containers ainda não estão rodando.

---

## ✅ SOLUÇÃO: DESABILITAR MIGRATIONS NO BUILD

### **PASSO 1: Criar arquivo de configuração do Railway**

No serviço **evolution-api**, adicione estas configurações:

#### **Settings → Build:**

Mude o **Build Command** para:
```bash
echo "Skipping migrations during build"
```

#### **Settings → Deploy:**

Adicione um **Start Command** customizado:
```bash
npm run db:deploy && npm run start:prod
```

---

### **PASSO 2: Configurar Variáveis de Ambiente**

No serviço **evolution-api** → **Variables** → **Raw Editor**:

```env
SERVER_URL=https://SEU-APP.up.railway.app
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024

# Database
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_URL}}?schema=public
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

# Port
PORT=8080
```

---

### **PASSO 3: Adicionar Health Check Delay**

Em **Settings** → **Deploy** → **Health Check**:

- **Health Check Path:** `/`
- **Health Check Timeout:** `300` segundos (5 minutos)
- **Health Check Interval:** `30` segundos

Isso dá tempo para as migrations rodarem no startup.

---

## 🚀 ALTERNATIVA MAIS SIMPLES (SE NÃO FUNCIONAR)

### **Desabilitar completamente as migrations automáticas:**

Adicione esta variável de ambiente:

```env
DOCKER_ENV=true
```

E mude o Dockerfile/nixpacks para **não rodar migrations no build**.

---

## 📋 RESUMO DOS PASSOS

1. ✅ Settings → Build → Build Command: `echo "Skip"`
2. ✅ Settings → Deploy → Start Command: `npm run db:deploy && npm run start:prod`
3. ✅ Variables → Cole todas as variáveis com `${{Postgres.DATABASE_URL}}` e `${{Redis.REDIS_URL}}`
4. ✅ Settings → Health Check → Timeout: 300s
5. ✅ Redesploy

---

## 🔍 POR QUE ISSO FUNCIONA?

- ✅ Build não tenta conectar no banco (porque pulamos migrations)
- ✅ Migrations rodam no **startup** (quando variáveis já estão disponíveis)
- ✅ Health check aguarda migrations terminarem antes de marcar como "healthy"
- ✅ `${{Postgres.DATABASE_URL}}` funciona perfeitamente no runtime

---

## ⚠️ SE AINDA ASSIM DER ERRO

Use a **DATABASE_PUBLIC_URL** diretamente:

```env
DATABASE_CONNECTION_URI=${{Postgres.DATABASE_PUBLIC_URL}}?schema=public
```

Essa variável é pública e pode funcionar melhor em alguns casos.
