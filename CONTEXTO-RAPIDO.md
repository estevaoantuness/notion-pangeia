# 🚀 Contexto Rápido - Notion Pangeia Bot

**Documento para re-contextualização rápida do Claude Code**

---

## 📋 Informações Essenciais

### 🔑 Credenciais e API Keys

#### Notion
```bash
NOTION_TOKEN=[REDACTED - See .env file]
NOTION_TASKS_DB_ID=[REDACTED - See .env file]
```

#### Evolution API (Local)
```bash
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=pange-bot-secret-key-2024
EVOLUTION_INSTANCE_NAME=pangeia-bot
```

#### Docker Compose API Key
```bash
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024
```

#### Flask
```bash
FLASK_SECRET_KEY=pangeia-bot-secret-key-2025
PORT=5000
```

---

## 🐳 Docker - Evolution API

### Containers Rodando
```bash
evolution_api       - atendai/evolution-api:v2.1.1 (porta 8080)
evolution_postgres  - postgres:15-alpine
evolution_redis     - redis:7-alpine
```

### Comandos Úteis
```bash
# Ver status
docker ps | grep evolution

# Logs Evolution API
docker logs evolution_api --tail 50

# Restart
cd evolution-setup
docker-compose restart evolution-api

# Recriar do zero
docker-compose down
docker-compose up -d
```

---

## 📂 Estrutura do Projeto

```
notion-pangeia/
├── src/
│   ├── commands/         # Sistema de comandos + NLP
│   ├── webhook/          # Servidor Flask (app.py)
│   ├── notion/           # Integração Notion API
│   ├── whatsapp/         # Cliente Evolution API
│   ├── messaging/        # Humanização de mensagens
│   ├── onboarding/       # Sistema de onboarding
│   └── cache/            # Cache de tasks
├── config/
│   ├── settings.py       # Configurações centralizadas
│   ├── colaboradores.py  # 10 colaboradores
│   └── replies.yaml      # Mensagens humanizadas
├── evolution-setup/      # Scripts Docker + Evolution
├── tests/                # Suite de testes NLP (112 testes)
├── .env                  # Variáveis de ambiente
└── app.py               # Entry point para deploy
```

---

## 🧪 Testes Rápidos

### Testar Bot Offline (SEM WhatsApp)
```bash
python3 test_commands_only.py
```
**Resultado esperado:** 5/5 testes passam (Parser, Notion, Atualização, Humanização, Cache)

### Testar Integração Notion
```bash
python3 test_bot_basic.py
```

### Verificar NLP (90.2% accuracy)
```bash
python3 tests/test_normalizer.py
```

---

## 📱 Comandos do Bot

| Comando | Exemplos |
|---------|----------|
| **Listar tarefas** | "minhas tarefas", "lista", "tarefas" |
| **Marcar concluída** | "feito 3", "concluí 2", "terminei primeira" |
| **Iniciar tarefa** | "andamento 2", "fazendo 4" |
| **Bloquear** | "bloqueada 1 - sem acesso" |
| **Progresso** | "progresso", "status" |
| **Ajuda** | "ajuda", "help" |

---

## 🌐 Evolution API - Endpoints Importantes

### Health Check
```bash
curl http://localhost:8080/
```

### Listar Instâncias
```bash
curl -H "apikey: pange-bot-secret-key-2024" \
  http://localhost:8080/instance/fetchInstances | jq .
```

### Status da Conexão
```bash
curl -H "apikey: pange-bot-secret-key-2024" \
  http://localhost:8080/instance/connectionState/pangeia-bot | jq .
```

### Conectar WhatsApp (Gerar QR Code)
```bash
curl -H "apikey: pange-bot-secret-key-2024" \
  http://localhost:8080/instance/connect/pangeia-bot | jq .
```

### Manager UI
```
http://localhost:8080/manager
Senha: pange-bot-secret-key-2024
```

---

## 🔧 Problemas Comuns e Soluções

### 1. Evolution API não gera QR Code
**Solução:** Recriar instância
```bash
cd evolution-setup
./recreate-instance.sh
```

### 2. Container "unhealthy"
**Solução:** Verificar logs e reiniciar
```bash
docker logs evolution_api --tail 50
docker-compose restart evolution-api
```

### 3. Ngrok não conecta
**Solução:** Matar e recriar túnel
```bash
pkill -f ngrok
ngrok http 8080 --log=stdout > /tmp/ngrok.log 2>&1 &
sleep 5
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

### 4. Bot não responde no WhatsApp
**Checklist:**
- [ ] WhatsApp conectado? (`./check-connection.sh`)
- [ ] Webhook configurado? (ver abaixo)
- [ ] Servidor Flask rodando? (`python3 -m src.webhook.app`)
- [ ] API Keys batem? (`.env` vs `docker-compose.yml`)

---

## 🔗 Webhook Configuration

### Configurar Webhook (após conectar WhatsApp)
```bash
# Se bot rodando localmente
WEBHOOK_URL="http://localhost:5001/webhook/whatsapp"

# Se usando ngrok para bot
WEBHOOK_URL="https://seu-ngrok.ngrok-free.dev/webhook/whatsapp"

curl -X POST "http://localhost:8080/webhook/set/pangeia-bot" \
  -H "Content-Type: application/json" \
  -H "apikey: pange-bot-secret-key-2024" \
  -d "{
    \"enabled\": true,
    \"url\": \"$WEBHOOK_URL\",
    \"events\": [\"messages.upsert\"]
  }"
```

---

## 🚀 Startup Rápido

### 1. Iniciar Docker
```bash
cd evolution-setup
docker-compose up -d
```

### 2. Gerar HTTPS (ngrok)
```bash
pkill -f ngrok
ngrok http 8080 --log=stdout > /tmp/ngrok.log 2>&1 &
sleep 5
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

### 3. Acessar Manager
```bash
# URL do ngrok + /manager
# Senha: pange-bot-secret-key-2024
```

### 4. Conectar WhatsApp
- Escanear QR Code no Manager
- Aguardar status "open"

### 5. Iniciar Bot
```bash
python3 -m src.webhook.app
```

---

## 👥 Colaboradores (10 pessoas)

| Nome | WhatsApp |
|------|----------|
| Estevão Antunes | +55 41 91851256 |
| Julio Inoue | +55 11 94196-3006 |
| Arthur Pangeia | +55 11 93285-9599 |
| Leticia | +55 11 94729-8534 |
| Joaquim | +55 11 93268-8949 |
| Kevin | +55 11 97326-9851 |
| Leo Confettura | +55 11 95285-0856 |
| Rebeca Figueredo | +55 11 97576-2277 |
| Sami Monteleone | +55 11 97378-8866 |
| Saraiva | +55 11 93296-3950 |

---

## 📊 Status do Projeto

- **Versão:** 2.0 (Produção)
- **NLP Accuracy:** 90.2% (101/112 testes)
- **Linhas de Código:** ~7.120
- **Stack:** Python 3.9+, Flask, Evolution API, Notion API, PostgreSQL, Redis

---

## 🔐 Segurança

- ✅ `.env` no `.gitignore`
- ✅ API Keys nunca commitadas
- ✅ Rate limiting implementado
- ✅ Retry logic com backoff
- ✅ Logs sem dados sensíveis

---

## 📚 Documentação Completa

- `README.md` - Overview completo do projeto
- `MIGRATION.md` - Migração Twilio → Evolution API
- `NLP-SISTEMA.md` - Detalhes do sistema NLP
- `evolution-setup/README.md` - Setup da Evolution API
- `evolution-setup/STATUS.md` - Status técnico atual

---

## ⚡ Quick Reference

```bash
# Teste offline
python3 test_commands_only.py

# Status Docker
docker ps | grep evolution

# Ngrok Evolution API
ngrok http 8080

# Servidor webhook
python3 -m src.webhook.app

# Verificar conexão WhatsApp
curl -H "apikey: pange-bot-secret-key-2024" \
  http://localhost:8080/instance/connectionState/pangeia-bot
```

---

**Última atualização:** 18/10/2025
**Caminho:** `/Users/estevaoantunes/notion-pangeia/`
**Repositório:** https://github.com/estevaoantuness/notion-pangeia.git
