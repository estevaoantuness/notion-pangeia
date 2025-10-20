# 🔧 Troubleshooting Railway - Bot Pangeia

## ❌ Erro: "Application not found" (404)

Esse erro significa que o Railway não consegue encontrar a aplicação. Possíveis causas:

### 1. Build falhou
**Como verificar:**
- Dashboard → Clique no serviço "botpangeia"
- Veja o ícone de status (bolinha ao lado do nome)
  - 🔴 Vermelho = Falhou
  - 🟢 Verde = Rodando
  - 🟡 Amarelo = Building

**Se está vermelho (falhou):**
- Clique em "Deployments"
- Veja os logs do último deployment
- Procure por linhas com "ERROR" ou "FAILED"

**Erros comuns:**
```
ERROR: Could not find a version that satisfies the requirement...
→ Problema no requirements.txt

ERROR: [Errno 2] No such file or directory: '/app/src'
→ Código não foi copiado corretamente

ERROR: gunicorn: command not found
→ gunicorn não instalado
```

### 2. Variáveis de ambiente faltando
**Verificar:**
- Vá em "Variables"
- Confirme que TEM estas variáveis:
  - ✅ `PORT=5000`
  - ✅ `EVOLUTION_API_URL`
  - ✅ `EVOLUTION_API_KEY`
  - ✅ `NOTION_TOKEN`
  - ✅ `NOTION_TASKS_DB_ID`

**Se faltar alguma:**
- Copie do arquivo `DEPLOY_RAILWAY_AGORA.md`
- Adicione uma por uma
- Railway vai fazer redeploy automático

### 3. Porta incorreta
**Verificar:**
- Em "Settings" → "Networking"
- Confirme que tem um domínio gerado
- Se não tiver: clique em "Generate Domain"

### 4. Dockerfile/railway.toml com problema
**Verificar no dashboard:**
- Em "Settings" → "Build"
- Deve estar usando "Dockerfile"
- Se estiver usando "Nixpacks", mude para "Dockerfile"

---

## 🩺 DIAGNÓSTICO RÁPIDO

### Passo 1: Verificar status
```
Status do serviço: [   ]  (🔴/🟢/🟡)
```

### Passo 2: Ver logs recentes
Copie as últimas 10 linhas dos logs aqui:
```
[Cole os logs aqui]
```

### Passo 3: Verificar variáveis
Quantas variáveis tem configuradas? ___

### Passo 4: URL correta?
A URL que você me passou: `botpangeia-production.up.railway.app`
Confirme no Railway se é exatamente essa.

---

## ✅ SOLUÇÃO RÁPIDA

Se tudo falhou, **DELETE o serviço e crie novamente**:

1. Railway Dashboard → Serviço "botpangeia"
2. Settings → Danger Zone → "Delete Service"
3. Crie novamente:
   - "+ New" → "GitHub Repo"
   - Escolha `estevaoantuness/notion-pangeia`
   - Settings → Build → Use "Dockerfile"
4. Adicione TODAS as variáveis de `DEPLOY_RAILWAY_AGORA.md`
5. Settings → Networking → "Generate Domain"
6. Aguarde 3-5 minutos para build

---

## 📞 ME MANDE ESSAS INFORMAÇÕES:

1. Status do serviço: 🔴/🟢/🟡
2. Últimas 5 linhas dos logs
3. Número de variáveis configuradas
4. URL exata do Railway

Com isso consigo te ajudar melhor! 🚀
