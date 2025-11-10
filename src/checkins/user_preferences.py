"""
User Preferences Management for Random Check-ins

Manages user preferences for check-in behavior:
- Enable/disable late-night check-ins
- Preferred check-in frequency (2-4 per day)
- Opt-out times (quiet hours)
- Message preferences
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CheckinPreferences:
    """Preferências de check-in para um usuário"""
    user_id: str
    enable_late_night: bool = False
    preferred_frequency: int = 3  # 2-4 (check-ins per day)
    quiet_hours_start: Optional[str] = None  # "22:00" (HH:MM format)
    quiet_hours_end: Optional[str] = None  # "08:00" (HH:MM format)
    enabled: bool = True  # Se check-ins estão desabilitados completamente
    updated_at: str = None  # ISO timestamp

    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_json(self) -> str:
        """Converter para JSON para armazenar no Redis"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "CheckinPreferences":
        """Converter de JSON para objeto"""
        return cls(**json.loads(data))


class CheckinPreferencesManager:
    """
    Gerenciador de preferências de check-in com Redis backend

    Armazena em Redis:
    - checkins:prefs:{user_id} → JSON com preferências
    - checkins:opted_out → SET com user_ids que desabilitaram
    - checkins:late_night_enabled → SET com user_ids que habilitaram noturno

    Exemplo:
        manager = CheckinPreferencesManager(redis_client)

        # Obter preferências
        prefs = manager.get_preferences("user123")

        # Atualizar
        manager.set_preference("user123", "enable_late_night", True)

        # Check if user has quiet hours
        if manager.is_in_quiet_hours("user123"):
            # Skip check-in
            pass
    """

    def __init__(self, redis_client: object):
        """
        Inicializar manager

        Args:
            redis_client: Cliente Redis para persistência
        """
        self.redis = redis_client
        logger.info("CheckinPreferencesManager initialized")

    def get_preferences(self, user_id: str) -> CheckinPreferences:
        """
        Obter preferências de um usuário

        Se não existem, retorna defaults

        Args:
            user_id: ID do usuário

        Returns:
            CheckinPreferences com as preferências do usuário
        """
        try:
            key = f"checkins:prefs:{user_id}"
            data = self.redis.get(key)

            if data:
                return CheckinPreferences.from_json(data)
            else:
                # Retornar defaults
                return CheckinPreferences(user_id=user_id)

        except Exception as e:
            logger.error(f"Error getting preferences for {user_id}: {e}")
            return CheckinPreferences(user_id=user_id)

    def save_preferences(self, prefs: CheckinPreferences) -> bool:
        """
        Salvar preferências de um usuário

        Args:
            prefs: CheckinPreferences a salvar

        Returns:
            True se salvo com sucesso
        """
        try:
            key = f"checkins:prefs:{prefs.user_id}"
            prefs.updated_at = datetime.now().isoformat()

            self.redis.set(key, prefs.to_json())

            # Atualizar sets auxiliares
            if prefs.enable_late_night:
                self.redis.sadd("checkins:late_night_enabled", prefs.user_id)
            else:
                self.redis.srem("checkins:late_night_enabled", prefs.user_id)

            if not prefs.enabled:
                self.redis.sadd("checkins:opted_out", prefs.user_id)
            else:
                self.redis.srem("checkins:opted_out", prefs.user_id)

            logger.info(f"Preferences saved for {prefs.user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving preferences for {prefs.user_id}: {e}")
            return False

    def set_preference(self, user_id: str, key: str, value: Any) -> bool:
        """
        Atualizar uma preferência específica

        Args:
            user_id: ID do usuário
            key: Nome da preferência (ex: "enable_late_night")
            value: Novo valor

        Returns:
            True se atualizado com sucesso

        Exemplo:
            manager.set_preference("user123", "enable_late_night", True)
            manager.set_preference("user123", "preferred_frequency", 2)
        """
        try:
            prefs = self.get_preferences(user_id)

            if hasattr(prefs, key):
                setattr(prefs, key, value)
                return self.save_preferences(prefs)
            else:
                logger.warning(f"Unknown preference key: {key}")
                return False

        except Exception as e:
            logger.error(f"Error setting preference {key} for {user_id}: {e}")
            return False

    def is_enabled(self, user_id: str) -> bool:
        """
        Verificar se check-ins estão habilitados para o usuário

        Args:
            user_id: ID do usuário

        Returns:
            True se check-ins estão habilitados
        """
        prefs = self.get_preferences(user_id)
        return prefs.enabled

    def has_late_night_enabled(self, user_id: str) -> bool:
        """
        Verificar se late-night check-ins estão habilitados

        Args:
            user_id: ID do usuário

        Returns:
            True se late-night está habilitado
        """
        prefs = self.get_preferences(user_id)
        return prefs.enable_late_night

    def get_preferred_frequency(self, user_id: str) -> int:
        """
        Obter frequência de check-ins preferida

        Args:
            user_id: ID do usuário

        Returns:
            Número de check-ins por dia (2-4)
        """
        prefs = self.get_preferences(user_id)
        return max(2, min(4, prefs.preferred_frequency))  # Clamp 2-4

    def is_in_quiet_hours(self, user_id: str) -> bool:
        """
        Verificar se estamos em quiet hours para o usuário

        Quiet hours permitem que usuários desabilitem check-ins em certos horários
        (ex: 22:00-08:00 para não acordar à noite)

        Args:
            user_id: ID do usuário

        Returns:
            True se está em quiet hours
        """
        prefs = self.get_preferences(user_id)

        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False  # Sem quiet hours configuradas

        try:
            current_time = datetime.now().strftime("%H:%M")

            start = prefs.quiet_hours_start
            end = prefs.quiet_hours_end

            # Caso 1: Quiet hours não cruza meia-noite (ex: 22:00-08:00)
            if start > end:
                # Está em quiet hours se >= start OU < end
                return current_time >= start or current_time < end
            # Caso 2: Quiet hours dentro do mesmo dia (ex: 12:00-14:00)
            else:
                # Está em quiet hours se >= start E < end
                return start <= current_time < end

        except Exception as e:
            logger.warning(f"Error checking quiet hours for {user_id}: {e}")
            return False

    def set_quiet_hours(self, user_id: str, start: str, end: str) -> bool:
        """
        Configurar quiet hours para um usuário

        Args:
            user_id: ID do usuário
            start: Hora de início (HH:MM, ex: "22:00")
            end: Hora de término (HH:MM, ex: "08:00")

        Returns:
            True se configurado com sucesso

        Exemplo:
            # Sem check-ins entre 22:00 e 08:00 (à noite)
            manager.set_quiet_hours("user123", "22:00", "08:00")

            # Sem check-ins entre 12:00 e 13:00 (intervalo de almoço)
            manager.set_quiet_hours("user123", "12:00", "13:00")
        """
        try:
            # Validar formato HH:MM
            for hour_str in [start, end]:
                datetime.strptime(hour_str, "%H:%M")

            return self.set_preference(user_id, "quiet_hours_start", start) and \
                   self.set_preference(user_id, "quiet_hours_end", end)

        except ValueError:
            logger.error(f"Invalid time format: {start} or {end}")
            return False

    def clear_quiet_hours(self, user_id: str) -> bool:
        """
        Limpar quiet hours para um usuário

        Args:
            user_id: ID do usuário

        Returns:
            True se removido com sucesso
        """
        return self.set_preference(user_id, "quiet_hours_start", None) and \
               self.set_preference(user_id, "quiet_hours_end", None)

    def disable_checkins(self, user_id: str) -> bool:
        """
        Desabilitar completamente check-ins para um usuário

        Args:
            user_id: ID do usuário

        Returns:
            True se desabilitado com sucesso
        """
        return self.set_preference(user_id, "enabled", False)

    def enable_checkins(self, user_id: str) -> bool:
        """
        Habilitar check-ins para um usuário

        Args:
            user_id: ID do usuário

        Returns:
            True se habilitado com sucesso
        """
        return self.set_preference(user_id, "enabled", True)

    def get_opted_out_users(self) -> set:
        """
        Obter SET de usuários que desabilitaram check-ins

        Returns:
            Set de user_ids
        """
        try:
            return self.redis.smembers("checkins:opted_out")
        except Exception as e:
            logger.error(f"Error getting opted out users: {e}")
            return set()

    def get_late_night_enabled_users(self) -> set:
        """
        Obter SET de usuários com late-night habilitado

        Returns:
            Set de user_ids
        """
        try:
            return self.redis.smembers("checkins:late_night_enabled")
        except Exception as e:
            logger.error(f"Error getting late night enabled users: {e}")
            return set()


# Instância global
_manager: Optional[CheckinPreferencesManager] = None


def get_preferences_manager(redis_client: object) -> CheckinPreferencesManager:
    """
    Obter instância global do preferences manager (singleton)

    Args:
        redis_client: Cliente Redis para persistência

    Returns:
        Instância do CheckinPreferencesManager
    """
    global _manager
    if _manager is None:
        _manager = CheckinPreferencesManager(redis_client)
    return _manager
