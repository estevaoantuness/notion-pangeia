"""
Pange.IA LangChain Agent - Agent principal com ReAct pattern.

Este agent usa:
- Tools (NotionTaskTool, PsychologyTool)
- Memory (RedisChatMessageHistory)
- LLM (GPT-4o-mini)
"""

import logging
from typing import Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

from config.openai_config import OPENAI_API_KEY, GPT_MODEL, TEMPERATURE
from config.settings import settings

from .tools import NotionTaskTool, PsychologyTool, CoordinationTool
from .prompts import AGENT_PROMPT

logger = logging.getLogger(__name__)


class PangeiaAgent:
    """
    Agent principal do Pange.IA usando LangChain.

    Features:
    - ReAct agent com tools
    - Memory persistente (Redis)
    - Contextualização automática
    """

    def __init__(self, person_name: str, user_id: str):
        """
        Inicializa o Pange.IA Agent.

        Args:
            person_name: Nome da pessoa (ex: "Saraiva")
            user_id: ID único do usuário (telefone)
        """
        self.person_name = person_name
        self.user_id = user_id

        logger.info(f"Inicializando PangeiaAgent para {person_name} ({user_id})")

        # Inicializa LLM
        self.llm = ChatOpenAI(
            model=GPT_MODEL,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )

        # Inicializa Tools
        self.tools = [
            NotionTaskTool(),
            PsychologyTool(),
            CoordinationTool(),
        ]

        # Inicializa Memory (Redis)
        self.message_history = RedisChatMessageHistory(
            session_id=user_id,
            url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            key_prefix="pangeia_chat:"
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=self.message_history,
            return_messages=True
        )

        # Cria Agent (ReAct pattern)
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=AGENT_PROMPT.partial(person_name=person_name)
        )

        # Cria Agent Executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,  # Para debugging
            handle_parsing_errors=True,
            max_iterations=5
        )

        logger.info(f"✅ PangeiaAgent pronto com {len(self.tools)} tools")

    def chat(self, message: str) -> str:
        """
        Envia mensagem para o agent e recebe resposta.

        Args:
            message: Mensagem do usuário

        Returns:
            Resposta do agent
        """
        try:
            logger.info(f"User ({self.person_name}): {message}")

            # Executa agent
            response = self.executor.invoke({
                "input": message
            })

            output = response.get("output", "Desculpa, não consegui processar.")

            logger.info(f"Agent: {output}")

            return output

        except Exception as e:
            logger.error(f"Erro no PangeiaAgent: {e}", exc_info=True)
            return (
                "Algo bugou do meu lado. Me manda de novo que eu te respondo agora."
            )

    def clear_memory(self):
        """Limpa histórico de conversa."""
        self.message_history.clear()
        logger.info(f"Memória limpa para {self.person_name}")

    def get_conversation_history(self) -> List[Dict]:
        """
        Retorna histórico de conversa.

        Returns:
            Lista de mensagens {role, content}
        """
        messages = self.message_history.messages

        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.type,  # 'human' ou 'ai'
                "content": msg.content
            })

        return formatted


# Factory function para facilitar criação
def create_pangeia_agent(person_name: str, user_id: str) -> PangeiaAgent:
    """
    Cria instância do PangeiaAgent.

    Args:
        person_name: Nome da pessoa
        user_id: ID do usuário

    Returns:
        PangeiaAgent configurado
    """
    return PangeiaAgent(person_name=person_name, user_id=user_id)
