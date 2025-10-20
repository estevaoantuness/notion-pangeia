# 🚀 Deploy NOVO no Render - Pangeia Bot

## 📋 Guia Completo de Deploy

### 1️⃣ Criar Conta no Render

1. Acesse: **https://dashboard.render.com/register**
2. Use GitHub para login
3. Autorize acesso ao repositório `notion-pangeia`

---

### 2️⃣ Criar Novo Web Service

1. No dashboard: **https://dashboard.render.com/**
2. Clique em **"New +"** → **"Web Service"**
3. Selecione o repositório: **`estevaoantuness/notion-pangeia`**
4. Clique em **"Connect"**

---

### 3️⃣ Configurar o Service

**Nome:**
```
pangeia-bot-novo
```

**Region:**
```
Oregon (US West) ou escolha mais próxima
```

**Branch:**
```
main
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Plan:**
```
Free (ou Starter se preferir)
```

---

### 4️⃣ Configurar Variáveis de Ambiente

Clique em **"Advanced"** → **"Add Environment Variable"**

Adicione TODAS estas variáveis:

#### 🔐 Evolution API (Obrigatório)
```
EVOLUTION_API_URL=https://pange-evolution-api.u5qiqp.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=Pange.IA Bot
```

#### 🔐 Notion API (Obrigatório)
```
NOTION_TOKEN=<PEGAR DO .env LOCAL>
NOTION_TASKS_DB_ID=<PEGAR DO .env LOCAL>
```

#### 🔐 OpenAI GPT (Obrigatório - SmartTaskAgent)
```
OPENAI_API_KEY=<PEGAR DO .env LOCAL>
```

#### ⚙️ Flask & App Settings
```
FLASK_SECRET_KEY=<GERAR AUTOMÁTICO ou usar qualquer string segura>
WEBHOOK_PATH=/webhook/whatsapp
LOG_LEVEL=INFO
ENVIRONMENT=production
TIMEZONE=America/Sao_Paulo
```

#### 💾 Databases (OPCIONAL - se Saraiva configurou)
```
REDIS_URL=<se tiver>
DATABASE_URL=<se tiver>
```

---

### 5️⃣ Deploy Automático

1. Clique em **"Create Web Service"**
2. Aguarde o build (3-5 minutos)
3. Quando terminar, você verá:
   ```
   ✅ Live at: https://pangeia-bot-novo-XXXX.onrender.com
   ```

---

### 6️⃣ Testar o Bot

Teste o health endpoint:

```bash
curl https://SEU-BOT-URL.onrender.com/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "notion-pangeia-webhook",
  "version": "1.0.0",
  "scheduler": "disabled"
}
```

---

### 7️⃣ Configurar Webhook na Evolution API

**IMPORTANTE:** Copie a URL do Render (ex: `https://pangeia-bot-novo-abc123.onrender.com`)

Execute este comando (substitua `SEU-BOT-URL`):

```bash
curl -X POST 'https://pange-evolution-api.u5qiqp.easypanel.host/webhook/set/Pange.IA%20Bot' \
  -H 'apikey: 429683C4C977415CAAFCCE10F7D57E11' \
  -H 'Content-Type: application/json' \
  -d '{
    "webhook": {
      "url": "https://SEU-BOT-URL.onrender.com/webhook/whatsapp",
      "enabled": true,
      "events": ["MESSAGES_UPSERT"],
      "webhookByEvents": false,
      "webhookBase64": false
    }
  }'
```

---

### 8️⃣ Habilitar Auto-Deploy

Para que o bot atualize automaticamente quando você fizer push no GitHub:

1. No Render Dashboard → Seu serviço
2. **Settings** → **Build & Deploy**
3. Ative: **"Auto-Deploy"** → **Yes**

Agora sempre que fizer `git push origin main`, o Render vai fazer deploy automático!

---

## ✅ CHECKLIST FINAL

- [ ] Service criado no Render
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Build completou com sucesso
- [ ] `/health` retorna `status: healthy`
- [ ] Webhook configurado na Evolution API
- [ ] Auto-Deploy habilitado
- [ ] Teste no WhatsApp: enviar "oi" → resposta humanizada com GPT

---

## 🐛 Troubleshooting

### Bot não responde no WhatsApp?

1. Verifique webhook:
```bash
curl -H 'apikey: 429683C4C977415CAAFCCE10F7D57E11' \
  'https://pange-evolution-api.u5qiqp.easypanel.host/webhook/find/Pange.IA%20Bot'
```

2. Veja logs no Render:
   - Dashboard → Seu serviço → **Logs**

### Build falhou?

- Verifique se `requirements.txt` está completo
- Veja logs de build no Render

### GPT não funciona?

- Confirme que `OPENAI_API_KEY` está configurada
- Veja logs: procure por "SmartTaskAgent"

---

## 📊 Monitoramento

**Logs em tempo real:**
```
Dashboard → pangeia-bot-novo → Logs
```

**Métricas:**
```
Dashboard → pangeia-bot-novo → Metrics
```

---

## 🔄 Como Atualizar o Bot

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
```

Render vai fazer deploy automático em 2-5 minutos!

---

**PRONTO! Bot no ar com:**
- ✅ GPT-4o-mini humanizado
- ✅ Respostas conversacionais
- ✅ Scheduler desabilitado
- ✅ Deploy automático do GitHub
