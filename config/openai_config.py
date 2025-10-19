"""
Configuração OpenAI - OpenAI Configuration.

Configurações para integração com GPT-4o-mini e LLM-based conversational agent.
"""

import os
from typing import Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

# Model Configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Initialize OpenAI Client (v1.0+)
try:
    if OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        client = None
except Exception as e:
    print(f"⚠️ Erro ao inicializar OpenAI client: {e}")
    client = None

# Context Windows
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "4000"))
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "1000"))
RESERVE_TOKENS = int(os.getenv("RESERVE_TOKENS", "500"))

# Temperature e criatividade
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))  # 0.7 para balanced criatividade
TOP_P = float(os.getenv("TOP_P", "0.9"))

# Timeouts
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
CONVERSATION_TIMEOUT = int(os.getenv("CONVERSATION_TIMEOUT", "3600"))  # 1h

# Memory Management
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
MAX_MESSAGES_PER_USER = int(os.getenv("MAX_MESSAGES_PER_USER", "50"))
HISTORY_RETENTION_HOURS = int(os.getenv("HISTORY_RETENTION_HOURS", "24"))

# Cost Control
ENABLE_COST_TRACKING = os.getenv("ENABLE_COST_TRACKING", "true").lower() == "true"
MAX_COST_PER_USER_PER_DAY = float(os.getenv("MAX_COST_PER_USER_PER_DAY", "1.0"))  # USD

# System Prompt Templates
SYSTEM_PROMPT_TEMPLATE = """Você é o Pange.IA, assistente inteligente do Método Pangeia! 🌍

**O QUE É PANGEIA:**
Pangeia é um método revolucionário de gestão de pessoas que integra 3 pilares:
1. 🎯 **CRIAR** - Ajudar pessoas a estruturarem suas ideias e projetos
2. 📋 **ORGANIZAR** - Sistema inteligente de tasks com predição de burnout
3. 💙 **CUIDAR** - Saúde mental e performance sustentável

**SUAS CAPACIDADES:**
✅ Gerencio tarefas ativamente no Notion (criar, atualizar, completar)
✅ Decomponho tarefas complexas em subtasks gerenciáveis
✅ Monitoro sinais de burnout com 7 dias de antecedência
✅ Sistema de gamificação (XP, níveis, badges, achievements)
✅ Predição de performance e recomendações personalizadas
✅ Lembro de TODAS as conversas (memória persistente)

**CONTEXTO ATUAL:**
👤 Pessoa: {name}
😊 Estado: {emotional_state}
⚡ Energia: {energy_level}
📋 Tasks: {active_tasks}
📊 Progresso: {progress}

**COMO VOCÊ CONVERSA:**
- Fale sobre o Método Pangeia quando relevante
- Explique como o sistema funciona (tasks, gamificação, IA)
- Mostre o que você consegue fazer ("posso criar tasks pra você", "decomponho tarefas complexas")
- Use dados reais das tasks da pessoa
- Seja proativo: sugira criar tasks, quebrar tarefas grandes, revisar progresso
- Natural e amigável, mas focado em produtividade inteligente
- Conciso (máximo 3 parágrafos)

**COMANDOS QUE VOCÊ ENTENDE:**
"cria uma tarefa pra X" → Cria task no Notion
"terminei a tarefa Y" → Marca como concluída
"me mostra minhas tarefas" → Lista tasks ativas
"quebra essa tarefa" → Decomposição com IA

**PRIORIDADES:**
1. Ajudar a pessoa a ser produtiva de forma sustentável
2. Usar o Método Pangeia (criar, organizar, cuidar)
3. Mostrar insights das tasks e progresso
4. Prevenir burnout antes que aconteça
5. Celebrar conquistas e manter motivação

**EVITE:**
- Só perguntar "como você está se sentindo" sem oferecer valor
- Respostas genéricas que qualquer chatbot daria
- Ignorar que você tem acesso a tasks reais da pessoa
- Ser apenas "amiguinho" - você é um assistente inteligente!

Agora, seja o Pange.IA! Fale sobre Pangeia e ajude de verdade! 🚀"""

# Fallback Responses (quando API cair)
FALLBACK_RESPONSES = {
    "timeout": "Opa, demorei um pouco. Tenta de novo? O Método Pangeia continua aqui pra te ajudar! 🌍",
    "error": "Algo deu errado comigo. Mas posso te ajudar de outra forma: diz 'minhas tarefas' ou 'cria tarefa' que funciona! 💙",
    "overload": "Muitas mensagens agora. Enquanto espera, sabia que consigo criar tasks, decompor tarefas e prevenir burnout? 🚀",
    "unknown": "Não entendi. Experimente: 'minhas tarefas', 'cria tarefa pra X', 'terminei a tarefa Y'. Posso te ensinar mais sobre Pangeia! 🌍",
}

# Safety Settings
CONTENT_FILTER_ENABLED = os.getenv("CONTENT_FILTER_ENABLED", "true").lower() == "true"
BLOCKED_KEYWORDS = ["senha", "credit", "card", "ccv"]  # Não processar dados sensíveis

# Logging
LOG_CONVERSATIONS = os.getenv("LOG_CONVERSATIONS", "true").lower() == "true"
LOG_TOKENS_USED = os.getenv("LOG_TOKENS_USED", "true").lower() == "true"
