# Contextual Follow-up Messages - Status Report

**Date**: 2025-11-11 21:51 UTC  
**Status**: ✅ DEPLOYED & OPERATIONAL

---

## What Was Implemented

Contextual follow-up messages that adapt to **time of day** and **actual task progress**.

### System Flow

```
18:11:00 → Bot sends check-in → System records pending
18:11-18:26 → Follow-up window (15 minutes)
18:26:00 → Follow-up job executes
         ├─ Checks if user responded
         ├─ YES → Skip follow-up ✓
         └─ NO → Send contextual follow-up
                 ├─ Detect current hour
                 ├─ Fetch task progress (done/total)
                 ├─ Select period-appropriate template
                 └─ Format with real data → Send
```

---

## Follow-up Messages by Period

### 🌅 Morning (00:00 - 11:59)
**Context**: User starting their day (Metas check-in)  
**Content**: Simple motivational, no progress data  
**Examples**:
- "🌅 E aí! Ainda não respondeu a meta de hoje. Qual a prioridade? 🎯"
- "☀️ Bom dia! Qual é o foco principal para hoje? Vamo começar?"
- 5 variations total

### 📊 Afternoon (12:00 - 17:59)
**Context**: User mid-day (Planning/Status check-ins)  
**Content**: Shows progress stats {done}/{total}/{percent}  
**Examples**:
- "📊 Opa! Você fez **{done}/{total}** tarefas (**{percent}%**). Consegue responder rápido? 💪"
- "💡 E aí! Você conquistou **{percent}%** do dia. Como está o ritmo? Algum bloqueio?"
- 7 variations total

### 🌆 Evening (18:00 - 23:59)
**Context**: User finishing day (Closing check-in)  
**Content**: Shows progress with retrospective tone {done}/{total}/{percent}  
**Examples**:
- "🌆 Reta final! Você fez **{done}/{total}** (**{percent}%**). O que fica para amanhã? 🎯"
- "🎉 Dia produtivo! **{done}/{total}** concluídas (**{percent}%**). Como foi? 💪"
- 7 variations total

---

## Technical Implementation

### Code Locations

| Component | File | Method | Lines |
|-----------|------|--------|-------|
| **Messages** | `config/replies.yaml` | N/A | `checkin_followups` section |
| **Generator** | `src/messaging/humanizer.py` | `get_contextual_followup()` | 361-407 |
| **Scheduler** | `src/scheduler/scheduler.py` | `_send_followup_if_needed()` | 513-585 |

### Data Flow

1. **User receives check-in** (18:11)
   - System records pending check-in with ID

2. **Follow-up job scheduled** (15 min after send)
   - APScheduler creates DateTrigger job for 18:26

3. **Follow-up job executes** (18:26)
   - Fetch TasksManager data → count done/total
   - Get current hour → determine period (morning/afternoon/evening)
   - Call `get_contextual_followup(hour, done, total)`
   - Format placeholders: `{done}=4, {total}=6, {percent}=67`
   - Send via WhatsApp with SID tracking

4. **Graceful degradation**
   - If TasksManager fails → continue without progress data
   - If Notion unavailable → send generic message (period still applies)
   - No exceptions propagated to user

---

## Production Status

### Railway Logs (Latest)
```
2025-11-11 21:49:18 - Scheduler ACTIVATED ✅
2025-11-11 21:49:18 - Check-in jobs scheduled correctly ✅
2025-11-11 21:49:18 - File lock working (workers skip init) ✅
2025-11-11 21:49:18 - No syntax errors ✅
```

### Active Jobs
- ✅ Check-in Reflexão scheduled for 21:54
- ✅ Daily rescheduler configured for 00:05

---

## Example Follow-ups in Action

### Scenario 1: Afternoon, 60% Progress
```
User doesn't respond to 14:00 planning check-in
14:15 → Follow-up sent:

"📊 Opa! Você fez 3/5 tarefas (60%). Consegue responder rápido? 💪"
```

### Scenario 2: Evening, 40% Progress
```
User doesn't respond to 18:11 closing check-in
18:26 → Follow-up sent:

"🌆 Reta final! Você fez 2/5 (40%). O que fica para amanhã? 🎯"
```

### Scenario 3: Morning, No Progress Data Available
```
Morning check-in, Notion temporarily unavailable
08:15 → Follow-up sent (graceful fallback):

"💪 Começando o dia! Qual meta vamos atacar primeiro?"
```

---

## Configuration

### To Change Follow-up Delay (currently 15 min)
Edit `src/scheduler/scheduler.py:481`:
```python
followup_time = datetime.now(TZ) + timedelta(minutes=15)  # Change this
```

### To Add More Messages
Edit `config/replies.yaml` `checkin_followups` section:
```yaml
afternoon:
  - "Your new message here {done}/{total} ({percent}%)"
```

### To Disable Follow-ups
Comment out lines 477-498 in `src/scheduler/scheduler.py` (`try` block in `_send_checkin()`)

---

## Monitoring

### Logs to Watch
```
# Follow-up scheduled:
⏰ Follow-up agendado para 18:26:00

# Follow-up sent:
📬 ENVIANDO FOLLOW-UP PARA [user]
📊 Progresso: 4/6 tarefas (67%)
✅ Follow-up enviado para [user]. SID: ...

# Follow-up skipped (user already responded):
✓ Follow-up skipped: [user] já respondeu

# Error sending:
❌ Erro ao enviar follow-up para [user]: ...
```

---

**Last Updated**: 2025-11-11 21:51 UTC  
**Deployment Commit**: `98d193c`  
**Next Step**: Monitor first real follow-up messages when users don't respond to check-ins
