# 🚀 Notion Pangeia - Bot WhatsApp para Gestão de Tasks

**Assistente WhatsApp focado em produtividade: gestão de tarefas direto no Notion com NLP robusto.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Evolution API](https://img.shields.io/badge/WhatsApp-Evolution%20API-25D366)](https://github.com/EvolutionAPI/evolution-api)
[![Notion API](https://img.shields.io/badge/Notion-API%202.x-000000)](https://developers.notion.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

---

## 📊 Status do Projeto

**Versão:** 2.1 - Produção
**Última Atualização:** Outubro 2025
**Cobertura NLP:** 90.2% (101/112 testes)
**Foco:** 90% Gestão de Tasks + 10% Social
**Status:** ✅ **Funcional e em Produção**

---

## 🎯 Propósito do Bot

O **Notion Pangeia** é um **assistente de produtividade** que ajuda equipes a gerenciar tarefas via WhatsApp:

### ✅ **90% - Gestão de Tasks**
- Listar tarefas pendentes
- Marcar tarefas como concluídas
- Acompanhar progresso diário
- Reportar bloqueios
- Ver estatísticas

### ✅ **10% - Interações Sociais**
- Saudações contextuais ("Bom dia!", "Boa tarde!")
- Mensagens educadas e profissionais
- Parabéns por conquistas
- Tom amigável sem exageros

### ❌ **Sem Análise Psicológica**
- Motor psicológico **desabilitado** por padrão
- Sem análise emocional ou de burnout
- Sem perguntas reflexivas profundas
- Foco 100% em produtividade

---

## ✨ Funcionalidades Principais

### 🤖 **Processamento de Linguagem Natural**
- Entende variações de comandos naturais
- Reconhece sinônimos ("feito", "concluí", "terminei")
- Converte números por extenso ("três" → 3)
- Aceita emojis como comandos (👍 = sim, ❌ = não)
- **90.2% de taxa de sucesso** em compreensão

### 📱 **Comandos Disponíveis**

| Comando | Variações | Exemplo |
|---------|-----------|---------|
| **Listar tarefas** | "minhas tarefas", "lista", "tasks" | `minhas tarefas` |
| **Marcar concluída** | "feito N", "concluí N", "terminei N" | `feito 3` |
| **Iniciar tarefa** | "andamento N", "fazendo N", "começando N" | `andamento 2` |
| **Bloquear** | "bloqueada N - motivo" | `bloqueada 4 - aguardando aprovação` |
| **Ver progresso** | "progresso", "status", "percentual" | `progresso` |
| **Ajuda** | "ajuda", "help", "comandos" | `ajuda` |

### ⏰ **Check-ins Automáticos (Simplificados)**

Check-ins diretos e objetivos ao longo do dia:

| Horário | Tipo | Mensagem |
|---------|------|----------|
| **08:00** | Metas Diárias | "☀️ Bom dia! Suas tarefas de hoje: [lista]" |
| **13:30** | Check-in Rápido | "☕ Como estão as tarefas? Algum bloqueio?" |
| **15:30** | Status | "⏰ Progresso do dia OK? Conseguindo avançar?" |
| **18:00** | Fechamento | "🌆 O que você conseguiu fazer hoje?" |
| **22:00** | Resumo Automático | "🌙 Boa noite! 📊 Resumo: 3/5 tarefas concluídas. Descanse bem! 😴" |

**Nota:** O check-in das 22h **calcula automaticamente** o progresso do dia e envia um resumo simples. Sem perguntas reflexivas.

### 🧠 **Slot-Filling Inteligente**

Bot completa informações faltantes automaticamente:

```
📱 Você: "bloqueada 4"
🤖 Bot: "Qual o motivo do bloqueio?"
📱 Você: "aguardando aprovação do cliente"
🤖 Bot: "✅ Tarefa 4 bloqueada: aguardando aprovação do cliente"
```

### 💬 **Humanização de Mensagens**
- Saudações contextuais (manhã/tarde/noite/segunda/sexta)
- Respostas variadas (sistema não repete textos)
- Tom educado, amigável e profissional
- Sistema baseado em YAML com 50+ variações

---

## 🛠️ Arquitetura Técnica

### Stack Tecnológica

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  WhatsApp ←→ Evolution API ←→ Flask Webhook        │
│                                  ↓                  │
│                          NLP Processor              │
│                                  ↓                  │
│                          Command Handler            │
│                                  ↓                  │
│                          Notion API                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Componentes:**
- **Python 3.10+** - Linguagem principal
- **Flask 3.0** - Servidor webhook
- **Evolution API** - Ponte WhatsApp (self-hosted, gratuito)
- **Notion API 2.x** - Gerenciamento de databases
- **APScheduler** - Jobs automáticos (check-ins)

### Estrutura de Diretórios

```
notion-pangeia/
├── config/
│   ├── settings.py              # Configurações centralizadas
│   ├── colaboradores.py         # Mapeamento de colaboradores
│   ├── checkin_schedule.py      # Horários dos check-ins
│   ├── nlp/
│   │   └── intents.pt-BR.yaml  # Banco de intenções NLP
│   └── replies.yaml            # Templates de mensagens
│
├── src/
│   ├── webhook/                 # Servidor Flask
│   │   └── app.py              # Webhook principal + scheduler
│   │
│   ├── commands/                # Sistema de comandos
│   │   ├── processor.py        # Orquestração de comandos
│   │   ├── normalizer.py       # Motor NLP (90.2% accuracy)
│   │   ├── handlers.py         # Handlers específicos
│   │   └── parser.py           # Parse de mensagens
│   │
│   ├── whatsapp/                # Integração Evolution API
│   │   ├── client.py           # Cliente REST com retry
│   │   ├── sender.py           # Envio de mensagens
│   │   └── formatter.py        # Formatação de números
│   │
│   ├── notion/                  # Integração Notion
│   │   ├── client.py           # Cliente com rate limiting
│   │   ├── tasks.py            # Gerenciador de tasks
│   │   ├── updater.py          # Atualização de status
│   │   └── users.py            # Gerenciamento de usuários
│   │
│   ├── messaging/               # Humanização
│   │   ├── humanizer.py        # Variações de mensagens
│   │   ├── formatter.py        # Formatação de listas
│   │   └── templates.py        # Templates de resposta
│   │
│   ├── scheduler/               # Jobs automáticos
│   │   └── scheduler.py        # Setup de jobs + check-ins
│   │
│   └── cache/                   # Sistema de cache
│       └── task_mapper.py      # Mapeamento tarefa ↔ índice
│
├── tests/
│   └── test_normalizer.py      # 112 testes NLP
│
├── app.py                       # Entry point para deploy
├── requirements.txt             # Dependências Python
├── .env.example                 # Template de variáveis
└── README.md                    # Este arquivo
```

---

## 🚀 Instalação e Deploy

### Pré-requisitos

- Python 3.10+
- Conta Notion com Integration
- Evolution API rodando (self-hosted ou serviço público)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/estevaoantuness/notion-pangeia.git
cd notion-pangeia

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
nano .env  # Edite com suas credenciais

# 5. Execute o servidor
python -m src.webhook.app
```

### Variáveis de Ambiente Essenciais

```bash
# Notion
NOTION_TOKEN=secret_xxxxx
NOTION_TASKS_DB_ID=xxxxx

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua_chave_aqui
EVOLUTION_INSTANCE_NAME=Pange.IA Bot

# Flask
PORT=5000
FLASK_SECRET_KEY=chave-aleatoria-segura

# Scheduler (Check-ins)
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo

# Motor Psicológico (DESABILITADO por padrão)
ENABLE_PSYCHOLOGY=false
ENABLE_MESSAGE_CHUNKING=true
ENABLE_DEDUPLICATION=true
```

---

## 📱 Como Usar

### Exemplos Práticos

```
📱 Você: "oi"
🤖 Bot: "Oi! 👋 Como posso ajudar?
• minhas tarefas
• progresso
• ajuda"

📱 Você: "minhas tarefas"
🤖 Bot: "📋 Suas tarefas de hoje:

1. [🔵 Fazer] Implementar login OAuth
2. [🟢 Andamento] Revisar PRs pendentes
3. [🔴 Bloqueada] Deploy em produção

Progresso: 0/3 concluídas (0%)"

📱 Você: "andamento 1"
🤖 Bot: "🔄 Boa! Tarefa 1 está rodando.

'Implementar login OAuth'

Quando terminar: 'feito 1'"

📱 Você: "feito 1"
🤖 Bot: "✅ Tarefa 1 marcada como concluída!

'Implementar login OAuth' ✓

Progresso atualizado: 0% → 33%
Continue assim! 🚀"

📱 Você: "progresso"
🤖 Bot: "📊 Progresso do dia: 33%

✅ 1 de 3 tarefas concluídas

Você está começando bem! Continue assim. 💪"
```

---

## 🔧 Configuração de Colaboradores

Adicione ou edite colaboradores em `config/colaboradores.py`:

```python
COLABORADORES: Dict[str, Dict[str, any]] = {
    "Seu Nome": {
        "telefone": "+5511999999999",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None  # Preenchido automaticamente
    }
}
```

---

## 🧪 Testes

### Suite de Testes NLP

**112 testes automatizados** cobrindo:
- Normalização de texto
- Equivalência de comandos
- Confirmações (emojis)
- Saudações e smalltalk
- Comandos de tarefas
- Slot-filling

```bash
# Rodar todos os testes
python3 tests/test_normalizer.py

# Resultado esperado:
# ✅ 101/112 testes passaram (90.2%)
```

---

## 📊 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check do serviço |
| `/scheduler/jobs` | GET | Lista jobs agendados |
| `/scheduler/run/<job_id>` | POST | Executa job manualmente |
| `/webhook/whatsapp` | POST | Webhook principal (Evolution API) |
| `/webhook/whatsapp/status` | POST | Status de mensagens |

---

## 🔒 Segurança e Boas Práticas

### Implementado

✅ **Credenciais:**
- `.env` no `.gitignore`
- Variáveis de ambiente nunca commitadas
- API Keys rotacionáveis

✅ **Rate Limiting:**
- Notion API: 3 requests/segundo
- Evolution API: retry com backoff exponencial
- Cache para reduzir chamadas

✅ **Validações:**
- Números de telefone validados
- API Key verificada em webhooks
- Mensagens do próprio bot ignoradas
- Inputs sanitizados antes de enviar ao Notion

✅ **Logs:**
- Logging estruturado
- Sem exposição de dados sensíveis
- Rotação automática de logs

---

## 📈 Roadmap

### ✅ Concluído (v2.1)
- [x] Bot focado em gestão de tasks (90%)
- [x] Motor psicológico desabilitado por padrão
- [x] Check-ins simplificados
- [x] Resumo automático às 22h (sem perguntas)
- [x] Sistema NLP robusto (90.2% accuracy)
- [x] Slot-filling inteligente
- [x] Humanização de mensagens
- [x] Cache de tasks
- [x] Webhooks Flask

### 🔄 Planejado (v2.2)
- [ ] Dashboard web de analytics
- [ ] Relatórios semanais automáticos
- [ ] Sistema de priorização de tarefas
- [ ] Notificações de deadlines
- [ ] Comandos de voz (transcrição)

### 🎯 Futuro (v3.0)
- [ ] Multi-idioma (EN, ES)
- [ ] Integração com Jira/Linear
- [ ] Time tracking automático
- [ ] Análise de produtividade (BI)

---

## 🆘 Troubleshooting

### Bot não responde

**Possíveis causas:**
1. Webhook não configurado na Evolution API
2. API Keys diferentes entre Evolution API e Bot
3. Serviço offline

**Solução:**
```bash
# 1. Verificar health
curl https://seu-bot.com/health

# 2. Verificar webhook na Evolution API
# Acesse: Manager → Instância → Webhook → URL correta?

# 3. Ver logs do bot
tail -f logs/pangeia_bot.log
```

### Evolution API retorna 404

**Causa:** Nome da instância incorreto

**Solução:**
- Verifique o nome exato da instância na Evolution API
- Atualize `EVOLUTION_INSTANCE_NAME` no `.env`
- Reinicie o bot

---

## 🤝 Contribuindo

### Como contribuir

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Add: nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Áreas que precisam de ajuda

- [ ] Melhorar cobertura NLP (90% → 95%)
- [ ] Adicionar mais variações de mensagens
- [ ] Testes unitários (coverage atual: ~60%)
- [ ] Documentação de código (docstrings)

---

## 📄 Licença

**Propriedade da Pange.iA** - Todos os direitos reservados.

Uso interno e privado. Não redistribuir sem permissão.

---

## 📞 Suporte

**Problemas ou dúvidas?**

- **Issues**: https://github.com/estevaoantuness/notion-pangeia/issues
- **Email**: estevao@pangeia.com.br
- **WhatsApp**: +55 41 91851-256

---

## 🎉 Créditos

Desenvolvido com ❤️ pela equipe **Pange.iA**

**Tech Stack:**
- [Evolution API](https://github.com/EvolutionAPI/evolution-api) - WhatsApp Integration
- [Notion API](https://developers.notion.com/) - Task Management
- [Flask](https://flask.palletsprojects.com/) - Web Framework
- [APScheduler](https://apscheduler.readthedocs.io/) - Job Scheduling

---

## 📊 Estatísticas do Projeto

- **Iniciado em:** Janeiro 2025
- **Versão Atual:** 2.1 (Produção)
- **Linhas de Código:** ~7.500
- **Commits:** 155+
- **Colaboradores:** 10 pessoas
- **Mensagens Processadas:** ~12.000/mês
- **Taxa de Sucesso NLP:** 90.2%
- **Uptime:** 99.5%

---

**Status:** ✅ **Sistema em Produção**
**Última Atualização:** Outubro 2025
**Commit:** [`7e3725c`](https://github.com/estevaoantuness/notion-pangeia/commit/7e3725c) - Reversão ao propósito original

🚀 **Foco total em produtividade: 90% Tasks + 10% Social**
