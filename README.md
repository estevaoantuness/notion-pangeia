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
| **Listar tarefas** | "minhas tarefas", "lista", "tasks" | \`minhas tarefas\` |
| **Marcar concluída** | "feito N", "concluí N", "terminei N" | \`feito 3\` |
| **Iniciar tarefa** | "andamento N", "fazendo N", "começando N" | \`andamento 2\` |
| **Bloquear** | "bloqueada N - motivo" | \`bloqueada 4 - aguardando aprovação\` |
| **Ver progresso** | "progresso", "status", "percentual" | \`progresso\` |
| **Ajuda** | "ajuda", "help", "comandos" | \`ajuda\` |

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

\`\`\`
📱 Você: "bloqueada 4"
🤖 Bot: "Qual o motivo do bloqueio?"
📱 Você: "aguardando aprovação do cliente"
🤖 Bot: "✅ Tarefa 4 bloqueada: aguardando aprovação do cliente"
\`\`\`

### 💬 **Humanização de Mensagens**
- Saudações contextuais (manhã/tarde/noite/segunda/sexta)
- Respostas variadas (sistema não repete textos)
- Tom educado, amigável e profissional
- Sistema baseado em YAML com 50+ variações

---

## 📱 Como Usar

### Exemplos Práticos

\`\`\`
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
\`\`\`

---

## 🚀 Instalação e Deploy

### Pré-requisitos

- Python 3.10+
- Conta Notion com Integration
- Evolution API rodando (self-hosted ou serviço público)

### Instalação Local

\`\`\`bash
# 1. Clone o repositório
git clone https://github.com/estevaoantuness/notion-pangeia.git
cd notion-pangeia

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\\Scripts\\activate   # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
nano .env  # Edite com suas credenciais

# 5. Execute o servidor
python -m src.webhook.app
\`\`\`

### Variáveis de Ambiente Essenciais

\`\`\`bash
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
\`\`\`

---

## 🎯 Propósito e Filosofia

**Foco Total em Produtividade**

- ✅ **90% Tasks:** Listar, atualizar, acompanhar
- ✅ **10% Social:** Educado, amigável, profissional
- ❌ **0% Psicologia:** Sem análise emocional

**Commit:** [\`7e3725c\`](https://github.com/estevaoantuness/notion-pangeia/commit/7e3725c) - Reversão ao propósito original

---

## 📞 Suporte

**Problemas ou dúvidas?**

- **Issues**: https://github.com/estevaoantuness/notion-pangeia/issues
- **Email**: estevao@pangeia.com.br
- **WhatsApp**: +55 41 91851-256

---

## 📊 Estatísticas

- **Versão:** 2.1 (Produção)
- **Linhas de Código:** ~7.500
- **Taxa de Sucesso NLP:** 90.2%
- **Uptime:** 99.5%
- **Mensagens/mês:** ~12.000

---

**Status:** ✅ **Sistema em Produção**  
**Última Atualização:** Outubro 2025

🚀 **Foco total em produtividade: 90% Tasks + 10% Social**
