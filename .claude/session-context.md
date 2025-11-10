# Notion Pangeia - Contexto de Sessão

## Status Atual (10/11/2025 19:30 UTC-3)

### ✅ Resolvido
1. **UnboundLocalError (Redis)**: Removido completamente bloco Redis do webhook
   - Commits: `0d7f3d5`, `2b2bd87`, `13c6722`
   - Código agora 100% síncrono
   - Webhook funciona sem erros de Redis

2. **404 Evolution API**: Nome da instância estava errado
   - Era: "Pange.IA Bot" ❌
   - Agora: "Pangeia Bot" ✅
   - Configurado em: `EVOLUTION_INSTANCE_NAME=Pangeia Bot`
   - Local: Railway env vars (web service)

### 🚀 Deploy Status
- **Último commit local**: `0d7f3d5` (refactor: Remover Redis)
- **GitHub**: Sincronizado ✅
- **Railway**: Deveria estar rodando nova versão com "Pangeia Bot"
- **Problema anterior**: Railway levava 5-10min para pegar novo commit (não era instantâneo)

### ⚠️ Pendente
- [ ] Testar webhook com mensagem WhatsApp
- [ ] Confirmar se bot responde com "Pangeia Bot" correto

---

## Problema: Por que Railway não deployava commits rapidamente?

### Causa
Railway tem **auto-deploy desativado ou lento** porque:
1. Usa `.railway` config ou GitHub Actions
2. Pode estar em fila de build
3. Sem webhook GitHub → polling lento (5-10min)

### Forçar Deploy Manual no Railway

```bash
# Opção 1: Fazer novo commit (força rebuild)
git commit --allow-empty -m "chore: force railway redeploy"
git push origin main

# Opção 2: Redeploy via CLI (se configurado)
railway up

# Opção 3: Redeploy via Dashboard
# 1. Ir para: https://railway.app
# 2. Selecionar projeto "notionpangeia"
# 3. Clicar em "Service" → "Deploy"
# 4. Clicar botão "Redeploy"

# Opção 4: Checar status do deploy
railway status
railway logs --service web --tail 50
```

### Melhorar Velocidade de Deploy

**Adicionar webhook GitHub → Railway:**
```bash
# 1. Railway Dashboard → Settings → Webhooks
# 2. GitHub → Settings → Webhooks
# 3. Add: https://webhooks.railway.app/github
# 4. Eventos: Push, Pull requests
```

**Ou usar**: `railway up` (push direto sem GitHub)

---

## Arquitetura do Projeto

### Componentes Ativos
- **Webhook**: `/src/webhook/app.py` (Flask, síncrono)
- **NLP**: `/src/commands/processor.py` (CommandProcessor)
- **WhatsApp**: `/src/whatsapp/sender.py` + `client.py`
- **Notion**: `/src/notion/client.py`
- **Scheduler**: `/src/scheduler/scheduler.py` (jobs automáticos)

### Removido/Desativado
- ❌ Redis Queue (`/src/queue/redis_client.py`)
- ❌ Workers (`/src/workers/executor.py`, `responder.py`)
- ❌ Modo assíncrono com 3 nodes

---

## Configurações Railway (Environment)

```
EVOLUTION_API_URL: https://evo.pictorial.cloud
EVOLUTION_API_KEY: 7LjVQc6PJJFFgzy14pzH90QffOOus0z2
EVOLUTION_INSTANCE_NAME: Pangeia Bot ✅ (CORRIGIDO)

NOTION_TOKEN: [secreto]
NOTION_TASKS_DB_ID: [secreto]

PORT: 5000
TIMEZONE: America/Sao_Paulo
```

---

## Debug Rápido

```bash
# Ver últimos logs
railway logs --service web --tail 100

# Ver variáveis
railway variables --service web | grep -i evolution

# Monitorar em tempo real
watch -n 2 'railway logs --service web --tail 20'

# Testar webhook local
curl -X POST http://localhost:5000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"554191851256","body":"test"}]}}]}]}'
```

---

## Próximos Passos

1. **Testar bot**: Enviar mensagem no WhatsApp
2. **Se não responder**:
   - [ ] Verificar `railway logs` para novo erro
   - [ ] Confirmar "Pangeia Bot" está sendo usado
   - [ ] Testar conexão com Evolution API
3. **Se responder**: 🎉 Tudo funcionando!

---

## Links Úteis

- Railway Dashboard: https://railway.app
- Evolution API: https://evo.pictorial.cloud
- GitHub Repo: https://github.com/estevaoantuness/notion-pangeia
- Notion DB: [verificar settings.py]

