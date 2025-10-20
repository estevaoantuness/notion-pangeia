"""
Smart Task Agent - Agente Conversacional Inteligente para Tasks.

Usa GPT-4o-mini com contexto de 10 mensagens para entender comandos
de forma natural e conversacional.
"""

import logging
import json
from typing import Optional, Dict, Tuple
from config.openai_config import client
from src.memory.conversation_history import get_conversation_history
from src.agents.task_manager_agent import TaskManagerAgent

logger = logging.getLogger(__name__)


class SmartTaskAgent:
    """
    Agente conversacional inteligente para gerenciamento de tasks.

    Usa GPT-4o-mini com contexto de 10 mensagens para:
    - Entender comandos em linguagem natural
    - Manter contexto da conversa
    - Detectar intenções complexas
    - Processar comandos ambíguos
    """

    SYSTEM_PROMPT = """Você é Pangeia Bot - assistente minimalista de tarefas.

REGRAS:
✅ MÁXIMO 1 linha de resposta
✅ Zero filosofia/reflexões
✅ Direto ao ponto
✅ Use contexto anterior

COMANDOS:
- listar: "tarefas", "o que tenho"
- completar: "feito 2", "terminei X"
- andamento: "fazendo 3", "comecei X"
- progresso: "progresso", "resumo"
- criar: "cria tarefa X"

JSON:
{
  "intent": "list_tasks|complete_task|create_task|progress|greeting|unknown",
  "params": {"task_id": 2, "title": "X"},
  "needs_clarification": false,
  "response": "Mensagem curta (1 linha)"
}

IMPORTANTE: 1 linha, zero enrolação."""

    def __init__(self):
        """Inicializa o agente inteligente."""
        self.conversation_history = get_conversation_history()
        self.task_agent = TaskManagerAgent()
        logger.info("SmartTaskAgent inicializado com GPT-4o-mini + contexto")

    def process_message(
        self,
        person_name: str,
        message: str
    ) -> Optional[Tuple[bool, str]]:
        """
        Processa mensagem com contexto conversacional.

        Args:
            person_name: Nome da pessoa
            message: Mensagem recebida

        Returns:
            Tuple (sucesso, resposta) ou None se for saudação simples
        """
        try:
            # Adicionar mensagem do usuário ao histórico
            self.conversation_history.add_message(
                user_id=person_name,
                message=message,
                role="user"
            )

            # Obter contexto das últimas 10 mensagens
            context = self.conversation_history.get_context_for_llm(
                user_id=person_name,
                max_messages=9  # 9 anteriores + 1 atual = 10
            )

            # Adicionar mensagem atual
            context.append({
                "role": "user",
                "content": message
            })

            logger.info(f"Processando mensagem com {len(context)} msgs de contexto")

            # Chamar GPT-4o-mini
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    *context
                ],
                temperature=0.3,  # Baixa para ser consistente
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            # Parsear resposta
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            intent = result.get("intent", "unknown")
            params = result.get("params", {})
            needs_clarification = result.get("needs_clarification", False)
            response_text = result.get("response", "")

            logger.info(f"GPT detectou intent: {intent} (clarify: {needs_clarification})")

            # Se precisa clarificação, retornar resposta direta
            if needs_clarification:
                self.conversation_history.add_message(
                    user_id=person_name,
                    message=response_text,
                    role="assistant",
                    metadata={"intent": intent, "needs_clarification": True}
                )
                return True, response_text

            # Processar intent detectado
            result = self._execute_intent(person_name, intent, params)

            if result:
                success, response_msg = result

                # Adicionar resposta ao histórico
                self.conversation_history.add_message(
                    user_id=person_name,
                    message=response_msg,
                    role="assistant",
                    metadata={"intent": intent, "success": success}
                )

                return success, response_msg

            # Se GPT não conseguiu processar, retornar resposta dele
            if response_text:
                self.conversation_history.add_message(
                    user_id=person_name,
                    message=response_text,
                    role="assistant",
                    metadata={"intent": "fallback"}
                )
                return True, response_text

            return None

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON do GPT: {e}")
            logger.error(f"Resposta recebida: {result_text}")
            return None

        except Exception as e:
            logger.error(f"Erro no SmartTaskAgent: {e}", exc_info=True)
            return None

    def _execute_intent(
        self,
        person_name: str,
        intent: str,
        params: Dict
    ) -> Optional[Tuple[bool, str]]:
        """
        Executa intent detectado pelo GPT.

        Args:
            person_name: Nome da pessoa
            intent: Intent detectado
            params: Parâmetros extraídos

        Returns:
            Tuple (sucesso, resposta) ou None
        """
        # Delegar para TaskManagerAgent
        if intent == "list_tasks":
            return self.task_agent.handle_list_tasks(person_name, params)

        elif intent == "complete_task":
            return self.task_agent.handle_complete_task(person_name, params)

        elif intent == "start_task":
            return self.task_agent.handle_start_task(person_name, params)

        elif intent == "create_task":
            return self.task_agent.handle_create_task(person_name, params)

        elif intent == "decompose_task":
            return self.task_agent.handle_decompose_task(person_name, params)

        elif intent == "progress":
            # Usar handler de list_tasks para mostrar progresso
            return self.task_agent.handle_list_tasks(person_name, params)

        elif intent == "greeting":
            # Saudação simples - não processar
            return None

        elif intent == "unknown":
            # GPT não entendeu - retornar None para fallback
            return None

        return None


# Instância global
_smart_task_agent = None


def get_smart_task_agent() -> SmartTaskAgent:
    """
    Retorna instância global do SmartTaskAgent.

    Returns:
        SmartTaskAgent singleton
    """
    global _smart_task_agent
    if _smart_task_agent is None:
        _smart_task_agent = SmartTaskAgent()
    return _smart_task_agent
