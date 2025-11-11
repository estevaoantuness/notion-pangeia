"""
Scheduler para envios automáticos de mensagens.

Este módulo gerencia jobs programados com horários variados por dia da semana,
incluindo jitter aleatório para parecer mais natural.

Horários base por dia:
- Segunda: 08:00 metas; 13:30 planejamento; 15:30 status; 18:00 fechamento; 22:00 reflexão
- Terça: 08:00 metas; 13:15 planejamento; 15:45 status; 18:10 fechamento; 21:50 reflexão
- Quarta: 08:10 metas; 13:40 planejamento; 16:00 status; 18:05 fechamento; 22:05 reflexão
- Quinta: 08:05 metas; 13:20 planejamento; 15:30 status; 18:20 fechamento; 21:55 reflexão
- Sexta: 08:00 metas; 12:00 consolidado; 17:00 fechamento; 21:30 reflexão
- Sábado/Domingo: 10:00 digest único (apenas se houver tasks)

Jitter: ±7 minutos por evento
Quiet hours: 07:30 - 22:30
"""

import logging
import random
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from config.colaboradores import get_colaboradores_ativos
from src.whatsapp.sender import WhatsAppSender
from src.messaging.humanizer import get_humanizer
from src.checkins.scheduler_adapter import get_random_checkin_adapter, is_random_checkins_enabled
from src.checkins.pending_tracker import get_pending_checkin_tracker

logger = logging.getLogger(__name__)

# Timezone
TZ = ZoneInfo("America/Sao_Paulo")

# Mapa de horários base por dia da semana (0=seg, 1=ter, ..., 6=dom)
BASE_SCHEDULE = {
    0: [  # Segunda
        ("metas", time(8, 0)),
        ("planning", time(13, 30)),
        ("status", time(15, 30)),
        ("closing", time(18, 0)),
        ("reflection", time(22, 0))
    ],
    1: [  # Terça
        ("metas", time(8, 0)),
        ("planning", time(13, 15)),
        ("status", time(15, 45)),
        ("closing", time(18, 10)),
        ("reflection", time(21, 50))
    ],
    2: [  # Quarta
        ("metas", time(8, 10)),
        ("planning", time(13, 40)),
        ("status", time(16, 0)),
        ("closing", time(18, 5)),
        ("reflection", time(22, 5))
    ],
    3: [  # Quinta
        ("metas", time(8, 5)),
        ("planning", time(13, 20)),
        ("status", time(15, 30)),
        ("closing", time(18, 20)),
        ("reflection", time(21, 55))
    ],
    4: [  # Sexta
        ("metas", time(8, 0)),
        ("consolidado", time(12, 0)),
        ("closing", time(17, 0)),
        ("reflection", time(21, 30))
    ],
    5: [  # Sábado
        ("weekend_digest", time(10, 0))
    ],
    6: [  # Domingo
        ("weekend_digest", time(10, 0))
    ]
}


def add_jitter(dt: datetime, minutes: int = 7) -> datetime:
    """
    Adiciona jitter aleatório a um datetime.

    Args:
        dt: Datetime base
        minutes: Variação máxima em minutos (±)

    Returns:
        Datetime com jitter aplicado
    """
    delta = random.randint(-minutes, minutes)
    return dt + timedelta(minutes=delta)


def is_within_quiet_hours(dt: datetime) -> bool:
    """
    Verifica se horário está fora do quiet hours (07:30 - 22:30).

    Args:
        dt: Datetime para verificar

    Returns:
        True se está FORA do quiet hours (precisa ajustar)
    """
    start = dt.replace(hour=7, minute=30, second=0, microsecond=0)
    end = dt.replace(hour=22, minute=30, second=0, microsecond=0)
    return not (start <= dt <= end)


def clamp_to_quiet_hours(dt: datetime) -> datetime:
    """
    Ajusta horário para ficar dentro do quiet hours.

    Args:
        dt: Datetime original

    Returns:
        Datetime ajustado para 07:30 ou 22:30 se necessário
    """
    lower = dt.replace(hour=7, minute=30, second=0, microsecond=0)
    upper = dt.replace(hour=22, minute=30, second=0, microsecond=0)

    if dt < lower:
        return lower
    elif dt > upper:
        return upper
    return dt


class TaskScheduler:
    """
    Gerencia jobs programados com horários dinâmicos e jitter.

    Features:
    - Horários variados por dia da semana
    - Jitter aleatório de ±7 minutos
    - Quiet hours (07:30 - 22:30)
    - Reagendamento diário automático às 00:05
    - Digest único para fins de semana
    """

    def __init__(self):
        """Inicializa o scheduler."""
        self.scheduler = BackgroundScheduler(timezone=TZ)
        self.whatsapp_sender = WhatsAppSender()
        self.humanizer = get_humanizer()

        # Initialize Redis for random check-ins
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis connected for random check-ins")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Random check-ins will not work.")
            self.redis_client = None

        # Initialize random check-in adapter (if Redis available and feature enabled)
        if self.redis_client and is_random_checkins_enabled():
            self.random_checkin_adapter = get_random_checkin_adapter(
                self.redis_client,
                self.whatsapp_sender
            )
            logger.info("Random check-in adapter initialized")
        else:
            self.random_checkin_adapter = None

        # Adiciona listeners de eventos
        self.scheduler.add_listener(
            self._job_executed,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._job_error,
            EVENT_JOB_ERROR
        )

        logger.info("TaskScheduler inicializado")

    def _job_executed(self, event):
        """Handler para job executado com sucesso."""
        logger.info(f"✅ Job '{event.job_id}' executado com sucesso")

    def _job_error(self, event):
        """Handler para erro em job."""
        logger.error(f"❌ Erro no job '{event.job_id}': {event.exception}")

    def send_morning_tasks(self):
        """
        Job: Envia tasks do dia para todos os colaboradores (9h).

        Envia mensagem matinal personalizada com:
        - Saudação temporal
        - Lista de tasks do dia
        - Estatísticas de progresso
        """
        logger.info("=" * 60)
        logger.info("🌅 INICIANDO ENVIO MATINAL DE TASKS")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_enviados = 0
        total_erros = 0

        for nome, info in colaboradores.items():
            try:
                logger.info(f"Enviando tasks matinais para {nome}...")

                # Envia tasks com saudação matinal
                success, sid, error = self.whatsapp_sender.send_daily_tasks(
                    person_name=nome,
                    include_greeting=True  # Vai usar saudação temporal
                )

                if success:
                    logger.info(f"✅ Tasks enviadas para {nome}. SID: {sid}")
                    total_enviados += 1
                else:
                    logger.error(f"❌ Falha ao enviar para {nome}: {error}")
                    total_erros += 1

            except Exception as e:
                logger.error(f"❌ Erro ao processar {nome}: {e}")
                total_erros += 1

        logger.info("=" * 60)
        logger.info(f"📊 RESUMO: {total_enviados} enviados, {total_erros} erros")
        logger.info("=" * 60)

    def _send_checkin_metas(self):
        """Wrapper para check-in de metas (08:00)."""
        self._send_checkin("metas", "Metas")

    def _send_checkin_planning(self):
        """Wrapper para check-in de planejamento."""
        self._send_checkin("planning", "Planejamento")

    def _send_checkin_status(self):
        """Wrapper para check-in de status."""
        self._send_checkin("status", "Status")

    def _send_checkin_consolidado(self):
        """Wrapper para check-in de consolidado (sexta)."""
        self._send_checkin("consolidado", "Consolidado")

    def _send_checkin_closing(self):
        """Wrapper para check-in de fechamento."""
        self._send_checkin("closing", "Fechamento")

    def _send_weekend_digest(self):
        """Wrapper para digest do fim de semana."""
        self._send_checkin("weekend_digest", "Digest do Fim de Semana")

    def _send_checkin_reflection(self):
        """
        Envia resumo automático do dia às 22h (sem perguntas reflexivas).

        Calcula progresso do dia e envia mensagem simples.
        """
        logger.info("=" * 60)
        logger.info("🌙 INICIANDO RESUMO NOTURNO (22H)")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_enviados = 0
        total_erros = 0

        from src.notion.tasks import TasksManager
        tasks_manager = TasksManager()

        for nome, info in colaboradores.items():
            try:
                # Calcula progresso do dia
                progress = tasks_manager.calculate_progress(nome)
                done = progress.get("concluidas", 0)
                total = progress.get("total", 0)
                percent = progress.get("percentual", 0)

                # Monta mensagem de resumo simples
                if total == 0:
                    message = f"🌙 Boa noite, {nome.split()[0]}!\n\nNenhuma tarefa pendente hoje. Descanse bem! 😴"
                elif done == total:
                    message = (
                        f"🌙 Boa noite, {nome.split()[0]}!\n\n"
                        f"📊 Resumo do dia: {done}/{total} tarefas concluídas (100%)! 🎉\n\n"
                        "Excelente trabalho! Descanse bem! 😴"
                    )
                else:
                    message = (
                        f"🌙 Boa noite, {nome.split()[0]}!\n\n"
                        f"📊 Resumo do dia: {done}/{total} tarefas concluídas ({percent:.0f}%).\n\n"
                        "Descanse bem! 😴"
                    )

                logger.info(f"Enviando resumo noturno para {nome}...")

                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=nome,
                    message=message
                )

                if success:
                    logger.info(f"✅ Resumo enviado para {nome}. SID: {sid}")
                    total_enviados += 1
                else:
                    logger.error(f"❌ Falha ao enviar para {nome}: {error}")
                    total_erros += 1

            except Exception as e:
                logger.error(f"❌ Erro ao processar {nome}: {e}")
                total_erros += 1

        logger.info("=" * 60)
        logger.info(f"📊 RESUMO: {total_enviados} enviados, {total_erros} erros")
        logger.info("=" * 60)

    def send_consolidated_midday(self):
        """
        Job: Consolidado de meio-dia (sexta-feira às 12:00).

        Envia resumo consolidado do dia, substituindo os check-ins
        de 13:30 e 15:30 na sexta-feira.
        """
        logger.info("=" * 60)
        logger.info("📊 INICIANDO CONSOLIDADO DE MEIO-DIA (SEXTA)")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_enviados = 0
        total_erros = 0

        # Mensagem personalizada para sexta
        message = (
            "🎉 *Sexta-feira!*\n\n"
            "Como está o andamento das tasks de hoje?\n\n"
            "💡 Lembre-se: fechamento antecipado às 17h!\n\n"
            "Use:\n"
            "• `minhas tarefas` - Ver lista\n"
            "• `feito N` - Marcar concluída\n"
            "• `progresso` - Ver percentual"
        )

        for nome, info in colaboradores.items():
            try:
                logger.info(f"Enviando consolidado para {nome}...")

                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=nome,
                    message=message
                )

                if success:
                    logger.info(f"✅ Consolidado enviado para {nome}. SID: {sid}")
                    total_enviados += 1
                else:
                    logger.error(f"❌ Falha ao enviar para {nome}: {error}")
                    total_erros += 1

            except Exception as e:
                logger.error(f"❌ Erro ao processar {nome}: {e}")
                total_erros += 1

        logger.info("=" * 60)
        logger.info(f"📊 RESUMO: {total_enviados} enviados, {total_erros} erros")
        logger.info("=" * 60)

    def send_weekend_digest(self):
        """
        Job: Digest de fim de semana (sábado/domingo às 10:00).

        Envia apenas se houver tasks pendentes.
        """
        logger.info("=" * 60)
        logger.info("🏖️  INICIANDO WEEKEND DIGEST")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_enviados = 0
        total_pulados = 0

        from src.notion.tasks import TasksManager
        tasks_manager = TasksManager()

        for nome, info in colaboradores.items():
            try:
                # Verifica se tem tasks pendentes
                tasks_grouped = tasks_manager.get_person_tasks(nome)
                total_tasks = sum(len(tasks) for tasks in tasks_grouped.values())

                if total_tasks == 0:
                    logger.info(f"⏭️  {nome}: sem tasks pendentes, pulando")
                    total_pulados += 1
                    continue

                # Monta mensagem de digest
                message = (
                    f"🏖️ *Bom fim de semana, {nome.split()[0]}!*\n\n"
                    f"Você tem *{total_tasks} task(s)* pendente(s).\n\n"
                    "💡 Aproveite o descanso!\n"
                    "Use `minhas tarefas` se quiser ver a lista."
                )

                logger.info(f"Enviando digest para {nome} ({total_tasks} tasks)...")

                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=nome,
                    message=message
                )

                if success:
                    logger.info(f"✅ Digest enviado para {nome}. SID: {sid}")
                    total_enviados += 1
                else:
                    logger.error(f"❌ Falha ao enviar para {nome}: {error}")

            except Exception as e:
                logger.error(f"❌ Erro ao processar {nome}: {e}")

        logger.info("=" * 60)
        logger.info(f"📊 RESUMO: {total_enviados} enviados, {total_pulados} pulados")
        logger.info("=" * 60)

    def _send_checkin(self, checkin_key: str, time_label: str):
        """
        Envia check-in para todos os colaboradores.

        Args:
            checkin_key: Chave do check-in no humanizer ("13h30", "15h30", etc)
            time_label: Label do horário para logs ("13:30", "15:30", etc)
        """
        logger.info("=" * 60)
        logger.info(f"💬 INICIANDO CHECK-IN {time_label}")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_enviados = 0
        total_erros = 0

        # Get pending check-in tracker for recording sent messages
        tracker = get_pending_checkin_tracker()

        # Pega pergunta humanizada
        question = self.humanizer.get_checkin_question(checkin_key)

        for nome, info in colaboradores.items():
            try:
                logger.info(f"Enviando check-in para {nome}...")

                # Envia pergunta via WhatsApp
                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=nome,
                    message=question
                )

                if success:
                    logger.info(f"✅ Check-in enviado para {nome}. SID: {sid}")

                    # Record pending check-in so responses can be routed correctly
                    checkin_id = tracker.record_sent_checkin(
                        user_id=nome,
                        person_name=nome,
                        checkin_type=checkin_key,
                        checkin_message=question,
                        response_window_minutes=120  # 2 hours to respond
                    )
                    logger.info(f"📍 Recorded pending check-in: {checkin_id}")

                    # ═══════════════════════════════════════════════════════════════════
                    # AGENDAR FOLLOW-UP (15 MINUTOS APÓS ENVIO)
                    # ═══════════════════════════════════════════════════════════════════
                    try:
                        followup_time = datetime.now(TZ) + timedelta(minutes=15)
                        followup_job_id = f"followup-{checkin_id}"

                        self.scheduler.add_job(
                            func=self._send_followup_if_needed,
                            trigger=DateTrigger(run_date=followup_time),
                            id=followup_job_id,
                            name=f"Follow-up: {checkin_key} para {nome}",
                            replace_existing=True,
                            kwargs={
                                'user_id': nome,
                                'checkin_id': checkin_id,
                                'checkin_type': checkin_key
                            }
                        )
                        logger.info(f"⏰ Follow-up agendado para {followup_time.strftime('%H:%M:%S')}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao agendar follow-up: {e}")

                    total_enviados += 1
                else:
                    logger.error(f"❌ Falha ao enviar para {nome}: {error}")
                    total_erros += 1

            except Exception as e:
                logger.error(f"❌ Erro ao processar {nome}: {e}")
                total_erros += 1

        logger.info("=" * 60)
        logger.info(f"📊 RESUMO: {total_enviados} enviados, {total_erros} erros")
        logger.info("=" * 60)

    def _send_followup_if_needed(self, user_id: str, checkin_id: str, checkin_type: str):
        """
        Envia follow-up de check-in se o usuário ainda não respondeu.

        Chamado automaticamente 15 minutos após o envio do check-in inicial.
        Verifica se há um check-in pendente e, se houver, envia uma mensagem
        de follow-up aleatória das 15 opções.

        Args:
            user_id: ID do usuário
            checkin_id: ID do check-in enviado
            checkin_type: Tipo de check-in (metas, planning, closing, etc)
        """
        try:
            from src.checkins.pending_tracker import get_pending_checkin_tracker

            tracker = get_pending_checkin_tracker()
            pending_checkin = tracker.get_pending_checkin(user_id)

            # Verifica se ainda há check-in pendente
            if pending_checkin and pending_checkin.checkin_id == checkin_id:
                # Usuário não respondeu - enviar follow-up
                followup_msg = self.humanizer.get_followup_message()

                logger.info("=" * 60)
                logger.info(f"📬 ENVIANDO FOLLOW-UP PARA {user_id}")
                logger.info("=" * 60)

                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=user_id,
                    message=followup_msg
                )

                if success:
                    logger.info(f"✅ Follow-up enviado para {user_id}. SID: {sid}")
                    logger.info(f"📨 Mensagem: {followup_msg[:80]}...")
                else:
                    logger.error(f"❌ Falha ao enviar follow-up para {user_id}: {error}")

                logger.info("=" * 60)

            else:
                # Usuário já respondeu - skip
                logger.info(
                    f"✓ Follow-up skipped: {user_id} já respondeu ao check-in {checkin_id}"
                )

        except Exception as e:
            logger.error(f"❌ Erro ao enviar follow-up para {user_id}: {e}", exc_info=True)

    def materialize_times_for_day(self, day: datetime) -> list:
        """
        Gera lista de eventos do dia com jitter aplicado.

        Args:
            day: Data para gerar eventos

        Returns:
            Lista de tuplas (nome_evento, datetime_com_jitter)
        """
        weekday = day.weekday()
        events = BASE_SCHEDULE[weekday]
        times = []

        for name, t in events:
            # Combina data + horário
            dt = datetime.combine(day.date(), t, TZ)

            # Adiciona jitter
            dt = add_jitter(dt, minutes=7)

            # Clamp para quiet hours se necessário
            if is_within_quiet_hours(dt):
                dt = clamp_to_quiet_hours(dt)

            times.append((name, dt))

        # Ordena por horário após jitter
        times.sort(key=lambda x: x[1])

        return times

    def schedule_today(self):
        """
        Agenda todos os jobs do dia atual com jitter.

        Chamado automaticamente às 00:05 de cada dia.
        """
        today = datetime.now(TZ)
        plan = self.materialize_times_for_day(today)

        logger.info("=" * 60)
        logger.info(f"📅 AGENDANDO JOBS PARA {today.strftime('%d/%m/%Y (%A)')}")
        logger.info("=" * 60)

        for name, dt in plan:
            # Só agenda se o horário ainda não passou
            if dt <= today:
                logger.info(f"⏭️  Pulando '{name}' às {dt.strftime('%H:%M')} (já passou)")
                continue

            # Mapeia nome do evento para função
            # IMPORTANTE: Usar métodos em vez de lambdas para evitar closure bug
            job_func = None
            job_name = ""

            if name == "metas":
                job_func = self.send_morning_tasks
                job_name = "Envio Matinal de Tasks"
            elif name == "planning":
                job_func = self._send_checkin_planning
                job_name = "Check-in Planejamento"
            elif name == "status":
                job_func = self._send_checkin_status
                job_name = "Check-in Status"
            elif name == "closing":
                job_func = self._send_checkin_closing
                job_name = "Check-in Fechamento"
            elif name == "reflection":
                job_func = self._send_checkin_reflection
                job_name = "Check-in Reflexão"
            elif name == "consolidado":
                job_func = self.send_consolidated_midday
                job_name = "Consolidado Meio-Dia (Sexta)"
            elif name == "weekend_digest":
                job_func = self.send_weekend_digest
                job_name = "Weekend Digest"
            else:
                logger.warning(f"Evento desconhecido: {name}")
                continue

            # Adiciona job com DateTrigger (one-time)
            job_id = f"{name}-{dt.strftime('%Y%m%d%H%M')}"

            self.scheduler.add_job(
                func=job_func,
                trigger=DateTrigger(run_date=dt),
                id=job_id,
                name=job_name,
                replace_existing=True  # ✅ FIXED: Replace duplicates (was False)
            )

            logger.info(f"✅ Agendado: {job_name} → {dt.strftime('%H:%M:%S')}")

        logger.info("=" * 60)
        logger.info(f"Total de {len(plan)} jobs agendados para hoje")

        # Log all scheduled jobs for verification
        logger.info("📋 JOBS AGENDADOS:")
        for job in self.scheduler.get_jobs():
            # next_run_time só existe depois do scheduler iniciar
            run_time = getattr(job, "next_run_time", None)
            run_time_str = run_time if run_time else "(pending)"
            logger.info(f"  - {job.id} @ {run_time_str}")

        logger.info("=" * 60)

        # Schedule random check-ins if enabled
        # ⚠️ DISABLED: Causing conflicts with regular check-in schedule
        # Both systems were triggering at same time, causing duplicates
        # Use either regular schedule OR random schedule, not both
        if False and self.random_checkin_adapter:  # DISABLED
            try:
                random_checkins_scheduled = self.random_checkin_adapter.schedule_random_checkins_for_day(
                    today,
                    self.scheduler
                )
                logger.info(f"Random check-ins scheduled: {random_checkins_scheduled}")
            except Exception as e:
                logger.error(f"Error scheduling random check-ins: {e}")

    def setup_jobs(self):
        """
        Configura sistema de agendamento dinâmico.

        - Agenda jobs do dia atual
        - Configura reagendamento diário às 00:05
        """
        logger.info("Configurando sistema de agendamento dinâmico...")

        # Agenda jobs de hoje
        self.schedule_today()

        # Configura reagendamento diário às 00:05
        self.scheduler.add_job(
            func=self.schedule_today,
            trigger=CronTrigger(hour=0, minute=5, timezone=TZ),
            id='daily_rescheduler',
            name='Reagendamento Diário',
            replace_existing=True
        )

        logger.info("✅ Reagendamento diário configurado (00:05)")
        logger.info("Todos os jobs foram configurados!")

    def start(self):
        """Inicia o scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Scheduler iniciado!")
            self.print_jobs()
        else:
            logger.warning("Scheduler já está rodando")

    def stop(self):
        """Para o scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️  Scheduler parado")
        else:
            logger.warning("Scheduler já está parado")

    def print_jobs(self):
        """Imprime lista de jobs agendados."""
        jobs = self.scheduler.get_jobs()

        if not jobs:
            logger.info("Nenhum job agendado")
            return

        logger.info("=" * 60)
        logger.info("📅 JOBS AGENDADOS")
        logger.info("=" * 60)

        for job in jobs:
            next_run = job.next_run_time
            next_run_str = next_run.strftime("%d/%m/%Y %H:%M:%S") if next_run else "N/A"
            logger.info(f"  • {job.name}")
            logger.info(f"    ID: {job.id}")
            logger.info(f"    Próxima execução: {next_run_str}")
            logger.info("")

        logger.info("=" * 60)

    def run_job_now(self, job_id: str):
        """
        Executa um job imediatamente (para testes).

        Args:
            job_id: ID do job ('morning_tasks', 'checkin_1330', etc)
        """
        job = self.scheduler.get_job(job_id)

        if not job:
            logger.error(f"Job '{job_id}' não encontrado")
            return False

        logger.info(f"▶️  Executando job '{job_id}' manualmente...")
        job.func()
        return True


# Singleton global
_scheduler_instance = None


def get_scheduler() -> TaskScheduler:
    """
    Retorna instância singleton do scheduler.

    Returns:
        Instância do TaskScheduler
    """
    global _scheduler_instance

    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler()

    return _scheduler_instance
