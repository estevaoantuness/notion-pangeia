# 🚀 Deploy COMPLETO do Notion Pangeia no Render.com

## 📦 O QUE VAMOS FAZER

Este guia vai te ajudar a fazer deploy de **TODO o sistema**:
1. **PostgreSQL** (banco de dados da Evolution API)
2. **Redis** (cache da Evolution API)
3. **Evolution API** (servidor WhatsApp)
4. **Bot Python Pangeia** (seu bot de tarefas Notion)

**Tempo total:** 15-20 minutos
**Custo:** R$ 0,00 (100% gratuito!)

---

## ✅ PRÉ-REQUISITOS

Antes de começar, você precisa ter:

- [ ] Conta no Render.com (vamos criar agora!)
- [ ] Token do Notion (Integration Token)
- [ ] ID do Database de Tarefas do Notion
- [ ] ID do Database de Usuários do Notion (opcional, para onboarding)
- [ ] Repositório do projeto no GitHub (vamos configurar)

---

## 🎯 ARQUITETURA FINAL

```
┌──────────────────┐
│  Evolution API   │ ← Container Docker (WhatsApp)
│  (Web Service)   │
└────────┬─────────┘
         │
         ├─────► PostgreSQL (dados)
         ├─────► Redis (cache)
         │
         │
┌────────▼─────────┐
│   Bot Pangeia    │ ← Aplicação Python
│  (Web Service)   │
└──────────────────┘
         │
         └─────► Notion API
```

---

## 📋 PASSO A PASSO

### **ETAPA 1: Preparar o Repositório GitHub**

#### 1.1. Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `notion-pangeia` (ou outro nome de sua preferência)
3. Visibilidade: **Private** (recomendado, contém configurações)
4. Clique em **"Create repository"**

#### 1.2. Fazer push do código

```bash
cd /Users/estevaoantunes/notion-pangeia

# Se já tem git configurado, adicione o remote:
git remote add origin https://github.com/SEU-USUARIO/notion-pangeia.git

# Adicione e commite todos os arquivos (exceto .env)
git add .
git commit -m "Initial commit - Notion Pangeia Bot"

# Faça push
git push -u origin main
```

**⚠️ IMPORTANTE:** O arquivo `.env` não será enviado (já está no `.gitignore`). Vamos configurar as variáveis direto no Render!

---

### **ETAPA 2: Criar Conta no Render**

1. Acesse: https://render.com/
2. Clique em **"Get Started"**
3. Escolha **"Sign in with GitHub"** (mais fácil para deploy!)
4. Autorize o Render a acessar seus repositórios
5. **NÃO PRECISA DE CARTÃO!** ✅

---

### **ETAPA 3: Criar PostgreSQL Database**

1. No dashboard do Render (https://dashboard.render.com/), clique em **"New +"**
2. Selecione **"PostgreSQL"**
3. Preencha:
   - **Name:** `pangeia-postgres`
   - **Database:** `evolution_db`
   - **User:** `evolution_user`
   - **Region:** Oregon (us-west) ou outra região
   - **PostgreSQL Version:** 16 (mais recente)
   - **Plan:** **FREE** ✅
4. Clique em **"Create Database"**
5. **Aguarde 2-3 minutos** para provisionar

**📝 COPIE E GUARDE:**
- Vá em **"Info"** (menu lateral)
- Copie a **"Internal Database URL"**
  - Exemplo: `postgresql://evolution_user:abc123@dpg-xxxxx-internal/evolution_db`

---

### **ETAPA 4: Criar Redis Instance**

1. No dashboard, clique em **"New +"**
2. Selecione **"Redis"**
3. Preencha:
   - **Name:** `pangeia-redis`
   - **Region:** **Mesma do PostgreSQL!** (importante para latência)
   - **Plan:** **FREE** ✅
   - **Maxmemory Policy:** `allkeys-lru` (recomendado)
4. Clique em **"Create Redis"**
5. **Aguarde 1-2 minutos**

**📝 COPIE E GUARDE:**
- Vá em **"Info"** (menu lateral)
- Copie a **"Internal Redis URL"**
  - Exemplo: `redis://red-xxxxx-internal:6379`

---

### **ETAPA 5: Criar Web Service - Evolution API**

#### 5.1. Criar o serviço

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Escolha **"Deploy an existing image from a registry"**
4. Preencha:
   - **Image URL:** `atendai/evolution-api:v2.1.1`
   - **Name:** `pangeia-evolution-api`
   - **Region:** **Mesma do PostgreSQL e Redis!**
   - **Plan:** **FREE** ✅

#### 5.2. Configurar Variáveis de Ambiente

Role até **"Environment Variables"** e clique em **"Add Environment Variable"**.

Cole TODAS essas variáveis (ajuste os valores conforme instruções abaixo):

```bash
# URL pública do servidor (vamos atualizar depois!)
SERVER_URL=https://pangeia-evolution-api.onrender.com

# Chave de autenticação (IMPORTANTE: use uma chave forte!)
AUTHENTICATION_API_KEY=pange-bot-secret-key-2024-MUDE-ISSO

# Configuração de banco de dados
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=COLE_AQUI_A_INTERNAL_DATABASE_URL?schema=public
DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=false
DATABASE_SAVE_MESSAGE_UPDATE=false
DATABASE_SAVE_DATA_CONTACTS=false
DATABASE_SAVE_DATA_CHATS=false

# Configuração de cache Redis
CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=COLE_AQUI_A_INTERNAL_REDIS_URL
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=false

# Logs
LOG_LEVEL=ERROR,WARN,INFO
LOG_COLOR=true

# CORS
CORS_ORIGIN=*
CORS_METHODS=GET,POST,PUT,DELETE
CORS_CREDENTIALS=true

# QR Code
QRCODE_LIMIT=30

# WhatsApp session
CONFIG_SESSION_PHONE_CLIENT=Pangeia Bot
CONFIG_SESSION_PHONE_NAME=Chrome

# Porta (obrigatória para Render)
PORT=8080
```

**⚠️ IMPORTANTE:**
- Substitua `COLE_AQUI_A_INTERNAL_DATABASE_URL` pela URL do PostgreSQL que você copiou
  - **ATENÇÃO:** Adicione `?schema=public` NO FINAL da URL!
  - Exemplo: `postgresql://evolution_user:abc123@dpg-xxxxx-internal/evolution_db?schema=public`
- Substitua `COLE_AQUI_A_INTERNAL_REDIS_URL` pela URL do Redis que você copiou
- Mude `AUTHENTICATION_API_KEY` para uma chave forte (ex: `pange-2024-xpto-secreto-12345`)

#### 5.3. Deploy!

1. Clique em **"Create Web Service"**
2. **Aguarde 3-5 minutos** para o deploy
3. Você verá logs do build e deploy
4. Quando aparecer **"Live"** em verde, está pronto! ✅

#### 5.4. Atualizar SERVER_URL

1. Após deploy completar, copie a **URL pública** gerada
   - Exemplo: `https://pangeia-evolution-api-abc123.onrender.com`
2. Vá em **"Environment"** (menu lateral esquerdo)
3. Encontre a variável `SERVER_URL`
4. Clique em **editar** e cole a URL real
5. Clique em **"Save Changes"**
6. Render vai fazer redeploy automático (1-2 minutos)

#### 5.5. Testar Evolution API

Acesse no navegador: `https://pangeia-evolution-api-SEU-ID.onrender.com`

Deve aparecer uma página de boas-vindas da Evolution API! 🎉

---

### **ETAPA 6: Criar Web Service - Bot Python Pangeia**

#### 6.1. Criar arquivo Procfile (se não existir)

O Render precisa saber como rodar sua aplicação Python. Verifique se você tem um arquivo `Procfile` na raiz do projeto com:

```
web: gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 src.webhook.app:app
```

Se não existir, vamos criar agora (vou fazer isso para você em seguida).

#### 6.2. Criar o serviço

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Escolha **"Build and deploy from a Git repository"**
4. Clique em **"Connect account"** se ainda não conectou o GitHub
5. Encontre seu repositório `notion-pangeia`
6. Clique em **"Connect"**

#### 6.3. Configurar o serviço

Preencha:

- **Name:** `pangeia-bot`
- **Region:** **Mesma dos outros serviços!**
- **Branch:** `main` (ou o nome do seu branch principal)
- **Root Directory:** (deixe vazio)
- **Runtime:** **Python 3**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 src.webhook.app:app`
- **Plan:** **FREE** ✅

#### 6.4. Configurar Variáveis de Ambiente do Bot

Role até **"Environment Variables"** e adicione:

```bash
# Notion Configuration
NOTION_TOKEN=seu_token_do_notion_aqui
NOTION_TASKS_DB_ID=seu_database_id_de_tarefas_aqui
NOTION_USERS_DB_ID=seu_database_id_de_usuarios_aqui

# Evolution API WhatsApp Configuration
EVOLUTION_API_URL=https://pangeia-evolution-api-SEU-ID.onrender.com
EVOLUTION_API_KEY=pange-bot-secret-key-2024-MUDE-ISSO
EVOLUTION_INSTANCE_NAME=pangeia-bot

# Flask Configuration
FLASK_SECRET_KEY=gere-uma-chave-secreta-forte-aqui
WEBHOOK_PATH=/webhook/whatsapp
PORT=10000

# Scheduler Configuration
DAILY_SEND_TIME=08:00
CHECKIN_1_TIME=13:30
CHECKIN_2_TIME=15:30
CHECKIN_3_TIME=18:00
CHECKIN_4_TIME=22:00
TIMEZONE=America/Sao_Paulo

# Application Settings
LOG_LEVEL=INFO
CACHE_EXPIRY_HOURS=24
MAX_RETRIES=3
ENVIRONMENT=production
```

**⚠️ IMPORTANTE:**
- `NOTION_TOKEN`: Token da sua integração do Notion
  - Como obter: https://www.notion.so/my-integrations
- `NOTION_TASKS_DB_ID`: ID do seu database de tarefas
  - Como obter: abra o database no Notion, copie o ID da URL
  - Exemplo: `https://notion.so/workspace/1234567890abcdef?v=...`
  - O ID é: `1234567890abcdef`
- `EVOLUTION_API_URL`: URL da Evolution API que você criou (passo 5)
- `EVOLUTION_API_KEY`: **MESMA CHAVE** que você usou na Evolution API
- `FLASK_SECRET_KEY`: Gere uma chave aleatória
  - No terminal: `python -c "import secrets; print(secrets.token_hex(32))"`

#### 6.5. Deploy do Bot!

1. Clique em **"Create Web Service"**
2. Render vai:
   - Clonar seu repositório
   - Instalar dependências (`pip install -r requirements.txt`)
   - Iniciar o servidor (`gunicorn...`)
3. **Aguarde 3-5 minutos**
4. Quando aparecer **"Live"**, seu bot está rodando! 🎉

#### 6.6. Copiar URL do Webhook

Após deploy, copie a URL pública do bot:
- Exemplo: `https://pangeia-bot-xyz.onrender.com`

Vamos precisar dela para configurar o webhook!

---

### **ETAPA 7: Conectar WhatsApp**

#### 7.1. Criar instância WhatsApp

Abra o terminal e execute:

```bash
curl -X POST 'https://pangeia-evolution-api-SEU-ID.onrender.com/instance/create' \
  -H 'apikey: SUA_API_KEY_AQUI' \
  -H 'Content-Type: application/json' \
  -d '{
    "instanceName": "pangeia-bot",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Substitua:**
- `pangeia-evolution-api-SEU-ID.onrender.com` → URL da sua Evolution API
- `SUA_API_KEY_AQUI` → Sua `AUTHENTICATION_API_KEY`

**Resposta esperada:**
```json
{
  "instance": {
    "instanceName": "pangeia-bot",
    "status": "created"
  }
}
```

#### 7.2. Configurar Webhook

Agora vamos conectar a Evolution API ao seu bot Python:

```bash
curl -X POST 'https://pangeia-evolution-api-SEU-ID.onrender.com/webhook/set/pangeia-bot' \
  -H 'apikey: SUA_API_KEY_AQUI' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://pangeia-bot-xyz.onrender.com/webhook/whatsapp",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "SEND_MESSAGE"
    ]
  }'
```

**Substitua:**
- `pangeia-evolution-api-SEU-ID.onrender.com` → URL da Evolution API
- `SUA_API_KEY_AQUI` → Sua API key
- `https://pangeia-bot-xyz.onrender.com` → URL do seu bot Python

#### 7.3. Gerar QR Code

Aguarde **10 segundos** após criar a instância, depois execute:

```bash
curl 'https://pangeia-evolution-api-SEU-ID.onrender.com/instance/connect/pangeia-bot' \
  -H 'apikey: SUA_API_KEY_AQUI'
```

**Resposta:**
```json
{
  "code": "iVBORw0KGgoAAAANS...",
  "base64": "data:image/png;base64,iVBORw0KG..."
}
```

#### 7.4. Visualizar QR Code

**Opção 1: No terminal (Mac/Linux)**
```bash
# Salvar em arquivo
echo "COLE_O_BASE64_AQUI" > qr.txt

# Decodificar e salvar imagem
cat qr.txt | sed 's/data:image\/png;base64,//' | base64 -d > qrcode.png

# Abrir imagem
open qrcode.png  # Mac
xdg-open qrcode.png  # Linux
```

**Opção 2: No navegador**
1. Copie o campo `base64` da resposta
2. Cole no navegador: `data:image/png;base64,COLE_AQUI`
3. QR Code vai aparecer!

**Opção 3: Site online**
1. Acesse: https://codebeautify.org/base64-to-image-converter
2. Cole o base64
3. Clique em "Decode"

#### 7.5. Escanear QR Code

1. Abra o WhatsApp no celular
2. Vá em **Configurações** → **Aparelhos conectados**
3. Clique em **"Conectar um aparelho"**
4. Escaneie o QR Code
5. **Pronto!** Bot conectado! 🎉

---

### **ETAPA 8: Testar o Bot**

#### 8.1. Health Check

Verifique se tudo está rodando:

**Evolution API:**
```bash
curl https://pangeia-evolution-api-SEU-ID.onrender.com/instance/fetchInstances \
  -H 'apikey: SUA_API_KEY_AQUI'
```

Deve retornar lista de instâncias, incluindo `pangeia-bot` com status `open`.

**Bot Python:**
```bash
curl https://pangeia-bot-xyz.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "notion-pangeia-webhook",
  "version": "1.0.0",
  "scheduler": "running"
}
```

#### 8.2. Testar Comandos

Envie uma mensagem para o número conectado:

```
oi
```

O bot deve responder com o menu de onboarding! 🎉

Teste outros comandos:
```
tarefas
ajuda
tutorial
```

---

## 🔧 CONFIGURAÇÕES ADICIONAIS

### Manter o App Acordado (Free Plan)

No plano FREE, o Render coloca apps para "dormir" após 15 minutos sem uso.

**Solução 1: UptimeRobot (grátis)**
1. Acesse: https://uptimerobot.com/
2. Crie uma conta gratuita
3. Adicione 2 monitores HTTP(S):
   - Evolution API: `https://pangeia-evolution-api-SEU-ID.onrender.com`
   - Bot Python: `https://pangeia-bot-xyz.onrender.com/health`
4. Intervalo: 5 minutos
5. Pronto! Apps sempre acordados ✅

**Solução 2: Cron Job (gratuito via GitHub Actions)**

Crie `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Render Apps Alive

on:
  schedule:
    - cron: '*/10 * * * *'  # A cada 10 minutos
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Evolution API
        run: curl https://pangeia-evolution-api-SEU-ID.onrender.com

      - name: Ping Bot Python
        run: curl https://pangeia-bot-xyz.onrender.com/health
```

Commit e push. GitHub vai pingar os apps automaticamente!

---

## 📊 Monitoramento

### Ver Logs

**Evolution API:**
1. Dashboard Render → `pangeia-evolution-api`
2. Menu lateral → **"Logs"**
3. Veja logs em tempo real

**Bot Python:**
1. Dashboard Render → `pangeia-bot`
2. Menu lateral → **"Logs"**
3. Filtre por "ERROR", "WARNING", etc.

### Ver Jobs Agendados

```bash
curl https://pangeia-bot-xyz.onrender.com/scheduler/jobs
```

Retorna lista de tarefas agendadas (envio diário, check-ins, etc.).

### Executar Job Manualmente

```bash
curl -X POST https://pangeia-bot-xyz.onrender.com/scheduler/run/daily_tasks
```

---

## 🆘 TROUBLESHOOTING

### Evolution API não inicia

**Sintoma:** App crashando constantemente

**Solução:**
1. Vá em **Logs** da Evolution API
2. Procure por:
   - `DATABASE_CONNECTION_URI` vazio
   - `connection refused` (PostgreSQL não está pronto)
   - `Redis connection failed`

**Fix:**
1. Verifique se PostgreSQL e Redis estão **"Available"** (verde)
2. Copie novamente as Internal URLs
3. Atualize variáveis de ambiente
4. Clique em **"Manual Deploy"** → **"Clear build cache & deploy"**

### Bot Python não recebe mensagens

**Sintoma:** Mensagens do WhatsApp não chegam no bot

**Solução:**
1. Verifique se webhook está configurado:
   ```bash
   curl https://pangeia-evolution-api-SEU-ID.onrender.com/webhook/find/pangeia-bot \
     -H 'apikey: SUA_API_KEY'
   ```
   Deve retornar a URL do seu bot.

2. Teste o endpoint do bot diretamente:
   ```bash
   curl -X POST https://pangeia-bot-xyz.onrender.com/webhook/whatsapp \
     -H 'Content-Type: application/json' \
     -d '{
       "event": "messages.upsert",
       "data": {
         "key": {"fromMe": false, "remoteJid": "5511999999999@s.whatsapp.net"},
         "message": {"conversation": "teste"},
         "pushName": "Teste"
       }
     }'
   ```

3. Se não funcionar, veja logs do bot e procure por erros.

### QR Code expirou

**Sintoma:** QR Code não funciona mais

**Solução:**
```bash
# 1. Deletar instância
curl -X DELETE 'https://pangeia-evolution-api-SEU-ID.onrender.com/instance/delete/pangeia-bot' \
  -H 'apikey: SUA_API_KEY'

# 2. Recriar (volte ao Passo 7.1)
```

### Scheduler não está rodando

**Sintoma:** Tarefas não são enviadas nos horários agendados

**Solução:**
1. Verifique status:
   ```bash
   curl https://pangeia-bot-xyz.onrender.com/health
   ```
   `scheduler` deve ser `"running"`

2. Veja os jobs:
   ```bash
   curl https://pangeia-bot-xyz.onrender.com/scheduler/jobs
   ```

3. Se estiver vazio, veja logs do bot para erros no startup.

### Notion API não responde

**Sintoma:** Erro "Invalid token" ou "Database not found"

**Solução:**
1. Verifique `NOTION_TOKEN`:
   - Acesse https://www.notion.so/my-integrations
   - Copie o token da integração
   - Atualize variável no Render

2. Verifique `NOTION_TASKS_DB_ID`:
   - Abra o database no Notion
   - Copie ID da URL (depois de `notion.so/workspace/`)
   - Atualize variável no Render

3. **IMPORTANTE:** Compartilhe o database com a integração!
   - No Notion, abra o database
   - Clique em "..." (três pontos)
   - "Add connections" → Selecione sua integração

---

## 💰 CUSTOS

### Plano FREE (o que estamos usando)

- **PostgreSQL:** GRÁTIS
  - 1 GB de armazenamento
  - 90 dias de retenção
  - Backups diários

- **Redis:** GRÁTIS
  - 25 MB de memória
  - Sem persistência (restart limpa dados)

- **Web Services (2x):** GRÁTIS
  - 512 MB RAM cada
  - Compartilhado CPU
  - 750 horas/mês (suficiente para 1 app rodando 24/7)
  - **Atenção:** Apps dormem após 15min sem uso

**TOTAL: R$ 0,00/mês** 🎉

### Upgrade (opcional)

Se quiser app sempre acordado e mais recursos:

- **Web Service (Starter):** $7/mês por app
  - 512 MB RAM
  - Apps não dormem
  - Deployment automático

- **PostgreSQL (Starter):** $7/mês
  - 10 GB storage
  - Backups com retenção de 30 dias

---

## 🎉 CHECKLIST FINAL

Marque cada item conforme completa:

- [ ] Conta criada no Render
- [ ] Repositório GitHub criado e sincronizado
- [ ] PostgreSQL criado e URL copiada
- [ ] Redis criado e URL copiada
- [ ] Evolution API deployed com todas variáveis
- [ ] SERVER_URL atualizada com URL real
- [ ] Evolution API testada e funcionando
- [ ] Procfile criado/verificado
- [ ] Bot Python deployed com todas variáveis
- [ ] Bot Python testado (health check OK)
- [ ] Instância WhatsApp criada
- [ ] Webhook configurado
- [ ] QR Code gerado e escaneado
- [ ] WhatsApp conectado (status "open")
- [ ] Comandos testados e funcionando
- [ ] UptimeRobot configurado (opcional)
- [ ] **SISTEMA COMPLETO NO AR!** 🚀

---

## 🔗 LINKS ÚTEIS

- Dashboard Render: https://dashboard.render.com/
- Notion API: https://developers.notion.com/
- Evolution API Docs: https://doc.evolution-api.com/
- UptimeRobot: https://uptimerobot.com/

---

## 📞 SUPORTE

Se tiver problemas:

1. **Logs são seus melhores amigos!**
   - Sempre verifique os logs no Render Dashboard

2. **Teste endpoints individualmente:**
   - Evolution API health
   - Bot health
   - Webhook connectivity

3. **Variáveis de ambiente:**
   - Maioria dos problemas vem de variáveis incorretas
   - Revise TODAS antes de fazer deploy

4. **Comunidade:**
   - Evolution API: https://github.com/EvolutionAPI/evolution-api/discussions
   - Render: https://community.render.com/

---

**🎉 Parabéns! Seu bot Notion Pangeia está no ar!**

Agora você tem um sistema completo de gerenciamento de tarefas via WhatsApp, 100% gratuito e hospedado na nuvem!

Qualquer dúvida, consulte este guia ou os logs do sistema. Bom uso! 🚀
