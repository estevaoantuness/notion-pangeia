"""
Scheduler Adapter - Integrates RandomCheckinScheduler with TaskScheduler

This module provides an adapter that allows RandomCheckinScheduler to work
seamlessly with the existing APScheduler infrastructure in TaskScheduler.

It handles:
- Feature flag checking
- Job scheduling for random check-ins
- Message loading and sending
- Error handling and logging
"""

import logging
import os
from datetime import datetime
from typing import Optional, List, Tuple
from zoneinfo import ZoneInfo

from src.checkins.random_scheduler import RandomCheckinScheduler
from src.checkins.user_preferences import CheckinPreferencesManager
from src.checkins.message_provider import get_message_provider
from config.colaboradores import get_colaboradores_ativos

logger = logging.getLogger(__name__)

TZ = ZoneInfo("America/Sao_Paulo")


def is_random_checkins_enabled() -> bool:
    """
    Verificar se random check-ins estão habilitados via feature flag

    Returns:
        True se ENABLE_RANDOM_CHECKINS=true
    """
    return os.getenv("ENABLE_RANDOM_CHECKINS", "false").lower() == "true"


class RandomCheckinSchedulerAdapter:
    """
    Adaptador para integrar RandomCheckinScheduler com TaskScheduler

    Responsibilities:
    - Check if feature is enabled
    - Schedule random check-ins para cada usuário
    - Load messages
    - Handle sending

    Exemplo de integração em TaskScheduler:
        adapter = RandomCheckinSchedulerAdapter(redis_client, whatsapp_sender)

        # Em schedule_today():
        if is_random_checkins_enabled():
            adapter.schedule_random_checkins_for_day(today)
    """

    def __init__(self, redis_client: object, whatsapp_sender: object):
        """
        Inicializar adapter

        Args:
            redis_client: Cliente Redis para preferences e scheduling
            whatsapp_sender: Instância de WhatsAppSender para envios
        """
        self.redis_client = redis_client
        self.whatsapp_sender = whatsapp_sender

        # Initialize components
        self.random_scheduler = RandomCheckinScheduler(
            timezone="America/Sao_Paulo",
            min_spacing_hours=int(os.getenv("RANDOM_CHECKIN_MIN_SPACING_HOURS", "2")),
            redis_client=redis_client
        )
        self.preferences_manager = CheckinPreferencesManager(redis_client)
        self.message_provider = get_message_provider()

        logger.info("RandomCheckinSchedulerAdapter initialized")

    def schedule_random_checkins_for_day(
        self,
        day: datetime,
        scheduler_instance
    ) -> int:
        """
        Agenda check-ins aleatórios para todos os usuários ativos

        Args:
            day: Data para agendar
            scheduler_instance: Instância do APScheduler (para add_job)

        Returns:
            Número de jobs agendados

        Process:
        1. Verificar se é weekday
        2. Para cada usuário ativo:
           a. Obter preferências
           b. Gerar check-ins aleatórios
           c. Agendar jobs via APScheduler
        """
        if not is_random_checkins_enabled():
            logger.debug("Random check-ins disabled (ENABLE_RANDOM_CHECKINS=false)")
            return 0

        if not self.random_scheduler.is_weekday(day):
            logger.debug(f"Skipping random check-ins for {day.strftime('%A')} (weekend)")
            return 0

        logger.info("=" * 60)
        logger.info(f"📅 AGENDANDO CHECK-INS ALEATÓRIOS PARA {day.strftime('%d/%m/%Y')}")
        logger.info("=" * 60)

        colaboradores = get_colaboradores_ativos()
        total_scheduled = 0

        for user_id, user_info in colaboradores.items():
            try:
                # Skip se usuário desabilitou check-ins
                if not self.preferences_manager.is_enabled(user_id):
                    logger.debug(f"Check-ins disabled for {user_id}, skipping")
                    continue

                # Obter preferências
                late_night_enabled = self.preferences_manager.has_late_night_enabled(user_id)
                frequency = self.preferences_manager.get_preferred_frequency(user_id)

                # Gerar horários aleatórios
                checkins = self.random_scheduler.schedule_daily_checkins(
                    user_id,
                    enable_late_night=late_night_enabled,
                    count=frequency
                )

                if not checkins:
                    logger.warning(f"No check-ins generated for {user_id}")
                    continue

                # Agendar cada check-in
                for checkin in checkins:
                    try:
                        self._schedule_single_checkin(
                            user_id=user_id,
                            user_info=user_info,
                            checkin=checkin,
                            day=day,
                            scheduler_instance=scheduler_instance
                        )
                        total_scheduled += 1

                    except Exception as e:
                        logger.error(f"Error scheduling checkin for {user_id}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error processing check-ins for {user_id}: {e}")
                continue

        logger.info("=" * 60)
        logger.info(f"Total de {total_scheduled} random check-ins agendados")
        logger.info("=" * 60)

        return total_scheduled

    def _schedule_single_checkin(
        self,
        user_id: str,
        user_info: dict,
        checkin: dict,
        day: datetime,
        scheduler_instance
    ) -> bool:
        """
        Agendar um único check-in via APScheduler

        Args:
            user_id: ID do usuário
            user_info: Dicionário com info do usuário (phone, etc)
            checkin: Dicionário com {"time": "HH:MM", "window": "morning", ...}
            day: Data
            scheduler_instance: APScheduler instance

        Returns:
            True se agendado com sucesso
        """
        try:
            # Parse time from checkin
            time_str = checkin["time"]  # "09:23"
            hour, minute = map(int, time_str.split(":"))

            # Criar datetime para este check-in
            checkin_datetime = day.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Verificar se ainda não passou
            now = datetime.now(TZ)
            if checkin_datetime <= now:
                logger.debug(f"Check-in for {user_id} at {time_str} already passed, skipping")
                return False

            # Gerar job ID único
            job_id = f"random_checkin-{user_id}-{day.strftime('%Y%m%d')}-{time_str.replace(':', '')}"

            # Criar função de callback (closure safe)
            def send_checkin_callback():
                self._send_random_checkin(user_id, user_info, checkin)

            # Agendar via APScheduler
            from apscheduler.triggers.date import DateTrigger

            scheduler_instance.add_job(
                func=send_checkin_callback,
                trigger=DateTrigger(run_date=checkin_datetime),
                id=job_id,
                name=f"Random Check-in ({checkin['window']}) para {user_id}",
                replace_existing=False
            )

            logger.info(
                f"✅ Agendado: Random check-in ({checkin['window']}) "
                f"para {user_id} → {checkin_datetime.strftime('%H:%M:%S')}"
            )

            return True

        except Exception as e:
            logger.error(f"Error scheduling check-in for {user_id}: {e}")
            return False

    def _send_random_checkin(
        self,
        user_id: str,
        user_info: dict,
        checkin: dict
    ) -> bool:
        """
        Enviar um check-in aleatório via WhatsApp

        Args:
            user_id: ID do usuário
            user_info: Dicionário com info (phone, etc)
            checkin: Dicionário com check-in info

        Returns:
            True se enviado com sucesso
        """
        try:
            logger.info(f"Enviando check-in ({checkin['window']}) para {user_id}...")

            # Verificar quiet hours
            if self.preferences_manager.is_in_quiet_hours(user_id):
                logger.info(f"User {user_id} is in quiet hours, skipping check-in")
                return False

            # Obter mensagem aleatória
            message = self.message_provider.get_message(checkin["message_type"])
            if not message:
                logger.error(f"No message found for window: {checkin['message_type']}")
                return False

            # Enviar via WhatsApp
            phone = user_info.get("phone")
            if not phone:
                logger.error(f"No phone number for {user_id}")
                return False

            success, sid, error = self.whatsapp_sender.send_text_message(
                phone_number=phone,
                message=message
            )

            if success:
                logger.info(f"✅ Check-in enviado para {user_id}. SID: {sid}")
                # Registrar envio no Redis
                self.random_scheduler.record_checkin_sent(user_id, checkin)
                return True
            else:
                logger.error(f"❌ Erro ao enviar check-in para {user_id}: {error}")
                return False

        except Exception as e:
            logger.error(f"Exception sending check-in to {user_id}: {e}")
            return False

    def validate_setup(self) -> bool:
        """
        Validar que o sistema está configurado corretamente

        Returns:
            True se tudo está ok
        """
        checks = []

        # Check message provider
        if not self.message_provider.validate():
            logger.error("Message provider validation failed")
            checks.append(False)
        else:
            checks.append(True)

        # Check Redis connection
        try:
            self.redis_client.ping()
            checks.append(True)
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            checks.append(False)

        # Check feature flag
        if is_random_checkins_enabled():
            logger.info("✅ Random check-ins feature flag is ENABLED")
        else:
            logger.info("⚠️  Random check-ins feature flag is DISABLED")

        return all(checks)


# Instância global
_adapter: Optional[RandomCheckinSchedulerAdapter] = None


def get_random_checkin_adapter(
    redis_client: object,
    whatsapp_sender: object
) -> RandomCheckinSchedulerAdapter:
    """
    Obter instância global do adapter (singleton)

    Args:
        redis_client: Cliente Redis
        whatsapp_sender: Instância de WhatsAppSender

    Returns:
        Instância do RandomCheckinSchedulerAdapter
    """
    global _adapter
    if _adapter is None:
        _adapter = RandomCheckinSchedulerAdapter(redis_client, whatsapp_sender)
    return _adapter
