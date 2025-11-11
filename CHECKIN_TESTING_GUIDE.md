# Check-in Response Testing Guide

## Resumo Rápido

Disparamos check-ins automaticamente via scheduler. Quando Estevão responde no WhatsApp, a resposta é:
1. ✅ Detectada como resposta a check-in (não comando)
2. ✅ Salva no PostgreSQL tabela `checkin_feedback`
3. ✅ Classificada por intent via NLP
4. ✅ Bot envia confirmação: "Obrigado! Registrei sua resposta. 👍"

---

## Como Testar

### Opção 1: Manual (Agora)

1. **Railway Dashboard**: Abra seu projeto
2. **Clique em "Check-in Test"** no menu scheduler
3. Escolha tipo: `planning`, `status`, `closing`, etc.
4. Check-in será enviado para Estevão via WhatsApp

### Opção 2: Automático (Scheduler)

O bot dispara automaticamente:
- **Metas**: 08:00
- **Planning (Tarde)**: 13:30
- **Status**: 15:30
- **Closing**: 18:00
- **Reflexão**: 22:00

Apenas aguarde o horário e deixe Estevão responder.

### Opção 3: Webhook Manual (Curl)

```bash
# Dispara check-in de teste
curl -X POST https://seu-app.railway.app/webhook/test/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "Estevao Antunes",
    "checkin_type": "planning",
    "phone": "+554191851256"
  }'
```

---

## Visualizar Respostas Salvas

### Via Railway Database Console

1. **Railway Dashboard** → Seu projeto
2. **Plugins** → PostgreSQL
3. **Connect** → Browser (abre pgAdmin)
4. **Query Editor**, cole:

```sql
SELECT * FROM checkin_feedback
WHERE user_id = 'Estevao Antunes'
ORDER BY created_at DESC
LIMIT 10;
```

### Colunas Importantes

| Coluna | Descrição |
|--------|-----------|
| `id` | ID único da resposta |
| `user_id` | Quem respondeu |
| `checkin_id` | ID do check-in (rastreia qual pergunta) |
| `checkin_type` | Tipo: planning, status, closing, etc |
| `checkin_message` | Que pergunta o bot fez |
| `response_text` | O que o usuário respondeu |
| `response_intent` | Classificação NLP: progressing/blocked/completed/other |
| `response_time_seconds` | Quantos segundos levou para responder |
| `checkin_timestamp` | Quando o check-in foi enviado |
| `response_timestamp` | Quando o usuário respondeu |
| `created_at` | Quando foi salvo no banco |

---

## Flow Completo (Exemplo Real)

### 1️⃣ Check-in Enviado
```
[15:30] Bot 🤖: ⏰ Status das 15:30!
         Progresso do dia OK? Conseguindo avançar?

[Backend registra em pending_tracker:
 - checkin_id: checkin-Estevao-20251111-153000-abc123
 - checkin_type: "status"
 - sent_timestamp: 2025-11-11 15:30:00
 - response_window_minutes: 120
]
```

### 2️⃣ Usuário Responde
```
[15:35] Estevao 👨: conseguindo bem, melhorando o bot!

[Webhook recebe...]
```

### 3️⃣ Webhook Processa
```
[Backend verifica:]
1. ✓ Há check-in pendente para Estevao
2. ✓ Ainda dentro da janela de 120 min
3. ✓ Classifica intent: "progressing"
4. ✓ Salva no PostgreSQL

[INSERT INTO checkin_feedback:
 - response_text: "conseguindo bem, melhorando o bot!"
 - response_intent: "progressing"
 - response_time_seconds: 300 (5 minutos)
]
```

### 4️⃣ Confirmação ao Usuário
```
[15:35] Bot 🤖: Obrigado! Registrei sua resposta. 👍
```

### 5️⃣ Visualizar no Banco
```sql
SELECT response_text, response_intent, response_time_seconds
FROM checkin_feedback
WHERE checkin_id = 'checkin-Estevao-20251111-153000-abc123';

-- Resultado:
-- response_text       | response_intent | response_time_seconds
-- "conseguindo bem..." | progressing     | 300
```

---

## Intent Classifications

Possíveis valores de `response_intent`:

| Intent | Significado | Exemplo |
|--------|-------------|---------|
| `progressing` | Fazendo progresso | "conseguindo bem" |
| `blocked` | Travado em algo | "estou com dúvida" |
| `completed` | Completou algo | "terminei" |
| `question` | Fez pergunta | "como funciona?" |
| `reflection` | Refletindo | "tava pensando" |
| `other` | Não se enquadra | resposta aleatória |

---

## Links Úteis

### Railway
- **Dashboard**: https://railway.app/dashboard
- **Project**: Seu projeto Pange.iA Bot
- **Database**: Plugin PostgreSQL

### Visualizar Respostas
```
Railway → Seu Projeto → Plugins → PostgreSQL → Connect → Browser
```

### Logs
```
Railway → Seu Projeto → Logs → Filtrar por "check-in response recorded"
```

---

## Troubleshooting

### Problema: Check-in não está sendo salvo
**Solução**:
1. Verifique se PostgreSQL está conectado
2. Check logs do Railway: `ERROR saving feedback`
3. Verifique se tabela `checkin_feedback` existe

### Problema: Response não é detectada como check-in
**Solução**:
1. Verifique se `pending_tracker.record_sent_checkin()` foi chamado
2. Check logs: `Recorded pending check-in`
3. Janela pode ter expirado (padrão 120 min)

### Problema: Intent classificado como "other"
**Solução**:
1. Resposta não corresponde a padrões conhecidos
2. Verifique `response_text` nos logs
3. Pode ser necessário treinar NLP com mais exemplos

---

## Estatísticas de Respostas

Para ver estatísticas agregadas:

```sql
SELECT
    checkin_type,
    response_intent,
    COUNT(*) as count,
    AVG(response_time_seconds) as avg_response_time_sec
FROM checkin_feedback
WHERE user_id = 'Estevao Antunes'
GROUP BY checkin_type, response_intent
ORDER BY checkin_type, count DESC;
```

---

## Próximos Passos

- ✅ Resposta é detectada e salva
- 🔄 Próximo: Criar dashboard visual das respostas
- 🔄 Próximo: Analytics de progresso do usuário
- 🔄 Próximo: Feedback baseado em padrões de respostas

---

**Status**: ✅ Check-in response system fully operational
**Data**: 2025-11-11
**Teste Recomendado**: Dispare em production e aguarde resposta
