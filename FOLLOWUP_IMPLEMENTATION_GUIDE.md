# Follow-up Messages Implementation Guide

## Status: ✅ DEPLOYED

Follow-up messages for unanswered check-ins foram implementadas e deployadas em produção.

---

## O Que Foi Implementado

### 1. **15 Mensagens de Follow-up Genéricas**
```yaml
# config/replies.yaml - seção checkin_followups
- "Oi! Vi que você não respondeu ao check-in. Tudo bem por aí? 😊"
- "Só lembrando do check-in de mais cedo. Consegue responder quando puder?"
- "Hey! Ainda preciso da sua resposta. Como estão as coisas?"
- ... (12 more variations)
```

**Características:**
- ✅ 15 variações diferentes (humanizado, não repetitivo)
- ✅ Genéricas (funcionam para qualquer tipo de check-in)
- ✅ Tom amigável e não invasivo
- ✅ Seleção aleatória (cada follow-up é único)

---

## Fluxo Implementado

```
Horário    | Evento                      | Ação
-----------|-----------------------------|-----------------------------------------
18:11:00   | Bot envia check-in          | ✅ Mensagem enviada ao usuário
           |                             | ✅ Check-in registrado em pending_tracker
           |                             | ✅ Follow-up agendado para 18:26
-----------|-----------------------------|-----------------------------------------
18:11-18:26| Janela aberta               | Usuário pode responder
-----------|-----------------------------|-----------------------------------------
18:26:00   | Job de follow-up executa    | ✅ Verifica: usuário respondeu?
           |                             |
           | SIM → Já respondeu          | ⏭️  Follow-up SKIPPED
           | NÃO → Não respondeu         | ✅ Follow-up ENVIADO
-----------|-----------------------------|-----------------------------------------
18:26-20:11| Janela ainda aberta         | Usuário ainda pode responder
-----------|-----------------------------|-----------------------------------------
20:11:00   | TIMEOUT                     | ❌ Janela fecha
           |                             | Próximas mensagens = commands normais
-----------|-----------------------------|-----------------------------------------
```

---

## Comportamento em Detalhes

### Cenário 1: Usuário Responde ANTES do Follow-up (18:11 → 18:25)

```
18:11:00 → Bot: "🌆 Finalizando o dia!..."
          └─ Registra pending check-in
          └─ Agenda follow-up para 18:26

18:20:00 → Usuário: "Fiz tudo que planejei!"
          └─ Sistema detecta pending check-in
          └─ Processa como FEEDBACK ✅
          └─ Remove de pending_tracker
          └─ Envia confirmação

18:26:00 → Follow-up job executa
          └─ Procura pending check-in para usuário
          └─ NÃO encontra (foi removido)
          └─ Log: "✓ Follow-up skipped: usuário já respondeu"
          └─ Nenhuma mensagem enviada ✅
```

**Resultado**: Usuário recebe 1 mensagem total (check-in inicial)

---

### Cenário 2: Usuário Responde DEPOIS do Follow-up (18:26 → 20:11)

```
18:11:00 → Bot: "🌆 Finalizando o dia!..."
          └─ Registra pending check-in
          └─ Agenda follow-up para 18:26

18:26:00 → Follow-up job executa
          └─ Procura pending check-in para usuário
          └─ ENCONTRA (usuário não respondeu)
          └─ Envia follow-up aleatório ✅
          └─ Ex: "Só lembrando do check-in de mais cedo..."

18:40:00 → Usuário: "Terminei algumas tarefas"
          └─ Sistema detecta pending check-in
          └─ Processa como FEEDBACK ✅
          └─ Remove de pending_tracker
          └─ Envia confirmação
```

**Resultado**: Usuário recebe 2 mensagens (check-in + follow-up)

---

### Cenário 3: Usuário NÃO Responde (18:11 → 20:11)

```
18:11:00 → Bot: "🌆 Finalizando o dia!..."
          └─ Registra pending check-in
          └─ Agenda follow-up para 18:26

18:26:00 → Follow-up job executa
          └─ ENCONTRA pending check-in
          └─ Envia follow-up ✅
          └─ Ex: "Tá corrido hoje? Quando puder, responde!"

20:11:00 → TIMEOUT
          └─ Pending check-in expira
          └─ Auto-cleanup remove da memória

20:30:00 → Usuário: "Como faço para criar uma task?"
          └─ Procura pending check-in: NÃO encontra (expirou)
          └─ Processa como COMANDO normal
          └─ NLP responde ao comando
          └─ Feedback do check-in é PERDIDO ❌
```

**Resultado**: Usuário recebe 2 mensagens (check-in + follow-up), feedback perdido após timeout

---

## Código-Chave

### Agendamento do Follow-up
```python
# Em src/scheduler/scheduler.py - método _send_checkin() linha 481
followup_time = datetime.now(TZ) + timedelta(minutes=15)
self.scheduler.add_job(
    func=self._send_followup_if_needed,
    trigger=DateTrigger(run_date=followup_time),
    id=f"followup-{checkin_id}",
    kwargs={'user_id': nome, 'checkin_id': checkin_id, ...}
)
```

### Envio do Follow-up
```python
# Em src/scheduler/scheduler.py - método _send_followup_if_needed() linha 513
pending_checkin = tracker.get_pending_checkin(user_id)

if pending_checkin and pending_checkin.checkin_id == checkin_id:
    # Usuário não respondeu
    followup_msg = self.humanizer.get_followup_message()  # Aleatória!
    self.whatsapp_sender.send_message(person_name=user_id, message=followup_msg)
else:
    # Usuário já respondeu
    logger.info(f"✓ Follow-up skipped: {user_id} já respondeu")
```

### Obter Mensagem Aleatória
```python
# Em src/messaging/humanizer.py - método get_followup_message() linha 349
def get_followup_message(self) -> str:
    followups = self.replies.get('checkin_followups', [])
    return random.choice(followups)  # Uma das 15 mensagens
```

---

## Como Customizar

### Adicionar mais mensagens de follow-up

Edit `config/replies.yaml` seção `checkin_followups`:
```yaml
checkin_followups:
  - "Mensagem 1..."
  - "Mensagem 2..."
  # Adicione quantas quiser aqui
```

### Mudar o intervalo de 15 minutos

Edit `src/scheduler/scheduler.py` linha 481:
```python
# Mudar para 30 minutos:
followup_time = datetime.now(TZ) + timedelta(minutes=30)

# Ou para 5 minutos:
followup_time = datetime.now(TZ) + timedelta(minutes=5)
```

### Desabilitar follow-ups completamente

Comment out o bloco de agendamento (linhas 477-498 em src/scheduler/scheduler.py):
```python
# try:
#     followup_time = ...
#     self.scheduler.add_job(...)
# except Exception as e:
#     ...
```

---

## Logs Para Monitoramento

Procure por essas linhas nas logs do Railway (`railway logs --service web`):

**Follow-up Agendado com Sucesso:**
```
⏰ Follow-up agendado para 18:26:00
```

**Follow-up Enviado:**
```
📬 ENVIANDO FOLLOW-UP PARA Estevao Antunes
✅ Follow-up enviado para Estevao Antunes. SID: 3EB0...
📨 Mensagem: Oi! Vi que você não respondeu...
```

**Follow-up Skipped (Usuário já respondeu):**
```
✓ Follow-up skipped: Estevao Antunes já respondeu ao check-in checkin-...
```

**Erro ao Enviar Follow-up:**
```
❌ Erro ao enviar follow-up para Estevao Antunes: [erro aqui]
```

---

## Arquivos Modificados

| Arquivo | Linha | Mudança |
|---------|-------|---------|
| `config/replies.yaml` | 196-211 | Adicionada seção `checkin_followups` com 15 mensagens |
| `src/messaging/humanizer.py` | 349-362 | Adicionado método `get_followup_message()` |
| `src/scheduler/scheduler.py` | 477-498 | Agendamento de follow-up em `_send_checkin()` |
| `src/scheduler/scheduler.py` | 513-561 | Adicionado método `_send_followup_if_needed()` |

---

## Testes Realizados

✅ **Compilação**: Nenhum erro de sintaxe
✅ **Imports**: Todos os módulos importam corretamente
✅ **Deployment**: Scheduler inicializa sem erros
✅ **Worker Lock**: File lock funciona (apenas 1 worker inicializa)
✅ **APScheduler**: Jobs agendados corretamente

---

## Próximas Melhorias Opcionais

1. **Múltiplos Follow-ups**: Enviar 2ª mensagem depois de 30min (se ainda não respondeu)
2. **Aviso de Timeout**: Enviar mensagem quando janela expira ("Não consegui registrar sua resposta")
3. **Dashboard**: Mostrar estatísticas de resposta (quantos responderam ao check-in vs follow-up)
4. **Customização por Horário**: Diferentes mensagens para diferentes horários

---

**Última Atualização**: 2025-11-11 21:35 UTC
**Deploy Status**: ✅ Em Produção
**Commit**: c656c62
