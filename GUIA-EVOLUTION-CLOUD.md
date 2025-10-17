# 🚀 Guia Completo - Evolution Cloud Setup

## Passo 1: Criar Conta no Evolution Cloud

### Opção A: Evolution API Official (Recomendado)

1. Acesse: **https://evolution-api.com**
2. Clique em **"Get Started"** ou **"Sign Up"**
3. Crie sua conta (email + senha)
4. Confirme o email

### Opção B: Provedor Alternativo - TypeBot Cloud

1. Acesse: **https://cloud.typebot.io** (tem Evolution API integrado)
2. Criar conta gratuita
3. Acessar painel Evolution

### Opção C: Deploy Manual (DigitalOcean/Railway)

Se preferir hospedar você mesmo (recomendo Railway - mais fácil):

**Railway:**
1. Acesse: https://railway.app
2. Clique em "Deploy Evolution API"
3. Conecte GitHub
4. Aguarde deploy (3-5 minutos)

---

## Passo 2: Criar Instância WhatsApp

### No Painel Evolution Cloud:

1. Faça login no painel
2. Clique em **"Criar Nova Instância"** ou **"New Instance"**
3. Preencha:
   - **Nome da Instância:** `pangeia-bot`
   - **Tipo:** WhatsApp (Baileys)
   - **QR Code:** Habilitado ✅
4. Clique em **"Criar"**

---

## Passo 3: Copiar Credenciais

Você precisa de 3 informações:

### 1. URL da API:
```
Exemplo: https://api-evolution.seu-servidor.com
ou
https://evo-xxxxx.railway.app
```

### 2. API Key (Global):
```
Exemplo: B4F8A9D2-3C1E-4B7A-9F2D-8E5C6A1B3D4F
```

### 3. Nome da Instância:
```
pangeia-bot
```

**Onde encontrar:**
- URL: No painel, seção "API Endpoint" ou "Base URL"
- API Key: Configurações → API Key ou Segurança
- Nome: O que você escolheu ao criar

---

## Passo 4: Atualizar .env Local

Abra o arquivo `.env` no projeto e atualize:

```bash
# Evolution API WhatsApp Configuration
EVOLUTION_API_URL=https://sua-url-aqui.com
EVOLUTION_API_KEY=sua-api-key-aqui
EVOLUTION_INSTANCE_NAME=pangeia-bot
```

**Exemplo Real:**
```bash
EVOLUTION_API_URL=https://evo-production-abc123.up.railway.app
EVOLUTION_API_KEY=B4F8A9D2-3C1E-4B7A-9F2D-8E5C6A1B3D4F
EVOLUTION_INSTANCE_NAME=pangeia-bot
```

---

## Passo 5: Testar Conexão

Execute o script de teste:

```bash
# Teste 1: Verificar se a API está acessível
curl https://sua-url-aqui.com

# Deve retornar algo como:
# {"status":200,"message":"Welcome to the Evolution API..."}
```

Ou use nosso script Python:

```bash
python3 test_connections.py
```

Deve mostrar:
```
✅ Evolution API: Conectado
```

---

## Passo 6: Obter QR Code

### Método 1: Usando nosso servidor web

```bash
# Inicie o servidor local
python3 qr-web.py

# Abra no navegador
open http://localhost:8000
```

O QR Code deve aparecer automaticamente!

### Método 2: Via script direto

```bash
python3 get-qrcode.py
```

### Método 3: Via painel Evolution Cloud

1. Acesse o painel web
2. Clique na instância `pangeia-bot`
3. Clique em "Connect" ou ícone de QR Code
4. Escaneie com WhatsApp

---

## Passo 7: Conectar WhatsApp

1. **Abra WhatsApp no celular**
2. Toque em **⋮ (Menu)** ou **Configurações**
3. Toque em **Aparelhos conectados**
4. Toque em **Conectar um aparelho**
5. **Escaneie o QR Code** exibido

Aguarde alguns segundos...

✅ **Conectado!** Você verá uma mensagem de confirmação

---

## ✅ Verificar Se Está Funcionando

Execute:

```bash
# Verificar status da conexão
python3 -c "
from src.whatsapp.client import WhatsAppClient
client = WhatsAppClient()
success, msg = client.test_connection()
print(f'Status: {msg}')
"
```

Deve mostrar:
```
Status: Conectado à Evolution API. Estado da instância: open
```

---

## 🎯 Teste Completo do Bot

Envie uma mensagem de teste:

```bash
# Testar envio de mensagem
python3 -c "
from src.whatsapp.client import WhatsAppClient

client = WhatsAppClient()
success, msg_id, error = client.send_message(
    to_number='+5541999999999',  # Seu número
    message='🤖 Teste do Pangeia Bot - Evolution Cloud funcionando!'
)

if success:
    print(f'✅ Mensagem enviada! ID: {msg_id}')
else:
    print(f'❌ Erro: {error}')
"
```

---

## 📱 Configurar Webhook (Importante para Produção)

O webhook permite que o bot receba mensagens:

### 1. Deploy do Webhook

Você precisa de uma URL pública. Opções:

**Opção A: Railway (Recomendado)**
```bash
# Instalar Railway CLI
npm install -g railway

# Login
railway login

# Deploy
railway up
```

**Opção B: ngrok (Teste rápido)**
```bash
# Instalar ngrok
brew install ngrok

# Expor porta local
ngrok http 5001
```

### 2. Configurar no Evolution Cloud

No painel Evolution:
1. Vá em Configurações da Instância
2. Webhook URL: `https://sua-url.com/webhook/whatsapp`
3. Webhook Events: `messages.upsert`
4. Salvar

---

## 🔧 Troubleshooting

### Problema: "API Key inválida"
**Solução:** Verifique se copiou a API Key corretamente (sem espaços)

### Problema: "Instance not found"
**Solução:** Verifique se o nome da instância está correto (case-sensitive)

### Problema: "Connection refused"
**Solução:** Verifique se a URL está correta e acessível

### Problema: QR Code não aparece
**Solução:**
1. Aguarde 10-15 segundos
2. Clique em "Reconnect" no painel
3. Delete e recrie a instância

---

## 💰 Custos

### Evolution Cloud Official:
- **Free Tier:** 1 instância, 1000 mensagens/mês
- **Pro:** $5/mês - Instâncias ilimitadas
- **Business:** $15/mês - Suporte prioritário

### Self-hosted (Railway/DigitalOcean):
- **Railway:** ~$5/mês (500h grátis)
- **DigitalOcean:** $6/mês (droplet básico)

---

## 📋 Checklist Final

- [ ] Conta criada no Evolution Cloud
- [ ] Instância `pangeia-bot` criada
- [ ] Credenciais copiadas
- [ ] Arquivo `.env` atualizado
- [ ] Teste de conexão passou
- [ ] QR Code gerado e escaneado
- [ ] WhatsApp conectado (status: open)
- [ ] Mensagem de teste enviada com sucesso
- [ ] Webhook configurado (produção)
- [ ] Bot respondendo comandos

---

## 🎉 Pronto!

Seu bot Pangeia está conectado ao WhatsApp via Evolution Cloud!

**Próximos passos:**
1. Testar comandos do bot
2. Configurar scheduler para envios automáticos
3. Deploy do webhook em produção
4. Monitorar logs e performance

---

**Criado em:** 2025-10-16
**Última atualização:** 2025-10-16
