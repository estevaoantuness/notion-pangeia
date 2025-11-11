"""
Analytics API para Check-ins

Fornece endpoints para visualizar:
- Check-ins por pessoa
- Check-ins por dia
- Taxa de resposta
- Tempo médio de resposta
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Timezone São Paulo
TZ = ZoneInfo("America/Sao_Paulo")


class CheckinAnalytics:
    """Análise de dados de check-ins"""

    def __init__(self):
        """Inicializa analytics"""
        try:
            from src.database.connection import get_db_engine
            self.engine = get_db_engine()
            self.db_available = True
        except Exception as e:
            logger.warning(f"Database não disponível para analytics: {e}")
            self.db_available = False

    def get_checkins_by_person(self, person_name: str, days: int = 7) -> Dict:
        """
        Retorna check-ins de uma pessoa nos últimos N dias

        Args:
            person_name: Nome da pessoa
            days: Número de dias a consultar

        Returns:
            {
                'person': 'Estevao Antunes',
                'total': 5,
                'responded': 4,
                'pending': 1,
                'response_rate': 80,
                'avg_response_time': 300,
                'checkins': [
                    {
                        'date': '2025-11-11',
                        'type': 'closing',
                        'sent_at': '19:05:55',
                        'responded': True,
                        'response_time': 600,
                        'response': 'Fiz 4 tarefas...'
                    }
                ]
            }
        """
        if not self.db_available:
            return {
                'person': person_name,
                'status': 'database_unavailable',
                'message': 'Database não configurado (será disponível em produção)'
            }

        try:
            from sqlalchemy import text

            with self.engine.connect() as conn:
                # Query para buscar check-ins da pessoa
                query = text("""
                    SELECT 
                        DATE(sent_at AT TIME ZONE 'America/Sao_Paulo') as date,
                        checkin_type,
                        sent_at AT TIME ZONE 'America/Sao_Paulo' as sent_at,
                        response,
                        responded_at,
                        response_time
                    FROM checkin_responses
                    WHERE user_id = :user_id
                    AND sent_at >= NOW() - INTERVAL ':days days'
                    ORDER BY sent_at DESC
                """)

                result = conn.execute(
                    query,
                    {"user_id": person_name, "days": days}
                )

                checkins = []
                total = 0
                responded = 0
                response_times = []

                for row in result:
                    total += 1
                    sent_time = row[2].strftime("%H:%M:%S") if row[2] else None

                    checkin_data = {
                        'date': row[0].isoformat() if row[0] else None,
                        'type': row[1],
                        'sent_at': sent_time,
                        'responded': row[3] is not None,
                        'response': row[3],
                        'response_time': row[5],
                    }

                    if row[3] is not None:  # Respondeu
                        responded += 1
                        if row[5]:  # response_time
                            response_times.append(row[5])

                    checkins.append(checkin_data)

                avg_response = (
                    sum(response_times) / len(response_times)
                    if response_times
                    else None
                )

                return {
                    'person': person_name,
                    'period_days': days,
                    'total': total,
                    'responded': responded,
                    'pending': total - responded,
                    'response_rate': int((responded / total * 100) if total > 0 else 0),
                    'avg_response_time_seconds': int(avg_response) if avg_response else None,
                    'checkins': checkins
                }

        except Exception as e:
            logger.error(f"Erro ao buscar check-ins: {e}")
            return {
                'person': person_name,
                'error': str(e),
                'status': 'error'
            }

    def get_checkins_by_date(self, date: str) -> Dict:
        """
        Retorna check-ins de um dia específico

        Args:
            date: Data no formato YYYY-MM-DD

        Returns:
            {
                'date': '2025-11-11',
                'total': 5,
                'responded': 4,
                'response_rate': 80,
                'checkins': [
                    {
                        'person': 'Estevao Antunes',
                        'type': 'closing',
                        'sent_at': '19:05:55',
                        'responded': True,
                        'response_time': 600
                    }
                ]
            }
        """
        if not self.db_available:
            return {
                'date': date,
                'status': 'database_unavailable',
                'message': 'Database não configurado'
            }

        try:
            from sqlalchemy import text

            with self.engine.connect() as conn:
                query = text("""
                    SELECT 
                        user_id,
                        checkin_type,
                        sent_at AT TIME ZONE 'America/Sao_Paulo' as sent_at,
                        response,
                        response_time
                    FROM checkin_responses
                    WHERE DATE(sent_at AT TIME ZONE 'America/Sao_Paulo') = :date
                    ORDER BY sent_at DESC
                """)

                result = conn.execute(query, {"date": date})

                checkins = []
                total = 0
                responded = 0

                for row in result:
                    total += 1
                    sent_time = row[2].strftime("%H:%M:%S") if row[2] else None

                    checkin_data = {
                        'person': row[0],
                        'type': row[1],
                        'sent_at': sent_time,
                        'responded': row[3] is not None,
                        'response_time': row[4],
                    }

                    if row[3] is not None:
                        responded += 1

                    checkins.append(checkin_data)

                return {
                    'date': date,
                    'total': total,
                    'responded': responded,
                    'response_rate': int((responded / total * 100) if total > 0 else 0),
                    'checkins': checkins
                }

        except Exception as e:
            logger.error(f"Erro ao buscar check-ins por data: {e}")
            return {
                'date': date,
                'error': str(e),
                'status': 'error'
            }

    def get_all_stats(self) -> Dict:
        """
        Retorna estatísticas gerais de todos os check-ins

        Returns:
            {
                'total_checkins': 50,
                'total_people': 5,
                'response_rate': 75,
                'by_person': {...}
            }
        """
        if not self.db_available:
            return {
                'status': 'database_unavailable',
                'message': 'Database não configurado (será disponível em produção)'
            }

        try:
            from sqlalchemy import text

            with self.engine.connect() as conn:
                # Query geral
                query = text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(DISTINCT user_id) as people,
                        COUNT(CASE WHEN response IS NOT NULL THEN 1 END) as responded
                    FROM checkin_responses
                    WHERE sent_at >= NOW() - INTERVAL '30 days'
                """)

                result = conn.execute(query)
                row = result.fetchone()

                total = row[0] if row[0] else 0
                people = row[1] if row[1] else 0
                responded = row[2] if row[2] else 0

                return {
                    'period_days': 30,
                    'total_checkins': total,
                    'total_people': people,
                    'total_responded': responded,
                    'response_rate': int((responded / total * 100) if total > 0 else 0),
                    'status': 'success'
                }

        except Exception as e:
            logger.error(f"Erro ao buscar stats: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }


def get_checkin_analytics() -> CheckinAnalytics:
    """Singleton para analytics"""
    global _analytics_instance
    if '_analytics_instance' not in globals():
        _analytics_instance = CheckinAnalytics()
    return _analytics_instance
