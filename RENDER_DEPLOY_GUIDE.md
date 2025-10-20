# 🚀 Deploy Evolution API no Render.com - Guia Completo

## ✅ VANTAGENS DO RENDER

- ✅ **100% GRÁTIS** (não pede cartão!)
- ✅ PostgreSQL grátis (1GB)
- ✅ Redis grátis (25MB)
- ✅ Deploy via Docker
- ✅ Interface web simples

**Desvantagem:** App dorme após 15min sem uso (mas acorda automaticamente quando alguém acessa)

---

## 📋 PASSO A PASSO

### **PASSO 1: Criar Conta no Render**

1. Acesse: https://render.com/
2. Clique em **"Get Started"**
3. Faça signup com GitHub, GitLab ou Email
4. **NÃO PRECISA DE CARTÃO!** ✅

---

### **PASSO 2: Criar PostgreSQL Database**

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"PostgreSQL"**
3. Preencha:
   - **Name:** `pangeia-postgres`
   - **Database:** `pangeia_db`
   - **User:** `pangeia_user`
   - **Region:** Oregon (us-west) ou outra mais próxima
   - **Plan:** **FREE** ✅
4. Clique em **"Create Database"**
5. **Aguarde 2-3 minutos** para provisionar
6. **IMPORTANTE:** Copie a **"Internal Database URL"** (algo como: `postgresql://pangeia_user:...@dpg-xxxxx/pangeia_db`)

---

### **PASSO 3: Criar Redis Instance**

1. No dashboard, clique em **"New +"**
2. Selecione **"Redis"**
3. Preencha:
   - **Name:** `pangeia-redis`
   - **Region:** Mesma do PostgreSQL
   - **Plan:** **FREE** ✅
4. Clique em **"Create Redis"**
5. **Aguarde 1-2 minutos**
6. **IMPORTANTE:** Copie a **"Internal Redis URL"** (algo como: `redis://red-xxxxx:6379`)

---

### **PASSO 4: Criar Web Service (Evolution API)**

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Escolha **"Deploy an existing image from a registry"**
4. Preencha:
   - **Image URL:** `atendai/evolution-api:v2.1.1`
   - **Name:** `pangeia-evolution-api`
   - **Region:** Mesma do PostgreSQL e Redis
   - **Plan:** **FREE** ✅

---

### **PASSO 5: Configurar Variáveis de Ambiente**

Ainda na criação do Web Service, role até **"Environment Variables"** e adicione:

```
SERVER_URL=https://pangeia-evolution-api.onrender.com
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=<COLE_AQUI_A_INTERNAL_DATABASE_URL>?schema=public
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=false
DATABASE_SAVE_MESSAGE_UPDATE=false
DATABASE_SAVE_DATA_CONTACTS=false
DATABASE_SAVE_DATA_CHATS=false
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=<COLE_AQUI_A_INTERNAL_REDIS_URL>
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=false
LOG_LEVEL=ERROR,WARN,INFO
LOG_COLOR=true
CORS_ORIGIN=*
CORS_METHODS=GET,POST,PUT,DELETE
CORS_CREDENTIALS=true
QRCODE_LIMIT=30
CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome
PORT=8080
```

**⚠️ IMPORTANTE:**
- Substitua `<COLE_AQUI_A_INTERNAL_DATABASE_URL>` pela URL que você copiou do PostgreSQL (adicione `?schema=public` no final!)
- Substitua `<COLE_AQUI_A_INTERNAL_REDIS_URL>` pela URL que você copiou do Redis
- A URL do `SERVER_URL` será diferente - o Render vai gerar uma URL como `https://pangeia-evolution-api-XXXX.onrender.com`. Você pode atualizar depois.

---

### **PASSO 6: Deploy!**

1. Clique em **"Create Web Service"**
2. Aguarde 3-5 minutos para deploy
3. Render vai baixar a imagem Docker e iniciar

---

### **PASSO 7: Atualizar SERVER_URL**

1. Após deploy completar, copie a URL pública gerada (ex: `https://pangeia-evolution-api-abc123.onrender.com`)
2. Vá em **"Environment"** (menu lateral)
3. Edite a variável `SERVER_URL` e cole a URL real
4. Clique em **"Save Changes"**
5. Render vai fazer redeploy automático (1-2 minutos)

---

### **PASSO 8: Testar a API**

Acesse no navegador: `https://SEU-APP.onrender.com`

Deve aparecer uma página da Evolution API!

---

### **PASSO 9: Criar Instância WhatsApp**

```bash
curl -X POST 'https://SEU-APP.onrender.com/instance/create' \
  -H 'apikey: pange-bot-secret-key-2024' \
  -H 'Content-Type: application/json' \
  -d '{"instanceName":"pangeia-bot","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'
```

---

### **PASSO 10: Gerar QR Code**

Aguarde 10 segundos e execute:

```bash
curl 'https://SEU-APP.onrender.com/instance/connect/pangeia-bot' \
  -H 'apikey: pange-bot-secret-key-2024'
```

Vai retornar um JSON com o QR Code em base64! 🎉

---

## 🆘 TROUBLESHOOTING

### App não inicia / fica crashando
1. Vá em **"Logs"** (menu lateral)
2. Procure por erros relacionados a:
   - `DATABASE_CONNECTION_URI` vazio → Verifique se colou a URL correta
   - `REDIS_URI` vazio → Verifique se colou a URL correta
   - Migrations failed → Database pode não estar pronto ainda, aguarde 2min e redesploy

### QR Code não aparece
1. Aguarde 30 segundos após criar instância
2. Tente deletar e recriar:
```bash
curl -X DELETE 'https://SEU-APP.onrender.com/instance/delete/pangeia-bot' \
  -H 'apikey: pange-bot-secret-key-2024'
```
Depois crie novamente (Passo 9)

### App dorme (FREE plan)
- Normal! Após 15min sem acesso, o app dorme
- Quando alguém acessa, ele acorda automaticamente em ~30s
- **Solução:** Upgrade para plano pago ($7/mês) ou use um serviço de "ping" grátis como UptimeRobot

---

## 💰 CUSTO

- **PostgreSQL:** GRÁTIS (1GB, 90 dias de retenção)
- **Redis:** GRÁTIS (25MB)
- **Web Service:** GRÁTIS (512MB RAM, dorme após 15min)

**Total: R$ 0,00** 🎉

---

## 🔗 LINKS ÚTEIS

- Dashboard: https://dashboard.render.com/
- Docs Docker Deploy: https://render.com/docs/deploy-an-image
- Suporte: https://render.com/docs

---

## ✅ CHECKLIST RÁPIDO

- [ ] Criar conta no Render (sem cartão!)
- [ ] Criar PostgreSQL database
- [ ] Criar Redis instance
- [ ] Copiar Internal Database URL
- [ ] Copiar Internal Redis URL
- [ ] Criar Web Service com imagem `atendai/evolution-api:v2.1.1`
- [ ] Adicionar todas as variáveis de ambiente
- [ ] Aguardar deploy (3-5min)
- [ ] Atualizar SERVER_URL com URL real
- [ ] Testar endpoint
- [ ] Criar instância WhatsApp
- [ ] Gerar QR Code
- [ ] Escanear com WhatsApp
- [ ] **BOT NO AR!** 🚀
