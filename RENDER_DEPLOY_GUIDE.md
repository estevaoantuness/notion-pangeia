# 🚀 GUIA DE DEPLOY: Render.com

## 🎯 Por que Render?

- ✅ **Custo fixo:** $7/mês (vs $20-35 Railway)
- ✅ **Sem bug de truncamento** de variáveis de ambiente
- ✅ **PostgreSQL gratuito** incluído (até 1GB)
- ✅ **Interface simples** e estável
- ✅ **Deploy automático** via GitHub
- ✅ **render.yaml** já configurado neste repo

---

## 📋 MÉTODO 1: Deploy via render.yaml (RECOMENDADO) ⭐

### **Passo 1: Fazer push do render.yaml**

```bash
git add render.yaml RENDER_DEPLOY_GUIDE.md
git commit -m "feat: Adiciona configuração Render para deploy"
git push origin main
```

### **Passo 2: Criar serviço no Render**

1. **Acesse:** https://dashboard.render.com
2. **Clique:** "New +" → "Blueprint"
3. **Conecte:** GitHub repository `estevaoantuness/notion-pangeia`
4. **Selecione:** Branch `main`
5. **Render detecta** automaticamente o `render.yaml`
6. **Clique:** "Apply" (deploy inicia automaticamente)

### **Passo 3: Aguardar deploy (~3-5 minutos)**

Render vai:
- ✅ Criar serviço web Python
- ✅ Instalar dependências
- ✅ Configurar TODAS as variáveis de ambiente (sem truncar!)
- ✅ Iniciar Gunicorn
- ✅ Gerar URL pública

### **Passo 4: Pegar URL do serviço**

Após deploy, você terá uma URL tipo:
```
https://notion-pangeia-bot.onrender.com
```

---

## 📋 MÉTODO 2: Deploy Manual (alternativa)

Se preferir configurar manualmente:

### **Passo 1: Criar Web Service**

1. **Dashboard Render** → "New +" → "Web Service"
2. **Conectar GitHub:** `estevaoantuness/notion-pangeia`
3. **Configurar:**
   - **Name:** `notion-pangeia-bot`
   - **Runtime:** `Python 3`
   - **Region:** `Oregon` (mais barato)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT src.webhook.app:app`
   - **Plan:** `Starter` ($7/mês)

### **Passo 2: Configurar Environment Variables**

No Dashboard, adicionar todas as variáveis:

```bash
# Secrets (configure com seus valores reais)
OPENAI_API_KEY=[SUA_CHAVE_OPENAI_164_CHARS]
EVOLUTION_API_KEY=[SUA_CHAVE_EVOLUTION]
NOTION_TOKEN=[SEU_TOKEN_NOTION]
NOTION_TASKS_DB_ID=[ID_DATABASE_NOTION]

# Públicas
EVOLUTION_API_URL=https://evo.pictorial.cloud
EVOLUTION_INSTANCE_NAME=Pangeia Bot
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1UOo3kKlNCdNJwIVJqMDlnJdtxGLjlGmi9vuctU44324/edit
GPT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
LOG_LEVEL=INFO
TIMEZONE=America/Sao_Paulo
ENVIRONMENT=production
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
WEBHOOK_PATH=/webhook/whatsapp
```

**Valores secrets disponíveis no arquivo local:** `RAILWAY_ENV_VARS.txt`

---

## 🔧 APÓS O DEPLOY

### **1. Verificar funcionamento**

```bash
# Health check
curl https://[SUA-URL].onrender.com/health

# Debug (verificar env vars)
curl https://[SUA-URL].onrender.com/debug | jq .

# Deve mostrar:
# - openai_client.is_none: false ✅
# - OPENAI_API_KEY.length: 164 ✅
```

### **2. Atualizar webhook do Evolution API**

```bash
python3 << 'PYEOF'
import requests

EVOLUTION_URL = "https://evo.pictorial.cloud"
EVOLUTION_KEY = "7LjVQc6PJJFFgzy14pzH90QffOOus0z2"
RENDER_URL = "https://[SUA-URL].onrender.com"  # ← SUBSTITUIR

response = requests.post(
    f"{EVOLUTION_URL}/webhook/set/Pangeia%20Bot",
    headers={
        "Content-Type": "application/json",
        "apikey": EVOLUTION_KEY
    },
    json={
        "webhook": {
            "url": f"{RENDER_URL}/webhook/whatsapp",
            "enabled": True,
            "events": ["MESSAGES_UPSERT"],
            "webhook_by_events": False
        }
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
PYEOF
```

### **3. Testar bot via WhatsApp**

```
Você: "oi"
Bot: "E aí! Bora ver suas tasks?"

Você: "minhas tasks"
Bot: [lista suas tasks do Notion] ✅
```

---

## 💰 CUSTO COMPARATIVO

| Plataforma | Custo Mensal | Status |
|------------|--------------|--------|
| **Render** | **$7/mês** | ✅ Recomendado |
| Railway | $20-35/mês | ❌ Bug de truncamento |

**Economia:** ~$15-28/mês ($180-336/ano)

---

## 🔄 DESATIVAR RAILWAY

Após confirmar que Render está funcionando:

1. **Acesse:** https://railway.app/project/notionpangeiafinale
2. **Settings** → "Danger Zone"
3. **Delete Service:** `notion-pangeia`
4. Manter só `evolution-api` (se ainda estiver usando)

---

## 🆘 TROUBLESHOOTING

### **Deploy falhou?**

```bash
# Ver logs no Render Dashboard
# Ou via CLI:
render logs -s notion-pangeia-bot
```

### **OPENAI_API_KEY ainda truncada?**

**No Render isso NÃO acontece!** Mas se acontecer:
- Edite a variável no Dashboard
- Cole novamente a chave completa
- Clique "Save Changes"

### **Webhook não funciona?**

Verifique:
- URL do webhook está correta no Evolution
- Health check do Render retorna 200
- Logs do Render mostram requisições chegando

---

## 📊 PRÓXIMOS PASSOS

1. ✅ Deploy no Render
2. ✅ Verificar `/debug` endpoint
3. ✅ Atualizar webhook Evolution → Render
4. ✅ Testar via WhatsApp
5. ✅ Desativar serviço Railway

---

**Última atualização:** 31/10/2025
**Status:** Pronto para deploy! 🚀
