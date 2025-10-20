# 🔥 Railway Quick Fixes - Erros Comuns

## ❌ ERRO 1: "ModuleNotFoundError: No module named 'src'"

**Causa:** Código src/ não foi copiado no build

**Solução:**
Verificar que Dockerfile tem:
```dockerfile
COPY . .
```

**Fix rápido:** Garantir que src/ está no git:
```bash
git add src/
git commit -m "Ensure src is tracked"
git push
```

---

## ❌ ERRO 2: "ERROR: Could not find a version that satisfies"

**Causa:** Problema no requirements.txt

**Solução:**
Simplificar requirements.txt, remover versões específicas

---

## ❌ ERRO 3: "Port 5000 already in use"

**Causa:** Variável PORT conflitando

**Solução no Railway:**
1. Variables → Remover PORT
2. Deixar Railway definir automaticamente
3. Dockerfile já usa $PORT

---

## ❌ ERRO 4: "exec /bin/sh: exec format error"

**Causa:** Plataforma errada (ARM vs x86)

**Solução:** Mudar Dockerfile primeira linha:
```dockerfile
FROM --platform=linux/amd64 python:3.10-slim
```

---

## ❌ ERRO 5: "Application error" sem logs

**Causa:** App não está escutando na porta correta

**Solução:** Verificar que app.py tem:
```python
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

---

## ❌ ERRO 6: Build passa mas app não responde (404)

**Causa:** Domínio não foi gerado ou está errado

**Solução:**
1. Settings → Networking
2. Delete o domínio atual
3. "Generate Domain" novamente
4. Use a nova URL

---

## 🚀 SOLUÇÃO UNIVERSAL (se nada funcionar)

### Opção A: Usar Nixpacks (mais simples)

1. **Delete o Dockerfile temporariamente:**
   ```bash
   mv Dockerfile Dockerfile.backup
   git add Dockerfile
   git commit -m "Remove Dockerfile to use Nixpacks"
   git push
   ```

2. **Railway vai usar Nixpacks automaticamente**
   - Detecta Python pelo requirements.txt
   - Usa Procfile para start command

3. **Procfile já está correto:**
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```

### Opção B: Render (alternativa ao Railway)

Se Railway continuar falhando:
1. https://render.com → New Web Service
2. Connect: estevaoantuness/notion-pangeia
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Add environment variables
6. Deploy!

---

## 📋 ME ENVIE ESSES LOGS

Para diagnosticar, preciso saber:

1. **Qual linha do log tem "ERROR" ou "FAILED"?**
2. **O build completou ou falhou no meio?**
3. **App iniciou mas crashou, ou nem iniciou?**

Cole aqui as últimas 20 linhas dos logs! 🙏
