#!/usr/bin/env python3
"""
Configurar Check-ins para Estevão

Script para configurar as preferências de check-ins aleatórios do estevão.
Ativa late-night check-ins (20:00-21:45) e configura frequência.

Uso:
    python scripts/configure_estevao_checkins.py
"""

import sys
import os
import redis
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def configure_estevao_checkins():
    """Configurar preferências de check-in para Estevão"""

    try:
        # Conectar ao Redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("✓ Conectado ao Redis")

    except Exception as e:
        logger.error(f"✗ Erro ao conectar ao Redis: {e}")
        logger.error("Redis não está rodando. Inicie com: brew services start redis")
        sys.exit(1)

    try:
        from src.checkins.user_preferences import CheckinPreferencesManager

        manager = CheckinPreferencesManager(redis_client)
        user_id = "estevao"

        logger.info(f"\n{'='*60}")
        logger.info(f"Configurando preferências de check-in para {user_id.upper()}")
        logger.info(f"{'='*60}\n")

        # 1. Habilitar check-ins globalmente
        manager.enable_checkins(user_id)
        logger.info(f"✓ Check-ins habilitados globalmente")

        # 2. Habilitar late-night (boa noite 20:00-21:45)
        manager.set_preference(user_id, "enable_late_night", True)
        logger.info(f"✓ Late-night check-ins ativados (20:00-21:45)")

        # 3. Configurar frequência (3 check-ins por dia)
        manager.set_preference(user_id, "preferred_frequency", 3)
        logger.info(f"✓ Frequência configurada: 3 check-ins por dia")

        # 4. Configurar quiet hours (não enviar entre 23:00 e 08:00)
        manager.set_quiet_hours(user_id, "23:00", "08:00")
        logger.info(f"✓ Quiet hours configuradas: 23:00 até 08:00")

        # 5. Verificar configuração final
        prefs = manager.get_preferences(user_id)

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ CONFIGURAÇÃO FINAL")
        logger.info(f"{'='*60}\n")
        logger.info(f"Usuário: {user_id}")
        logger.info(f"Check-ins habilitados: {prefs.enabled}")
        logger.info(f"Late-night ativado: {prefs.enable_late_night}")
        logger.info(f"Frequência: {prefs.preferred_frequency} check-ins/dia")
        logger.info(f"Quiet hours: {prefs.quiet_hours_start} até {prefs.quiet_hours_end}")

        logger.info(f"\n{'='*60}")
        logger.info(f"HORÁRIOS DE DISPARO (randomizado):")
        logger.info(f"{'='*60}")
        logger.info(f"☕ Manhã:     08:00 - 11:30 (sempre)")
        logger.info(f"🎯 Tarde:    13:00 - 15:30 (80%)")
        logger.info(f"🌆 Noite:    17:00 - 19:30 (sempre)")
        logger.info(f"🌙 Boa Noite: 20:00 - 21:45 (ativado!)")
        logger.info(f"\nQuiet Hours: 23:00 - 08:00 (nenhuma mensagem)")

        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMO")
        logger.info(f"{'='*60}\n")
        logger.info(f"Apenas ESTEVÃO receberá disparos")
        logger.info(f"Todos os outros colaboradores foram desativados")
        logger.info(f"Random check-ins: ATIVADOS")
        logger.info(f"Late-night: ATIVADO")
        logger.info(f"\nPróximo passo: Reiniciar o servidor para ativar as mudanças")

    except Exception as e:
        logger.error(f"\n✗ Erro ao configurar preferências: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    configure_estevao_checkins()
