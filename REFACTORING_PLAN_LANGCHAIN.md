# 🔄 Plano de Refatoração: LangChain

## 📋 Arquitetura Atual → LangChain

### Componentes Atuais:
```
ConversationalAgent (OpenAI client direto)
├── PsychologicalEngine
├── TasksManager
├── TaskManagerAgent
├── NudgeEngine
├── Redis Memory (manual)
└── OpenAI GPT-4o-mini
```

### Nova Arquitetura LangChain:
```
LangChain Agent (ReAct)
├── Tools:
│   ├── NotionTaskTool (list/create/update/complete)
│   ├── PsychologyAnalysisTool
│   ├── TeamCoordinationTool
│   └── PatternDetectionTool
├── Memory:
│   └── RedisChatMessageHistory (LangChain)
├── Chains:
│   ├── TaskAnalysisChain
│   ├── EmotionalAnalysisChain
│   └── ResponseGenerationChain
└── LLM: ChatOpenAI (gpt-4o-mini)
```

---

## 🎯 Benefícios da Refatoração

1. **Estrutura Clara:** Tools explícitos em vez de métodos misturados
2. **Memória Gerenciada:** LangChain cuida de context window, trimming
3. **Debugging:** LangChain callbacks mostram exatamente o que acontece
4. **Extensibilidade:** Fácil adicionar novos tools
5. **RAG Ready:** Preparado para adicionar vector stores futuramente
6. **Streaming:** Suporte nativo para respostas streaming

---

## 📦 Dependências Necessárias

```txt
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
redis>=5.0.0
```

---

## 🗂️ Nova Estrutura de Arquivos

```
src/
├── langchain_integration/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── notion_task_tool.py       # Tool para tasks
│   │   ├── psychology_tool.py        # Tool para análise psicológica
│   │   ├── coordination_tool.py      # Tool para coordenação de time
│   │   └── pattern_tool.py           # Tool para detecção de padrões
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── task_analysis_chain.py
│   │   ├── emotional_chain.py
│   │   └── response_chain.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── redis_history.py          # RedisChatMessageHistory
│   ├── agent.py                      # LangChain Agent principal
│   └── prompts.py                    # Prompt templates
```

---

## 🔧 Mapeamento de Componentes

### 1. ConversationalAgent → LangChain Agent

**Antes:**
```python
class ConversationalAgent:
    def generate_response(self, message, person_name):
        # Monta context
        # Chama OpenAI diretamente
        # Processa resposta
```

**Depois:**
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI

agent = create_react_agent(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    tools=[notion_tool, psychology_tool, ...],
    prompt=prompt_template
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=redis_memory,
    verbose=True
)
```

### 2. TaskManagerAgent → NotionTaskTool

**Antes:**
```python
class TaskManagerAgent:
    def handle_list_tasks(self, person_name):
        tasks = self.tasks_manager.get_person_tasks(person_name)
        # Format response
```

**Depois:**
```python
from langchain.tools import BaseTool

class NotionTaskTool(BaseTool):
    name = "notion_tasks"
    description = "List, create, or update tasks in Notion"

    def _run(self, action: str, person_name: str, **kwargs):
        if action == "list":
            return self.tasks_manager.get_person_tasks(person_name)
        elif action == "create":
            return self.tasks_manager.create_task(...)
```

### 3. Redis Memory → RedisChatMessageHistory

**Antes:**
```python
memory_manager = get_memory_manager()
history = memory_manager.get_conversation(user_id)
```

**Depois:**
```python
from langchain.memory import RedisChatMessageHistory

memory = RedisChatMessageHistory(
    session_id=user_id,
    url="redis://localhost:6379"
)
```

### 4. System Prompt → PromptTemplate

**Antes:**
```python
SYSTEM_PROMPT_TEMPLATE = """Você é Pange.IA..."""
prompt = SYSTEM_PROMPT_TEMPLATE.format(name=name, ...)
```

**Depois:**
```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT_TEMPLATE),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

---

## 🛠️ Passos de Implementação

### Fase 1: Setup Base ✅
- [x] Instalar dependências LangChain
- [ ] Criar estrutura de pastas
- [ ] Configurar imports

### Fase 2: Tools ⏳
- [ ] NotionTaskTool
- [ ] PsychologyAnalysisTool
- [ ] CoordinationTool
- [ ] PatternDetectionTool

### Fase 3: Memory ⏳
- [ ] RedisChatMessageHistory
- [ ] ConversationBufferMemory integration

### Fase 4: Agent ⏳
- [ ] Create ReAct Agent
- [ ] AgentExecutor setup
- [ ] Prompt templates

### Fase 5: Chains (Opcional) ⏳
- [ ] Task analysis chain
- [ ] Emotional analysis chain

### Fase 6: Integration ⏳
- [ ] Substituir ConversationalAgent
- [ ] Testar com webhook
- [ ] Rollback plan

### Fase 7: Testing & Deploy ⏳
- [ ] Unit tests
- [ ] Integration tests
- [ ] Deploy

---

## 🚀 Exemplo de Uso Final

```python
from src.langchain_integration import PangeiaAgent

# Inicializar
agent = PangeiaAgent(user_id="5511999999999")

# Enviar mensagem
response = agent.chat("mostra minhas tarefas")

# Response incluirá:
# - Tool calls (notion_tasks.list)
# - Análise psicológica se necessário
# - Resposta natural formatada
# - Memória persistida automaticamente
```

---

## ⚠️ Riscos & Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Breaking changes na API | Alto | Feature flag, rollback fácil |
| Performance degradation | Médio | Benchmarks antes/depois |
| Memory leaks no Redis | Médio | TTL configurado, monitoring |
| LangChain updates | Baixo | Pin versions |

---

## 📊 Métricas de Sucesso

- [ ] Código 50% mais limpo
- [ ] Debugging 3x mais fácil
- [ ] Latência < 2s (mesmo que antes)
- [ ] 100% backward compatible
- [ ] Zero erros em produção

---

## 🎯 Next Steps

1. Instalar dependências
2. Criar NotionTaskTool (primeiro)
3. Testar tool isolado
4. Criar agent básico
5. Integrar com webhook
6. Deploy incremental

---

Status: **EM ANDAMENTO** 🚧
