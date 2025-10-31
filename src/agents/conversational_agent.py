"""
Conversational Agent - Agente 100% Conversacional baseado em GPT-4o-mini.

Substitui o sistema rígido de comandos por processamento de linguagem natural,
entendendo variações ilimitadas e gerando respostas humanizadas.
"""

import logging
import json
import os
from typing import Optional, Tuple, Dict, Any
from config.openai_config import client
from src.memory.conversation_history import get_conversation_history
from src.notion.tasks import TasksManager
from src.notion.task_creator import TaskCreator

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Agente conversacional 100% baseado em GPT-4o-mini.

    Processa TODAS as mensagens usando linguagem natural, sem comandos fixos.
    Suporta variações ilimitadas como:
    - "consegue me ajudar" → mostra ajuda
    - "me mostra o que falta" → lista tasks
    - "terminei aquela de estudar" → marca task como Done
    """

    SYSTEM_PROMPT = """Você é um assistente pessoal de produtividade que ajuda a gerenciar tarefas diárias.

TOM E ESTILO:
- Natural e amigável (como um amigo ajudando)
- Direto ao ponto (1-2 linhas no máximo)
- Focado em AÇÃO (fazer tasks, marcar progresso)
- Zero filosofia ou reflexões profundas

TAMANHO DE RESPOSTA:
- Padrão: 1 linha
- Lista de tasks: pode ter múltiplas linhas (formatada)
- Progresso/resumo: 2-3 linhas máximo

═══════════════════════════════════════════════════════════════════

FUNCIONALIDADES DISPONÍVEIS:

1. LISTAR TAREFAS
   Quando o usuário pedir para ver tasks, lista pendentes, status, etc.

   Variações aceitas:
   - "minhas tasks", "o que tenho pra fazer", "mostra minhas coisas"
   - "consegue me ajudar a ver o que falta", "me lista o que tem"
   - "quais são minhas tarefas", "mostra tudo", "o que tenho hoje"

   Action: list_tasks
   Params: {}

2. MARCAR TAREFA COMO CONCLUÍDA
   Quando o usuário disser que terminou/completou uma task.

   Variações aceitas:
   - "terminei a 2", "feito número 5", "completei task 3"
   - "task de estudar tá pronta", "finalizei aquela reunião"
   - "3 foi feita", "pronto task 1"

   Action: complete_task
   Params: {task_id: número da task (OBRIGATÓRIO)}

   IMPORTANTE: Se não conseguir identificar o número, pergunte qual task foi.

3. MARCAR TAREFA EM ANDAMENTO
   Quando o usuário disser que começou/vai começar uma task.

   Variações aceitas:
   - "vou começar a 4", "tô fazendo a segunda", "comecei task 3"
   - "iniciei task de estudar", "andamento 2", "começando 5"

   Action: start_task
   Params: {task_id: número da task (OBRIGATÓRIO)}

4. MARCAR TAREFA BLOQUEADA
   Quando a task está impedida/travada/bloqueada.

   Variações aceitas:
   - "travou a 3 por falta de aprovação"
   - "task 2 tá impedida - aguardando resposta"
   - "bloqueada 4: sem acesso ao sistema"
   - "não consigo 5, preciso de fulano"

   Action: block_task
   Params: {
       task_id: número da task (OBRIGATÓRIO),
       reason: string com o motivo do bloqueio
   }

   IMPORTANTE: Se não tiver motivo, pergunte "Por quê?" ou "Qual o problema?"

5. CRIAR NOVA TAREFA
   Quando o usuário quiser adicionar uma nova task.

   Variações aceitas:
   - "cria uma task pra estudar Python"
   - "quero adicionar fazer relatório"
   - "preciso fazer reunião com time"
   - "nova tarefa: comprar café"

   Action: create_task
   Params: {title: string com o título da task}

   IMPORTANTE: Extraia o título da task de forma natural. Se não tiver título claro, pergunte.

6. VER PROGRESSO/STATUS
   Quando o usuário perguntar como está indo, quanto falta, resumo do dia.

   Variações aceitas:
   - "como estou", "quanto falta", "me dá um resumo"
   - "tá indo bem?", "andamento do dia", "como tá"
   - "progresso", "status", "como estão as tasks"

   Action: show_progress
   Params: {}

7. AJUDA / O QUE VOCÊ FAZ
   Quando o usuário pedir ajuda ou quiser saber suas capacidades.

   Variações aceitas:
   - "consegue me ajudar", "o que você faz"
   - "quais comandos", "me ensina", "como usar"
   - "ajuda", "help", "?", "me explica"

   Action: show_help
   Params: {}

8. SAUDAÇÕES E SMALLTALK
   Quando o usuário cumprimentar ou fazer conversa fiada.

   Variações: "oi", "tudo bem", "como vai", "bora", "e aí"

   Action: greeting
   Params: {}

   RESPOSTA: Seja amigável (1 linha) + sugira ver tasks

9. DESPEDIDAS
   Quando o usuário se despedir.

   Variações: "tchau", "até logo", "valeu", "falou"

   Action: goodbye
   Params: {}

10. AGRADECIMENTOS
    Quando o usuário agradecer.

    Variações: "obrigado", "valeu", "thanks"

    Action: thanks
    Params: {}

═══════════════════════════════════════════════════════════════════

FORMATO DE RESPOSTA (OBRIGATÓRIO):

Você DEVE retornar sempre um JSON válido neste formato:

{
  "action": "list_tasks|complete_task|start_task|block_task|create_task|show_progress|show_help|greeting|goodbye|thanks|unknown",
  "params": {},
  "response": "Resposta humanizada em 1-2 linhas máximo"
}

EXEMPLOS DE CONVERSAS:

Usuário: "consegue me ajudar"
Resposta JSON:
{
  "action": "show_help",
  "params": {},
  "response": "Claro! Posso mostrar suas tasks, marcar como feito, criar novas... O que precisa?"
}

Usuário: "me mostra o que falta"
Resposta JSON:
{
  "action": "list_tasks",
  "params": {},
  "response": "Vou buscar suas tasks!"
}

Usuário: "terminei a 2"
Resposta JSON:
{
  "action": "complete_task",
  "params": {"task_id": 2},
  "response": "Boa! Task 2 completa 👍"
}

Usuário: "vou começar a estudar"
Resposta JSON:
{
  "action": "start_task",
  "params": {"task_id": null},
  "response": "Qual task você vai começar? Me passa o número"
}

Usuário: "travou a 3 por falta de aprovação"
Resposta JSON:
{
  "action": "block_task",
  "params": {"task_id": 3, "reason": "falta de aprovação"},
  "response": "Entendi! Task 3 marcada como bloqueada (falta de aprovação)"
}

Usuário: "cria task pra comprar café"
Resposta JSON:
{
  "action": "create_task",
  "params": {"title": "comprar café"},
  "response": "Task 'comprar café' criada! 🎯"
}

Usuário: "como estou"
Resposta JSON:
{
  "action": "show_progress",
  "params": {},
  "response": "Vou ver seu progresso!"
}

Usuário: "oi"
Resposta JSON:
{
  "action": "greeting",
  "params": {},
  "response": "E aí! Bora ver suas tasks?"
}

Usuário: "obrigado"
Resposta JSON:
{
  "action": "thanks",
  "params": {},
  "response": "Tranquilo! 😊"
}

═══════════════════════════════════════════════════════════════════

REGRAS IMPORTANTES:

1. SEMPRE retorne JSON válido (não texto comum)
2. Se não entender, use action: "unknown" e peça esclarecimento
3. Seja conciso: 1 linha é o ideal, 2 linhas é o máximo (exceto listas)
4. Extraia números de tasks com precisão (task_id é crítico)
5. Se faltar informação obrigatória (task_id, title, reason), PERGUNTE
6. Seja natural e humanizado, não robótico
7. Foque em AÇÃO, não em conversa filosófica
8. Use emojis com moderação (1 por resposta no máximo)

LEMBRE-SE: Seu objetivo é ajudar o usuário a completar tasks de forma rápida e eficiente!
"""

    def __init__(self):
        """Inicializa o agente conversacional."""
        self.conversation_history = get_conversation_history()
        self.tasks_manager = TasksManager()
        self.task_creator = TaskCreator()
        logger.info("ConversationalAgent inicializado (GPT-4o-mini)")

    def process(
        self,
        user_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa mensagem usando GPT-4o-mini para entender intenção.

        Args:
            user_name: Nome do usuário
            message: Mensagem recebida

        Returns:
            Tuple (sucesso, resposta)
        """
        logger.info(f"🤖 ConversationalAgent.process() - user: '{user_name}', msg: '{message[:50]}'")

        try:
            # Verificar API key
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("❌ FATAL: OPENAI_API_KEY não configurada!")
                return False, "Erro de configuração. Contate o suporte."

            # Verificar se o client foi inicializado
            if client is None:
                logger.error("❌ FATAL: OpenAI client é None!")
                logger.error("   OPENAI_API_KEY pode estar vazia ou inválida")
                return False, "Erro de configuração. Contate o suporte."

            # Adicionar mensagem do usuário ao histórico
            self.conversation_history.add_message(
                user_id=user_name,
                message=message,
                role="user"
            )

            # Obter contexto das últimas 10 mensagens
            context = self.conversation_history.get_context_for_llm(
                user_id=user_name,
                max_messages=9  # 9 anteriores + 1 atual = 10
            )

            # Adicionar mensagem atual
            context.append({
                "role": "user",
                "content": message
            })

            logger.info(f"📝 Processando com {len(context)} mensagens de contexto")

            # Chamar GPT-4o-mini
            logger.info("🔄 Chamando OpenAI API (gpt-4o-mini)...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    *context
                ],
                temperature=0.3,  # Baixa para ser consistente
                max_tokens=500,
                response_format={"type": "json_object"},
                timeout=20.0
            )

            # Parsear resposta
            result_text = response.choices[0].message.content.strip()
            logger.info(f"✅ GPT Response (raw): {result_text[:200]}")
            result = json.loads(result_text)

            action = result.get("action", "unknown")
            params = result.get("params", {})
            response_text = result.get("response", "")

            logger.info(f"📊 Action: {action}, Params: {params}")

            # Executar ação
            success, final_response = self._execute_action(
                user_name=user_name,
                action=action,
                params=params,
                gpt_response=response_text
            )

            # Adicionar resposta ao histórico
            self.conversation_history.add_message(
                user_id=user_name,
                message=final_response,
                role="assistant",
                metadata={"action": action, "params": params}
            )

            return success, final_response

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON DECODE ERROR: {e}")
            logger.error(f"Resposta do GPT (não é JSON válido): {result_text}")
            return False, "Não entendi direito. Pode reformular?"

        except NameError as e:
            logger.error(f"❌ NAME ERROR (variável não definida): {e}", exc_info=True)
            return False, "Ops, erro de configuração. Tenta de novo?"

        except AttributeError as e:
            logger.error(f"❌ ATTRIBUTE ERROR (método/atributo não existe): {e}", exc_info=True)
            return False, "Ops, erro interno. Tenta de novo?"

        except Exception as e:
            logger.error(f"❌ ERRO GENÉRICO NO CONVERSATIONAL AGENT")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            logger.error(f"Mensagem: {str(e)}")
            logger.error(f"User: {user_name}, Message: {message[:100]}")
            import traceback
            traceback.print_exc()
            return False, "Ops, tive um problema técnico. Tenta de novo?"

    def _execute_action(
        self,
        user_name: str,
        action: str,
        params: Dict[str, Any],
        gpt_response: str
    ) -> Tuple[bool, str]:
        """
        Executa ação detectada pelo GPT.

        Args:
            user_name: Nome do usuário
            action: Ação detectada
            params: Parâmetros extraídos
            gpt_response: Resposta gerada pelo GPT

        Returns:
            Tuple (sucesso, resposta_final)
        """
        logger.info(f"🎬 Executando action '{action}' com params: {params}")

        try:
            # LIST TASKS
            if action == "list_tasks":
                tasks_by_status = self.tasks_manager.get_person_tasks(user_name, include_completed=False)

                # Pega apenas as tasks ativas (não concluídas)
                active_tasks = []
                active_tasks.extend(tasks_by_status.get("em_andamento", []))
                active_tasks.extend(tasks_by_status.get("a_fazer", []))

                if not active_tasks:
                    return True, "Você não tem tasks pendentes! 🎉"

                # Formatar lista de tasks
                task_list = self._format_task_list(active_tasks)
                return True, f"Suas tasks:\n\n{task_list}"

            # COMPLETE TASK
            elif action == "complete_task":
                task_id = params.get("task_id")
                if not task_id:
                    return True, gpt_response  # GPT já pediu o número

                # Marcar como Done
                success = self.tasks_manager.update_task_status(
                    task_id=task_id,
                    new_status="Done"
                )
                if success:
                    return True, gpt_response or f"Boa! Task {task_id} completa 👍"
                else:
                    return False, f"Não encontrei a task {task_id}. Quer ver a lista?"

            # START TASK
            elif action == "start_task":
                task_id = params.get("task_id")
                if not task_id:
                    return True, gpt_response  # GPT já pediu o número

                success = self.tasks_manager.update_task_status(
                    task_id=task_id,
                    new_status="In Progress"
                )
                if success:
                    return True, gpt_response or f"Boa! Task {task_id} em andamento 🚀"
                else:
                    return False, f"Não encontrei a task {task_id}. Quer ver a lista?"

            # BLOCK TASK
            elif action == "block_task":
                task_id = params.get("task_id")
                reason = params.get("reason", "")

                if not task_id:
                    return True, gpt_response

                if not reason:
                    return True, f"Task {task_id} tá bloqueada por quê?"

                # Marcar como Blocked
                success = self.tasks_manager.update_task_status(
                    task_id=task_id,
                    new_status="Blocked",
                    block_reason=reason
                )
                if success:
                    return True, gpt_response or f"Task {task_id} marcada como bloqueada ({reason})"
                else:
                    return False, f"Não encontrei a task {task_id}"

            # CREATE TASK
            elif action == "create_task":
                title = params.get("title", "").strip()
                if not title:
                    return True, gpt_response or "Qual o título da nova task?"

                # Criar task
                success = self.task_creator.create_task(
                    title=title,
                    assignee=user_name
                )
                if success:
                    return True, gpt_response or f"Task '{title}' criada! 🎯"
                else:
                    return False, "Erro ao criar task. Tenta de novo?"

            # SHOW PROGRESS
            elif action == "show_progress":
                try:
                    progress = self.tasks_manager.calculate_progress(user_name)
                except Exception as e:
                    logger.error(f"Erro ao calcular progresso: {e}")
                    return False, "Deu erro ao pegar o progresso agora. Tenta de novo já já?"

                total = progress.get("total", 0)
                concluidas = progress.get("concluidas", 0)
                em_andamento = progress.get("em_andamento", 0)
                pendentes = progress.get("pendentes", 0)
                percentual = progress.get("percentual", 0)

                if total == 0:
                    return True, "Sem tasks no momento! 🎉"

                return True, (
                    f"{percentual}% completo! "
                    f"{concluidas}/{total} tasks feitas "
                    f"({em_andamento} em andamento, {pendentes} pendentes) 🚀"
                )

            # SHOW HELP
            elif action == "show_help":
                help_text = """Posso te ajudar com:

• Ver suas tasks: "mostra minhas tasks", "o que falta"
• Marcar como feito: "terminei a 2", "task 3 pronta"
• Iniciar task: "vou começar a 4", "fazendo 1"
• Bloquear: "travou a 5 - sem acesso"
• Criar nova: "cria task pra estudar Python"
• Ver progresso: "como estou", "quanto falta"

Só conversar natural comigo! 😊"""
                return True, help_text

            # GREETING
            elif action == "greeting":
                return True, gpt_response or "E aí! Bora ver suas tasks?"

            # GOODBYE
            elif action == "goodbye":
                return True, gpt_response or "Até logo! Qualquer coisa chama 👋"

            # THANKS
            elif action == "thanks":
                return True, gpt_response or "Tranquilo! 😊"

            # UNKNOWN
            else:
                return True, gpt_response or "Não entendi. Tenta: 'minhas tasks', 'progresso', 'ajuda'"

        except Exception as e:
            logger.error(f"❌ Erro ao executar action '{action}': {e}", exc_info=True)
            return False, "Erro ao executar ação. Tenta de novo?"

    def _format_task_list(self, tasks: list) -> str:
        """
        Formata lista de tasks de forma humanizada.

        Args:
            tasks: Lista de tasks

        Returns:
            String formatada
        """
        formatted = []
        for i, task in enumerate(tasks[:10], 1):  # Máximo 10 tasks
            title = task.get("title", "Sem título")
            status = task.get("status", "Not Started")

            # Emoji por status
            emoji = "⏸️" if status == "Not Started" else "🔄" if status == "In Progress" else "🚫" if status == "Blocked" else "✅"

            formatted.append(f"{i}. {emoji} {title}")

        return "\n".join(formatted)


# Instância global
_conversational_agent = None


def get_conversational_agent() -> ConversationalAgent:
    """
    Retorna instância global do ConversationalAgent.

    Returns:
        ConversationalAgent singleton
    """
    global _conversational_agent
    if _conversational_agent is None:
        _conversational_agent = ConversationalAgent()
    return _conversational_agent
