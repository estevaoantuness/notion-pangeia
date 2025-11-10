#!/usr/bin/env python3
"""
Visualizar Feedback de Check-ins

Script prático para visualizar respostas de check-ins direto do PostgreSQL
sem precisar escrever SQL manualmente.

Uso:
    python scripts/view_checkin_feedback.py estevao
    python scripts/view_checkin_feedback.py estevao --stats
    python scripts/view_checkin_feedback.py estevao --window morning
"""

import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL connection"""
    try:
        from sqlalchemy import create_engine
        from dotenv import load_dotenv
        import os

        load_dotenv()

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL não configurada no .env")
            sys.exit(1)

        engine = create_engine(db_url)
        return engine

    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        sys.exit(1)


def show_recent_feedback(user_id: str, limit: int = 10):
    """Mostrar últimas respostas"""
    from sqlalchemy import text

    engine = get_db_connection()

    query = text("""
        SELECT
            created_at,
            checkin_window,
            response_text,
            response_intent,
            response_time_seconds
        FROM checkin_feedback
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "limit": limit})
        rows = result.fetchall()

        if not rows:
            print(f"❌ Nenhuma resposta encontrada para {user_id}")
            return

        print(f"\n{'='*80}")
        print(f"📊 ÚLTIMAS {len(rows)} RESPOSTAS - {user_id.upper()}")
        print(f"{'='*80}\n")

        for i, row in enumerate(rows, 1):
            created_at, window, response_text, intent, response_time = row

            # Formatar tempo de resposta
            if response_time:
                minutes = response_time // 60
                seconds = response_time % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            else:
                time_str = "N/A"

            # Emoji por intent
            intent_emoji = {
                "progressing": "✅",
                "blocked": "🚫",
                "completed": "🎉",
                "question": "❓",
                "reflection": "🤔",
                "other": "📝"
            }
            emoji = intent_emoji.get(intent, "📝")

            print(f"{i}. [{window.upper()}] {emoji} {intent}")
            print(f"   Data: {created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Resposta: {response_text}")
            print(f"   Tempo para responder: {time_str}")
            print()


def show_statistics(user_id: str):
    """Mostrar estatísticas gerais"""
    from sqlalchemy import text

    engine = get_db_connection()

    # Query 1: Contagem total
    total_query = text("""
        SELECT COUNT(*) as total FROM checkin_feedback WHERE user_id = :user_id
    """)

    # Query 2: Estatísticas por intent
    intent_query = text("""
        SELECT
            response_intent,
            COUNT(*) as count,
            ROUND(AVG(response_time_seconds)) as avg_time_secs,
            MIN(response_time_seconds) as min_time_secs,
            MAX(response_time_seconds) as max_time_secs
        FROM checkin_feedback
        WHERE user_id = :user_id
        GROUP BY response_intent
        ORDER BY count DESC
    """)

    # Query 3: Estatísticas por janela
    window_query = text("""
        SELECT
            checkin_window,
            COUNT(*) as count,
            ROUND(AVG(response_time_seconds)) as avg_time_secs
        FROM checkin_feedback
        WHERE user_id = :user_id
        GROUP BY checkin_window
        ORDER BY count DESC
    """)

    with engine.connect() as conn:
        total = conn.execute(total_query, {"user_id": user_id}).scalar()

        print(f"\n{'='*80}")
        print(f"📈 ESTATÍSTICAS - {user_id.upper()}")
        print(f"{'='*80}\n")

        print(f"Total de respostas: {total}\n")

        print("POR TIPO DE RESPOSTA:")
        print("-" * 80)
        intent_results = conn.execute(intent_query, {"user_id": user_id}).fetchall()

        for row in intent_results:
            intent, count, avg_time, min_time, max_time = row
            percent = (count / total * 100) if total > 0 else 0

            intent_emoji = {
                "progressing": "✅",
                "blocked": "🚫",
                "completed": "🎉",
                "question": "❓",
                "reflection": "🤔",
                "other": "📝"
            }
            emoji = intent_emoji.get(intent, "📝")

            print(f"{emoji} {intent:15} : {count:3} ({percent:5.1f}%) | Tempo médio: {avg_time}s")

        print("\n\nPOR HORÁRIO:")
        print("-" * 80)
        window_results = conn.execute(window_query, {"user_id": user_id}).fetchall()

        for row in window_results:
            window, count, avg_time = row
            percent = (count / total * 100) if total > 0 else 0

            print(f"{window:15} : {count:3} ({percent:5.1f}%) | Tempo médio: {avg_time}s")

        print()


def show_by_window(user_id: str, window: str):
    """Mostrar respostas de um horário específico"""
    from sqlalchemy import text

    engine = get_db_connection()

    query = text("""
        SELECT
            created_at,
            response_text,
            response_intent,
            response_time_seconds
        FROM checkin_feedback
        WHERE user_id = :user_id AND checkin_window = :window
        ORDER BY created_at DESC
        LIMIT 20
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "window": window})
        rows = result.fetchall()

        if not rows:
            print(f"❌ Nenhuma resposta encontrada para {window}")
            return

        print(f"\n{'='*80}")
        print(f"📊 RESPOSTAS DO HORÁRIO: {window.upper()}")
        print(f"{'='*80}\n")

        for i, row in enumerate(rows, 1):
            created_at, response_text, intent, response_time = row

            # Formatar tempo de resposta
            if response_time:
                minutes = response_time // 60
                seconds = response_time % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            else:
                time_str = "N/A"

            intent_emoji = {
                "progressing": "✅",
                "blocked": "🚫",
                "completed": "🎉",
                "question": "❓",
                "reflection": "🤔",
                "other": "📝"
            }
            emoji = intent_emoji.get(intent, "📝")

            print(f"{i}. [{intent.upper()}] {emoji}")
            print(f"   {created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Resposta: {response_text}")
            print(f"   Tempo: {time_str}\n")


def show_by_intent(user_id: str, intent: str):
    """Mostrar respostas de um tipo específico"""
    from sqlalchemy import text

    engine = get_db_connection()

    query = text("""
        SELECT
            created_at,
            checkin_window,
            response_text,
            response_time_seconds
        FROM checkin_feedback
        WHERE user_id = :user_id AND response_intent = :intent
        ORDER BY created_at DESC
        LIMIT 20
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "intent": intent})
        rows = result.fetchall()

        if not rows:
            print(f"❌ Nenhuma resposta encontrada com intent '{intent}'")
            return

        print(f"\n{'='*80}")
        print(f"📊 RESPOSTAS COM INTENT: {intent.upper()}")
        print(f"{'='*80}\n")

        for i, row in enumerate(rows, 1):
            created_at, window, response_text, response_time = row

            # Formatar tempo de resposta
            if response_time:
                minutes = response_time // 60
                seconds = response_time % 60
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            else:
                time_str = "N/A"

            print(f"{i}. [{window.upper()}]")
            print(f"   {created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Resposta: {response_text}")
            print(f"   Tempo: {time_str}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Visualizar feedback de check-ins do PostgreSQL"
    )

    parser.add_argument("user_id", help="ID do usuário (ex: estevao)")
    parser.add_argument("--stats", action="store_true", help="Mostrar estatísticas")
    parser.add_argument("--window", type=str, help="Filtrar por horário (morning/afternoon/evening/late_night)")
    parser.add_argument("--intent", type=str, help="Filtrar por tipo (progressing/blocked/completed/question/reflection)")
    parser.add_argument("--limit", type=int, default=10, help="Número de respostas a mostrar (padrão: 10)")

    args = parser.parse_args()

    try:
        if args.stats:
            show_statistics(args.user_id)
        elif args.window:
            show_by_window(args.user_id, args.window)
        elif args.intent:
            show_by_intent(args.user_id, args.intent)
        else:
            show_recent_feedback(args.user_id, limit=args.limit)

    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
