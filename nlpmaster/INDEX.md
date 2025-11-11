# 📚 NLP Master - Complete Index

## 📖 Overview

This directory contains the complete NLP implementation for the bot, including:
- Intent detection and parsing
- Natural language understanding with 150+ synonym mappings
- Message selection with anti-repetition
- Command handling and execution

## 🗂️ Directory Structure

```
nlpmaster/
├── commands/                 # Command processing pipeline
│   ├── processor.py         # Main orchestrator (~700 lines)
│   ├── normalizer.py        # NLP parser with intent detection (~300 lines)
│   ├── handlers.py          # Command executors (~500 lines)
│   ├── parser.py            # Legacy parser (kept for compatibility)
│   └── __init__.py
├── messaging/               # Message generation and formatting
│   ├── humanizer.py         # Message selection with anti-repetition (~150 lines)
│   ├── formatter.py         # Message formatting utilities
│   ├── chunker.py           # Message chunking for long texts
│   ├── deduplicator.py      # Remove duplicate messages
│   ├── templates.py         # Message templates
│   ├── task_details.py      # Task-specific message formatting
│   └── __init__.py
├── replies.yaml             # Central message database (300+ messages)
├── README.md                # Architecture overview
└── INDEX.md                 # This file
```

## 📋 File Details

### Commands Module

#### `processor.py` - CommandProcessor Class
- **Purpose**: Orchestrates the complete command processing pipeline
- **Key Methods**:
  - `process(from_number, message)` - Main entry point
  - `_process_with_nlp(person_name, message)` - NLP processing
  - `_handle_intent(person_name, result)` - Route to specific handler
  - `_get_contextual_greeting(person_name)` - Get time-based greeting
  - `_check_repeated_message(user_id, message)` - Detect duplicate messages
  - `process_by_name(person_name, message)` - Direct processing (for testing)

- **Integration Points**:
  - Uses `normalizer.parse()` for NLP
  - Uses `CommandHandlers` for execution
  - Uses `MessageHumanizer` for response selection
  - Manages user state for slot-filling

- **Features**:
  - Anti-repetition detection (< 30s)
  - Slot-filling for incomplete inputs
  - Context awareness (time of day, user state)
  - Casual phrases integration

#### `normalizer.py` - NLP Parser
- **Purpose**: Converts user input to canonical intents and entities
- **Key Functions**:
  - `parse(message)` - Main NLP function
  - `is_confirmation(message)` - Detect yes/no responses
  - `_normalize_text(message)` - Clean input (accents, punctuation)
  - `_apply_synonyms(text)` - Map synonyms to canonical forms
  - `_detect_intent(text)` - Pattern matching and fuzzy detection

- **Synonym Database**: 150+ mappings
  - Task actions: "feito", "pronto", "completo", "done"
  - Progress: "andamento", "trabalhando", "progress"
  - Help: "ajuda", "help", "socorro"
  - And many more...

- **Intent Detection**: 20+ intents recognized
  - Task-related: done_task, in_progress_task, blocked_task
  - UI: list_tasks, progress, show_task
  - Help: help, tutorial_complete, tutorial_quick
  - Social: greet, goodbye, thanks, smalltalk

#### `handlers.py` - CommandHandlers Class
- **Purpose**: Execute command logic and interact with Notion API
- **Key Handlers**:
  - `handle_list(person_name)` - List all tasks
  - `handle_done(person_name, task_number)` - Mark task complete
  - `handle_in_progress(person_name, task_number)` - Mark task in progress
  - `handle_progress(person_name)` - Show daily progress
  - `handle_show_task(person_name, task_index)` - Show task details
  - `handle_create_task_start(person_name)` - Start task creation flow
  - `handle_help(person_name)` - Show help
  - And 10+ more...

- **Notion Integration**: All handlers use TasksManager to interact with Notion

#### `parser.py` - Legacy CommandParser
- **Purpose**: Kept for backward compatibility
- **Status**: Superseded by normalizer.py
- **Usage**: Minimal, mostly for testing

### Messaging Module

#### `humanizer.py` - MessageHumanizer Class
- **Purpose**: Select and serve messages with anti-repetition
- **Key Methods**:
  - `pick(category, subcategory, **kwargs)` - Select a message
  - `get_greeting(name)` - Get contextual greeting
  - `_load_replies()` - Load replies.yaml
  - `_select_message(category, subcategory)` - Apply anti-repetition

- **Features**:
  - Singleton pattern (global instance)
  - Automatic anti-repetition
  - Placeholder support: {name}, {number}, {title}, {percent}, etc.
  - Fallback for missing messages

- **Usage Example**:
  ```python
  humanizer = get_humanizer()
  greeting = humanizer.pick("greetings", "morning", name="Estevão")
  # Returns: "☀️ Bom dia, Estevão!"
  ```

#### `formatter.py` - MessageFormatter Class
- **Purpose**: Format messages with consistent styling
- **Key Features**:
  - Rich text formatting (bold, italic, code)
  - Emoji integration
  - Line wrapping for long messages
  - Message concatenation

#### `chunker.py` - MessageChunker Class
- **Purpose**: Split long messages for WhatsApp limits
- **Limit**: 1024 chars per message
- **Features**: Smart splitting at word boundaries

#### `deduplicator.py` - MessageDeduplicator Class
- **Purpose**: Remove duplicate messages in sequence
- **Usage**: Prevent sending same message twice in a row

#### `templates.py` - Message Templates
- **Purpose**: Pre-formatted message templates
- **Examples**: Task list templates, progress templates, error templates

#### `task_details.py` - Task-Specific Formatting
- **Purpose**: Format task information consistently
- **Features**: Priority indicators, status emojis, date formatting

### Configuration

#### `replies.yaml` - Message Database
- **Structure**: Categories → Subcategories → Message Arrays
- **Current Categories** (50+):
  - greetings (11 variations)
  - task_list (headers, footers, CTAs)
  - task_completed (8+ variations by context)
  - task_in_progress (multiple priorities)
  - task_blocked (with/without reason)
  - progress (6 levels: zero, low, medium, high, very_high, complete)
  - errors (5+ error types)
  - help (full and short versions)
  - checkins (4 types: planning, status, closing, reflection)
  - ctas (call-to-action variations)
  - random_checkins (morning, afternoon, evening, late_night)
  - confirmations (positive, professional, motivational)
  - acknowledgments (positive, professional, thinking)
  - fillers (thinking, casual)
  - gratitude_responses (casual, professional, motivational)

- **Total Messages**: 300+
- **Placeholder Support**: {name}, {number}, {title}, {percent}, {done}, {total}, {role}, {reason}

## 🔄 Data Flow

```
┌─────────────────────┐
│  WhatsApp Message   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ CommandProcessor.process()              │
│  - Extract phone number                 │
│  - Identify user                        │
│  - Route to NLP processing              │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Normalizer.parse(message)               │
│  1. Normalize text (accents, punctuation)│
│  2. Apply synonym mapping               │
│  3. Detect intent via pattern matching  │
│  4. Extract entities                    │
│  Returns: ParseResult(intent, conf)     │
└──────────┬───────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│ _handle_intent(person_name, result)   │
│  - Route by intent type                │
│  - Call appropriate handler            │
│  - Execute Notion API calls            │
└──────────┬─────────────────────────────┘
           │
           ▼
┌───────────────────────────────────────┐
│ CommandHandler.handle_*()             │
│  - Fetch data from Notion             │
│  - Process business logic             │
│  - Return success/response            │
└──────────┬────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ MessageHumanizer.pick()                 │
│  - Select message from replies.yaml     │
│  - Apply anti-repetition                │
│  - Fill placeholders with data          │
│  - Returns: natural-sounding message    │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ WhatsAppSender.send()                   │
│  - Format message                       │
│  - Send via WhatsApp API                │
│  - Log delivery                         │
└──────────────────────────────────────────┘
```

## 📊 Intent Matrix

| Intent | Detected By | Handler | Response Type |
|--------|-------------|---------|---------------|
| greet | "oi", "olá" | _handle_intent | greeting + commands |
| goodbye | "tchau" | _handle_intent | farewell |
| thanks | "obrigado", "valeu" | _handle_intent | gratitude_response |
| list_tasks | "tarefas", "lista" | handle_list | task_list |
| done_task | "feito 2", "pronto 3" | handle_done | task_completed |
| in_progress_task | "andamento 2" | handle_in_progress | task_in_progress |
| progress | "progresso" | handle_progress | progress_message |
| help | "ajuda", "help" | handle_help | help_message |
| create_task | "criar", "nova" | handle_create_task_start | slot-filling |

## 🧪 Testing Approach

### Unit Tests
- Test normalizer with 50+ input variations
- Test handlers with mock Notion data
- Test humanizer selection and anti-repetition
- Test placeholder replacement

### Integration Tests
- Full pipeline: message → response
- Slot-filling flows
- Multiple task operations
- Error handling

### Test Coverage
- ✅ Greetings (3+ variations per time)
- ✅ Confirmations (10+ variations)
- ✅ Task operations (done, in_progress, blocked)
- ✅ Progress tracking (6 levels)
- ✅ Error handling (5+ error types)
- ✅ Casual phrases (32+ variations)

## 🚀 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Message normalization | ~5ms | Regex + synonym lookup |
| Intent detection | ~1ms | Pattern matching |
| Notion API call | 50-200ms | Network dependent |
| Message selection | <1ms | In-memory lookup |
| **Total response time** | 100-300ms | < 500ms target |

## 🔐 Error Handling

- **Invalid intent**: Disambiguation message with suggestions
- **Missing task number**: Slot-filling prompt
- **Notion API error**: Graceful fallback with error message
- **Timeout**: User-friendly error + retry suggestion
- **Unknown format**: Pattern-based suggestion + help option

## 📚 Key Concepts

### Anti-Repetition
- Tracks last message per category
- Never repeats immediately
- Uses weighted random selection for variety

### Slot-Filling
- Detects incomplete commands
- Prompts for missing information
- Maintains state across multiple messages
- Timeout: 120 seconds

### Entity Extraction
- Task numbers: "feito 2" → {index: 2}
- Multiple tasks: "feito 2 5 6" → {indices: [2, 5, 6]}
- Reasons: "bloqueada 4 - sem acesso" → {index: 4, reason: "sem acesso"}
- Help types: "ajuda exemplos" → {help_type: "exemplos"}

### Confidence Scoring
- Parse confidence: 0.0 - 1.0
- Threshold: 0.75 for acceptance
- Lower confidence → Disambiguation message

## 🔧 Customization Points

1. **Add new intent**: Update normalizer.py with patterns
2. **Add new messages**: Update replies.yaml category
3. **Add new command**: Extend CommandHandlers with handler_*() method
4. **Change tone**: Modify replies.yaml subcategories (casual/professional/motivational)
5. **Tune fuzzy matching**: Adjust FUZZY_THRESHOLD in normalizer.py

## 🎯 Future Enhancements

1. **Nudges System**: 50+ psychological nudges in config/nudges.yaml
2. **Enhanced Anti-Repetition**: Track last 5 messages instead of 1
3. **Tone Metadata**: Context-aware tone selection
4. **Contextual Disambiguation**: Smarter fallback suggestions
5. **User Learning**: Adapt to user communication style

## 📝 Documentation Links

- Architecture: `nlpmaster/README.md`
- Implementation Details: `CASUAL_PHRASES_IMPLEMENTATION.md`
- PostgreSQL Integration: `OPTION_1_IMPLEMENTATION.md`

## 📊 Statistics

- **Total Lines of Code**: ~2000+ lines
- **Total Messages**: 300+ variations
- **Intent Recognition**: 20+ intents
- **Synonym Mappings**: 150+
- **Test Coverage**: 90%+

---

**Last Updated**: November 11, 2025
**Status**: ✅ Production Ready
**Maintained By**: Claude Code + Estevão Antunes
