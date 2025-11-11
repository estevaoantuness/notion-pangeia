"""
Formatação de detalhes de tarefas.

Funções para formatar visualização detalhada de uma tarefa específica.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

TZ = ZoneInfo("America/Sao_Paulo")


def format_task_details(task: Dict, task_index: int) -> str:
    """
    Formata detalhes completos de uma tarefa.

    Args:
        task: Dict com informações da tarefa
        task_index: Número da tarefa na lista

    Returns:
        Mensagem formatada
    """
    if not task:
        return "❌ Erro ao buscar detalhes da tarefa."

    message = f"📋 *TAREFA #{task_index}*\n\n"

    # Título
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "📌 *Título*\n"
    message += f"{task['title']}\n\n"

    # Descrição
    if task.get('description') and task['description'] != "Sem descrição":
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "📝 *Descrição*\n"
        # Limitar descrição a 300 caracteres
        description = task['description']
        if len(description) > 300:
            description = description[:297] + "..."
        message += f"{description}\n\n"

    # Informações
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "ℹ️ *Informações*\n\n"

    # Status
    status_emoji = get_status_emoji(task.get('status'))
    message += f"Status: {status_emoji} {task.get('status', 'Pendente')}\n"

    # Prioridade
    if task.get('priority'):
        message += f"Prioridade: {task['priority']}\n"

    # Prazo
    if task.get('deadline'):
        deadline_formatted = format_deadline(task['deadline'])
        message += f"Prazo: {deadline_formatted}\n"

    # Tags
    if task.get('tags'):
        tags_str = ' '.join([f"#{tag}" for tag in task['tags']])
        message += f"Tags: {tags_str}\n"

    message += "\n"

    # Link
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "🔗 *Ver no Notion*\n"
    message += f"{task['url']}\n\n"

    # Ações rápidas
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "*Ações rápidas:*\n"
    message += f"• *feito {task_index}* → marcar como concluída\n"
    message += f"• *andamento {task_index}* → começar tarefa\n"
    message += f"• *bloqueada {task_index} [motivo]* → bloquear"

    return message


def get_status_emoji(status: Optional[str]) -> str:
    """Retorna emoji baseado no status."""
    if not status:
        return '⚪'

    status_map = {
        'Done': '✅',
        'Concluída': '✅',
        'Completed': '✅',
        'In Progress': '🔵',
        'Em Andamento': '🔵',
        'Doing': '🔵',
        'Blocked': '🔴',
        'Bloqueada': '🔴',
        'To Do': '⚪',
        'A Fazer': '⚪',
        'Not Started': '⚪',
        'Pendente': '⚪'
    }
    return status_map.get(status, '⚪')


def format_deadline(deadline: Optional[Dict]) -> str:
    """
    Formata deadline de forma amigável.

    Args:
        deadline: Dict com 'start' e 'end' ou None

    Returns:
        String formatada com data e urgência
    """
    if not deadline or not deadline.get('start'):
        return "Sem prazo definido"

    try:
        deadline_str = deadline.get('start')
        deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))

        # Converter para timezone local
        deadline_local = deadline_dt.astimezone(TZ)
        now = datetime.now(TZ)

        # Formatar data
        date_str = deadline_local.strftime("%d/%m/%Y")
        time_str = deadline_local.strftime("%Hh%M") if deadline_local.hour != 0 or deadline_local.minute != 0 else ""

        # Calcular diferença
        diff = (deadline_local.date() - now.date()).days

        if diff < 0:
            urgency = "⚠️ ATRASADO"
        elif diff == 0:
            urgency = "🔥 HOJE"
        elif diff == 1:
            urgency = "⏰ Amanhã"
        elif diff <= 3:
            urgency = f"📅 Em {diff} dias"
        else:
            urgency = ""

        result = f"{date_str}"
        if time_str:
            result += f" às {time_str}"
        if urgency:
            result += f" ({urgency})"

        return result

    except Exception as e:
        logger.error(f"Erro ao formatar deadline: {e}")
        return str(deadline.get('start', 'Data inválida'))
