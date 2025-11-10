# 📊 Check-in Feedback Collection System - Documentation

## Overview

The Check-in Feedback System captures and analyzes user responses to random check-in messages. It stores response text, NLP intent classification, and timing data in PostgreSQL for later analysis.

**Status:** Ready for implementation
**Database:** PostgreSQL (new `checkin_feedback` table)
**NLP Integration:** Uses existing IntentClassifier

---

## 🗄️ Database Schema

### `checkin_feedback` Table

```sql
CREATE TABLE checkin_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    checkin_id VARCHAR(255) NOT NULL,      -- e.g., "random_checkin-estevao-20251110-0923"
    checkin_window VARCHAR(20) NOT NULL,   -- morning, afternoon, evening, late_night
    checkin_message TEXT NOT NULL,         -- Full message that was sent
    response_text TEXT NOT NULL,           -- User's response
    response_intent VARCHAR(50) NOT NULL,  -- progressing, blocked, completed, question, reflection, other
    checkin_timestamp TIMESTAMP NOT NULL,  -- When check-in was sent
    response_timestamp TIMESTAMP NOT NULL, -- When user responded
    response_time_seconds INTEGER,         -- Seconds between send and response
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Indexes

- `idx_checkin_feedback_user_id` - Query by user
- `idx_checkin_feedback_created_at` - Query by date
- `idx_checkin_feedback_response_intent` - Query by intent
- `idx_checkin_feedback_window` - Query by window
- `idx_checkin_feedback_user_created` - Combined user + date

---

## 📦 Components

### 1. **CheckinFeedback** (`feedback_model.py`)

Data model for feedback records:

```python
from src.checkins.feedback_model import CheckinFeedback, ResponseIntent

feedback = CheckinFeedback(
    user_id="estevao",
    checkin_id="random_checkin-estevao-20251110-0923",
    checkin_window="morning",
    checkin_message="☕ Bom dia! Como você está planejando o dia?",
    response_text="Vou trabalhar no projeto X hoje",
    response_intent=ResponseIntent.PROGRESSING,  # NLP classification
    response_time_seconds=245  # Responded after 4 minutes
)

# Convert to/from dict
data = feedback.to_dict()
feedback2 = CheckinFeedback.from_dict(data)
```

#### ResponseIntent Enum

- **PROGRESSING**: User is making progress on tasks
- **BLOCKED**: User is stuck/facing obstacles
- **COMPLETED**: User finished a task
- **QUESTION**: User asked a question
- **REFLECTION**: User is reflecting/introspecting
- **OTHER**: Doesn't fit above categories

### 2. **CheckinFeedbackRepository** (`feedback_model.py`)

Database access layer:

```python
from src.checkins.feedback_model import CheckinFeedbackRepository

repo = CheckinFeedbackRepository(db_connection)

# Save feedback
feedback_id = repo.save_feedback(feedback)

# Retrieve feedback for user
feedback_list = repo.get_feedback_for_user("estevao", limit=50)

# Get statistics
stats = repo.get_feedback_statistics("estevao")
# Returns: {
#   "total_responses": 42,
#   "by_intent": {
#     "progressing": {"count": 28, "avg_time": 182},
#     "blocked": {"count": 8, "avg_time": 456},
#     "completed": {"count": 4, "avg_time": 120},
#     ...
#   }
# }

# Delete old feedback (cleanup)
deleted = repo.delete_old_feedback(days=90)
```

### 3. **CheckinFeedbackHandler** (`feedback_handler.py`)

High-level handler for processing responses:

```python
from src.checkins.feedback_handler import CheckinFeedbackHandler

handler = CheckinFeedbackHandler(db_connection, redis_client)

# Process user's response
feedback = handler.process_checkin_response(
    user_id="estevao",
    response_text="Consegui avançar no projeto, mas fiquei bloqueado em uma dependência",
    checkin_id="random_checkin-estevao-20251110-0923",
    checkin_window="morning",
    checkin_message="☕ Bom dia! Como você está planejando o dia?",
    checkin_timestamp=datetime(2025, 11, 10, 9, 23),
    response_timestamp=datetime(2025, 11, 10, 9, 28, 30)  # 5m 30s later
)
# Returns: CheckinFeedback instance with intent=PROGRESSING (mixed signal)

# Get user statistics
stats = handler.get_user_stats("estevao")

# Get recent feedback
recent = handler.get_recent_feedback("estevao", limit=10)
```

---

## 🔄 Integration Flow

### 1. Check-in is Sent

```python
# In scheduler_adapter.py
adapter.schedule_random_checkins_for_day(today, scheduler)

# This schedules check-ins via APScheduler
# Each check-in has unique ID: "random_checkin-{user_id}-{YYYYMMDD}-{HHMM}"
```

### 2. User Responds via WhatsApp

```python
# User receives: "☕ Bom dia! Como você está planejando o dia?"
# User responds: "Vou trabalhar no projeto X"

# In message handler (webhook):
# Extract: user_id, response_text, check-in timing info
```

### 3. Store Feedback

```python
from src.checkins.feedback_handler import get_feedback_handler

handler = get_feedback_handler(db_connection, redis_client)

feedback = handler.process_checkin_response(
    user_id=message.from_id,
    response_text=message.body,
    checkin_id=stored_checkin_id,  # From Redis cache
    checkin_window="morning",
    checkin_message=original_message,
    checkin_timestamp=checkin_sent_time,
    response_timestamp=datetime.utcnow()
)

if feedback:
    logger.info(f"✓ Feedback recorded: {feedback.response_intent.value}")
else:
    logger.error(f"✗ Failed to record feedback")
```

### 4. Query and Analyze

```python
# Get stats for user
stats = handler.get_user_stats("estevao")
print(f"Total responses: {stats['total_responses']}")
print(f"Most common intent: {max(stats['by_intent'], key=...)}")
print(f"Avg response time: {stats['by_intent']['progressing']['avg_time']}s")

# Get recent feedback
recent = handler.get_recent_feedback("estevao", limit=5)
for feedback in recent:
    print(f"{feedback['response_intent']}: {feedback['response_text'][:50]}...")
```

---

## 🚀 Implementation Steps

### Step 1: Run Migration

```bash
# Connect to PostgreSQL and run migration
psql -h localhost -U postgres -d notion_pangeia < migrations/002_create_checkin_feedback_table.sql
```

### Step 2: Import Handler in Webhook

```python
# In your WhatsApp message handler
from src.checkins.feedback_handler import get_feedback_handler

handler = get_feedback_handler(db, redis_client)
```

### Step 3: Capture Check-in ID

When scheduling check-in, store in Redis:

```python
# In scheduler_adapter._schedule_single_checkin():
checkin_id = f"random_checkin-{user_id}-{day.strftime('%Y%m%d')}-{time_str.replace(':', '')}"

# Store in Redis for retrieval later
redis_client.setex(
    f"checkin:pending:{user_id}:{checkin_id}",
    86400,  # 24 hours
    json.dumps({
        "checkin_id": checkin_id,
        "window": checkin["window"],
        "message": message,
        "sent_at": datetime.utcnow().isoformat()
    })
)
```

### Step 4: Record Response

When user responds:

```python
# In webhook handler
pending_key = f"checkin:pending:{user_id}:*"
pending = redis_client.get(pending_key)

if pending:
    checkin_data = json.loads(pending)

    feedback = handler.process_checkin_response(
        user_id=user_id,
        response_text=message_text,
        checkin_id=checkin_data["checkin_id"],
        checkin_window=checkin_data["window"],
        checkin_message=checkin_data["message"],
        checkin_timestamp=datetime.fromisoformat(checkin_data["sent_at"]),
        response_timestamp=datetime.utcnow()
    )
```

---

## 📊 Querying Feedback

### Get All Feedback for User

```python
feedback_list = repository.get_feedback_for_user("estevao", limit=100)

for fb in feedback_list:
    print(f"[{fb.checkin_window}] {fb.response_intent.value}: {fb.response_text}")
    print(f"  Response time: {fb.response_time_seconds}s")
```

### Get Statistics

```python
stats = handler.get_user_stats("estevao")

# Output:
# {
#   "total_responses": 42,
#   "by_intent": {
#     "progressing": {
#       "count": 28,
#       "avg_time": 182,
#       "min_time": 30,
#       "max_time": 1200
#     },
#     "blocked": {...},
#     ...
#   }
# }
```

### Get by Window

```sql
SELECT checkin_window, response_intent, COUNT(*) as count
FROM checkin_feedback
WHERE user_id = 'estevao'
GROUP BY checkin_window, response_intent;
```

### Get by Intent

```sql
SELECT
    response_intent,
    COUNT(*) as count,
    AVG(response_time_seconds) as avg_response_time
FROM checkin_feedback
WHERE user_id = 'estevao'
GROUP BY response_intent
ORDER BY count DESC;
```

---

## 🔍 Analytics Queries

### Response Rate by Window

```sql
SELECT
    checkin_window,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN response_text != '' THEN 1 END) as responded,
    ROUND(100.0 * COUNT(CASE WHEN response_text != '' THEN 1 END) / COUNT(*), 2) as response_rate
FROM checkin_feedback
WHERE user_id = 'estevao'
  AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY checkin_window;
```

### Intent Distribution

```sql
SELECT
    response_intent,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM checkin_feedback
WHERE user_id = 'estevao'
GROUP BY response_intent
ORDER BY count DESC;
```

### Slowest Responses

```sql
SELECT
    checkin_window,
    checkin_message,
    response_time_seconds,
    created_at
FROM checkin_feedback
WHERE user_id = 'estevao'
ORDER BY response_time_seconds DESC
LIMIT 10;
```

---

## 🧪 Testing

### Test Feedback Recording

```python
import pytest
from datetime import datetime
from src.checkins.feedback_handler import CheckinFeedbackHandler

def test_record_feedback(db, redis_client):
    handler = CheckinFeedbackHandler(db, redis_client)

    feedback = handler.process_checkin_response(
        user_id="test_user",
        response_text="Vou trabalhar no projeto X",
        checkin_id="random_checkin-test_user-20251110-0923",
        checkin_window="morning",
        checkin_message="☕ Bom dia!",
        checkin_timestamp=datetime(2025, 11, 10, 9, 23),
        response_timestamp=datetime(2025, 11, 10, 9, 28, 30)
    )

    assert feedback is not None
    assert feedback.response_intent.value == "progressing"
    assert feedback.response_time_seconds == 330  # 5m 30s
```

### Test Statistics

```python
def test_get_statistics(db, redis_client):
    handler = CheckinFeedbackHandler(db, redis_client)
    stats = handler.get_user_stats("test_user")

    assert stats["total_responses"] > 0
    assert "by_intent" in stats
    assert "progressing" in stats["by_intent"]
```

---

## ⚠️ Considerations

### Data Privacy

- Feedback contains user responses - treat as sensitive
- Consider GDPR compliance for data retention
- Implement deletion policy (default: 90 days via `delete_old_feedback()`)

### Performance

- Indexes optimize common queries (user_id, created_at, response_intent)
- Consider archiving old feedback to separate table after 1 year
- Statistics queries may be slow on large datasets - consider materialized views

### Intent Classification

- Current implementation uses existing IntentClassifier
- May misclassify ambiguous responses
- Consider adding manual review/correction for low-confidence classifications

---

## 📋 Rollout Checklist

- [ ] Create `checkin_feedback` table via migration
- [ ] Add feedback handler import to webhook
- [ ] Implement check-in ID storage in Redis
- [ ] Implement response recording in message handler
- [ ] Add feedback statistics endpoint (if API needed)
- [ ] Test with sample responses
- [ ] Monitor feedback recording for errors
- [ ] Set up cleanup job (delete_old_feedback monthly)
- [ ] Create dashboard for viewing statistics

---

## 🔗 Related Files

- `src/checkins/feedback_model.py` - Data models and repository
- `src/checkins/feedback_handler.py` - High-level handler
- `migrations/002_create_checkin_feedback_table.sql` - Database schema
- `src/checkins/scheduler_adapter.py` - Where check-ins are scheduled
- `RANDOM_CHECKINS.md` - Check-in system overview

---

## 📞 Support

For issues with feedback collection:

1. Check feedback table exists: `SELECT * FROM checkin_feedback LIMIT 1;`
2. Verify intent classification: Check NLP logs for classification errors
3. Check response time calculation: Ensure timestamps are correct
4. Review statistics: `SELECT COUNT(*) FROM checkin_feedback WHERE user_id = 'estevao';`

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Ready for Phase 3 Integration
