# 🚀 Notion Pangeia - Contexto para Claude Desktop

## 📋 Resumo Executivo
**Notion Pangeia** é um bot WhatsApp inteligente para gestão de tarefas via Notion, com NLP robusto, check-ins automáticos e humanização de mensagens.

**Status:** ✅ Em Produção (v2.3) | **Uptime:** 99.5% | **Taxa NLP:** 85.2%

---

## 🏗️ Arquitetura (Production Stack)

```
┌─────────────────────────────────────────────────────────────┐
│  WhatsApp User                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Evolution API (EasyPanel)                                  │
│  URL: https://pange-evolution-api.u5qiqp.easypanel.host     │
│  → Gerencia conexão WhatsApp + fila de mensagens            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Railway (Flask Bot + NLP)                                  │
│  URL: https://botpangeia-production.up.railway.app          │
│  → Webhook receiver + Processamento de comandos             │
│  → NLP normalizer + Interpretação de intents                │
│  → Scheduler para check-ins automáticos (3x/dia)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Notion   PostgreSQL  Redis
          (Tasks)   (Cache)    (Session)
```

---

## 📁 Estrutura de Pastas

```
src/
├── agents/              # Agentes especializados (psychology, response gen)
├── api/                 # Endpoints Flask (/webhook, /dashboard)
├── checkins/            # Sistema de check-ins automáticos (3x dia)
├── commands/            # Parsing de comandos + normalizer.py (NLP core)
├── database/            # PostgreSQL + migrations
├── messaging/           # Envio de mensagens (Evolution API)
├── nlp/                 # Análise de intenção + fuzzy matching
├── notion/              # Integração com Notion API
├── tasks/               # Lógica de tarefas (CRUD)
├── webhook/             # Receptor do webhook WhatsApp
└── whatsapp/            # Formatação de mensagens WhatsApp
```

---

## 🎯 Funcionalidades Principais

### 1️⃣ **Gestão de Tasks (90%)**
```
minhas tarefas      → Lista tarefas do dia
feito 1             → Marca como concluída
andamento 2         → Marca como em progresso
bloqueada 3 - motivo → Marca como bloqueada
progresso           → Mostra % de conclusão
```

### 2️⃣ **NLP Robusto (85.2% cobertura)**
- ✅ Fuzzy matching (typos até 80-92%)
- ✅ Sinônimos temporais (50+ variações)
- ✅ Múltiplas tarefas ("feito 1, 2, 3")
- ✅ Emojis como comandos (👍 = sim, ❌ = não)
- ✅ Números por extenso ("três" → 3)

### 3️⃣ **Check-ins Automáticos (3x dia)**
```
06:00 AM → "Qual é a meta principal de hoje?"
12:00 PM → "Como está o ritmo do dia?"
18:00 PM → "Como foi seu dia?"
```
Respostas salvas em PostgreSQL → Visualizáveis no Dashboard

### 4️⃣ **Humanização de Mensagens**
- Saudações contextuais (manhã/tarde/noite/segunda/sexta)
- 50+ variações de respostas (sem repetição)
- Tom educado, amigável, profissional
- YAML-based message templates

### 5️⃣ **Slot-Filling Inteligente**
```
User: "bloqueada 4"
Bot: "Qual o motivo?"
User: "aguardando aprovação"
Bot: "✅ Tarefa 4 bloqueada!"
```

---

## 🔧 Tecnologias Chave

| Layer | Tecnologia | Função |
|-------|-----------|--------|
| **WhatsApp** | Evolution API | Conexão com WhatsApp |
| **Backend** | Flask + Python 3.10+ | Webhook + Business logic |
| **Banco** | PostgreSQL | Cache persistente + usuários |
| **Tarefas** | Notion API 2.x | Fonte de verdade das tarefas |
| **NLP** | Custom (NLTK + Fuzzy) | Interpretação de linguagem natural |
| **IA** | OpenAI GPT-4o-mini | Processamento conversacional |
| **Scheduler** | APScheduler | Check-ins automáticos |
| **Memory** | Redis (opcional) | Histórico conversacional |

---

## 📊 Métricas & Qualidade

| Métrica | Valor |
|---------|-------|
| Taxa de Sucesso NLP | 85.2% (127/149 testes) |
| Intents com 100% | 5 intents |
| Confiança Média | 0.884 |
| Conversas Realistas | 100% (55/55 passos) |
| Cobertura de Testes | 252+ testes |
| Uptime Produção | 99.5% |
| Mensagens/mês | ~12.000 |

---

## 🚀 Deploy & Configuração

### Variáveis de Ambiente (principais)
```bash
# Notion
NOTION_TOKEN=secret_xxxxx
NOTION_TASKS_DB_ID=xxxxx

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://pange-evolution-api.u5qiqp.easypanel.host
EVOLUTION_API_KEY=xxxxx
EVOLUTION_INSTANCE_NAME=Pange.IA Bot

# PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/notion_pangeia

# Scheduler
SCHEDULER_ENABLED=true
TIMEZONE=America/Sao_Paulo
```

### Comandos Úteis
```bash
# Rodar localmente
python -m src.webhook.app

# Dashboard Web
python dashboard.py  # http://localhost:5000

# Testes
python tests/nlp_metrics.py
python tests/test_conversations.py

# Deploy Railway
railway link && railway deploy
```

---

## 🧠 NLP Core (normalizer.py)

**Localização:** `src/commands/normalizer.py` (845+ linhas)

**Responsabilidades:**
1. Normalização de entrada (lowercase, trim, emoji parsing)
2. Fuzzy matching contra intents conhecidos
3. Extração de parâmetros (números de tarefas, motivos, etc)
4. Ranking de confiança de intenção

**Exemplo de Fluxo:**
```
Input: "fiz 1 e 2"
  ↓
Normalize: "fiz 1 e 2"
  ↓
Fuzzy Match: "completed_multiple" (confidence: 0.92)
  ↓
Extract: tasks=[1, 2]
  ↓
Return: Intent("mark_done", tasks=[1, 2], confidence=0.92)
```

---

## 🐛 Problemas Conhecidos & Fixes

### Recentes (Novembro 2025)
- ✅ [Fixed] Erro "Ops, tive um problema" no webhook (nov 11)
- ✅ [Fixed] Check-ins não salvando respostas corretamente (nov 13)
- ✅ [Fixed] Deduplicação de mensagens (nov 12)

### Em Monitoramento
- Check-ins tardios em dias com muitas requisições
- Latência Evolution API > 2s em picos

---

## 📚 Documentação Complementar

| Arquivo | Propósito |
|---------|----------|
| `VALIDATION_REPORT.md` | Análise completa NLP (Phase 1) |
| `RANDOM_CHECKINS.md` | Sistema de check-ins variado |
| `RAILWAY_VS_SUPABASE.md` | Comparação arquitetura |
| `tests/nlp_metrics.py` | Testes de qualidade NLP |
| `tests/test_conversations.py` | 10 conversas realistas |

---

## 💡 Quick Commands para Claude Desktop

```bash
# Explorar estrutura
find /tmp/notion-pangeia/src -type f -name "*.py" | wc -l

# Entender NLP
cat /tmp/notion-pangeia/src/commands/normalizer.py

# Ver testes
python /tmp/notion-pangeia/tests/nlp_metrics.py

# Listar intents implementados
grep -r "def handle_" /tmp/notion-pangeia/src/commands
```

---

## 🎓 Conceitos-Chave para Entender o Projeto

1. **Intent-Based Architecture**: Tudo é um "intent" (ação que user quer fazer)
2. **Fuzzy Matching**: Tolera typos e variações (até 92% de similaridade)
3. **Slot-Filling**: Bot completa informações faltantes conversacionalmente
4. **Message Chunking**: Divide respostas longas para WhatsApp
5. **PostgreSQL Cache**: Tasks do Notion cached por 24h para performance

---

## 🤝 Próximos Passos Sugeridos

- [ ] Implementar suporte a sub-tarefas
- [ ] Melhorar check-ins com ML (menos perguntas repetidas)
- [ ] Adicionar integração com Google Sheets
- [ ] Expandir NLP para + idiomas
- [ ] Dashboard mobile-friendly

---

**Última Atualização:** Novembro 14, 2025
**Status:** ✅ Pronto para análise e desenvolvimento
