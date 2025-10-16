# 🚀 Notion Pangeia - Sistema Bidirecional WhatsApp ↔ Notion

Sistema completo de automação para gestão de tasks via WhatsApp, integrado com Notion.

## 📋 Funcionalidades

### ✅ Já Implementado (ETAPA 1)
- Estrutura completa do projeto
- Cliente Notion com rate limiting
- Cliente Twilio/WhatsApp com retry logic
- Sistema de configurações centralizado
- Mapeamento de 10 colaboradores
- Sistema de check-ins (4 horários configurados)
- Logs automáticos

### 🔄 Em Desenvolvimento (Próximas Etapas)
- Sistema de leitura de tasks
- Comandos bidirecionais (feito, andamento, bloqueada)
- Envio automático de metas diárias (8h)
- Check-ins estratégicos automáticos
- Criação guiada de tasks via WhatsApp
- Postagem automática em grupo

## 🛠️ Stack Tecnológica

- **Python 3.10+**
- **Flask** - Webhook para receber mensagens
- **Notion API** - Integração com databases
- **Twilio API** - Envio/recebimento WhatsApp
- **APScheduler** - Agendamento de tarefas
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📁 Estrutura do Projeto

```
notion-pangeia/
├── config/                    # Configurações
│   ├── settings.py           # Configurações gerais
│   ├── colaboradores.py      # Mapeamento de colaboradores
│   └── checkin_schedule.py   # Horários dos check-ins
├── src/
│   ├── notion/              # Integração Notion
│   │   ├── client.py        # Cliente com rate limiting ✅
│   │   ├── tasks.py         # Gerenciador de tasks
│   │   ├── updater.py       # Atualização de tasks
│   │   └── insights.py      # Salvamento de insights
│   ├── whatsapp/            # Integração WhatsApp
│   │   ├── client.py        # Cliente Twilio ✅
│   │   ├── sender.py        # Envio de mensagens
│   │   ├── receiver.py      # Recebimento via webhook
│   │   └── group_poster.py  # Postagem em grupos
│   ├── commands/            # Sistema de comandos
│   │   ├── processor.py     # Processador de comandos
│   │   ├── parser.py        # Parse de mensagens
│   │   └── handlers.py      # Handlers específicos
│   ├── checkins/            # Sistema de check-ins
│   │   ├── manager.py       # Gerenciador de check-ins
│   │   ├── questions.py     # Perguntas por horário
│   │   └── collector.py     # Coleta de respostas
│   ├── task_creation/       # Criação guiada de tasks
│   │   ├── framework_handler.py
│   │   └── title_generator.py
│   ├── messaging/           # Formatação de mensagens
│   │   ├── formatter.py
│   │   └── templates.py
│   ├── cache/               # Sistema de cache
│   │   ├── task_mapper.py
│   │   └── checkin_state.py
│   └── scheduler/           # Agendamento
│       └── jobs.py
├── tests/                   # Testes automatizados
├── logs/                    # Logs automáticos
├── app.py                   # Flask app (webhook)
├── main.py                  # Orquestrador principal
├── requirements.txt         # Dependências ✅
├── Procfile                 # Deploy Heroku/Railway ✅
└── .env                     # Credenciais (gitignored) ✅
```

## 🚀 Instalação e Configuração

### Pré-requisitos

1. **Python 3.10+**
2. **Conta Notion** com Integration criada
3. **Conta Twilio** com WhatsApp Sandbox ativo

### Passo 1: Clone e Instale Dependências

```bash
# Clone o repositório
git clone <repo-url>
cd notion-pangeia

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Mac/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
```

### Passo 2: Configure Credenciais

1. **Notion Integration:**
   - Acesse: https://www.notion.so/my-integrations
   - Crie uma "New integration"
   - Copie o token (começa com `secret_...`)
   - Conecte a integration à sua database de Tasks

2. **Twilio WhatsApp:**
   - Acesse: https://console.twilio.com
   - Copie seu Account SID e Auth Token
   - Ative o WhatsApp Sandbox em Messaging → Try it out

3. **Configure o .env:**

O arquivo `.env` já foi criado com suas credenciais.

**⚠️ IMPORTANTE:** Você precisa adicionar o `TWILIO_AUTH_TOKEN`:

```bash
# Edite o arquivo .env e adicione o token:
TWILIO_AUTH_TOKEN=seu_token_aqui
```

### Passo 3: Teste as Conexões

```bash
# Teste conexão com Notion e Twilio
python -c "
from src.notion.client import NotionClient
from src.whatsapp.client import WhatsAppClient

# Teste Notion
notion = NotionClient()
success, msg = notion.test_connection()
print(f'Notion: {msg}')

# Teste Twilio
whatsapp = WhatsAppClient()
success, msg = whatsapp.test_connection()
print(f'Twilio: {msg}')
"
```

Se ambos retornarem mensagens de sucesso, está tudo pronto!

## 📊 Horários dos Check-ins

O sistema faz 4 check-ins diários:

| Horário | Nome | Objetivo |
|---------|------|----------|
| 08:00 | Metas Diárias | Enviar tasks do dia |
| 13:30 | Planejamento Profundo | Entender estratégia |
| 15:30 | Status e Adaptação | Monitorar progresso |
| 18:00 | Fechamento | Capturar aprendizados |
| 22:00 | Reflexão Noturna | Auto-avaliação (3 Perguntas Brutais) |

## 👥 Colaboradores Configurados

10 colaboradores já mapeados em `config/colaboradores.py`:

- Estevao Antunes (CEO)
- Julio Inoue (Desenvolvedor)
- Arthur Pangeia (Desenvolvedor)
- Leticia (Designer)
- Joaquim (Desenvolvedor)
- Kevin (Desenvolvedor)
- Leo Confettura (Desenvolvedor)
- Rebeca Figueredo (Product Manager)
- Sami Monteleone (Desenvolvedor)
- Saraiva (Desenvolvedor)

## 🧪 Testes

```bash
# Rodar todos os testes
pytest tests/

# Rodar testes específicos
pytest tests/test_notion.py
pytest tests/test_whatsapp.py
```

## 📝 Logs

Todos os logs são salvos automaticamente em `logs/pangeia_bot.log`.

Nível de log configurável via variável `LOG_LEVEL` no `.env`.

## 🔒 Segurança

- ✅ Arquivo `.env` está no `.gitignore`
- ✅ Credenciais nunca são commitadas
- ✅ Rate limiting para evitar ban
- ✅ Retry logic para requisições falhas
- ✅ Validação de números de telefone

## 🚧 Roadmap

### ETAPA 1: Fundação ✅ CONCLUÍDA
- [x] Estrutura de diretórios
- [x] Cliente Notion
- [x] Cliente WhatsApp
- [x] Configurações centralizadas
- [x] Teste de conexões

### ETAPA 2: Sistema de Tasks (Leitura)
- [ ] Buscar tasks por colaborador
- [ ] Formatação de mensagens
- [ ] Comando "minhas tarefas"

### ETAPA 3: Sistema de Tasks (Escrita)
- [ ] Atualizar status no Notion
- [ ] Parser de comandos
- [ ] Flask webhook

### ETAPA 4: Envio Automático
- [ ] Scheduler (APScheduler)
- [ ] Job de envio diário (8h)
- [ ] Orquestrador principal

### ETAPA 5: Check-ins Estratégicos
- [ ] Gerenciador de check-ins
- [ ] Fluxo conversacional
- [ ] Salvamento no Notion

### ETAPA 6: Criação de Tasks
- [ ] Frameworks (DEV + Padrão)
- [ ] Postagem em grupo
- [ ] Gerador de títulos

### ETAPA 7: Deploy e Polish
- [ ] Testes completos
- [ ] Deploy Railway/Heroku
- [ ] Documentação final

## 🤝 Contribuindo

Este é um projeto interno da Pange.iA. Contribuições são bem-vindas!

## 📄 Licença

Propriedade da Pange.iA - Todos os direitos reservados.

---

**Status Atual:** ETAPA 1 CONCLUÍDA ✅

**Próximo Passo:** ETAPA 2 - Sistema de Tasks (Leitura)

**Última Atualização:** 2025-01-15
