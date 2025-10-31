# 🔧 Guia de Correção: OpenAI Client None no Railway

## 🐛 Problema Identificado

O bot falha ao processar comandos com o erro:
```
AttributeError: 'NoneType' object has no attribute 'chat'
```

**Causa:** OpenAI client retorna `None` porque `OPENAI_API_KEY` não está configurada ou está vazia no Railway.

---

## ✅ Solução

### 1. Verificar Estado Atual

Acesse o endpoint de debug:
```bash
curl https://botpangeia-production.up.railway.app/debug
```

Verifique se `openai_client.is_none` está como `true` - isso confirma o problema.

### 2. Configurar OPENAI_API_KEY no Railway

**Passo a passo:**

1. Acesse o [Railway Dashboard](https://railway.app)
2. Entre no projeto `talented-expression`
3. Selecione o serviço `botpangeia`
4. Vá em **Variables**
5. Procure por `OPENAI_API_KEY`

**Verifique:**
- ✅ A chave deve ter **164 caracteres**
- ✅ Deve começar com `sk-proj-`
- ❌ NÃO pode estar truncada
- ❌ NÃO pode ter espaços ou quebras de linha

**Configurar chave:**
```bash
# Use a chave OpenAI do projeto (164 caracteres)
# Formato: sk-proj-XXXXX...
railway variables set OPENAI_API_KEY="[SUA_CHAVE_AQUI]"
```

### 3. Forçar Redeploy

Após atualizar a variável:
1. Vá em **Deployments**
2. Clique em **Deploy** no último commit
3. Aguarde ~2-3 minutos

### 4. Verificar Correção

Teste novamente o endpoint de debug:
```bash
curl https://botpangeia-production.up.railway.app/debug
```

**Resposta esperada:**
```json
{
  "openai_client": {
    "is_none": false,
    "type": "<class 'openai.OpenAI'>"
  },
  "environment_variables": {
    "OPENAI_API_KEY": {
      "present": true,
      "length": 164,
      "prefix": "sk-proj-JJ"
    }
  }
}
```

### 5. Testar Bot

Envie uma mensagem de teste via WhatsApp:
```
Usuário: "oi"
Bot: "E aí! Bora ver suas tasks?"

Usuário: "bora"
Bot: [deve listar as tasks corretamente]
```

---

## 🔍 Melhorias Implementadas Neste Commit

1. **Logs aprimorados** em `config/openai_config.py`:
   - Agora mostra claramente quando a API key não está configurada
   - Exibe o comprimento da chave quando encontrada

2. **Verificação adicional** em `src/agents/conversational_agent.py`:
   - Checa se o client é `None` antes de tentar usar
   - Retorna erro descritivo se não estiver configurado

3. **Endpoint /debug melhorado**:
   - Mostra status de todas variáveis de ambiente críticas
   - Exibe se o OpenAI client foi inicializado corretamente
   - Útil para diagnosticar problemas de configuração

---

## 📋 Checklist de Deploy

- [ ] Atualizar `OPENAI_API_KEY` no Railway (164 caracteres)
- [ ] Verificar outras variáveis críticas (NOTION_TOKEN, etc)
- [ ] Fazer commit das mudanças
- [ ] Push para GitHub
- [ ] Railway faz deploy automático
- [ ] Acessar `/debug` para confirmar
- [ ] Testar bot via WhatsApp

---

## 🚨 Alternativa: Deploy no Render

Se preferir migrar do Railway para Render:

1. **Criar novo Web Service no Render**
2. **Conectar ao repositório GitHub**
3. **Configurar variáveis de ambiente** (todas as mesmas do Railway)
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT src.webhook.app:app`

---

## 📞 Contato

Se o problema persistir após seguir este guia, verifique os logs do Railway em **Deployments > Logs**.

**Última atualização:** 31/10/2025
