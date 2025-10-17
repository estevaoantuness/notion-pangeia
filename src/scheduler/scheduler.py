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

    def _send_checkin_planning(self):
        """Wrapper para check-in de planejamento."""
        self._send_checkin("13h30", "Planejamento")

    def _send_checkin_status(self):
        """Wrapper para check-in de status."""
        self._send_checkin("15h30", "Status")

    def _send_checkin_closing(self):
        """Wrapper para check-in de fechamento."""
        self._send_checkin("18h00", "Fechamento")

    def _send_checkin_reflection(self):
        """Wrapper para check-in de reflexão."""
        self._send_checkin("22h00", "Reflexão")

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
                replace_existing=False
            )

            logger.info(f"✅ Agendado: {job_name} → {dt.strftime('%H:%M:%S')}")

        logger.info("=" * 60)
        logger.info(f"Total de {len(plan)} jobs agendados para hoje")
        logger.info("=" * 60)

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
