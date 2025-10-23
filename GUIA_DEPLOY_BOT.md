# 🚀 GUIA COMPLETO: Deploy do Notion Pangeia Bot

**Documento para nova sessão do Claude**

---

## 📋 CONTEXTO DO PROJETO

**Nome:** Notion Pangeia Bot
**Propósito:** Bot WhatsApp para gestão de tarefas via Notion
**Stack:** Python + Flask + Evolution API + OpenAI GPT-4o-mini + Notion API
**Estado Atual:** Código limpo, mas bot com erro ao listar tasks

---

## 🏗️ ARQUITETURA ATUAL

```
EasyPanel (https://pange-evolution-api.u5qiqp.easypanel.host)
├── Evolution API (WhatsApp connection)
├── PostgreSQL
└── Redis
         ↓ HTTP calls
Railway (https://botpangeia-production.up.railway.app)
├── Flask Webhook (/webhook/whatsapp)
├── Conversational Agent (GPT-4o-mini)
└── Business Logic
         ↓ API calls
Notion API (Tasks Database)
```

---

## ❌ PROBLEMA ATUAL

**Sintoma:**
```
Usuário: "oi"
Bot: "E aí! Bora ver suas tasks?" ✅
Usuário: "bora"
Bot: "Ops, tive um problema. Tenta de novo?" ❌
```

**Causa Identificada:**
- OpenAI client retorna `None` ao tentar processar comandos
- OPENAI_API_KEY estava truncada/duplicada no Railway
- Foi corrigida, mas erro persiste

**Localização do Erro:**
- Arquivo: `src/agents/conversational_agent.py:316`
- Erro: `AttributeError: 'NoneType' object has no attribute 'chat'`

---

## 🎯 OBJETIVO

**Fazer o bot funcionar completamente:**
1. ✅ Receber mensagens (FUNCIONANDO)
2. ✅ Responder primeira interação (FUNCIONANDO)
3. ❌ Listar tarefas via GPT (QUEBRADO)
4. ❌ Processar comandos completos (QUEBRADO)

---

## 🔧 CONFIGURAÇÕES

### Variáveis de Ambiente (Railway)

```bash
# Notion
NOTION_TOKEN=ntn_[SEE RAILWAY VARIABLES]
NOTION_TASKS_DB_ID=[SEE RAILWAY VARIABLES]

# Evolution API (EasyPanel)
EVOLUTION_API_URL=https://pange-evolution-api.u5qiqp.easypanel.host
EVOLUTION_API_KEY=[SEE RAILWAY VARIABLES]
EVOLUTION_INSTANCE_NAME=Pange.IA Bot

# OpenAI (CRÍTICO - key completa 164 caracteres)
OPENAI_API_KEY=sk-proj-[SEE RAILWAY VARIABLES - deve ter 164 caracteres completos]

# Groq (alternativa)
GROQ_API_KEY=gsk_[SEE RAILWAY VARIABLES]

# Flask
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
PORT=8080
WEBHOOK_PATH=/webhook/whatsapp

# Config
GPT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
LOG_LEVEL=INFO
TIMEZONE=America/Sao_Paulo
ENVIRONMENT=production
```

### URLs Importantes

- **Bot Produção:** https://botpangeia-production.up.railway.app
- **Health Check:** https://botpangeia-production.up.railway.app/health
- **Debug Info:** https://botpangeia-production.up.railway.app/debug
- **Evolution API:** https://pange-evolution-api.u5qiqp.easypanel.host
- **WhatsApp Bot:** +353 83 465 6345

### Railway Project Info

```
Project ID: fb858822-82bf-4c44-afaf-c1e37005fd4c
Project Name: talented-expression
Service: botpangeia
Environment: production
```

---

## 🔍 DIAGNÓSTICO RÁPIDO

### 1. Verificar Status dos Componentes

```bash
# Evolution API (WhatsApp)
curl -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
  "https://pange-evolution-api.u5qiqp.easypanel.host/instance/connectionState/Pange.IA%20Bot"

# Esperado: {"instance": {"state": "open"}}

# Bot Railway
curl https://botpangeia-production.up.railway.app/health

# Esperado: {"status": "healthy"}

# Webhook configurado?
curl -H "apikey: 429683C4C977415CAAFCCE10F7D57E11" \
  "https://pange-evolution-api.u5qiqp.easypanel.host/webhook/find/Pange.IA%20Bot"

# Esperado: {"enabled": true, "url": "https://botpangeia-production.up.railway.app/webhook/whatsapp"}
```

### 2. Testar Localmente

```bash
cd /Users/estevaoantunes/notion-pangeia

# Testar imports
python3 -c "from src.webhook.app import app; print('✅ OK')"

# Testar conversational agent (vai falhar sem OPENAI_API_KEY local)
python3 -c "
from src.agents.conversational_agent import get_conversational_agent
agent = get_conversational_agent()
print(agent.process('Teste', 'oi'))
"
```

---

## 🛠️ PASSOS PARA CORRIGIR

### Opção 1: Debug do OpenAI Client

**Investigar por que o client está None mesmo com API key presente:**

1. Verificar `config/openai_config.py:16-23`
2. Adicionar logs para debug:
   ```python
   print(f"DEBUG: OPENAI_API_KEY presente? {bool(OPENAI_API_KEY)}")
   print(f"DEBUG: OPENAI_API_KEY length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")
   print(f"DEBUG: Client inicializado? {client is not None}")
   ```
3. Fazer commit e push
4. Aguardar deploy Railway
5. Verificar logs

### Opção 2: Fallback para Processamento Simples

Se OpenAI continuar falhando, implementar fallback:

1. Detectar quando GPT falha
2. Usar NLP local (já existe em `src/commands/`)
3. Processar comandos sem GPT para casos básicos

### Opção 3: Trocar para Groq

Groq é mais rápido e mais confiável:

1. Editar `config/openai_config.py`
2. Usar `GROQ_API_KEY` ao invés de `OPENAI_API_KEY`
3. Alterar endpoint para Groq API

### Opção 4: Consolidar Tudo no Railway

Trazer Evolution API para dentro do Railway:

1. Criar novo serviço Railway com Evolution API
2. Adicionar PostgreSQL e Redis via Railway addons
3. Atualizar `EVOLUTION_API_URL` para URL interna Railway
4. Eliminar dependência do EasyPanel

---

## 📝 COMANDOS ÚTEIS

### Git

```bash
# Ver últimos commits
git log --oneline -5

# Status
git status

# Commit e push
git add .
git commit -m "Fix: descrição"
git push origin main
```

### Railway CLI

```bash
# Ver variáveis
railway variables

# Setar variável
railway variables --set "NOME=valor"

# Deploy manual
railway up

# Logs (não funciona sem link correto)
railway logs
```

### Testar Webhook

```bash
# Enviar mensagem teste
curl -X POST https://botpangeia-production.up.railway.app/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"test": "ping"}'
```

---

## 📊 HISTÓRICO DO QUE FOI FEITO

### 2025-10-23 (Hoje)

1. ✅ Limpeza massiva do código
   - Removidas 3 pastas de motor psicológico (src/cognitive, src/ml, src/coordination)
   - Deletados 26 arquivos de troubleshooting
   - -9.375 linhas de código
   - Commit: `5f37bef`

2. ✅ Identificado problema: OPENAI_API_KEY truncada
   - Havia 2 variáveis no Railway (maiúscula e minúscula)
   - A maiúscula estava truncada
   - Corrigida via `railway variables --set`

3. ❌ Problema persiste
   - Bot ainda retorna erro ao listar tasks
   - OpenAI client continua None
   - Deploy pode não ter sido efetivado

### Commits Recentes

```
5f37bef - 🧹 Limpeza massiva (23/10/2025)
f3d871f - Commit anterior (antes da limpeza)
27814ab - Deploy atual em produção (20/10/2025)
```

---

## 🎯 PRÓXIMAS AÇÕES RECOMENDADAS

**Prioridade 1: Fazer o bot funcionar**
1. Debug completo do OpenAI client initialization
2. Adicionar logs detalhados
3. Testar com API key hardcoded temporariamente (debug)
4. Se falhar, implementar fallback ou trocar para Groq

**Prioridade 2: Estabilidade**
1. Implementar monitoring da Evolution API
2. Alertas quando WhatsApp desconectar
3. Considerar consolidar no Railway (tudo em um lugar)

**Prioridade 3: Longo prazo**
1. Migrar para WhatsApp Cloud API oficial (elimina QR code)
2. Upgrade Railway para plano pago ($5/mês - sem throttling)

---

## 🔗 LINKS E RECURSOS

- **Repositório:** https://github.com/estevaoantuness/notion-pangeia
- **Railway Dashboard:** https://railway.app/project/fb858822-82bf-4c44-afaf-c1e37005fd4c
- **Evolution API Docs:** https://doc.evolution-api.com
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Notion API Docs:** https://developers.notion.com

---

## 📞 CONTATOS

- **Email:** estevao@pangeia.com.br
- **WhatsApp:** +55 41 91851-256
- **WhatsApp Bot:** +353 83 465 6345

---

## 🚨 NOTAS IMPORTANTES

1. **Nunca commitar secrets** - `.gitignore` já configurado
2. **Railway free tier** - $5 crédito/mês (pode acabar e causar throttling)
3. **EasyPanel fora do controle** - Evolution API pode desconectar
4. **Deploy Railway** - Pode demorar 2-3 minutos
5. **QR Code expira** - Precisa reconectar WhatsApp ocasionalmente

---

**Última atualização:** 2025-10-23 16:40 BRT
**Status:** Bot respondendo mas falhando ao processar comandos
**Bloqueador:** OpenAI client initialization
