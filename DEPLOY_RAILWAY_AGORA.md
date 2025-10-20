# 🚀 DEPLOY NO RAILWAY - PASSO A PASSO FINAL

## ⚡ AÇÃO RÁPIDA (5 minutos)

### 1️⃣ Abra o Railway
**Link direto:** https://railway.app/project/notion-pangeia

### 2️⃣ Crie o novo serviço
- Clique no botão **"+ New"** (canto superior direito)
- Selecione **"GitHub Repo"**
- Escolha: **`estevaoantuness/notion-pangeia`**
- Clique em **"Deploy Now"**

### 3️⃣ Railway vai fazer o build automático
O Railway vai detectar:
- ✅ `Dockerfile` → vai usar para build
- ✅ `railway.toml` → configurações de deploy
- ✅ `requirements.txt` → dependências Python

**Aguarde 2-3 minutos** para o build completar.

### 4️⃣ Configure as variáveis de ambiente
Clique no serviço que acabou de criar → Aba **"Variables"**

Cole estas variáveis (COPIAR TUDO):

```
NOTION_TOKEN=[REDACTED - See .env file]
NOTION_TASKS_DB_ID=[REDACTED - See .env file]
EVOLUTION_API_URL=https://pange-evolution-api.u5qiqp.easypanel.host
EVOLUTION_API_KEY=429683C4C977415CAAFCCE10F7D57E11
EVOLUTION_INSTANCE_NAME=Pange.IA Bot
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
WEBHOOK_PATH=/whatsapp/incoming
PORT=5000
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo
LOG_LEVEL=INFO
CACHE_EXPIRY_HOURS=24
MAX_RETRIES=3
ENVIRONMENT=production
```

Clique em **"Add Variable"** e cole cada linha.

### 5️⃣ Gere o domínio público
- Vá na aba **"Settings"**
- Clique em **"Networking"**
- Clique em **"Generate Domain"**
- Copie a URL gerada (ex: `https://notion-pangeia-production-abc123.up.railway.app`)

### 6️⃣ Teste o bot
Abra no navegador ou use curl:
```bash
curl https://SUA-URL-AQUI/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "notion-pangeia-webhook",
  "version": "1.0.0",
  "scheduler": "running"
}
```

### 7️⃣ ME ENVIE A URL!
Assim que tiver a URL, me mande aqui e eu configuro o webhook automaticamente!

---

## 🆘 PROBLEMAS COMUNS

### Build falhou?
- Verifique os logs no Railway (aba "Deployments")
- Erro comum: falta de variável `PORT`

### Deploy passou mas não responde?
- Verifique se gerou o domínio público
- Teste o endpoint `/health`

### Não encontra o repo?
- Verifique se está logado no GitHub correto
- Reconecte o Railway ao GitHub: Settings → Integrations

---

## ✅ PRÓXIMOS PASSOS (DEPOIS DO DEPLOY)

Quando me enviar a URL, vou:
1. Configurar webhook na Evolution API automaticamente
2. Testar envio de mensagem
3. Confirmar que tudo está funcionando

🎯 **Vamos lá! Acesse agora: https://railway.app/project/notion-pangeia**
