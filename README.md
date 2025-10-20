# 🚀 Notion Pangeia - Bot WhatsApp Inteligente para Gestão de Tasks

**Sistema completo de automação WhatsApp ↔ Notion com NLP robusto e check-ins automáticos.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Evolution API](https://img.shields.io/badge/WhatsApp-Evolution%20API-25D366)](https://github.com/EvolutionAPI/evolution-api)
[![Notion API](https://img.shields.io/badge/Notion-API%202.x-000000)](https://developers.notion.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

---

## 📊 Status do Projeto

**Versão:** 2.1 - Produção (Focado em Gestão de Tarefas)
**Última Atualização:** Outubro 2025
**Cobertura NLP:** 90.2% (101/112 testes)
**Foco:** Gestão de Tarefas (Task Management)
**Status:** ✅ **Totalmente Funcional e em Produção**

---

## 🎯 O que o Pangeia Faz

O **Notion Pangeia** é um **sistema de gestão de tarefas via WhatsApp** que conecta sua equipe ao Notion de forma inteligente:

### 🎯 **Foco Principal: Gestão de Tarefas**
Gerencie suas tarefas do Notion diretamente pelo WhatsApp com comandos naturais e intuitivos.

### ✨ Funcionalidades Principais

#### 🤖 **Processamento de Linguagem Natural**
- Entende variações de comandos naturais
- Reconhece sinônimos ("feito", "concluí", "terminei")
- Converte números por extenso ("três" → 3)
- Aceita emojis como comandos (👍 = sim, ❌ = não)
- **90.2% de taxa de sucesso** em compreensão

#### 📱 **Gestão de Tasks via WhatsApp**
- **Listar tarefas**: "minhas tarefas", "lista", "ver tarefas"
- **Marcar como feita**: "feito 3", "concluí a segunda"
- **Iniciar tarefa**: "andamento 2", "fazendo 4"
- **Bloquear tarefa**: "bloqueada 1 - sem acesso"
- **Ver progresso**: "progresso", "status do dia"

#### ⏰ **Check-ins Automáticos**
5 horários estratégicos configurados:
- **08:00** - Metas Diárias (envia tasks do dia)
- **13:30** - Planejamento Profundo
- **15:30** - Status e Adaptação
- **18:00** - Fechamento do Dia
- **22:00** - Reflexão Noturna (3 Perguntas Brutais)

#### 🧠 **Slot-Filling Inteligente**
Bot completa informações faltantes:
```
Usuário: "bloqueada 4"
Bot: "Qual o motivo do bloqueio?"
Usuário: "sem acesso ao servidor"
Bot: "✅ Tarefa 4 bloqueada: sem acesso ao servidor"
```

#### 💬 **Humanização de Mensagens**
- Saudações contextuais (manhã/tarde/noite)
- Respostas variadas (não repete textos)
- Tom amigável e profissional
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
- **PostgreSQL** - Persistência (onboarding, cache)
- **Redis** - Cache de sessões

### Estrutura de Diretórios

```
notion-pangeia/
├── config/
│   ├── settings.py              # Configurações centralizadas
│   ├── colaboradores.py         # Mapeamento de 10 colaboradores
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
│   ├── onboarding/              # Sistema de onboarding
│   │   ├── manager.py          # Fluxo de boas-vindas
│   │   └── state.py            # Persistência de estado
│   │
│   ├── scheduler/               # Jobs automáticos
│   │   ├── scheduler.py        # Setup de jobs
│   │   └── jobs.py             # Definição de tarefas
│   │
│   └── cache/                   # Sistema de cache
│       └── task_mapper.py      # Mapeamento tarefa ↔ índice
│
├── tests/
│   ├── test_normalizer.py      # 112 testes NLP
│   └── test_onboarding_improvements.py
│
├── evolution-setup/             # Scripts de setup Evolution API
├── logs/                        # Logs automáticos
├── app.py                       # Entry point para deploy
├── requirements.txt             # Dependências Python
├── Procfile                     # Deploy Render/Railway
├── .env.example                 # Template de variáveis
└── README.md                    # Este arquivo
```

---

## 🚀 Instalação e Deploy

### Opção 1: Deploy Automático no Render (Recomendado)

**Grátis e pronto em 10 minutos!**

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/estevaoantuness/notion-pangeia.git
   cd notion-pangeia
   ```

2. **Prepare credenciais Notion:**
   - Acesse: https://www.notion.so/my-integrations
   - Crie nova integration
   - Copie o token (começa com `secret_`)
   - Conecte ao seu database de Tasks

3. **Execute o script de deploy:**
   ```bash
   python3 render_deploy_pangeia.py
   ```

   O script irá:
   - ✅ Criar PostgreSQL (free tier)
   - ✅ Criar Redis (free tier)
   - ✅ Criar Evolution API (WhatsApp)
   - ✅ Criar Bot Python (seu código)
   - ✅ Configurar todas as variáveis de ambiente

4. **Configure webhook e conecte WhatsApp:**
   - Acesse: `https://pangeia-evolution-api.onrender.com/manager`
   - Login com API Key
   - Crie instância "pangeia"
   - Escaneie QR Code
   - Configure webhook: `https://notion-pangeia-bot.onrender.com/webhook/whatsapp`

**📖 Guia completo de deploy:** [GUIA_DEPLOY_FINAL.md](GUIA_DEPLOY_FINAL.md)

---

### Opção 2: Instalação Local (Desenvolvimento)

#### Pré-requisitos
- Python 3.10+
- Conta Notion com Integration
- Evolution API rodando (ou use serviço público)

#### Passo a Passo

```bash
# 1. Clone e entre no diretório
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

#### Variáveis de Ambiente Necessárias

```bash
# Notion
NOTION_TOKEN=secret_xxxxx
NOTION_TASKS_DB_ID=xxxxx
NOTION_USERS_DB_ID=xxxxx  # Opcional

# Evolution API
EVOLUTION_API_URL=https://sua-api.com
EVOLUTION_API_KEY=sua_chave
EVOLUTION_INSTANCE_NAME=pangeia

# Flask
FLASK_SECRET_KEY=chave-aleatoria
PORT=5000

# Scheduler
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo

# App
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 📱 Como Usar

### Comandos Disponíveis

#### Gestão de Tarefas

| Comando | Variações | Exemplo |
|---------|-----------|---------|
| **Listar tarefas** | "minhas tarefas", "lista", "ver tarefas" | "lista" |
| **Marcar concluída** | "feito N", "concluí N", "terminei N" | "feito 3" |
| **Iniciar tarefa** | "andamento N", "fazendo N", "iniciei N" | "andamento 2" |
| **Bloquear** | "bloqueada N - motivo" | "bloqueada 4 - sem acesso" |
| **Ver progresso** | "progresso", "status", "andamento do dia" | "progresso" |
| **Ajuda** | "ajuda", "help", "comandos" | "ajuda" |

#### Confirmações e Interações

| Tipo | Variações |
|------|-----------|
| **Sim** | "sim", "s", "👍", "✅", "ok" |
| **Não** | "não", "n", "❌", "nao" |
| **Saudação** | "oi", "olá", "bom dia", "boa tarde" |
| **Agradecimento** | "obrigado", "valeu", "thanks" |

### Exemplos Reais de Uso

```
📱 Usuário: "oi"
🤖 Bot: "Oi Estevão! 👋 Como posso ajudar?
• minhas tarefas
• progresso
• ajuda"

📱 Usuário: "minhas tarefas"
🤖 Bot: "📋 Suas tarefas de hoje:

1. [🔵 Fazer] Implementar login OAuth
2. [🟢 Andamento] Revisar PRs pendentes
3. [🔴 Bloqueada] Deploy em produção

Progresso: 1/3 concluídas (33%)"

📱 Usuário: "feito 1"
🤖 Bot: "✅ Boa! 'Implementar login OAuth' marcada como concluída!"

📱 Usuário: "bloqueada 3"
🤖 Bot: "Entendi que a tarefa 3 está bloqueada. Qual o motivo?"

📱 Usuário: "aguardando aprovação do cliente"
🤖 Bot: "✅ Tarefa 3 bloqueada: aguardando aprovação do cliente"
```

---

## 👥 Colaboradores

10 colaboradores pré-configurados em `config/colaboradores.py`:

| Nome | Função | WhatsApp |
|------|--------|----------|
| Estevão Antunes | CEO | +55 41 91851256 |
| Julio Inoue | Desenvolvedor | +55 11 94196-3006 |
| Arthur Pangeia | Desenvolvedor | +55 11 93285-9599 |
| Leticia | Designer | +55 11 94729-8534 |
| Joaquim | Desenvolvedor | +55 11 93268-8949 |
| Kevin | Desenvolvedor | +55 11 97326-9851 |
| Leo Confettura | Desenvolvedor | +55 11 95285-0856 |
| Rebeca Figueredo | Product Manager | +55 11 97576-2277 |
| Sami Monteleone | Desenvolvedor | +55 11 97378-8866 |
| Saraiva | Desenvolvedor | +55 11 93296-3950 |

**Adicionar novos colaboradores:** Edite `config/colaboradores.py`

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

### Testar Localmente

```bash
# 1. Iniciar servidor
python -m src.webhook.app

# 2. Health check
curl http://localhost:5001/health

# 3. Listar jobs agendados
curl http://localhost:5001/scheduler/jobs

# 4. Simular webhook
curl -X POST http://localhost:5001/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -H "apikey: SUA_API_KEY" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": false},
      "message": {"conversation": "minhas tarefas"},
      "pushName": "Teste"
    }
  }'
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

## 📈 Roadmap e Melhorias Futuras

### ✅ Concluído (v2.1) - **Foco em Gestão de Tarefas**
- [x] Migração Twilio → Evolution API (WhatsApp gratuito)
- [x] Sistema NLP robusto (90.2% accuracy)
- [x] Comandos naturais para gestão de tarefas
- [x] Listar, iniciar, concluir e bloquear tarefas
- [x] 5 check-ins automáticos diários
- [x] Sistema de onboarding
- [x] Cache de tasks para performance
- [x] Slot-filling inteligente
- [x] Webhooks Flask otimizados

### 🔄 Próximas Melhorias (v2.2) - **Gestão de Tarefas Avançada**
- [ ] Criar tarefas via WhatsApp ("criar tarefa: nome da tarefa")
- [ ] Definir prazos ("prazo tarefa 3: amanhã")
- [ ] Atribuir tarefas a colaboradores
- [ ] Filtrar tarefas por status/prioridade
- [ ] Relatórios de produtividade semanal
- [ ] Notificações de deadlines próximos

### 🎯 Planejado (v3.0) - **Expansão do Sistema**
- [ ] Integração com Jira/Linear/Asana
- [ ] Time tracking automático
- [ ] Análise de produtividade (BI)
- [ ] Dashboard web de analytics
- [ ] Multi-idioma (EN, ES)
- [ ] Comandos de voz (transcrição)

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

✅ **Resiliência:**
- Retry logic em todas as APIs
- Fallbacks para erros
- Health checks configurados

---

## 📚 Documentação Adicional

- **[MIGRATION.md](MIGRATION.md)** - Detalhes da migração Twilio → Evolution API
- **[NLP-SISTEMA.md](NLP-SISTEMA.md)** - Sistema NLP completo (90.2% accuracy)
- **[WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)** - Setup de webhooks
- **[USERS_DB_SETUP.md](USERS_DB_SETUP.md)** - Configuração do database de usuários
- **[GUIA_DEPLOY_FINAL.md](GUIA_DEPLOY_FINAL.md)** - Deploy completo no Render

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
curl https://seu-bot.onrender.com/health

# 2. Ver logs
# Acesse: Dashboard Render → notion-pangeia-bot → Logs

# 3. Verificar webhook
# Evolution Manager → Instância → Webhook → URL correta?
```

### QR Code não aparece

**Solução:**
1. Acesse: `https://sua-evolution-api.com/manager`
2. Delete a instância existente
3. Crie nova instância "pangeia"
4. QR Code deve aparecer em 10 segundos

### Scheduler não executa

**Verificar:**
```bash
curl https://seu-bot.onrender.com/scheduler/jobs
```

**Se vazio:**
- Verificar variáveis de ambiente (horários configurados?)
- Reiniciar serviço no Render

### Evolution API retorna 401

**Causa:** API Keys diferentes

**Solução:**
1. Evolution API → Environment → `AUTHENTICATION_API_KEY`
2. Bot Python → Environment → `EVOLUTION_API_KEY`
3. **Ambas devem ser IGUAIS**

---

## 🤝 Contribuindo

Este é um projeto interno da **Pange.iA**, mas contribuições são bem-vindas!

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
- [ ] Internacionalização (i18n)

---

## 📄 Licença

**Propriedade da Pange.iA** - Todos os direitos reservados.

Uso interno e privado. Não redistribuir sem permissão.

---

## 📞 Suporte e Contato

**Problemas ou dúvidas?**

- **Issues**: https://github.com/estevaoantuness/notion-pangeia/issues
- **Email**: estevao@pangeia.com.br
- **WhatsApp**: +55 41 91851-256

---

## 🎉 Agradecimentos

Desenvolvido com ❤️ pela equipe **Pange.iA**

**Tech Stack:**
- Evolution API Community
- Notion API Team
- Flask Contributors
- Python Community

---

## 📊 Estatísticas do Projeto

- **Iniciado em:** Janeiro 2025
- **Versão Atual:** 2.1 (Produção - Foco em Gestão de Tarefas)
- **Foco Principal:** Task Management via WhatsApp
- **Colaboradores:** 10 pessoas
- **Uptime:** 99.5% (Render free tier)
- **Mensagens Processadas:** ~10.000/mês
- **Taxa de Sucesso NLP:** 90.2%

---

**Status:** ✅ **Sistema em Produção - Focado em Gestão de Tarefas**
**Última Atualização:** Outubro 2025
**Próxima Release:** v2.2 - Criação de Tarefas via WhatsApp (Novembro 2025)

🚀 **Deploy agora:** Execute `python3 render_deploy_pangeia.py`
