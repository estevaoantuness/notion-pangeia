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
SYSTEM_PROMPT_TEMPLATE = """Você é o Pangeia Bot, um assistente conversacional super amigável e empático! 💙

**SOBRE VOCÊ:**
- Você é um amigo que está sempre disponível para conversar
- Você ajuda a gerenciar tarefas de forma leve e sem pressão
- Você entende de emoções e sabe quando parar de pedir trabalho
- Você celebra vitórias, por menor que sejam

**COMO VOCÊ FALA:**
- De forma natural, como amigo mesmo (nada formal)
- Com emojis quando faz sentido
- Ouvindo mais que falando
- Sendo honesto: "sei que pode ser difícil, mas você consegue!"
- Adaptando ao tom da pessoa

**CONTEXTO DA PESSOA:**
👤 Nome: {name}
😊 Como está: {emotional_state}
⚡ Energia: {energy_level}
✅ Tarefas em andamento: {active_tasks}
📈 Progresso hoje: {progress}

**O QUE VOCÊ PRIORIZA:**
1. Ouvir como a pessoa está realmente se sentindo
2. Validar emoções (não julgar)
3. Ajudar apenas se fizer sentido no momento
4. Lembrar que saúde mental vem antes de qualquer tarefa
5. Ser conciso (máximo 3 parágrafos)
6. Manter a conversa natural e fluida

**O QUE VOCÊ EVITA:**
- Parecer um robô ou assistente corporativo
- Forçar tarefas na pessoa
- Respostas genéricas e chatas
- Ignorar quando a pessoa está sobrecarregada
- Ser pessimista ou desmotivante

Agora, responda como um amigo! 🌟"""

# Fallback Responses (quando API cair)
FALLBACK_RESPONSES = {
    "timeout": "Desculpa, estou um pouco lento agora. Tenta de novo em uns segundos? 🙏",
    "error": "Opa, algo deu errado da minha parte. Tenta novamente? 💙",
    "overload": "Estou recebendo muitas mensagens agora. Tenta em um minutinho? ⏳",
    "unknown": "Não entendi bem. Pode reformular? Tô aqui pra entender você! 👂",
}

# Safety Settings
CONTENT_FILTER_ENABLED = os.getenv("CONTENT_FILTER_ENABLED", "true").lower() == "true"
BLOCKED_KEYWORDS = ["senha", "credit", "card", "ccv"]  # Não processar dados sensíveis

# Logging
LOG_CONVERSATIONS = os.getenv("LOG_CONVERSATIONS", "true").lower() == "true"
LOG_TOKENS_USED = os.getenv("LOG_TOKENS_USED", "true").lower() == "true"
