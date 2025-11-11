#!/usr/bin/env python3
"""
Sync Google Sheets → PostgreSQL (Manual Trigger)

Sincroniza colaboradores da Google Sheets para PostgreSQL.
Pode ser executado manualmente para testes ou como job agendado.

Uso:
    python3 scripts/sync_sheets_to_db.py
    python3 scripts/sync_sheets_to_db.py --stats
    python3 scripts/sync_sheets_to_db.py --db postgresql://evolution:evolution123@localhost:5432/evolution
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_sheets_data_mock():
    """
    Mock data para testar sem Google Sheets configurado.

    Em produção, isso seria:
    sheets_client.get_sheet_data("Tab")
    """
    return [
        ["Nome", "Email", "Telefone", "Papel", "Status", "Data Entrada"],  # Header
        ["Estevao Antunes", "estevao@pangeia.ai", "+554191851256", "Desenvolvedor", "ativo", "2024-01-15"],
        ["Julio Inoue", "julio@pangeia.ai", "+5511999322027", "Desenvolvedor", "inativo", "2024-02-20"],
        ["Arthur Leuzzi", "arthur@pangeia.ai", "+554888428246", "PM", "ativo", "2024-01-10"],
        ["Luna Machado", "luna@pangeia.ai", "+554484282600", "Desenvolvedora", "saída", "2023-06-01"],
        ["Joaquim", "joaquim@pangeia.ai", "+5511980992410", "Desenvolvedor", "inativo", "2024-03-05"],
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Sincronizar colaboradores do Google Sheets para PostgreSQL"
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Database URL (default: evolution://localhost)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estatísticas após sync"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todos os colaboradores"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Usar dados mock (para teste sem Google Sheets)"
    )

    args = parser.parse_args()

    # Determine database URL
    db_url = args.db or os.getenv(
        "DATABASE_URL",
        "postgresql://evolution:evolution123@localhost:5432/evolution"
    )

    logger.info("=" * 70)
    logger.info("📊 SINCRONIZAÇÃO DE COLABORADORES")
    logger.info("=" * 70)
    logger.info(f"Database: {db_url.split('@')[1] if '@' in db_url else db_url}")

    try:
        from src.sync.collaborators_sync import get_collaborators_sync

        # Initialize sync
        sync = get_collaborators_sync(db_url)
        logger.info("✓ Sync inicializado\n")

        # Get data (mock for now)
        logger.info("📥 Buscando dados...")
        sheets_data = get_sheets_data_mock()
        logger.info(f"✓ {len(sheets_data) - 1} colaboradores encontrados (1 header)\n")

        # Run sync
        logger.info("🔄 Sincronizando...")
        stats = sync.sync_from_sheets(sheets_data)

        # Print results
        logger.info("\n" + "=" * 70)
        logger.info("✅ RESULTADO DA SINCRONIZAÇÃO")
        logger.info("=" * 70)
        logger.info(f"Status:      {stats['status'].upper()}")
        logger.info(f"Criados:     {stats['created']}")
        logger.info(f"Atualizados: {stats['updated']}")
        logger.info(f"Inativos:    {stats['deleted']}")
        logger.info(f"Total:       {stats['total']}")
        logger.info(f"Tempo:       {stats['duration_seconds']:.2f}s")

        if stats['status'] == 'error':
            logger.error(f"Erro:        {stats.get('error', 'Unknown error')}")

        # Show stats if requested
        if args.stats:
            logger.info("\n" + "=" * 70)
            logger.info("📈 ESTATÍSTICAS")
            logger.info("=" * 70)

            stats_data = sync.get_statistics()
            logger.info(f"Total:            {stats_data.get('total', 0)}")
            logger.info(f"Ativos:           {stats_data.get('ativos', 0)}")
            logger.info(f"Inativos:         {stats_data.get('inativos', 0)}")
            logger.info(f"Saída:            {stats_data.get('saida', 0)}")
            logger.info(f"Papéis únicos:    {stats_data.get('total_roles', 0)}")

        # List collaborators if requested
        if args.list:
            logger.info("\n" + "=" * 70)
            logger.info("👥 LISTA DE COLABORADORES")
            logger.info("=" * 70)

            collaborators = sync.get_all_collaborators()

            for collab in collaborators:
                status_emoji = {
                    "ativo": "🟢",
                    "inativo": "🟡",
                    "saída": "🔴"
                }.get(collab['status'], "⚪")

                logger.info(
                    f"{status_emoji} {collab['name']:20} | "
                    f"{collab['role']:15} | "
                    f"{collab['email'] or 'N/A':30}"
                )

        logger.info("\n" + "=" * 70)

        return 0 if stats['status'] == 'success' else 1

    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("Make sure you're running from project root:")
        logger.error("  cd /Users/estevaoantunes/notion-pangeia")
        logger.error("  python3 scripts/sync_sheets_to_db.py")
        return 1

    except Exception as e:
        logger.error(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
