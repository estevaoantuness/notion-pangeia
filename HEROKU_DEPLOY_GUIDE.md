# 🚀 Guia Completo: Deploy Evolution API no Heroku

## ✅ PASSO 1: Login no Heroku

Abra o terminal e execute:

```bash
heroku login
```

Isso vai abrir o navegador para você fazer login. Depois volte ao terminal.

---

## ✅ PASSO 2: Criar App no Heroku

```bash
heroku create pangeia-bot-evolution
```

**Anote a URL que o Heroku criar!** (algo como: `https://pangeia-bot-evolution.herokuapp.com`)

---

## ✅ PASSO 3: Adicionar PostgreSQL (GRÁTIS)

```bash
heroku addons:create heroku-postgresql:essential-0 -a pangeia-bot-evolution
```

**Aguarde 1-2 minutos** para o addon ser provisionado.

---

## ✅ PASSO 4: Adicionar Redis (GRÁTIS)

```bash
heroku addons:create heroku-redis:mini -a pangeia-bot-evolution
```

**Aguarde 1-2 minutos** para o addon ser provisionado.

---

## ✅ PASSO 5: Configurar Variáveis de Ambiente

```bash
heroku config:set \
  SERVER_URL=https://pangeia-bot-evolution.herokuapp.com \
  AUTHENTICATION_API_KEY=pange-bot-secret-key-2024 \
  DATABASE_ENABLED=true \
  DATABASE_PROVIDER=postgresql \
  DATABASE_SAVE_DATA_INSTANCE=true \
  DATABASE_SAVE_DATA_NEW_MESSAGE=false \
  DATABASE_SAVE_MESSAGE_UPDATE=false \
  DATABASE_SAVE_DATA_CONTACTS=false \
  DATABASE_SAVE_DATA_CHATS=false \
  CACHE_REDIS_ENABLED=true \
  CACHE_REDIS_PREFIX_KEY=evolution \
  CACHE_REDIS_SAVE_INSTANCES=false \
  LOG_LEVEL=ERROR,WARN,INFO \
  LOG_COLOR=true \
  CORS_ORIGIN=* \
  CORS_METHODS=GET,POST,PUT,DELETE \
  CORS_CREDENTIALS=true \
  QRCODE_LIMIT=30 \
  CONFIG_SESSION_PHONE_CLIENT="Evolution API" \
  CONFIG_SESSION_PHONE_NAME=Chrome \
  -a pangeia-bot-evolution
```

---

## ✅ PASSO 6: Configurar DATABASE_CONNECTION_URI

O Heroku já criou a variável `DATABASE_URL` automaticamente. Precisamos copiá-la para `DATABASE_CONNECTION_URI`:

```bash
# Ver a DATABASE_URL
heroku config:get DATABASE_URL -a pangeia-bot-evolution

# Copiar para DATABASE_CONNECTION_URI
heroku config:set DATABASE_CONNECTION_URI=$(heroku config:get DATABASE_URL -a pangeia-bot-evolution)?schema=public -a pangeia-bot-evolution
```

---

## ✅ PASSO 7: Configurar CACHE_REDIS_URI

O Heroku já criou a variável `REDIS_URL` automaticamente. Precisamos copiá-la para `CACHE_REDIS_URI`:

```bash
# Ver a REDIS_URL
heroku config:get REDIS_URL -a pangeia-bot-evolution

# Copiar para CACHE_REDIS_URI
heroku config:set CACHE_REDIS_URI=$(heroku config:get REDIS_URL -a pangeia-bot-evolution) -a pangeia-bot-evolution
```

---

## ✅ PASSO 8: Deploy via Container Registry

O Heroku não suporta Docker Compose diretamente, mas podemos usar a imagem Docker da Evolution API:

### **Opção A: Via Heroku Container Registry (RECOMENDADO)**

1. Login no Container Registry:
```bash
heroku container:login
```

2. Criar Dockerfile temporário:
```bash
cd /Users/estevaoantunes/notion-pangeia
cat > Dockerfile.heroku << 'EOF'
FROM atendai/evolution-api:v2.1.1

# Heroku usa a variável PORT, mas Evolution usa 8080
ENV PORT=8080

CMD ["npm", "run", "start:prod"]
EOF
```

3. Build e push:
```bash
heroku container:push web -a pangeia-bot-evolution
```

4. Release:
```bash
heroku container:release web -a pangeia-bot-evolution
```

---

### **Opção B: Deploy de imagem direta (MAIS SIMPLES)**

Se a Opção A der problema, use este comando:

```bash
# 1. Criar stack com container
heroku stack:set container -a pangeia-bot-evolution

# 2. Criar heroku.yml
cat > heroku.yml << 'EOF'
build:
  docker:
    web: Dockerfile.heroku
run:
  web: npm run start:prod
EOF

# 3. Commit e push
git add heroku.yml Dockerfile.heroku
git commit -m "Add Heroku deployment"
heroku git:remote -a pangeia-bot-evolution
git push heroku main
```

---

## ✅ PASSO 9: Verificar Deploy

```bash
# Ver logs em tempo real
heroku logs --tail -a pangeia-bot-evolution

# Ver status
heroku ps -a pangeia-bot-evolution

# Abrir app no navegador
heroku open -a pangeia-bot-evolution
```

---

## ✅ PASSO 10: Criar Instância e Gerar QR Code

```bash
# Criar instância
curl -X POST 'https://pangeia-bot-evolution.herokuapp.com/instance/create' \
  -H 'apikey: pange-bot-secret-key-2024' \
  -H 'Content-Type: application/json' \
  -d '{"instanceName":"pangeia-bot","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'

# Aguardar 10 segundos
sleep 10

# Obter QR Code
curl 'https://pangeia-bot-evolution.herokuapp.com/instance/connect/pangeia-bot' \
  -H 'apikey: pange-bot-secret-key-2024'
```

---

## 🆘 TROUBLESHOOTING

### Erro: "Couldn't find that app"
```bash
heroku apps
# Veja o nome correto e use ele nos comandos
```

### Erro: "Missing required flag: -a"
Sempre adicione `-a pangeia-bot-evolution` no final dos comandos.

### Erro: "No addons found"
```bash
heroku addons -a pangeia-bot-evolution
# Verifique se os addons foram criados
```

### Ver todas as variáveis:
```bash
heroku config -a pangeia-bot-evolution
```

---

## 📋 RESUMO DOS COMANDOS (COPIAR E COLAR)

```bash
# 1. Login
heroku login

# 2. Criar app
heroku create pangeia-bot-evolution

# 3. Addons
heroku addons:create heroku-postgresql:essential-0 -a pangeia-bot-evolution
heroku addons:create heroku-redis:mini -a pangeia-bot-evolution

# 4. Aguardar addons (2 minutos)
sleep 120

# 5. Configurar variáveis (comando grande acima - PASSO 5)

# 6. Database URI
heroku config:set DATABASE_CONNECTION_URI=$(heroku config:get DATABASE_URL -a pangeia-bot-evolution)?schema=public -a pangeia-bot-evolution

# 7. Redis URI
heroku config:set CACHE_REDIS_URI=$(heroku config:get REDIS_URL -a pangeia-bot-evolution) -a pangeia-bot-evolution

# 8. Deploy
cd /Users/estevaoantunes/notion-pangeia
cat > Dockerfile.heroku << 'EOF'
FROM atendai/evolution-api:v2.1.1
ENV PORT=8080
CMD ["npm", "run", "start:prod"]
EOF

heroku container:login
heroku container:push web -a pangeia-bot-evolution
heroku container:release web -a pangeia-bot-evolution

# 9. Ver logs
heroku logs --tail -a pangeia-bot-evolution
```

---

## 🎯 DEPOIS DO DEPLOY

Acesse: `https://pangeia-bot-evolution.herokuapp.com`

Se aparecer algo (mesmo que erro 404), está funcionando!

Aí você cria a instância e gera o QR Code (PASSO 10).

---

## 💰 CUSTO

- **PostgreSQL Essential-0:** GRÁTIS (1GB, 20 conexões)
- **Redis Mini:** GRÁTIS (25MB)
- **Dyno Eco:** GRÁTIS (1000 horas/mês)

**Total: R$ 0,00** 🎉
