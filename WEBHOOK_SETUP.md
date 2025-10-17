# 🔗 Configuração do Webhook WhatsApp

Este guia explica como configurar e testar o webhook do WhatsApp com Twilio Sandbox.

## 📋 Pré-requisitos

- ✅ Servidor Flask implementado (`src/webhook/app.py`)
- ✅ Twilio Sandbox configurado
- ✅ ngrok instalado (para expor localhost)

## 🚀 Passo a Passo

### 1. Instalar ngrok (se necessário)

```bash
# macOS com Homebrew
brew install ngrok

# Ou baixe de: https://ngrok.com/download
```

### 2. Iniciar o servidor Flask

Em um terminal:

```bash
python3 -m src.webhook.app
```

Você verá:
```
🚀 SERVIDOR WEBHOOK INICIANDO
Porta: 5000
Endpoint: http://localhost:5000/webhook/whatsapp
```

### 3. Expor o servidor com ngrok

Em OUTRO terminal:

```bash
ngrok http 5000
```

Você verá algo como:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

**COPIE** a URL HTTPS (ex: `https://abc123.ngrok.io`)

### 4. Configurar Webhook no Twilio

1. Acesse: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. Na seção **"Sandbox Configuration"**:
   - **WHEN A MESSAGE COMES IN**: Cole sua URL ngrok + `/webhook/whatsapp`
     - Exemplo: `https://abc123.ngrok.io/webhook/whatsapp`
     - Método: `HTTP POST`
   - **STATUS CALLBACK URL** (opcional): Cola sua URL ngrok + `/webhook/whatsapp/status`
     - Exemplo: `https://abc123.ngrok.io/webhook/whatsapp/status`
3. Clique em **Save**

### 5. Conectar seu WhatsApp ao Sandbox

1. No Twilio Console, na página do Sandbox, você verá um código tipo: `join [palavra-código]`
2. No seu WhatsApp, envie uma mensagem para `+1 415 523 8886` com esse código
3. Você receberá: "You are all set! The Sandbox is now ready to receive and send messages."

### 6. Testar!

Agora você pode enviar mensagens direto do seu WhatsApp para o número do Sandbox!

**Comandos para testar:**
```
ajuda
minhas tarefas
progresso
andamento 1
feito 1
```

## 🧪 Testes Locais (sem ngrok)

Para testar o webhook SEM expor publicamente (útil durante desenvolvimento):

```bash
# Terminal 1: Inicia o servidor
python3 -m src.webhook.app

# Terminal 2: Executa testes simulados
python3 test_webhook.py
```

O script `test_webhook.py` simula requisições do Twilio localmente.

## 📊 Monitoramento

### Logs do Flask

O servidor Flask mostra todos os logs no terminal:

```
📨 MENSAGEM RECEBIDA VIA WEBHOOK
From: whatsapp:+554191851256
Message: feito 1
SID: SM1234...
✅ Comando processado com sucesso
```

### Logs do ngrok

O ngrok mostra todas as requisições HTTP no terminal dele.

Você também pode acessar: http://localhost:4040 para ver UI do ngrok com:
- Todas as requisições
- Payloads completos
- Replay de requisições (útil para debug!)

## 🔒 Segurança

### Validação de Signature (Produção)

No código, há a função `validate_twilio_request()` que valida que a requisição veio do Twilio.

Para ATIVAR em produção, adicione no webhook:

```python
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    # Valida signature do Twilio
    request_url = request.url
    if not validate_twilio_request(request_url):
        logger.warning("⚠️  Requisição rejeitada: signature inválida")
        return Response("Forbidden", status=403)

    # ... resto do código
```

**ATENÇÃO**: Desabilitado por padrão pois o ngrok muda a URL e quebra a validação.

## 🐛 Troubleshooting

### "Não foi possível conectar ao servidor"

- Verifique se o Flask está rodando: `curl http://localhost:5000/health`
- Verifique se a porta 5000 não está em uso: `lsof -i :5000`

### "Webhook não responde no WhatsApp"

1. Verifique se o ngrok está rodando
2. Verifique se a URL no Twilio Console está correta
3. Verifique os logs do Flask - a mensagem está chegando?
4. Verifique os logs do ngrok em http://localhost:4040

### "Comando não reconhecido"

- Verifique os padrões aceitos em `src/commands/parser.py`
- Teste o comando com: `python3 test_webhook.py`

## 📱 Fluxo Completo

```
Seu WhatsApp
     ↓
Envia "feito 1" para +1 415 523 8886
     ↓
Twilio Sandbox recebe
     ↓
Twilio faz POST para https://abc123.ngrok.io/webhook/whatsapp
     ↓
ngrok encaminha para http://localhost:5000/webhook/whatsapp
     ↓
Flask processa com CommandProcessor
     ↓
TaskUpdater atualiza no Notion
     ↓
WhatsAppSender envia confirmação
     ↓
Você recebe no WhatsApp: "✅ Task concluída!"
```

## 🎯 Próximos Passos

Após validar que o webhook funciona localmente:

1. **Deploy em produção** (Render, Railway, etc)
2. **Configurar domínio próprio** (opcional)
3. **Implementar ETAPA 4**: Scheduler para envios automáticos às 8h
4. **Implementar ETAPA 5**: Check-ins estratégicos

## 💡 Dicas

- **Mantenha o ngrok rodando** enquanto estiver testando
- **Cada vez que reiniciar o ngrok**, a URL muda → atualize no Twilio Console
- **Use o ngrok UI** (localhost:4040) para debugar payloads
- **Os logs do Flask** são sua melhor ferramenta de debug
