# Comando "mostre" - Passos restantes

## ✅ JÁ IMPLEMENTADO:

1. ✅ `src/notion/client.py` - Métodos `get_task_details()` e helpers
2. ✅ `src/messaging/task_details.py` - Funções de formatação
3. ✅ `src/commands/handlers.py` - Handler `handle_show_task()`

## 🔧 FALTA IMPLEMENTAR:

### 1. Adicionar sinônimos no normalizer

**Arquivo: `src/commands/normalizer.py`**

Adicionar padrão para detectar "mostre N":

```python
# Adicionar no dicionário de padrões (procure por INTENT_PATTERNS)
'show_task': [
    r'(?:mostre?|mostra|ver|veja|abra?|detalhes?|info)\s+(?:a\s+)?(\d+)',
    r'(?:o\s+)?que\s+[eé]\s+(?:a\s+)?(\d+)',
    r'(\d+)\s+(?:detalhes?|info)'
],
```

### 2. Registrar intent no processor

**Arquivo: `src/commands/processor.py`**

Adicionar handler no método `_execute_intent()`:

```python
# Adicionar após o handler de 'progress'
if intent == 'show_task':
    task_index = entities.get('index')
    if task_index:
        return self.handlers.handle_show_task(person_name, task_index)
    else:
        return True, "❌ Informe o número da tarefa.\n\nExemplo: mostre 2"
```

### 3. Reiniciar Flask

```bash
pkill -f "python.*app.py"
PYTHONPATH=. nohup python3 src/webhook/app.py > /tmp/flask.log 2>&1 &
```

### 4. Testar

```
mostre 2
ver 3
detalhes 1
info 5
```

## 📝 OBSERVAÇÕES:

- O comando já funciona com o mapeamento de tasks existente
- Busca detalhes completos do Notion (título, descrição, status, prioridade, deadline, tags)
- Formata com emojis e informações de urgência
- Inclui link direto para o Notion
- Mostra ações rápidas (feito, andamento, bloqueada)

## 🎯 PRÓXIMOS PASSOS:

1. Adicionar padrão regex no normalizer
2. Registrar intent no processor
3. Reiniciar Flask
4. Testar comando
5. (Opcional) Adicionar "mostre 2" no tutorial de ajuda
