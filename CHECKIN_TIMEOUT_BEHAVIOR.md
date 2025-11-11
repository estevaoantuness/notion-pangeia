# Check-in Timeout & No-Response Behavior

## Resumo Executivo

- **Janela de resposta**: 120 minutos (2 horas) por padrão
- **Sem respostas**: Sistema limpa automaticamente após expiração
- **Próximo check-in**: Funciona normalmente (permite novo check-in)
- **Comportamento**: Silencioso (sem mensagens de erro ou timeout)

---

## Fluxo Completo: O que Acontece

### Cenário 1: Usuário RESPONDE dentro da janela (0-120 min)

```
18:11:00 (PT) → Bot envia: "🌆 Finalizando o dia!..."
                └─ Sistema REGISTRA check-in pendente com ID único
                └─ Janela de resposta ABRE: 18:11:00 até 20:11:00

18:45:00       → Usuário responde: "Fiz X tarefas, Y fica pro amanhã"
                └─ Sistema DETETA que há check-in pendente
                └─ Processa resposta como FEEDBACK (não como comando)
                └─ Armazena feedback no banco de dados ✅
                └─ Envia confirmação: "Obrigado! Registrei sua resposta. 👍"
                └─ Limpa check-in pendente da memória
```

**Status**: ✅ SUCESSO - Feedback registrado

---

### Cenário 2: Usuário NÃO RESPONDE (passa 120 min)

```
18:11:00 (PT) → Bot envia: "🌆 Finalizando o dia!..."
                └─ Sistema REGISTRA check-in pendente
                └─ Janela ABRE: 18:11:00 até 20:11:00

20:11:01       → Janela EXPIRA (120 minutos passaram)
                └─ Próxima mensagem do usuário NÃO será tratada como resposta
                └─ Será processada como COMANDO NORMAL via NLP
                └─ Feedback NÃO é registrado ❌

20:30:00       → Usuário escreve: "Como faço pra adicionar uma task?"
                └─ Sistema verifica: "há check-in pendente?" → NÃO (expirou)
                └─ Processa como comando normal
                └─ NLP responde: "Para adicionar task..."
```

**Status**: ❌ FEEDBACK PERDIDO - Será ignorado após timeout

---

## Comportamento do Sistema

### 1️⃣ **Recordação do Check-in Enviado**

```python
# Quando bot envia check-in, registra:
pending = PendingCheckin(
    checkin_id="checkin-Estevao Antunes-20251111-181100-6492ee",
    checkin_type="closing",  # "metas", "planning", "status", "closing", etc
    sent_timestamp=2025-11-11 18:11:00,
    response_window_minutes=120  # 2 HORAS
)
```

### 2️⃣ **Verificação de Timeout**

```python
# Cada vez que usuário envia mensagem:
pending = tracker.get_pending_checkin(user_id)

if pending:
    if pending.is_expired:  # elapsed > (120 * 60) segundos?
        del self._pending[user_id]  # Remove da memória
        return None  # Trata como comando normal
    else:
        # Dentro da janela! Processa como feedback
        feedback_handler.process_response(pending)
else:
    # Nenhum check-in pendente - comando normal
    command_processor.process(message)
```

### 3️⃣ **Limpeza Automática**

```python
# A cada 5 minutos (300 segundos):
expired_users = [user for user in pending if user.is_expired]
for user in expired_users:
    del self._pending[user]  # Remove da memória
    logger.info(f"Auto-cleanup: removed expired check-in for {user}")
```

---

## Impacto Prático para Você

### Se você NÃO responder em 2 horas:

| Tempo | Evento | Resultado |
|-------|--------|-----------|
| 18:11 | Recebe "Finalizando o dia!" | Janela abre ⏱️ |
| 19:00 | Responde "Fiz tudo!" | ✅ Feedback registrado |
| 19:30 | Não respondeu mais | Janela ainda aberta ⏱️ (50 min restantes) |
| 20:10 | Ainda não respondeu | ⚠️ Faltam 1 minuto! |
| 20:11 | TIMEOUT! Janela FECHA | ❌ Janela fechou |
| 20:30 | Escreve "oi" | ⚠️ Processado como comando, não feedback |
| 21:46 | Recebe novo check-in "Reflexão" | ✅ Nova janela abre (120 min) |

---

## Configuração Atual

**Arquivo**: `src/scheduler/scheduler.py:473`

```python
tracker.record_sent_checkin(
    user_id=nome,
    person_name=nome,
    checkin_type=checkin_key,
    checkin_message=question,
    response_window_minutes=120  # ← AQUI (pode ser customizado)
)
```

---

## Como Mudar o Timeout (se necessário)

Se você quer **mais** ou **menos** tempo para responder:

**Aumentar para 3 horas (180 min)**:
```python
response_window_minutes=180  # Em vez de 120
```

**Reduzir para 1 hora (60 min)**:
```python
response_window_minutes=60  # Em vez de 120
```

**Tornar ilimitado**:
```python
response_window_minutes=999999  # Praticamente infinito
```

---

## Próximo Check-in

**Importante**: Após expiração, você pode receber um **novo check-in** normalmente no próximo horário agendado:

```
18:11 → 1º Check-in "Fechamento" (timeout 20:11)
        └─ Não responde até 20:11
        └─ Janela FECHA ❌

21:46 → 2º Check-in "Reflexão" (NOVO, timeout 23:46)
        └─ Janela completamente NOVA
        └─ Pode responder normalmente
        └─ ✅ Feedback será registrado
```

---

## Visibilidade de Timeout

**Atualmente**: O sistema é **silencioso** sobre expiração:
- ❌ Bot NÃO envia mensagem "Janela de resposta expirou"
- ❌ Você NÃO vê aviso de timeout
- ℹ️ Apenas aparecem logs internos do servidor

**Se quiser avisos**, isso pode ser implementado:
- Option 1: Enviar mensagem automática ao expirar
- Option 2: Mostrar feedback no painel/dashboard

---

## Resumo

| Pergunta | Resposta |
|----------|----------|
| Quanto tempo tenho? | **2 horas (120 min)** |
| Depois expira? | ✅ Sim, silenciosamente |
| Posso responder depois? | ❌ Não, será comando normal |
| Qual o impacto? | Feedback não registrado |
| Próximo check-in? | ✅ Funciona normalmente com nova janela |
| Tem aviso? | ❌ Não (silencioso) |
| Posso customizar? | ✅ Sim (alterar minutos) |

---

**Última atualização**: 2025-11-11 21:30 UTC
**Arquivo de configuração**: `src/checkins/pending_tracker.py` (linha 30)
