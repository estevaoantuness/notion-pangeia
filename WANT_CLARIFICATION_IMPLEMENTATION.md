# Want Clarification Feature - Implementation Guide

## Overview
Implemented intelligent recognition of user expressions of desire/willingness ("quero", "gostaria", etc.) in response to bot questions, enabling contextual routing to appropriate actions (tasks list or progress).

**Issue Resolved:** Bot was returning "Ops, tive um problema" error when user said "quero" in response to greeting question.

**Solution:** Added `want_clarification` intent detection with state-aware routing.

---

## Changes Made

### 1. `src/commands/normalizer.py`

#### Added WANT_SET (lines 70-75)
```python
WANT_SET: Set[str] = {
    "quero", "quer", "gostaria", "prefiro", "escolho", "seleciono",
    "queria", "eu quero", "eu gosto", "prefiro",
    "😍", "🙌", "👀"
}
```

12 expressions covering various ways users express desire/willingness:
- Direct: "quero", "quer"
- Formal: "gostaria", "prefiro", "seleciono"
- Colloquial: "queria", "eu quero"
- Emojis: "😍", "🙌", "👀"

#### Added "want" keyword set (lines 112-115)
```python
"want": {
    "quero", "quer", "gostaria", "prefiro", "escolho", "seleciono",
    "queria", "eu quero", "eu gosto", "preference"
}
```

#### Added intent detection (lines 920-922)
```python
# Expressões de desejo/vontade (respostas a perguntas do bot)
if any(word in normalized for word in WANT_SET):
    return ParseResult("want_clarification", {}, 0.88, normalized, original)
```

**Detection Logic:**
- Scans normalized text for any WANT_SET expression
- Returns confidence of 0.88 (high confidence)
- Intent name: `want_clarification`

---

### 2. `src/commands/processor.py`

#### Modified `_get_contextual_greeting()` (lines 143-144)
```python
# Before: return greeting + suggestion, None
# After:
return greeting + suggestion, "ask_task_or_progress"
```

Now returns a tuple with pending action for routing.

#### Modified greeting handler (lines 427-438)
```python
if intent == "greet":
    logger.info(f"Intent 'greet' detectado - respondendo com saudação")
    greeting, pending_action = self._get_contextual_greeting(person_name)
    # Setar estado pendente para que próxima resposta seja roteada corretamente
    if pending_action:
        self._set_user_state(person_name, {
            "pending_confirm": {
                "action": pending_action,
                "question": "ask_task_or_progress"
            }
        })
    return True, greeting
```

**Behavior:**
- Extracts pending_action from greeting
- Sets `pending_confirm` state with question context
- State persists until user responds with yes/no/want

#### Added `want_clarification` handler (lines 688-728)

**Handler Flow:**

1. **Check pending state:**
   - If user has pending question from bot, retrieve it
   - Clear the state after processing

2. **Route based on question type:**
   - Question: "ask_task_or_progress"
   - Check normalized message for context keywords:
     - "tarefa", "tasks", "lista", "ver" → `handle_list()`
     - "progresso", "progress", "status", "como" → `handle_progress()`
     - Ambiguous → Ask for clarification

3. **Fallback behavior:**
   - If no pending state but "want" expression detected
   - Try to infer intent from additional context
   - Still route to tasks/progress if clear
   - Otherwise ask "Você quer ver tarefas ou progresso?"

---

## Intent Detection Behavior

### Pure "want" expressions (no context)
```
Input: "quero"
→ Intent: want_clarification
→ Confidence: 0.88
→ Expected behavior: Ask for clarification (tarefas ou progresso?)
```

### Want expressions with context (intelligent routing)
```
Input: "quero tarefas"
→ Intent: list_tasks (more specific)
→ Expected behavior: Show task list directly

Input: "quero progresso"
→ Intent: progress
→ Expected behavior: Show progress directly

Input: "quero ver como está"
→ Intent: progress (context detected)
→ Expected behavior: Show progress directly
```

---

## Conversation Flow Example

```
User: "Oi"
  ↓ (greet detected)
Bot: "Oi! Tudo bem?"
     "Quer ver suas tarefas ou como está o progresso do dia?"
     [Sets: pending_confirm = {question: "ask_task_or_progress"}]
  ↓
User: "quero"
  ↓ (want_clarification detected)
Bot: "Você quer ver:"
     "• Tarefas"
     "• Progresso"
     "Me diga qual dos dois! 😊"
  ↓
User: "tarefas"
  ↓ (list_tasks detected)
Bot: [Shows task list]
```

---

## Testing

### Run comprehensive tests:
```bash
python3 << 'EOF'
from src.commands.normalizer import parse

# Test pure "want" expression
result = parse("quero")
assert result.intent == "want_clarification"
assert result.confidence >= 0.80

# Test variations
for var in ["gostaria", "prefiro", "quer", "escolho"]:
    result = parse(var)
    assert result.intent == "want_clarification"

# Test with context (intelligent routing)
result = parse("quero tarefas")
assert result.intent == "list_tasks"

result = parse("quero progresso")
assert result.intent == "progress"

print("✅ All tests passed!")
EOF
```

### Run full test suite:
```bash
pytest tests/ -v
# All 45+ tests should pass
```

---

## State Management

### User state structure when pending:
```python
{
    "pending_confirm": {
        "action": "ask_task_or_progress",
        "question": "ask_task_or_progress"
    },
    "timestamp": datetime_object
}
```

### State lifecycle:
1. **Created:** When greeting handler runs → `_set_user_state()`
2. **Checked:** When want_clarification detected → `_get_user_state()`
3. **Cleared:** After routing to final action → `_clear_user_state()`

---

## Backward Compatibility

✅ **No breaking changes:**
- All existing intents work unchanged
- YES_SET and NO_SET still function
- Other handlers unaffected
- Greeting handler fully backward compatible

**Verification:**
- `parse("sim")` → "confirm_yes" ✓
- `parse("não")` → "confirm_no" ✓
- `parse("oi")` → "greet" ✓
- `parse("obrigado")` → "thanks" ✓

---

## Error Prevention

### Previously failing case:
```
User input: "quero" (after bot asks question)
Old behavior: intent="unknown" → confidence drops →
              delegates to expensive GPT-4o-mini → error
```

### New behavior:
```
User input: "quero" (after bot asks question)
New behavior: intent="want_clarification" →
              checks pending state →
              routes to clarification or task list/progress
```

---

## Performance Impact

- **Detection:** O(n) where n = number of WANT_SET expressions (12)
- **Routing:** O(1) - simple string matching
- **State lookup:** O(1) - dict-based lookup
- **Overall:** Negligible, faster than previous fallback to GPT-4o-mini

---

## Future Enhancements

1. **Add more expressions** to WANT_SET based on user interactions
2. **Confidence calibration:** Adjust 0.88 threshold based on real data
3. **Multi-step questions:** Support more complex pending states
4. **Language expansion:** Add English equivalents if needed

---

## Related Files

- `config/replies.yaml` - Response templates for "Tarefas/Progresso" choice
- `src/commands/handlers.py` - `handle_list()` and `handle_progress()` implementations
- `src/messaging/humanizer.py` - Anti-repetition for clarification messages
- `tests/` - Comprehensive test suites

---

## Commit Info

**Branch:** main
**Files modified:** 2
- `src/commands/normalizer.py` - Intent detection
- `src/commands/processor.py` - State management and routing

**Test status:** ✅ All 45+ tests passing

---

**Implementation Date:** 2025-11-11
**Status:** ✅ Complete and tested
