# 🚀 Deploy no Railway

O app estava em Heroku, mas agora está no Railway. Aqui está como fazer deploy.

## 1️⃣ Verificar Status do Railway

```bash
railway status
```

Você deve ver algo como:
```
Project: notion-pangeia
Service: bot (running)
```

## 2️⃣ Ver Logs em Tempo Real

```bash
# Ver últimos 100 linhas
railway logs --tail 100

# Ver logs contínuos (tipo tail -f)
railway logs -f
```

## 3️⃣ Fazer Deploy (Automático via Git)

Railway detecta automaticamente mudanças via Git:

```bash
# 1. Verificar status
git status

# 2. Adicionar mudanças
git add .

# 3. Commit
git commit -m "Fix: checkin webhook integration"

# 4. Push para Railway (se conectado via Railway CLI)
git push

# OU apenas fazer push no repositório (Railway faz deploy automático)
```

## 4️⃣ Verificar Variáveis de Ambiente

```bash
railway variables
```

Deve ter:
- `DATABASE_URL` ✅
- `SUPABASE_URL` ✅
- `SUPABASE_ANON_KEY` ✅
- Outras...

## 5️⃣ Redeploy Manual

Se quiser redeploy sem novo commit:

```bash
# Trigger redeploy
railway deploy
```

## 6️⃣ Testar no Telefone Real

1. Envie mensagem WhatsApp para **+55 41 9185-1256** (Estevão)
2. Aguarde resposta do bot
3. Verifique logs:
   ```bash
   railway logs -f | grep -i "estevao\|checkin"
   ```

## 7️⃣ Troubleshooting

### Erro de conexão com banco
```bash
railway logs -f | grep -i "database\|connection"
```

### Webhook não recebe mensagens
```bash
railway logs -f | grep -i "webhook\|received"
```

### Ver todas as variáveis
```bash
railway variables ls
```

## 📱 Link do App

Seu bot está em: **https://sara-ai-production-2a4f.up.railway.app**

(ou confira com `railway domains`)

---

**Próximos passos:**
1. Faça commit das mudanças
2. Verifique logs para confirmar deploy
3. Envie mensagem WhatsApp para testar
4. Veja dados com `python3 view_postgres_data.py`
