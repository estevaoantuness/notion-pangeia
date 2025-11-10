# 🎯 Random Check-in System - Documentation

## Overview

The Random Check-in System creates natural-feeling check-in messages at randomized times throughout the day, replacing fixed schedules with a more conversational rhythm.

**Status:** Phase 1 complete (Foundation + Message Bank)
**Timeline:** Ready for Phase 2 (Integration + Testing)

---

## 📦 Components

### 1. **RandomCheckinScheduler** (`src/checkins/random_scheduler.py`)

Core scheduling logic with:
- **Time Windows**: Morning (08:00-11:30), Afternoon (13:00-15:30), Evening (17:00-19:30), Late Night (20:00-21:45)
- **Smart Distribution**: Ensures variety across windows
- **Minimum Spacing**: Enforces 2-3 hours between check-ins
- **Weekday-Only**: Skips weekends

#### Key Methods:
```python
scheduler = RandomCheckinScheduler()

# Schedule check-ins for a user
checkins = scheduler.schedule_daily_checkins("user123", enable_late_night=False)
# Returns: [
#   {"time": "09:23", "window": "morning", "message_type": "morning"},
#   {"time": "14:47", "window": "afternoon", "message_type": "afternoon"},
#   {"time": "18:15", "window": "evening", "message_type": "evening"}
# ]

# Get next pending check-in
next_checkin = scheduler.get_next_checkin_for_user("user123")

# Record when check-in was sent
scheduler.record_checkin_sent("user123", checkin)
```

### 2. **CheckinPreferencesManager** (`src/checkins/user_preferences.py`)

User preference management with:
- **Late-Night Toggle**: Opt-in/out for 20:00-21:45 window
- **Quiet Hours**: Custom silent times (e.g., 22:00-08:00)
- **Enable/Disable**: Completely turn off check-ins
- **Frequency Control**: 2-4 check-ins per day

#### Key Methods:
```python
manager = CheckinPreferencesManager(redis_client)

# Get user preferences
prefs = manager.get_preferences("user123")
# Returns: CheckinPreferences(enable_late_night=False, preferred_frequency=3, ...)

# Toggle late night
manager.set_preference("user123", "enable_late_night", True)

# Set quiet hours
manager.set_quiet_hours("user123", "22:00", "08:00")

# Disable/enable
manager.disable_checkins("user123")
manager.enable_checkins("user123")

# Check if in quiet hours
if manager.is_in_quiet_hours("user123"):
    # Skip check-in
    pass
```

### 3. **CheckinMessageProvider** (`src/checkins/message_provider.py`)

Message loading and selection:
- **YAML Integration**: Loads from `config/replies.yaml`
- **Random Selection**: `get_message(window)` for random message
- **Validation**: Ensures all required windows have messages
- **Caching**: Avoids repeated YAML reads

#### Key Methods:
```python
provider = get_message_provider()

# Get random message for window
msg = provider.get_message("morning")
# "☕ Bom dia! Como você está planejando o dia?"

# Get all messages for window
all_msgs = provider.get_messages_for_window("afternoon")
# [List of 7 afternoon variations]

# Validate setup
if provider.validate():
    print("All windows have messages")
```

### 4. **Message Bank** (`config/replies.yaml`)

Pre-written messages organized by window:

```yaml
random_checkins:
  morning:      # 6 variations
    - "☕ Bom dia! Como você está planejando o dia?"
    - "🌅 E aí! Qual vai ser o foco principal hoje?"
    # ... 4 more

  afternoon:    # 7 variations
    - "⏰ E aí, como está o ritmo? Conseguindo avançar nas tasks?"
    - "🔄 Rápido check-in: no que você está trabalhando agora?"
    # ... 5 more

  evening:      # 5 variations
    - "🌅 Finalizando o expediente. O que você conseguiu avançar hoje?"
    - "🌆 E aí, como foi o dia? Conseguiu fazer o que tinha planejado?"
    # ... 3 more

  late_night:   # 2 variations
    - "🌙 Ainda por aí? Como foi o fechamento do dia?"
    - "✨ Dia longo, hein? Conseguiu finalizar o que precisava?"
```

---

## 🔧 Configuration (.env)

```bash
# Enable the system (default: false - starts disabled for safety)
ENABLE_RANDOM_CHECKINS=false

# Minimum hours between consecutive check-ins
RANDOM_CHECKIN_MIN_SPACING_HOURS=2

# Check-in frequency per day
RANDOM_CHECKIN_MIN_PER_DAY=2
RANDOM_CHECKIN_MAX_PER_DAY=3

# Late-night check-ins (20:00-21:45)
ENABLE_LATE_NIGHT_CHECKINS=false

# Timezone for calculations
RANDOM_CHECKIN_TIMEZONE=America/Sao_Paulo
```

---

## 🚀 Usage Examples

### Example 1: Schedule Check-ins for a User

```python
from src.checkins.random_scheduler import RandomCheckinScheduler
from src.checkins.message_provider import get_message_provider

# Initialize
scheduler = RandomCheckinScheduler(redis_client=redis_client)
provider = get_message_provider()

# Schedule check-ins
checkins = scheduler.schedule_daily_checkins("user123", enable_late_night=False)

# Get messages and send
for checkin in checkins:
    message = provider.get_message(checkin["message_type"])
    # Send via WhatsApp...
    scheduler.record_checkin_sent("user123", checkin)
```

### Example 2: Manage User Preferences

```python
from src.checkins.user_preferences import get_preferences_manager

manager = get_preferences_manager(redis_client)

# Check if late night is enabled
if manager.has_late_night_enabled("user123"):
    print("User has late-night enabled")

# Set quiet hours
manager.set_quiet_hours("user123", "22:00", "08:00")

# Skip check-in if in quiet hours
if not manager.is_in_quiet_hours("user123"):
    # Send check-in
    pass
```

### Example 3: WhatsApp Command Handler

```python
def handle_checkin_command(user_id: str, command: str):
    manager = get_preferences_manager(redis_client)

    if command == "/checkin-off-late":
        manager.set_preference(user_id, "enable_late_night", False)
        return "✓ Late-night check-ins disabled"

    elif command == "/checkin-on-late":
        manager.set_preference(user_id, "enable_late_night", True)
        return "✓ Late-night check-ins enabled"

    elif command.startswith("/checkin-frequency"):
        freq = int(command.split()[-1])
        manager.set_preference(user_id, "preferred_frequency", freq)
        return f"✓ Frequency set to {freq} check-ins per day"
```

---

## 🧪 Testing

### Unit Tests (Coming Soon)

```python
def test_random_time_generation():
    scheduler = RandomCheckinScheduler()
    for _ in range(100):
        window = RandomCheckinScheduler.TIME_WINDOWS["morning"]
        time = scheduler.get_random_time_in_window(window)
        assert window.start <= time <= window.end

def test_minimum_spacing():
    scheduler = RandomCheckinScheduler()
    times = [("morning", time(9, 0)), ("afternoon", time(9, 30))]
    spaced = scheduler.ensure_minimum_spacing(times)
    # Should remove afternoon time due to spacing violation
    assert len(spaced) == 1
```

### Integration Tests (Coming Soon)

```python
def test_schedule_and_send():
    scheduler = RandomCheckinScheduler(redis_client=redis)
    provider = get_message_provider()

    # Schedule
    checkins = scheduler.schedule_daily_checkins("test_user")
    assert len(checkins) >= 2

    # Get messages
    for checkin in checkins:
        msg = provider.get_message(checkin["message_type"])
        assert msg is not None
        assert len(msg) > 0
```

---

## 📅 Rollout Plan

### Phase 1: Foundation ✅
- [x] RandomCheckinScheduler class
- [x] CheckinPreferencesManager class
- [x] CheckinMessageProvider class
- [x] Message bank (20 variations)
- [x] Environment configuration

### Phase 2: Integration (Next)
- [ ] Integrate with existing scheduler.py
- [ ] Feature flag system (`ENABLE_RANDOM_CHECKINS`)
- [ ] User commands (`/checkin-*`)
- [ ] Message history tracking
- [ ] Unit tests

### Phase 3: Testing (Week 2)
- [ ] Integration tests
- [ ] A/B testing framework
- [ ] Metrics collection
- [ ] User feedback gathering

### Phase 4: Production (Week 3+)
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitoring and alerting
- [ ] Performance optimization
- [ ] Optional: deprecate old system

---

## 🔄 Migration Path

### Option A: Feature Flag (Recommended)
```python
if os.getenv("ENABLE_RANDOM_CHECKINS") == "true":
    # Use RandomCheckinScheduler
else:
    # Use existing scheduler
```

### Option B: Per-User Rollout
```python
def should_use_random_checkins(user_id: str) -> bool:
    # Check if user in beta group
    beta_users = redis.smembers("random_checkins:beta")
    return user_id in beta_users
```

### Option C: Percentage-Based
```python
import random

def should_use_random_checkins(user_id: str, percentage: float = 10.0) -> bool:
    # Roll dice for each user
    return random.random() < (percentage / 100.0)
```

---

## ⚠️ Considerations

### Potential Issues

1. **Message Fatigue**: Using same message twice in 5-7 days might feel repetitive
   - **Solution**: Add message history tracking in Redis (dedup within N days)

2. **Timezone Handling**: Quiet hours might not work correctly across timezones
   - **Solution**: Store quiet hours as offsets from user's local time

3. **Random Clustering**: Pure random might pick times too close together
   - **Solution**: Already implemented minimum spacing enforcement

4. **User Onboarding**: Users need to know about `/checkin-*` commands
   - **Solution**: Add help text in bot responses

### Performance Notes

- **Redis Calls**: Each scheduling operation makes 2-3 Redis calls
- **YAML Loading**: Message provider caches YAML in memory
- **APScheduler**: Can handle 1000s of jobs without issues

---

## 📊 Metrics to Track (Coming Soon)

```python
# After Phase 3, track:
- Check-in delivery success rate (%)
- User response rate by window
- Opt-out rate for late night feature
- Average time to first response after check-in
- User engagement increase vs. fixed schedule
```

---

## 🛠️ Maintenance

### Adding New Messages

Edit `config/replies.yaml` and add to the appropriate window:

```yaml
random_checkins:
  morning:
    - "☕ Bom dia! Qual o foco de hoje?"
    # Add new variation here
```

Then validate with:

```python
provider = get_message_provider()
provider._load_messages()  # Reload
provider.validate()  # Verify all windows have messages
```

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger("src.checkins").setLevel(logging.DEBUG)
```

Check scheduled checkins in Redis:

```python
redis.get("checkins:scheduled:user123:2025-11-10")
```

---

## 📞 Support

For issues or questions:
1. Check logs: `logs/scheduler.log`
2. Verify Redis connection: `redis-cli ping`
3. Check message bank: `python -c "from src.checkins.message_provider import get_message_provider; get_message_provider().validate()"`
4. Inspect user prefs: `redis> HGETALL checkins:prefs:user123`

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Ready for Phase 2 Integration
