# Pangeia Bot - Contexto do Projeto

**Última Atualização:** 2025-10-18

---

## 📊 STATUS ATUAL DO PROJETO

### Informações Gerais
- **Nome:** Pangeia Bot (Notion Pangeia)
- **Status:** Em Migração (Evolution API)
- **Stack:** Flask + Evolution API + Notion API
- **Deploy Anterior:** Render.com (desativado)
- **Novo Deploy:** Railway (em configuração)
- **Usuários:** 10 colaboradores ativos
- **Métricas:** 7.894 linhas de código, 90.2% NLP accuracy

### Uptime & Performance
- **Uptime Anterior:** 99.5% (Render)
- **Último Incidente:** QR Code expirado (requires reconnection)

---

## 🔧 CONFIGURAÇÕES CRÍTICAS

### Evolution API (NOVA - Railway)
```
URL: [PENDING - Em deploy no Railway]
API Key: 4487C5C69D4A-4795-8FE8-E1296D76978F
Instance Name: pangeia
Integration: WHATSAPP-BAILEYS (v2.1.1)
Database: PostgreSQL (Railway)
Cache: Redis (Railway)
```

### Evolution API (ANTIGA - Render - DESATIVADA)
```
URL: https://pangeia-evolution-api.onrender.com
API Key: 6218B541-8860-404F-85CF-D5AB9B8384A (DEPRECATED)
Status: Deletada e substituída
```

### Bot Application
```
URL: https://notion-pangeia-bot.onrender.com (OFFLINE - precisa atualizar)
Port: 5000
Webhook Path: /whatsapp/incoming
```

### Notion API
```
Token: [REDACTED - See .env file]
Tasks DB ID: [REDACTED - See .env file]
```

### Colaboradores Mapeados
10 usuários ativos no sistema com onboarding completo

---

## 🎯 DECISÕES TÉCNICAS IMPORTANTES

### 1. WhatsApp Integration
**Decisão:** Baileys (Evolution API) em vez de Cloud API
**Motivo:** Custo-benefício superior, sem custos por mensagem
**Status:** ✅ Implementado e funcionando
**Versão:** Evolution API v2.1.1

### 2. Hosting & Deploy
**Decisão Anterior:** Render.com para ambos serviços
**Status:** 🔄 Em migração
**Nova Decisão:** Railway para Evolution API
**Motivo:** Melhor performance, sem cold starts, integração com PostgreSQL e Redis

### 3. NLP & Processamento
**Decisão:** NLP customizado (não terceirizado)
**Performance:** 90.2% accuracy
**Status:** ✅ Produção

### 4. Onboarding System
**Decisão:** Sistema sem repetição de onboarding
**Implementação:** Verificação de estado no Notion
**Status:** ✅ Funcionando

### 5. Comandos Removidos
- ❌ "bloqueada" - Removido por não fazer sentido no contexto
- ❌ Percentuais de progresso - Removido (causava bugs)

---

## 🐛 PROBLEMAS RESOLVIDOS

### 1. QR Code Expiration Issue (2025-10-18)
**Problema:** QR Code da Evolution API expirou
**Causa:** Instância antiga no Render com timeout
**Solução:** Migração completa para nova Evolution API no Railway
**Status:** 🔄 Em andamento

### 2. Render Cold Start Issues
**Problema:** Evolution API no Render tinha cold starts frequentes
**Impacto:** Timeouts de 2+ minutos em requisições
**Solução:** Migração para Railway
**Status:** 🔄 Em andamento

### 3. Database Provider Error
**Problema:** Evolution API não funcionava sem database
**Causa:** v2.x+ requer PostgreSQL (não aceita apenas memória)
**Solução:** PostgreSQL configurado via Railway
**Status:** ✅ Resolvido

### 4. Redis Cache for QR Code
**Problema:** QR Code não aparecia sem cache
**Solução:** Redis habilitado no setup
**Status:** ✅ Implementado

---

## 🏗️ ARQUITETURA ATUAL

### Stack Completo
```
┌─────────────────────────────────────┐
│     WhatsApp (10 usuários)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Evolution API (Railway - NOVO)     │
│  - Baileys v2.1.1                   │
│  - PostgreSQL (persistência)        │
│  - Redis (cache QR Code)            │
└──────────────┬──────────────────────┘
               │ Webhook
               ▼
┌─────────────────────────────────────┐
│  Flask Bot App (Render)             │
│  - Webhook Handler                  │
│  - NLP Processing (90.2%)           │
│  - Business Logic                   │
│  - Scheduler (APScheduler)          │
└──────────────┬──────────────────────┘
               │ API Calls
               ▼
┌─────────────────────────────────────┐
│      Notion API                     │
│  - Tasks Database                   │
│  - User States                      │
│  - Onboarding Control               │
└─────────────────────────────────────┘
```

### Fluxo de Mensagens
1. **Usuário → WhatsApp**: Envia mensagem
2. **WhatsApp → Evolution API**: Recebe via Baileys
3. **Evolution API → Flask Bot**: Webhook POST
4. **Flask Bot**: Processa com NLP (90.2% accuracy)
5. **Flask Bot → Notion**: Atualiza tasks/estados
6. **Flask Bot → Evolution API**: Envia resposta
7. **Evolution API → WhatsApp**: Entrega ao usuário

---

## 📋 TAREFAS EM ANDAMENTO

### Migração Evolution API (ATUAL)
- [x] Criar nova Evolution API com nova API Key
- [x] Configurar arquivos para deploy Railway
- [x] Commit e push para GitHub
- [x] Documentação de setup
- [ ] **Deploy no Railway** ⬅️ PRÓXIMO PASSO
- [ ] Gerar domínio público Railway
- [ ] Atualizar .env com nova URL
- [ ] Criar instância "pangeia"
- [ ] Escanear novo QR Code
- [ ] Atualizar webhook no bot
- [ ] Testar envio/recebimento
- [ ] Atualizar bot no Render com novas configs

---

## 📁 ESTRUTURA DE ARQUIVOS

### Principais Diretórios
```
notion-pangeia/
├── src/
│   ├── whatsapp/client.py       # WhatsApp client (Evolution API)
│   ├── webhook/app.py            # Flask webhook handler
│   ├── notion/client.py          # Notion API integration
│   └── nlp/processor.py          # NLP engine (90.2%)
├── evolution-setup/              # Docker local (deprecated)
│   └── docker-compose.yml
├── evolution-api-railway/        # NEW: Railway deployment
│   ├── Dockerfile
│   ├── railway.json
│   └── README.md
├── .env                          # Environment variables
└── config/settings.py            # App configuration
```

### Arquivos de Configuração
- `.env`: Credenciais e URLs (não commitado)
- `.env.example`: Template de configuração
- `railway.json`: Config do Railway
- `docker-compose.yml`: Setup local (deprecated)

---

## 🔐 SEGURANÇA & CREDENCIAIS

### Variáveis de Ambiente (.env)
```bash
# Notion
NOTION_TOKEN=[REDACTED - See .env file]
NOTION_TASKS_DB_ID=[REDACTED - See .env file]

# Evolution API (NOVA)
EVOLUTION_API_URL=[PENDING Railway URL]
EVOLUTION_API_KEY=4487C5C69D4A-4795-8FE8-E1296D76978F
EVOLUTION_INSTANCE_NAME=pangeia

# Flask
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
WEBHOOK_PATH=/whatsapp/incoming
PORT=5000

# Scheduler
TIMEZONE=America/Sao_Paulo
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
```

---

## 📊 MÉTRICAS & MONITORAMENTO

### Performance
- **NLP Accuracy:** 90.2%
- **Response Time:** <500ms (média)
- **Uptime (Render):** 99.5% (histórico)
- **Webhook Success Rate:** 98%+

### Usuários
- **Total:** 10 colaboradores
- **Ativos Diários:** ~8-9
- **Taxa de Onboarding:** 100%
- **Retenção:** Alta (uso diário)

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Aguardar URL do Railway** ⬅️ BLOQUEADOR
2. Atualizar `.env` com nova URL
3. Criar instância "pangeia" via API
4. Gerar e escanear QR Code
5. Testar envio/recebimento
6. Atualizar bot no Render
7. Validar com usuários

---

## 📝 NOTAS IMPORTANTES

### Cold Start no Render
- Evolution API no plano gratuito entra em sleep após 15min inatividade
- Causa timeouts de 2+ minutos no primeiro request
- **Solução:** Migrar para Railway (sem cold starts no plano pago básico)

### PostgreSQL Obrigatório
- Evolution API v2.x+ **requer** PostgreSQL
- Não funciona apenas com memória (DATABASE_ENABLED=false)
- SQLite não é suportado

### Redis para QR Code
- Redis é **necessário** para QR Code funcionar corretamente
- Cache ativado com `CACHE_REDIS_ENABLED=true`

### Baileys vs Cloud API
- **Baileys:** Grátis, sem limites, mais flexível
- **Cloud API:** Pago, aprovação Meta, mais restritivo
- **Decisão:** Baileys mantido por custo-benefício

---

## 🔗 LINKS ÚTEIS

- **Evolution API Docs:** https://doc.evolution-api.com
- **Railway Dashboard:** https://railway.app
- **Render Dashboard:** https://dashboard.render.com
- **Notion API Docs:** https://developers.notion.com
- **GitHub Repo:** https://github.com/estevaoantuness/notion-pangeia

---

## 🆘 COMANDOS RÁPIDOS

### Verificar Status Evolution API
```bash
curl -X GET "$EVOLUTION_API_URL/instance/fetchInstances?instanceName=pangeia" \
  -H "apikey: $EVOLUTION_API_KEY"
```

### Criar Instância
```bash
curl -X POST "$EVOLUTION_API_URL/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: $EVOLUTION_API_KEY" \
  -d '{"instanceName":"pangeia","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'
```

### Obter QR Code
```bash
curl -X GET "$EVOLUTION_API_URL/instance/connect/pangeia" \
  -H "apikey: $EVOLUTION_API_KEY"
```

### Git Commands
```bash
# Commit e push
git add . && git commit -m "msg" && git push

# Status
git status

# Ver logs
git log --oneline -5
```

---

**Última Sincronização:** 2025-10-18 20:20 BRT
**Status:** 🔄 Migração Evolution API para Railway em andamento
