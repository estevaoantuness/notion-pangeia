# Evolution API - Setup Completo ✅

## Status: **FUNCIONANDO** 🎉

A Evolution API v2.2.3 está rodando com sucesso em `http://localhost:8080`

---

## 🐳 Containers Rodando

```
evolution_api       -> Porta 8080 (Evolution API)
evolution_postgres  -> Porta 5432 (PostgreSQL database)
```

---

## 🔑 Credenciais

### API Key (para autenticação):
```
pange-bot-secret-key-2024
```

### PostgreSQL (internal):
```
User: evolution
Password: evolution123
Database: evolution
Host: postgres (dentro da network Docker)
```

---

## 📡 Endpoints Principais

### Health Check:
```bash
curl http://localhost:8080
```

### Manager (UI Web):
```
http://localhost:8080/manager
```

### Documentação:
```
https://doc.evolution-api.com
```

---

## 🚀 Próximos Passos

### 1. Criar Instância WhatsApp

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: pange-bot-secret-key-2024" \
  -d '{
    "instanceName": "pangeia-bot",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Resposta esperada:**
- `instanceName`: pangeia-bot
- `hash`: (ID único)
- QR Code base64 para scan

### 2. Obter QR Code

```bash
curl http://localhost:8080/instance/connect/pangeia-bot \
  -H "apikey: pange-bot-secret-key-2024"
```

**Resposta:**
- `base64`: imagem do QR Code
- `code`: QR Code em texto (pode escanear direto do terminal)

### 3. Conectar WhatsApp

1. Abra o WhatsApp no celular
2. Vá em **Aparelhos Conectados** > **Conectar um Aparelho**
3. Escaneie o QR Code retornado pela API

### 4. Verificar Conexão

```bash
curl http://localhost:8080/instance/connectionState/pangeia-bot \
  -H "apikey: pange-bot-secret-key-2024"
```

**Estado esperado:** `open` (conectado)

### 5. Configurar Webhook

```bash
curl -X POST http://localhost:8080/webhook/set/pangeia-bot \
  -H "Content-Type: application/json" \
  -H "apikey: pange-bot-secret-key-2024" \
  -d '{
    "url": "http://seu-servidor.com/webhook/whatsapp",
    "enabled": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "CONNECTION_UPDATE"
    ]
  }'
```

### 6. Testar Envio de Mensagem

```bash
curl -X POST http://localhost:8080/message/sendText/pangeia-bot \
  -H "Content-Type: application/json" \
  -H "apikey: pange-bot-secret-key-2024" \
  -d '{
    "number": "5511999999999",
    "text": "Teste Evolution API - Pange.iA Bot"
  }'
```

---

## 🔧 Atualizar .env do Projeto

Atualize o arquivo `/Users/estevaoantunes/notion-pangeia/.env`:

```bash
# Evolution API Configuration
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=pange-bot-secret-key-2024
EVOLUTION_INSTANCE_NAME=pangeia-bot
```

---

## 🧪 Testar Integração Python

```python
from src.whatsapp.client import WhatsAppClient

# Testar conexão
client = WhatsAppClient()
success, message = client.test_connection()
print(f"Conexão: {message}")

# Enviar mensagem
success, msg_id, error = client.send_message(
    to_number="+5511999999999",
    message="Olá! Este é um teste do Pange.iA Bot via Evolution API"
)
print(f"Enviado: {success}, ID: {msg_id}")
```

---

## 🐳 Comandos Docker Úteis

### Ver logs:
```bash
docker-compose logs -f evolution-api
docker-compose logs -f postgres
```

### Reiniciar containers:
```bash
docker-compose restart
```

### Parar containers:
```bash
docker-compose down
```

### Limpar tudo (⚠️ apaga dados):
```bash
docker-compose down -v
```

### Ver status:
```bash
docker-compose ps
```

---

## 📊 Monitoramento

### Health Check automático:
O Docker verifica a saúde do container a cada 30s

### Status da instância:
```bash
curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: pange-bot-secret-key-2024"
```

---

## 🔍 Troubleshooting

### Container em loop de restart:
✅ **RESOLVIDO** - Era necessário PostgreSQL como database provider

### API não responde:
```bash
# Verificar logs
docker logs evolution_api

# Verificar se porta 8080 está livre
lsof -i:8080
```

### QR Code não aparece:
- Aguarde 10-15 segundos após criar instância
- Tente acessar via Manager UI: http://localhost:8080/manager

### Mensagens não chegam:
1. Verificar se webhook está configurado
2. Testar endpoint do webhook manualmente
3. Ver logs: `docker logs evolution_api`

---

## 📝 Notas Importantes

1. **Database**: PostgreSQL é obrigatório na v2.x+
   - Não é possível usar apenas memória (DATABASE_ENABLED=false não funciona)
   - SQLite não é suportado

2. **Persistência**: Dados são salvos nos volumes Docker:
   - `postgres_data`: Banco de dados PostgreSQL
   - `evolution_instances`: Sessões WhatsApp

3. **Backup**: Para backup, copie os volumes:
   ```bash
   docker run --rm -v evolution-setup_postgres_data:/data \
     -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
   ```

4. **Production**: Para produção, use:
   - Senha forte no PostgreSQL
   - API Key complexa
   - HTTPS com certificado válido
   - Firewall configurado

---

## ✅ Checklist de Setup

- [x] Docker Compose configurado
- [x] PostgreSQL rodando
- [x] Evolution API rodando (v2.2.3)
- [x] API respondendo (http://localhost:8080)
- [ ] Instância WhatsApp criada
- [ ] QR Code escaneado
- [ ] WhatsApp conectado
- [ ] Webhook configurado
- [ ] Teste de envio de mensagem
- [ ] Integração Python testada
- [ ] Scheduler configurado

---

## 🎯 Status Final

**Container Evolution API:** ✅ Up and running
**PostgreSQL:** ✅ Connected
**API:** ✅ Responding on port 8080
**Versão:** 2.2.3

**Próximo passo:** Criar instância WhatsApp e escanear QR Code
