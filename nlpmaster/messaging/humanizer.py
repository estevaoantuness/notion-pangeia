"""
Humanizador de mensagens do bot.

Sistema completo de respostas contextuais baseado em YAML.
Evita repetições imediatas e adiciona variação natural.
"""

import logging
import random
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MessageHumanizer:
    """
    Gerencia respostas humanizadas do bot.

    Features:
    - Carrega respostas de config/replies.yaml
    - Evita repetição imediata da mesma variação
    - Suporta formatação com placeholders
    - Respostas contextuais (prioridade, hora do dia, etc)
    """

    def __init__(self):
        """Inicializa o humanizador carregando o YAML."""
        # Carrega arquivo de respostas
        replies_path = Path(__file__).parent.parent.parent / 'config' / 'replies.yaml'

        try:
            with open(replies_path, 'r', encoding='utf-8') as f:
                self.replies = yaml.safe_load(f)
            logger.info(f"Replies carregadas de {replies_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar replies.yaml: {e}")
            self.replies = {}

        # Cache para evitar repetições imediatas
        self.last_used = {}

    def pick(
        self,
        category: str,
        subcategory: str = 'default',
        **kwargs
    ) -> str:
        """
        Seleciona uma variação aleatória, evitando repetição imediata.

        Args:
            category: Categoria principal (ex: 'task_completed')
            subcategory: Subcategoria (ex: 'first_of_day')
            **kwargs: Variáveis para formatação (ex: index=2, name="João")

        Returns:
            Mensagem formatada com placeholders preenchidos
        """
        key = f"{category}.{subcategory}"

        # Busca opções - suporta aninhamento com '.'
        parts = subcategory.split('.')
        options = self.replies.get(category, {})

        for part in parts:
            if isinstance(options, dict):
                options = options.get(part, [])
            else:
                break

        if not options:
            logger.warning(f"Resposta não configurada: {key}")
            return f"[Resposta não configurada: {key}]"

        # Garante que seja lista
        if isinstance(options, str):
            options = [options]

        # Evita repetir a última usada (se houver mais de uma opção)
        if len(options) > 1:
            available = [opt for opt in options if opt != self.last_used.get(key)]
            if not available:
                available = options
        else:
            available = options

        # Seleciona aleatoriamente
        selected = random.choice(available)
        self.last_used[key] = selected

        # Formata com kwargs
        try:
            return selected.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Placeholder ausente em {key}: {e}")
            return selected

    def get_greeting(self, name: Optional[str] = None) -> str:
        """
        Retorna saudação contextual baseada em hora e dia da semana.

        Args:
            name: Nome da pessoa (opcional)

        Returns:
            Saudação formatada
        """
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 4=Friday

        first_name = name.split()[0] if name else "você"

        # Prioriza dia da semana especial
        if weekday == 0:  # Segunda
            return self.pick('greetings', 'monday', name=first_name)
        elif weekday == 4:  # Sexta
            return self.pick('greetings', 'friday', name=first_name)

        # Saudação por horário
        if 5 <= hour < 12:
            return self.pick('greetings', 'morning', name=first_name)
        elif 12 <= hour < 18:
            return self.pick('greetings', 'afternoon', name=first_name)
        else:
            return self.pick('greetings', 'evening', name=first_name)

    def get_task_completed_message(
        self,
        task_number: int,
        task_title: str,
        is_first: bool = False,
        is_last: bool = False,
        is_high_priority: bool = False,
        old_percent: Optional[float] = None,
        new_percent: Optional[float] = None
    ) -> str:
        """
        Retorna mensagem de tarefa concluída com contexto.

        Args:
            task_number: Número da task
            task_title: Título da task
            is_first: Se é a primeira do dia
            is_last: Se é a última do dia
            is_high_priority: Se tem prioridade alta
            old_percent: Percentual anterior (opcional)
            new_percent: Percentual novo (opcional)

        Returns:
            Mensagem formatada
        """
        # Escolhe subcategoria baseada no contexto
        if is_last:
            subcategory = 'last_of_day'
        elif is_first:
            subcategory = 'first_of_day'
        elif is_high_priority:
            subcategory = 'high_priority'
        else:
            subcategory = 'default'

        message = self.pick(
            'task_completed',
            subcategory,
            number=task_number,
            title=task_title
        )

        # Adiciona progresso se fornecido
        if old_percent is not None and new_percent is not None:
            progress_msg = self.pick(
                'task_completed',
                'with_progress',
                old_percent=int(old_percent),
                new_percent=int(new_percent)
            )
            message += f"\n\n{progress_msg}"

        # Adiciona CTA
        message += f"\n\n{self.pick('ctas', 'see_tasks')}"

        return message

    def get_task_in_progress_message(
        self,
        task_number: int,
        task_title: str,
        priority: str = 'medium'
    ) -> str:
        """
        Retorna mensagem de tarefa em andamento.

        Args:
            task_number: Número da task
            task_title: Título da task
            priority: Prioridade (high, medium, low)

        Returns:
            Mensagem formatada
        """
        if priority == 'high':
            subcategory = 'high_priority'
        elif priority == 'medium':
            subcategory = 'medium_priority'
        else:
            subcategory = 'default'

        return self.pick(
            'task_in_progress',
            subcategory,
            number=task_number,
            title=task_title
        )

    def get_task_blocked_message(
        self,
        task_number: int,
        task_title: str,
        reason: Optional[str] = None,
        is_high_priority: bool = False
    ) -> str:
        """
        Retorna mensagem de tarefa bloqueada.

        Args:
            task_number: Número da task
            task_title: Título da task
            reason: Motivo do bloqueio (opcional)
            is_high_priority: Se tem prioridade alta

        Returns:
            Mensagem formatada
        """
        if not reason:
            return self.pick(
                'task_blocked',
                'without_reason',
                number=task_number,
                title=task_title
            )

        if is_high_priority:
            subcategory = 'high_priority_blocked'
        else:
            subcategory = 'with_reason'

        return self.pick(
            'task_blocked',
            subcategory,
            number=task_number,
            title=task_title,
            reason=reason
        )

    def get_progress_message(
        self,
        percent: float,
        done: int,
        total: int
    ) -> str:
        """
        Retorna mensagem de progresso baseada na porcentagem.

        Args:
            percent: Percentual de conclusão (0-100)
            done: Número de tasks concluídas
            total: Total de tasks

        Returns:
            Mensagem formatada
        """
        if percent == 0:
            subcategory = 'zero'
        elif percent < 25:
            subcategory = 'low'
        elif percent < 50:
            subcategory = 'medium'
        elif percent < 75:
            subcategory = 'high'
        elif percent < 100:
            subcategory = 'very_high'
        else:
            subcategory = 'complete'

        return self.pick(
            'progress',
            subcategory,
            percent=int(percent),
            done=done,
            total=total
        )

    def get_error_message(
        self,
        error_type: str,
        **kwargs
    ) -> str:
        """
        Retorna mensagem de erro.

        Args:
            error_type: Tipo do erro (invalid_index, invalid_format, etc)
            **kwargs: Dados adicionais (index, total, etc)

        Returns:
            Mensagem formatada
        """
        return self.pick('errors', error_type, **kwargs)

    def get_help_message(self, short: bool = False) -> str:
        """
        Retorna mensagem de ajuda.

        Args:
            short: Se deve usar versão curta

        Returns:
            Mensagem de ajuda
        """
        subcategory = 'short' if short else 'full'
        return self.pick('help', subcategory)

    def get_checkin_question(self, checkin_type: str) -> str:
        """
        Retorna pergunta de check-in.

        Args:
            checkin_type: Tipo do check-in (planning, status, closing, reflection)

        Returns:
            Pergunta formatada
        """
        return self.pick('checkins', checkin_type)

    def get_task_list_message(
        self,
        has_tasks: bool,
        header: bool = True,
        footer: bool = True
    ) -> Dict[str, str]:
        """
        Retorna partes da mensagem de listagem de tasks.

        Args:
            has_tasks: Se há tasks ou não
            header: Se deve incluir header
            footer: Se deve incluir footer

        Returns:
            Dict com 'header', 'footer', 'footer_cta', ou 'no_tasks'
        """
        if not has_tasks:
            return {
                'message': self.pick('task_list', 'no_tasks')
            }

        result = {}

        if header:
            result['header'] = self.pick('task_list', 'with_tasks.header')

        if footer:
            result['footer'] = self.pick('task_list', 'with_tasks.footer')
            result['footer_cta'] = self.pick('task_list', 'with_tasks.footer_cta')

        return result


# Singleton global
_humanizer_instance = None


def get_humanizer() -> MessageHumanizer:
    """
    Retorna instância singleton do humanizador.

    Returns:
        Instância do MessageHumanizer
    """
    global _humanizer_instance

    if _humanizer_instance is None:
        _humanizer_instance = MessageHumanizer()

    return _humanizer_instance
