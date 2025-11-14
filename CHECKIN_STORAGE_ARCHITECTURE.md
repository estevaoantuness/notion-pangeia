# 🗄️ Arquitetura de Armazenamento de Respostas de Checkin

**Data:** 13 de Novembro de 2025
**Versão:** 2.3
**Status:** ✅ Funcionando em Produção

---

## 📍 Localização das Respostas

### 1️⃣ Banco de Dados Primário: Railway Postgres

**URL de Conexão:** `postgresql://postgres:YmKpRTbrCYQLkFuaKDVhuBSEiVfWlxqc@tramway.proxy.rlwy.net:36286/railway`

**Tabela:** `daily_checkins`

```sql
CREATE TABLE daily_checkins (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  date DATE NOT NULL,

  -- Período Manhã (06:00)
  morning_question TEXT,      -- Pergunta enviada
  morning_answer TEXT,        -- Resposta do usuário ← ARMAZENADA AQUI

  -- Período Tarde (12:00)
  afternoon_question TEXT,    -- Pergunta enviada
  afternoon_answer TEXT,      -- Resposta do usuário ← ARMAZENADA AQUI

  -- Período Noite (18:00)
  evening_question TEXT,      -- Pergunta enviada
  evening_answer TEXT,        -- Resposta do usuário ← ARMAZENADA AQUI

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(user_id, date)
);
```

### 2️⃣ Supabase (Secundário - Vazio)

**URL:** `https://vazwxcjylswoxdyhxgnc.supabase.co`
**Status:** ⚠️ Não sincronizado automaticamente

> Supabase é um banco SEPARADO que apenas possui a tabela `users` sincronizada manualmente.
> As respostas de checkin NÃO estão em Supabase - apenas em Railway Postgres.

---

## 🔄 Fluxo Completo de Armazenamento

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUÁRIO NO WHATSAPP                          │
│                 (Arthur, Julio, Estevão, etc)                   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
        ┌─────────────────────────────────┐
        │  Bot envia pergunta via WhatsApp│
        │  Ex: "Qual é sua meta de hoje?" │
        └──────────────┬──────────────────┘
                       ↓
        ┌──────────────────────────────────────────┐
        │  Scheduler (APScheduler)                 │
        │  - 06:00: Envia pergunta de metas        │
        │  - 12:00: Envia pergunta de status       │
        │  - 18:00: Envia pergunta de fechamento   │
        └──────────┬───────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  PendingCheckinTracker (Em memória)      │
        │  Registra como "PENDENTE" por 2 horas    │
        │  Espera resposta do usuário              │
        └──────────┬───────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  Usuário responde via WhatsApp           │
        │  "Terminar feature de análise"           │
        └──────────┬───────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  Webhook (src/webhook/app.py)            │
        │  POST /webhook/whatsapp                  │
        │  Recebe mensagem WhatsApp                │
        └──────────┬───────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  CheckinResponseHandler                  │
        │  - Detecta como resposta de checkin      │
        │  - Valida conteúdo da resposta           │
        │  - Mapeia para período correto           │
        │    (morning/afternoon/evening)           │
        └──────────┬───────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────────────┐
        │  CheckinsIntegration.register_checkin_response() │
        │  - Obtém user_id do banco                        │
        │  - Identifica qual período responder             │
        │  - Executa UPDATE no banco de dados              │
        └──────────┬───────────────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────────────┐
        │  Railway Postgres                                │
        │  UPDATE daily_checkins                           │
        │  SET morning_answer = 'Terminar feature...'      │
        │  WHERE user_id = 5 AND date = 2025-11-13        │
        │                                                   │
        │  ✅ RESPOSTA ARMAZENADA                          │
        └──────────┬───────────────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  Bot envia confirmação                   │
        │  "✅ Sua resposta foi registrada!"       │
        └──────────────────────────────────────────┘
                   ↓
        ┌──────────────────────────────────────────┐
        │  Dashboard (http://localhost:5000)       │
        │  Consulta Railway Postgres               │
        │  Exibe respostas em tempo real            │
        │  Atualiza gráficos e estatísticas        │
        └──────────────────────────────────────────┘
```

---

## 📂 Código-Fonte: Onde as Respostas São Processadas

### 1️⃣ Recepção da Resposta (Webhook)

**Arquivo:** `src/webhook/app.py` (linha 426-451)

```python
# Webhook recebe mensagem WhatsApp
@app.route("/webhook/whatsapp", methods=["POST"])
def webhook():
    # ... validação ...

    # Verifica se é resposta a checkin pendente
    tracker = get_pending_checkin_tracker()
    pending_checkin = tracker.get_pending_checkin(push_name)

    if pending_checkin:
        # ✅ É uma resposta de checkin!
        response_handler = get_checkin_response_handler()
        success, bot_message = response_handler.handle_checkin_response(
            person_name=push_name,
            message=message_body  # A resposta do usuário
        )
```

### 2️⃣ Processamento da Resposta

**Arquivo:** `src/checkins/response_handler.py` (linhas 56-120)

```python
def handle_checkin_response(self, person_name: str, message: str) -> Tuple[bool, str]:
    """Processa resposta a um checkin"""

    # 1. Verifica se há checkin pendente
    pending_checkin = self.pending_tracker.get_pending_checkin(person_name)

    if not pending_checkin:
        return False, ""

    checkin_type = pending_checkin.checkin_type  # "metas", "status", "closing"

    # 2. Mapeia tipo para período
    period_map = {
        "metas": "morning",
        "status": "afternoon",
        "closing": "evening"
    }
    period = period_map[checkin_type]

    # 3. Registra a resposta no banco
    integration = get_checkins_integration()
    success = integration.register_checkin_response(
        user_id=person_name,
        period=period,        # "morning", "afternoon", ou "evening"
        response=message      # A resposta do usuário
    )

    # 4. Limpa do pendente
    if success:
        self.pending_tracker.clear_pending_checkin(person_name)
        return True, f"✅ Sua resposta foi registrada, {person_name}!"
```

### 3️⃣ Salvamento no Banco

**Arquivo:** `src/database/checkins_integration.py` (linhas 120-160)

```python
def register_checkin_response(
    self,
    user_id: str,
    period: str,      # "morning", "afternoon", "evening"
    response: str
) -> bool:
    """Registra resposta do usuário no banco"""

    try:
        # Mapear período para coluna correta
        column_map = {
            "morning": "morning_answer",
            "afternoon": "afternoon_answer",
            "evening": "evening_answer"
        }
        column = column_map[period]

        # Atualizar banco com SQL dinâmico
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                UPDATE daily_checkins
                SET {column} = :response,
                    updated_at = NOW()
                WHERE user_id = (SELECT id FROM users WHERE name = :user_id)
                AND date = CURRENT_DATE
            """), {"response": response, "user_id": user_id})

            conn.commit()
            logger.info(f"✅ Resposta salva para {user_id} ({period})")
            return True

    except Exception as e:
        logger.error(f"❌ Erro ao salvar: {e}")
        return False
```

### 4️⃣ Armazenamento no PostgreSQL

**Arquivo:** `src/database/checkins_manager.py`

```python
def save_answer(self, user_id: int, period: str, answer: str) -> bool:
    """Salva resposta no banco"""

    column_map = {
        "morning": "morning_answer",
        "afternoon": "afternoon_answer",
        "evening": "evening_answer"
    }

    with self.engine.connect() as conn:
        conn.execute(text(f"""
            UPDATE daily_checkins
            SET {column_map[period]} = :answer,
                updated_at = NOW()
            WHERE user_id = :user_id
            AND date = CURRENT_DATE
        """), {"answer": answer, "user_id": user_id})

        conn.commit()

    return True
```

---

## 🔍 Visualizando as Respostas Armazenadas

### Via SQL Direto

```sql
-- Ver todas as respostas de hoje
SELECT
  u.name,
  dc.date,
  dc.morning_answer,
  dc.afternoon_answer,
  dc.evening_answer
FROM daily_checkins dc
JOIN users u ON dc.user_id = u.id
WHERE dc.date = CURRENT_DATE
ORDER BY u.name;
```

### Via Python (Dashboard)

**Arquivo:** `dashboard.py` (linhas 280-320)

```python
@app.route('/api/stats')
def api_stats():
    """API que retorna dados para o dashboard"""

    with engine.connect() as conn:
        # Query para obter checkins recentes
        result = conn.execute(text("""
            SELECT dc.id, u.name, dc.date,
                   dc.morning_answer, dc.afternoon_answer, dc.evening_answer
            FROM daily_checkins dc
            JOIN users u ON dc.user_id = u.id
            ORDER BY dc.date DESC
            LIMIT 10
        """))

        recent_checkins = [
            {
                "date": str(row[2]),
                "user_name": row[1],
                "morning_answer": row[3],
                "afternoon_answer": row[4],
                "evening_answer": row[5]
            }
            for row in result.fetchall()
        ]

        return jsonify({
            "recent_checkins": recent_checkins,
            # ... outros dados
        })
```

### Via CLI

```bash
# Visualizar dados atuais
python3 view_postgres_data.py

# Visualizar histórico completo
python3 view_postgres_history.py

# Verificar uma resposta específica
python3 -c "
from src.database.connection import get_db_engine
from sqlalchemy import text
from datetime import date

engine = get_db_engine()
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT morning_answer, afternoon_answer, evening_answer
        FROM daily_checkins
        WHERE user_id = 5 AND date = :today
    '''), {'today': date.today()})
    print(result.fetchone())
"
```

---

## 📊 Estrutura de Dados Armazenada

### Exemplo Real (Estevão - ID: 5)

```
┌─────────────────────────────────────────────────────────────┐
│ Tabela: daily_checkins (Railway Postgres)                  │
├─────────────────────────────────────────────────────────────┤
│ id: 1                                                       │
│ user_id: 5 (Estevão)                                       │
│ date: 2025-11-13                                           │
│                                                             │
│ morning_question: "Como você amanheceu hoje?"             │
│ morning_answer: "Acordei muito bem com energia!"          │ ← SALVO
│                                                             │
│ afternoon_question: "Como está o ritmo do dia?"           │
│ afternoon_answer: "Ritmo perfeito! Tarefas completas"     │ ← SALVO
│                                                             │
│ evening_question: "Como foi seu dia?"                     │
│ evening_answer: "Dia EXCELENTE! Completo sucesso!"        │ ← SALVO
│                                                             │
│ created_at: 2025-11-13 20:12:40                           │
│ updated_at: 2025-11-13 20:12:52                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Segurança do Armazenamento

### ✅ O Que É Seguro

- ✅ Dados em PostgreSQL (Railway) com autenticação
- ✅ Conexão criptografada (SSL/TLS)
- ✅ Banco privado (não acessível publicamente)
- ✅ Credenciais em `.env` (não em código)

### ⚠️ Considerações

- ⚠️ Senhas em `.env` devem ser protegidas
- ⚠️ Railway pode ser acessado via conta
- ⚠️ Backup recomendado em Supabase (opcional)

### Proteção Recomendada

```bash
# Backup manual do banco
pg_dump "postgresql://user:pass@host:port/db" > backup.sql

# Ou usar sync automático para Supabase (Fase 3)
python3 src/integrations/supabase_sync.py
```

---

## 📈 Visualizando no Dashboard

**Acesso:** `http://localhost:5000`

O dashboard consulta Railway Postgres a cada 30 segundos e exibe:

```
┌─────────────────────────────────────────────┐
│ 📊 Dashboard de Checkins                   │
├─────────────────────────────────────────────┤
│                                             │
│ 👥 Total de Usuários: 9                    │
│ 📋 Total de Checkins: 5                    │
│ ✅ Completos Hoje: 3                       │
│ 🎯 Taxa de Resposta: 60%                   │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ 👤 Progresso dos Usuários           │   │
│ │ ├─ Estevão       ████████████ 100% │   │
│ │ ├─ Arthur        ████████████ 100% │   │
│ │ └─ Julio         ████████████ 100% │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ ┌─────────────────────────────────────┐   │
│ │ 📅 Histórico Recente                │   │
│ │ 2025-11-13 Estevão ☀️✅ 🌤️✅ 🌙✅    │   │
│ │ 2025-11-13 Arthur   ☀️✅ 🌤️✅ 🌙✅    │   │
│ │ 2025-11-13 Julio    ☀️✅ 🌤️✅ 🌙✅    │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ 🔄 Atualização automática a cada 30s      │
└─────────────────────────────────────────────┘
```

---

## 🔄 Fluxo Resumido

```
WhatsApp → Webhook → ResponseHandler → CheckinsIntegration → Railway Postgres
   ↓                                                              ↓
Usuário responde                                            Resposta armazenada
   ↓                                                              ↓
Confirmação enviada ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
   ↓
Dashboard consulta Railway
   ↓
Dados exibidos em tempo real
```

---

## 📝 Resumo

| Componente | Localização | Função |
|-----------|-----------|--------|
| **Respostas** | Railway Postgres (`daily_checkins.morning_answer`, etc) | Armazenamento primário |
| **Webhook** | `src/webhook/app.py` | Recebe mensagem WhatsApp |
| **Handler** | `src/checkins/response_handler.py` | Processa resposta |
| **Integração** | `src/database/checkins_integration.py` | Salva no banco |
| **Manager** | `src/database/checkins_manager.py` | Operações SQL |
| **Dashboard** | `dashboard.py` | Visualização |
| **Backup** | Supabase (futuro) | Redundância opcional |

---

**Conclusão:** ✅ **Todas as respostas são armazenadas em Railway Postgres, tabela `daily_checkins`, em colunas específicas para cada período (morning_answer, afternoon_answer, evening_answer).**
