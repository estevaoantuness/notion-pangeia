"""
Rotas para visualizar analytics de check-ins

GET /api/checkins/person/<name>?days=7     - Check-ins de uma pessoa
GET /api/checkins/date/<YYYY-MM-DD>        - Check-ins de um dia
GET /api/checkins/stats                    - Estatísticas gerais
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
TZ = ZoneInfo("America/Sao_Paulo")

# Blueprint
checkins_bp = Blueprint('checkins', __name__, url_prefix='/api/checkins')


@checkins_bp.route('/person/<person_name>', methods=['GET'])
def get_person_checkins(person_name):
    """
    Retorna check-ins de uma pessoa

    Query params:
    - days: número de dias (padrão 7)

    Exemplo: GET /api/checkins/person/Estevao%20Antunes?days=7
    """
    try:
        from src.api.checkins_analytics import get_checkin_analytics

        days = request.args.get('days', default=7, type=int)
        analytics = get_checkin_analytics()

        result = analytics.get_checkins_by_person(person_name, days)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Erro ao buscar check-ins: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@checkins_bp.route('/date/<date_str>', methods=['GET'])
def get_date_checkins(date_str):
    """
    Retorna check-ins de um dia específico

    Format: YYYY-MM-DD

    Exemplo: GET /api/checkins/date/2025-11-11
    """
    try:
        # Valida formato da data
        datetime.strptime(date_str, '%Y-%m-%d')

        from src.api.checkins_analytics import get_checkin_analytics

        analytics = get_checkin_analytics()
        result = analytics.get_checkins_by_date(date_str)

        return jsonify(result), 200

    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        logger.error(f"Erro ao buscar check-ins por data: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@checkins_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Retorna estatísticas gerais de check-ins

    Exemplo: GET /api/checkins/stats
    """
    try:
        from src.api.checkins_analytics import get_checkin_analytics

        analytics = get_checkin_analytics()
        result = analytics.get_all_stats()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Erro ao buscar stats: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@checkins_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    Retorna resumo formatado dos check-ins

    Exemplo: GET /api/checkins/summary?person=Estevao%20Antunes
    """
    try:
        person_name = request.args.get('person')

        from src.api.checkins_analytics import get_checkin_analytics

        analytics = get_checkin_analytics()

        if person_name:
            data = analytics.get_checkins_by_person(person_name, days=7)
            title = f"Check-ins de {person_name} (últimos 7 dias)"
        else:
            data = analytics.get_all_stats()
            title = "Estatísticas Gerais de Check-ins"

        summary = {
            'title': title,
            'timestamp': datetime.now(TZ).isoformat(),
            'data': data
        }

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"Erro ao gerar summary: {e}")
        return jsonify({'error': str(e)}), 500


def register_checkins_routes(app):
    """Registra rotas de check-ins no Flask app"""
    app.register_blueprint(checkins_bp)
    logger.info("✅ Rotas de check-ins registradas")
