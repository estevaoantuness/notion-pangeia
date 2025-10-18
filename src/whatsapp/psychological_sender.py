"""
Psychological Sender - Sender Evolution API + Motor Psicológico.

Combina Evolution API com análise psicológica, chunking e deduplicação.
"""

import logging
from typing import Optional

from src.whatsapp.sender import WhatsAppSender
from src.messaging.chunker import MessageChunker
from src.messaging.deduplicator import get_deduplicator
from src.psychology.engine import PsychologicalEngine
from src.psychology.communicator import EmpatheticCommunicator
from src.people.analytics import PeopleAnalytics
from config.colaboradores import get_phone_by_name
from config.settings import settings

logger = logging.getLogger(__name__)


class PsychologicalSender(WhatsAppSender):
    """
    Sender Evolution API com inteligência psicológica.

    Adiciona:
    - Análise de estado emocional
    - Mensagens empáticas
    - Chunking automático
    - Deduplicação
    """

    def __init__(self):
        super().__init__()

        # Componentes psicológicos
        self.psych_engine = PsychologicalEngine() if settings.ENABLE_PSYCHOLOGY else None
        self.communicator = EmpatheticCommunicator() if settings.ENABLE_PSYCHOLOGY else None
        self.people_analytics = PeopleAnalytics() if settings.ENABLE_PSYCHOLOGY else None

        # Otimizações
        self.chunker = MessageChunker() if settings.ENABLE_MESSAGE_CHUNKING else None
        self.deduplicator = get_deduplicator() if settings.ENABLE_DEDUPLICATION else None

        logger.info(
            f"PsychologicalSender inicializado - "
            f"Psicologia: {settings.ENABLE_PSYCHOLOGY}, "
            f"Chunking: {settings.ENABLE_MESSAGE_CHUNKING}, "
            f"Dedup: {settings.ENABLE_DEDUPLICATION}"
        )

    def send_message(
        self,
        person_name: str,
        message: str,
        enrich: bool = True
    ) -> bool:
        """
        Envia mensagem com processamento psicológico.

        Args:
            person_name: Nome da pessoa
            message: Mensagem a enviar
            enrich: Se deve enriquecer psicologicamente

        Returns:
            True se enviou com sucesso
        """
        try:
            # Deduplicação
            if self.deduplicator:
                should_send, reason = self.deduplicator.should_send(person_name, message)

                if not should_send:
                    logger.info(f"Mensagem duplicada bloqueada para {person_name}: {reason}")
                    return True  # Retorna True porque não é erro, só skip

            # Chunking se mensagem é longa
            if self.chunker and len(message) > 1000:
                chunks = self.chunker.chunk_message(message)
                logger.info(f"Mensagem dividida em {len(chunks)} chunks")

                for i, chunk in enumerate(chunks):
                    logger.debug(f"Enviando chunk {i+1}/{len(chunks)}")
                    super().send_message(person_name, chunk)
                    # Pequeno delay entre chunks (opcional)
                    if i < len(chunks) - 1:
                        import time
                        time.sleep(0.5)

                return True

            # Enviar normalmente
            return super().send_message(person_name, message)

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {person_name}: {e}")
            return False

    def analyze_and_respond(
        self,
        person_name: str,
        phone: str,
        context: str = "completion",
        **kwargs
    ) -> Optional[str]:
        """
        Analisa estado psicológico e gera resposta empática.

        Args:
            person_name: Nome da pessoa
            phone: Telefone
            context: Contexto (completion, checkin, intervention)
            **kwargs: Argumentos adicionais (task_name, period, etc)

        Returns:
            Mensagem empática ou None se psicologia desabilitada
        """
        if not self.psych_engine or not self.communicator:
            return None

        try:
            # Analisar estado
            metrics = self._analyze_person(person_name, phone)

            if not metrics:
                return None

            # Gerar mensagem baseada no contexto
            if context == "completion":
                task_name = kwargs.get("task_name", "")
                is_first = kwargs.get("is_first_today", False)
                is_last = kwargs.get("is_last_today", False)

                return self.communicator.generate_task_completion_message(
                    name=person_name,
                    task_name=task_name,
                    metrics=metrics,
                    is_first_today=is_first,
                    is_last_today=is_last
                )

            elif context == "checkin":
                period = kwargs.get("period", "morning")
                tasks = kwargs.get("tasks")

                return self.communicator.generate_check_in_message(
                    name=person_name,
                    period=period,
                    metrics=metrics,
                    tasks=tasks
                )

            elif context == "intervention":
                return self.communicator.generate_intervention_message(
                    name=person_name,
                    metrics=metrics,
                    intervention_type="burnout"
                )

            return None

        except Exception as e:
            logger.error(f"Erro na análise psicológica de {person_name}: {e}")
            return None

    def _analyze_person(self, person_name: str, phone: str):
        """Analisa pessoa e retorna métricas."""
        if not self.psych_engine or not self.people_analytics:
            return None

        # Obter/criar perfil
        profile = self.people_analytics.get_or_create_profile(
            name=person_name,
            phone=phone
        )

        # Coletar dados
        tasks_data = self._collect_tasks_data(person_name)
        communication_data = {"recent_messages": [], "response_times": []}

        # Analisar
        metrics = self.psych_engine.analyze_person(tasks_data, communication_data)

        # Atualizar perfil
        self.people_analytics.update_profile_from_metrics(phone, metrics)

        return metrics

    def _collect_tasks_data(self, person_name: str):
        """Coleta dados de tarefas."""
        try:
            from src.notion.tasks import TasksManager
            tasks_manager = TasksManager()
            progress = tasks_manager.calculate_progress(person_name)

            return {
                "total": progress.get("total", 0),
                "completed": progress.get("concluidas", 0),
                "pending": progress.get("pendentes", 0),
                "blocked": progress.get("bloqueadas", 0)
            }
        except:
            return {"total": 0, "completed": 0, "pending": 0, "blocked": 0}


# Instância global
_psychological_sender = None


def get_psychological_sender() -> PsychologicalSender:
    """Retorna instância global."""
    global _psychological_sender

    if _psychological_sender is None:
        _psychological_sender = PsychologicalSender()

    return _psychological_sender
