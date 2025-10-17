"""
Templates de mensagens para WhatsApp.

Este módulo contém todos os templates de mensagens formatadas
para envio via WhatsApp, incluindo contexto de horário.
"""

from datetime import datetime
from typing import Dict, List
from zoneinfo import ZoneInfo

# Timezone
TZ = ZoneInfo("America/Sao_Paulo")


def get_number_emoji(num: int) -> str:
    """
    Converte número para emojis.

    Exemplos:
    - 1 → "1️⃣"
    - 9 → "9️⃣"
    - 10 → "1️⃣0️⃣"
    - 11 → "1️⃣1️⃣"
    - 25 → "2️⃣5️⃣"

    Args:
        num: Número a ser convertido

    Returns:
        String com emojis representando o número
    """
    emoji_map = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣'
    }

    # Converte cada dígito do número para emoji
    return ''.join(emoji_map[digit] for digit in str(num))


def get_time_context() -> dict:
    """
    Retorna contexto baseado no horário atual (America/Sao_Paulo).

    Returns:
        {
            'period': str,      # 'morning', 'afternoon', 'evening', 'night'
            'emoji': str,       # Emoji da saudação
            'greeting': str,    # Texto da saudação
            'tone': str        # Tom da mensagem
        }
    """
    now = datetime.now(TZ)
    hour = now.hour

    if 5 <= hour < 12:
        return {
            'period': 'morning',
            'emoji': '🌅',
            'greeting': 'Bom dia',
            'tone': 'energetic'
        }
    elif 12 <= hour < 18:
        return {
            'period': 'afternoon',
            'emoji': '☀️',
            'greeting': 'Boa tarde',
            'tone': 'productive'
        }
    elif 18 <= hour < 24:
        return {
            'period': 'evening',
            'emoji': '🌙',
            'greeting': 'Boa noite',
            'tone': 'reflective'
        }
    else:  # 0 <= hour < 5
        return {
            'period': 'night',
            'emoji': '🌃',
            'greeting': 'Olá',
            'tone': 'neutral'
        }


def format_daily_tasks_message(
    person_name: str,
    tasks_grouped: Dict[str, List[Dict]],
    progress: Dict
) -> str:
    """
    Formata mensagem diária com tasks do colaborador.

    Args:
        person_name: Nome do colaborador
        tasks_grouped: Tasks agrupadas por status (concluidas, em_andamento, a_fazer)
        progress: Estatísticas de progresso

    Returns:
        Mensagem formatada para WhatsApp
    """
    # Conta total de tasks
    total_concluidas = len(tasks_grouped.get("concluidas", []))
    total_em_andamento = len(tasks_grouped.get("em_andamento", []))
    total_a_fazer = len(tasks_grouped.get("a_fazer", []))
    total_tasks = total_concluidas + total_em_andamento + total_a_fazer

    # Data de hoje
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")

    # Primeiro nome
    first_name = person_name.split()[0]

    # Obter contexto de horário
    time_ctx = get_time_context()

    # Header com saudação contextual
    message = f"{time_ctx['emoji']} {time_ctx['greeting']}, {first_name}!\n\n"
    message += f"📋 {total_tasks} tarefa{'s' if total_tasks != 1 else ''} hoje ({hoje}).\n\n"

    # Coleta todas as tasks em ordem (a_fazer → em_andamento → concluidas)
    all_tasks = []

    # A FAZER
    for task in tasks_grouped.get("a_fazer", []):
        all_tasks.append(task)

    # EM ANDAMENTO
    for task in tasks_grouped.get("em_andamento", []):
        all_tasks.append(task)

    # CONCLUÍDAS
    for task in tasks_grouped.get("concluidas", []):
        all_tasks.append(task)

    # Renderiza as primeiras 5 tasks com numeração em emoji
    MAX_TASKS_PREVIEW = 5
    for i, task in enumerate(all_tasks[:MAX_TASKS_PREVIEW], start=1):
        emoji_num = get_number_emoji(i)
        nome = task['nome']
        message += f"{emoji_num} {nome}\n"

    # Linha "ver mais" imediatamente após a 5ª task (SEM linha vazia)
    remaining_count = total_tasks - MAX_TASKS_PREVIEW
    if remaining_count > 0:
        message += f"*+{remaining_count} tarefas — digite: ver mais*\n"

    # Progresso
    message += f"\nProgresso: {progress.get('concluidas', 0)} concluídas | {progress.get('em_andamento', 0)} em andamento\n"

    # Mensagem contextual baseada no horário e progresso
    done_count = progress.get('concluidas', 0)
    percent = (done_count / total_tasks * 100) if total_tasks > 0 else 0

    if time_ctx['period'] == 'morning':
        if done_count == 0:
            message += "💪 Hora de começar!\n"
        else:
            message += "🚀 Já começou bem! Continue assim.\n"

    elif time_ctx['period'] == 'afternoon':
        if percent < 30:
            message += "⏰ Acelere o ritmo para não acumular!\n"
        elif percent < 70:
            message += "👍 Bom ritmo! Continue focado.\n"
        else:
            message += "🔥 Quase lá! Finalize forte.\n"

    elif time_ctx['period'] == 'evening':
        if percent < 50:
            message += "⚠️ Ainda tem bastante pendente.\n"
        elif percent < 100:
            message += "💪 Última hora para finalizar!\n"
        else:
            message += "🎉 Dia completo! Descanse bem.\n"

    elif time_ctx['period'] == 'night':
        if done_count < total_tasks:
            message += "🌙 Amanhã você continua.\n"
        else:
            message += "✨ Dia produtivo! Boa noite.\n"

    # Link para central de tasks no Notion
    from config.settings import settings
    tasks_db_url = f"https://notion.so/{settings.NOTION_TASKS_DB_ID.replace('-', '')}"
    message += f"Ver todas: {tasks_db_url}\n"

    # CTAs
    message += f"\nUse: feito N | andamento N | ajuda"

    return message


def format_full_task_list(
    person_name: str,
    tasks_grouped: Dict[str, List[Dict]],
    progress: Dict
) -> str:
    """
    Formata lista COMPLETA de tarefas (sem limite de 5).

    Args:
        person_name: Nome do colaborador
        tasks_grouped: Tasks agrupadas por status
        progress: Estatísticas de progresso

    Returns:
        Mensagem formatada com todas as tarefas
    """
    # Conta total de tasks
    total_concluidas = len(tasks_grouped.get("concluidas", []))
    total_em_andamento = len(tasks_grouped.get("em_andamento", []))
    total_a_fazer = len(tasks_grouped.get("a_fazer", []))
    total_tasks = total_concluidas + total_em_andamento + total_a_fazer

    # Data de hoje
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")

    # Primeiro nome
    first_name = person_name.split()[0]

    # Obter contexto de horário
    time_ctx = get_time_context()

    # Header com contexto de horário
    message = f"{time_ctx['emoji']} Todas as suas tarefas, {first_name}\n\n"
    message += f"📅 {hoje} • {total_tasks} tarefa{'s' if total_tasks != 1 else ''} no total\n\n"

    # Coleta todas as tasks em ordem (a_fazer → em_andamento → concluidas)
    all_tasks = []

    # A FAZER
    for task in tasks_grouped.get("a_fazer", []):
        all_tasks.append(task)

    # EM ANDAMENTO
    for task in tasks_grouped.get("em_andamento", []):
        all_tasks.append(task)

    # CONCLUÍDAS
    for task in tasks_grouped.get("concluidas", []):
        all_tasks.append(task)

    # Renderiza TODAS as tasks com numeração em emoji
    for i, task in enumerate(all_tasks, start=1):
        emoji_num = get_number_emoji(i)
        nome = task['nome']
        message += f"{emoji_num} {nome}\n"

    # Progresso
    message += f"\nProgresso: {progress.get('concluidas', 0)} concluídas | {progress.get('em_andamento', 0)} em andamento\n"

    # Mensagem contextual (igual à versão resumida)
    done_count = progress.get('concluidas', 0)
    percent = (done_count / total_tasks * 100) if total_tasks > 0 else 0

    if time_ctx['period'] == 'morning':
        if done_count == 0:
            message += "💪 Hora de começar!\n"
        else:
            message += "🚀 Já começou bem! Continue assim.\n"

    elif time_ctx['period'] == 'afternoon':
        if percent < 30:
            message += "⏰ Acelere o ritmo para não acumular!\n"
        elif percent < 70:
            message += "👍 Bom ritmo! Continue focado.\n"
        else:
            message += "🔥 Quase lá! Finalize forte.\n"

    elif time_ctx['period'] == 'evening':
        if percent < 50:
            message += "⚠️ Ainda tem bastante pendente.\n"
        elif percent < 100:
            message += "💪 Última hora para finalizar!\n"
        else:
            message += "🎉 Dia completo! Descanse bem.\n"

    elif time_ctx['period'] == 'night':
        if done_count < total_tasks:
            message += "🌙 Amanhã você continua.\n"
        else:
            message += "✨ Dia produtivo! Boa noite.\n"

    # Link para central de tasks no Notion
    from config.settings import settings
    tasks_db_url = f"https://notion.so/{settings.NOTION_TASKS_DB_ID.replace('-', '')}"
    message += f"Ver no Notion: {tasks_db_url}\n"

    # CTAs
    message += f"\nUse: feito N | andamento N | ajuda"

    return message


def format_no_tasks_message(person_name: str) -> str:
    """
    Mensagem quando não há tasks.

    Args:
        person_name: Nome do colaborador

    Returns:
        Mensagem formatada
    """
    # Obter contexto de horário
    time_ctx = get_time_context()
    first_name = person_name.split()[0]

    return f"""{time_ctx['emoji']} {time_ctx['greeting']}, {first_name}!

✨ Você não tem tarefas pendentes no momento!

Aproveite para:
• Revisar tasks futuras
• Ajudar outros membros do time
• Planejar próximas entregas

Se houver algo importante, me avise! 😊
"""


def format_confirmation_message(
    action: str,
    task_name: str,
    progress: Dict
) -> str:
    """
    Formata mensagem de confirmação de ação.

    Args:
        action: Tipo de ação (done, in_progress, blocked)
        task_name: Nome da task
        progress: Progresso atualizado

    Returns:
        Mensagem de confirmação
    """
    emojis = {
        "done": "✅",
        "in_progress": "⏳",
        "blocked": "🚫"
    }

    messages = {
        "done": "Perfeito! Tarefa concluída",
        "in_progress": "Ok! Tarefa em andamento",
        "blocked": "Tarefa marcada como bloqueada"
    }

    emoji = emojis.get(action, "✅")
    msg = messages.get(action, "Ação realizada")

    message = f"""{emoji} {msg}:
   "{task_name}"
"""

    if action == "done" and progress.get("total", 0) > 0:
        percentual = progress.get("percentual", 0)
        concluidas = progress.get("concluidas", 0)
        total = progress.get("total", 0)

        message += f"""
📊 Progresso de hoje: {concluidas}/{total} ({percentual}%)

Continue assim! 🚀
"""

    return message


def format_help_message() -> str:
    """
    Formata mensagem de ajuda com todos os comandos.

    Returns:
        Mensagem de ajuda
    """
    return """📖 COMANDOS DISPONÍVEIS

━━━━━━━━━━━━━━━━━━━━━━
📋 GERENCIAR TASKS

• 'feito [N]' ou 'concluí [N]'
  → Marca task N como concluída

• 'andamento [N]' ou 'fazendo [N]'
  → Marca task N como em andamento

• 'bloqueada [N] - [motivo]'
  → Marca task N como bloqueada

━━━━━━━━━━━━━━━━━━━━━━
📊 CONSULTAR

• 'minhas tarefas' ou 'lista'
  → Lista suas tasks do dia

• 'progresso' ou 'status'
  → Mostra seu progresso

━━━━━━━━━━━━━━━━━━━━━━
❓ AJUDA

• 'ajuda' ou 'help'
  → Mostra esta mensagem

━━━━━━━━━━━━━━━━━━━━━━

Dúvidas? Só perguntar! 😊
"""


def format_error_message(error_type: str = "generic") -> str:
    """
    Formata mensagem de erro amigável.

    Args:
        error_type: Tipo do erro

    Returns:
        Mensagem de erro
    """
    messages = {
        "invalid_command": """❌ Comando não reconhecido.

Digite 'ajuda' para ver os comandos disponíveis.""",

        "task_not_found": """❌ Task não encontrada.

Verifique o número da task e tente novamente.
Digite 'minhas tarefas' para ver a lista atualizada.""",

        "generic": """❌ Ops! Algo deu errado.

Tente novamente em alguns instantes ou digite 'ajuda' para ver os comandos."""
    }

    return messages.get(error_type, messages["generic"])


def format_checkin_question(
    checkin_type: str,
    question_number: int,
    question_text: str
) -> str:
    """
    Formata pergunta de check-in.

    Args:
        checkin_type: Tipo do check-in
        question_number: Número da pergunta
        question_text: Texto da pergunta

    Returns:
        Pergunta formatada
    """
    emojis = {
        "planning": "🎯",
        "status": "🔄",
        "closing": "🌅",
        "reflection": "🌙"
    }

    emoji = emojis.get(checkin_type, "❓")

    return f"""{emoji} PERGUNTA {question_number}

{question_text}
"""


def format_progress_report(
    person_name: str,
    tasks_grouped: Dict[str, List[Dict]],
    progress: Dict
) -> str:
    """
    Formata relatório visual de progresso do dia.

    Mostra TODAS as tarefas agrupadas por status com estatísticas.

    Args:
        person_name: Nome do colaborador
        tasks_grouped: Tasks agrupadas (concluidas, em_andamento, a_fazer)
        progress: Estatísticas de progresso

    Returns:
        Mensagem formatada com relatório visual
    """
    from config.settings import settings

    # Dados básicos
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")
    first_name = person_name.split()[0]

    # Estatísticas
    total = progress.get("total", 0)
    concluidas = progress.get("concluidas", 0)
    em_andamento = progress.get("em_andamento", 0)
    pendentes = progress.get("pendentes", 0)

    # Percentuais
    done_percent = (concluidas / total * 100) if total > 0 else 0
    in_progress_percent = (em_andamento / total * 100) if total > 0 else 0
    pending_percent = (pendentes / total * 100) if total > 0 else 0

    # Header
    message = f"📊 Seu progresso hoje ({hoje})\n\n"

    # Seção: CONCLUÍDAS (se houver)
    # Busca tasks concluídas do Notion (não do grouped que está filtrado)
    from src.notion.tasks import TasksManager
    tasks_manager = TasksManager()
    all_results = tasks_manager.notion_client.query_database(database_id=tasks_manager.database_id)

    concluidas_list = []
    em_andamento_list = []
    pendentes_list = []

    # Filtra por pessoa e agrupa
    for task in all_results:
        assignees_prop = task.get("properties", {}).get("Assignees", {})
        assignees = assignees_prop.get("multi_select", [])

        is_responsible = False
        for assignee in assignees:
            assignee_name = assignee.get("name", "")
            if tasks_manager._normalize_name(person_name) in tasks_manager._normalize_name(assignee_name):
                is_responsible = True
                break

        if not is_responsible:
            continue

        parsed = tasks_manager._parse_task(task)
        status = parsed.get("status", "")

        if status == "Concluída":
            concluidas_list.append(parsed)
        elif status == "Em Andamento":
            em_andamento_list.append(parsed)
        else:
            pendentes_list.append(parsed)

    # CONCLUÍDAS
    if concluidas_list:
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"✅ CONCLUÍDAS ({len(concluidas_list)}/{total} - {done_percent:.0f}%)\n\n"
        for i, task in enumerate(concluidas_list, 1):
            title = _truncate_text(task['nome'], 50)
            message += f"{i}. {title}\n"
        message += "\n"

    # EM ANDAMENTO
    if em_andamento_list:
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🔵 EM ANDAMENTO ({len(em_andamento_list)}/{total} - {in_progress_percent:.0f}%)\n\n"
        for i, task in enumerate(em_andamento_list, 1):
            title = _truncate_text(task['nome'], 50)
            message += f"{i}. {title}\n"
        message += "\n"

    # PENDENTES
    if pendentes_list:
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"⚪ PENDENTES ({len(pendentes_list)}/{total} - {pending_percent:.0f}%)\n\n"
        for i, task in enumerate(pendentes_list, 1):
            title = _truncate_text(task['nome'], 50)
            message += f"{i}. {title}\n"
        message += "\n"

    # RESUMO
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "📈 RESUMO DO DIA\n\n"
    message += f"Total: {total} tarefas\n"
    message += f"Concluídas: {concluidas} ({done_percent:.0f}%)\n"
    message += f"Em andamento: {em_andamento} ({in_progress_percent:.0f}%)\n"
    message += f"Pendentes: {pendentes} ({pending_percent:.0f}%)\n\n"

    # Mensagem motivacional
    message += _get_motivational_message(done_percent, em_andamento, pendentes)

    # Link
    tasks_db_url = f"https://notion.so/{settings.NOTION_TASKS_DB_ID.replace('-', '')}"
    message += f"\n\nVer no Notion: {tasks_db_url}"

    return message


def _truncate_text(text: str, max_length: int) -> str:
    """Trunca texto se ultrapassar max_length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def _get_motivational_message(done_percent: float, in_progress: int, pending: int) -> str:
    """Retorna mensagem motivacional baseada no progresso."""

    if done_percent == 100:
        return "🎉 Parabéns! Todas as tarefas concluídas!"

    elif done_percent >= 75:
        return "🔥 Quase lá! Finalize forte!"

    elif done_percent >= 50:
        return "💪 Você está com bom ritmo! Continue assim."

    elif done_percent >= 25:
        if in_progress > 0:
            return "👍 Bom começo! Foque nas tarefas em andamento."
        else:
            return "⏰ Acelere o ritmo para não acumular!"

    else:
        if pending > 5:
            return "⚠️ Muitas tarefas pendentes. Priorize as mais importantes!"
        else:
            return "💪 Hora de começar! Você consegue!"
