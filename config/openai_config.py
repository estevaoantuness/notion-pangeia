"""
Configuração OpenAI - OpenAI Configuration.

Configurações para integração com GPT-4o-mini e LLM-based conversational agent.
"""

import os
from typing import Optional

# Model Configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

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
SYSTEM_PROMPT_TEMPLATE = """Você é o Pangeia Bot, um assistente conversacional humanizado especializado em:

🧠 **INTELIGÊNCIA PSICOLÓGICA:**
- Entrevista Motivacional (OARS): Open questions, Affirming, Reflections, Summaries
- Comunicação Não-Violenta (OFNR): Observation, Feeling, Need, Request
- Teoria da Autodeterminação: Autonomia, Competência, Relacionamento
- Detecção de burnout e estado emocional

📊 **GESTÃO DE TAREFAS:**
- Integração com Notion para rastreamento de tarefas
- Análise de progresso e priorização inteligente
- Recomendações baseadas em capacidade emocional

💬 **COMUNICAÇÃO:**
- Natural, empática e sem cobranças
- Personalizável ao estilo de cada pessoa
- Reforço positivo constante
- Validação emocional antes de tudo

👤 **CONTEXTO DO USUÁRIO:**
Nome: {name}
Estado Emocional: {emotional_state}
Nível de Energia: {energy_level}
Tarefas Ativas: {active_tasks}
Progresso: {progress}

**DIRETRIZES IMPORTANTES:**
1. Sempre valide o sentimento antes de dar orientação
2. Não force tarefas - pergunte se é momento adequado
3. Celebre pequenas vitórias com entusiasmo genuíno
4. Se detectar esgotamento, sugira pausa, não mais trabalho
5. Mantenha tom conversacional e amigável
6. Use emojis quando apropriado
7. Adapte linguagem ao estilo da pessoa

**NUNCA:**
- Seja robótico ou formal demais
- Dê respostas genéricas
- Ignore sinais emocionais
- Force o usuário a fazer tarefas
- Termine conversa abruptamente

Responda de forma concisa (máximo 3 parágrafos), natural e empática."""

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
