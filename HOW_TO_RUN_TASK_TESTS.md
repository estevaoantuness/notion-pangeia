# 🧪 Como Executar os Testes de Criação de Tasks

## 📋 Pré-requisitos

Antes de executar os testes, certifique-se de ter:

✅ Python 3.9+
✅ Variáveis de ambiente configuradas (`.env`)
✅ Railway Postgres conectado e funcionando
✅ Notion API credentials válidas

## 🚀 Execução Rápida

### Opção 1: Executar Tudo Automaticamente

```bash
# Teste de criação de tasks
python3 test_task_creation_local.py

# Teste de atualização de status
python3 test_task_status_update.py
```

### Opção 2: Executar com Output Detalhado

```bash
# Mostra logs detalhados
python3 -u test_task_creation_local.py 2>&1 | tee task_creation.log

# Mostra logs detalhados
python3 -u test_task_status_update.py 2>&1 | tee task_status.log
```

### Opção 3: Debugar com Breakpoints

```bash
# Usar Python debugger
python3 -m pdb test_task_creation_local.py

# Ou usar IDE com debugging integrado
# VSCode, PyCharm, etc.
```

---

## 📊 O Que Cada Teste Faz

### `test_task_creation_local.py`

```
1️⃣  CRIA USUÁRIO DE TESTE
   └─ "TestBot Usuario" no Railway Postgres

2️⃣  TESTA CRIAÇÃO DE 4 TASKS
   ├─ 📱 Notificações de checkin atrasado
   ├─ 📊 Dashboard de relatórios
   ├─ 🌙 Dark mode
   └─ 🔄 Sincronizar com Supabase

3️⃣  VALIDA DADOS NO BANCO
   └─ Confirma que usuário foi criado

4️⃣  EXIBE RELATÓRIO
   └─ Mostra todos os IDs das tasks criadas
```

**Tempo de Execução:** ~15 segundos

**Resultado Esperado:**
```
✅ Usuário de teste criado: 'TestBot Usuario' (ID: 10)
✅ Tasks criadas: 4
✅ Taxa de sucesso: 100%
```

---

### `test_task_status_update.py`

```
1️⃣  ATUALIZA 2 TASKS PARA "EM ANDAMENTO"
   ├─ Task 1: A Fazer → Em Andamento
   └─ Task 2: A Fazer → Em Andamento

2️⃣  ATUALIZA 2 TASKS PARA "CONCLUÍDO"
   ├─ Task 3: A Fazer → Concluído
   └─ Task 4: A Fazer → Concluído

3️⃣  EXIBE RELATÓRIO
   └─ Mostra todas as transições de estado
```

**Tempo de Execução:** ~5 segundos

**Resultado Esperado:**
```
✅ 2 tasks movidas para 'Em Andamento'
✅ 2 tasks movidas para 'Concluído'
✅ Taxa de sucesso: 100%
```

---

## 🔍 Verificar Resultados

### No Banco de Dados (Railway)

```bash
# Ver o usuário criado
python3 -c "
from src.database.connection import get_db_engine
from sqlalchemy import text

engine = get_db_engine()
with engine.connect() as conn:
    result = conn.execute(
        text('SELECT id, name, phone, created_at FROM users WHERE name = \\'TestBot Usuario\\'')
    )
    user = result.fetchone()
    if user:
        print(f'✅ Usuário encontrado!')
        print(f'   ID: {user[0]}')
        print(f'   Nome: {user[1]}')
        print(f'   Telefone: {user[2]}')
        print(f'   Criado: {user[3]}')
    else:
        print('❌ Usuário não encontrado')
"
```

### No Notion

1. Abra seu Notion
2. Vá para a database de tasks
3. Procure por tasks criadas por "TestBot Usuario"
4. Confirme que os status foram atualizados:
   - 2 em "Em Andamento"
   - 2 em "Concluído"

---

## 🐛 Troubleshooting

### Erro: "Invalid status option"

```
❌ Invalid status option. Status option "Concluída" does not exist
```

**Solução:** Use "Concluído" (sem til) em vez de "Concluída"

```python
# ❌ ERRADO
task_creator.update_task_status(task_id, "Concluída")

# ✅ CORRETO
task_creator.update_task_status(task_id, "Concluído")
```

### Erro: "Database engine creation failed"

```
❌ Error: Could not connect to database
```

**Solução:** Verifique suas variáveis de ambiente

```bash
# Verificar variáveis
echo $DATABASE_URL
echo $NOTION_API_KEY
echo $NOTION_TASKS_DB_ID

# Se não estiverem setadas, adicione ao .env
cat .env
```

### Erro: "Notion API authentication failed"

```
❌ NotionClient: Failed to authenticate
```

**Solução:** Verifique suas credenciais Notion

```bash
# Validar token Notion
curl -X GET "https://api.notion.com/v1/users/me" \
  -H "Notion-Version: 2022-06-28" \
  -H "Authorization: Bearer YOUR_NOTION_TOKEN"
```

### Erro: "Could not find task_id"

```
❌ Task not found in Notion
```

**Solução:** Execute primeiro `test_task_creation_local.py` antes do status update

```bash
python3 test_task_creation_local.py   # Cria as tasks
python3 test_task_status_update.py    # Atualiza os status
```

---

## 📈 Monitorar Execução em Tempo Real

### Usar Logging Verboso

```bash
# Linux/Mac
LOGLEVEL=DEBUG python3 test_task_creation_local.py

# Windows
set LOGLEVEL=DEBUG
python3 test_task_creation_local.py
```

### Usar Tail para Logs

```bash
# Ver logs em tempo real
tail -f task_creation.log

# Em outra aba, executar teste
python3 test_task_creation_local.py > task_creation.log 2>&1
```

---

## 🔗 Integração com Outros Testes

### Executar Todos os Testes de Tasks

```bash
#!/bin/bash
# run_all_task_tests.sh

echo "🧪 EXECUTANDO TODOS OS TESTES DE TASKS"
echo ""

echo "1️⃣  Teste de Criação"
python3 test_task_creation_local.py
if [ $? -ne 0 ]; then
    echo "❌ Teste de criação falhou"
    exit 1
fi

echo ""
echo "2️⃣  Teste de Atualização"
python3 test_task_status_update.py
if [ $? -ne 0 ]; then
    echo "❌ Teste de atualização falhou"
    exit 1
fi

echo ""
echo "✅ TODOS OS TESTES PASSARAM!"
```

```bash
# Tornar executável e rodar
chmod +x run_all_task_tests.sh
./run_all_task_tests.sh
```

---

## 📊 Analisar Resultados

### Gerar Relatório

```bash
# Executar e salvar resultados
python3 test_task_creation_local.py > results_creation.txt 2>&1
python3 test_task_status_update.py > results_status.txt 2>&1

# Combinar relatórios
cat results_creation.txt results_status.txt > results_combined.txt

# Visualizar
cat results_combined.txt
```

### Métricas de Performance

```bash
# Medir tempo de execução
time python3 test_task_creation_local.py
time python3 test_task_status_update.py

# Resultado esperado:
# real    0m15.234s
# user    0m5.123s
# sys     0m2.456s
```

---

## 🎯 Checklist de Validação

Após executar os testes, confirme:

- [ ] Usuário "TestBot Usuario" criado no Railway (ID: 10)
- [ ] 4 tasks criadas no Notion
- [ ] Task 1 em "Em Andamento"
- [ ] Task 2 em "Em Andamento"
- [ ] Task 3 em "Concluído"
- [ ] Task 4 em "Concluído"
- [ ] Nenhum erro HTTP retornado
- [ ] Todos os logs mostram sucesso (✅)
- [ ] Taxa de sucesso = 100%
- [ ] Operações < 1 segundo cada

---

## 🚀 Próximos Testes

Após validar estes testes locais:

1. **Teste de Integração:** Testar via webhook WhatsApp
2. **Teste de Checkins:** Integrar com sistema de checkins
3. **Teste de Notificações:** Validar notificações de atraso
4. **Teste de Sincronização:** Validar Supabase sync

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique o arquivo `TASK_CREATION_TEST_REPORT.md`
2. Verifique os logs em `task_creation.log`
3. Consulte o README.md do projeto
4. Abra um issue no repositório

---

**Última Atualização:** 14 de Novembro de 2025
**Status:** ✅ Todos os testes funcionando perfeitamente
