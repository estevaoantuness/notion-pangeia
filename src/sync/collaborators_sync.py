"""
Collaborators Sync - Google Sheets ↔ PostgreSQL

Sincroniza lista de colaboradores (membros, papéis, status) da Google Sheets
para PostgreSQL, mantendo dados sempre atualizados sem redeploy.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy import create_engine, text
import os

logger = logging.getLogger(__name__)


class CollaboratorsSync:
    """Sincroniza colaboradores do Google Sheets para PostgreSQL"""

    def __init__(self, database_url: str, sheets_client=None):
        """
        Inicializar sync

        Args:
            database_url: URL de conexão PostgreSQL
            sheets_client: Cliente para Google Sheets (opcional)
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.sheets_client = sheets_client

        logger.info("CollaboratorsSync initialized")

    def sync_from_sheets(self, sheets_data: List[Dict]) -> Dict:
        """
        Sincronizar colaboradores da Google Sheets para PostgreSQL

        Args:
            sheets_data: Lista de dicionários com dados da Sheets

        Returns:
            {
                "created": 5,
                "updated": 3,
                "deleted": 1,
                "total": 9,
                "status": "success",
                "duration_seconds": 2.5
            }
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Starting sync: {len(sheets_data)} rows from Google Sheets")

            # 1. Parse e validar dados
            parsed_data = self._parse_sheets_data(sheets_data)
            logger.info(f"Parsed {len(parsed_data)} valid collaborators")

            # 2. Sincronizar com banco
            stats = self._upsert_collaborators(parsed_data)

            # 3. Registrar log
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_sync(stats, "success", None, duration)

            logger.info(
                f"✓ Sync completo: {stats['created']} criados, "
                f"{stats['updated']} atualizados, {stats['deleted']} inativos "
                f"({duration:.1f}s)"
            )

            stats["status"] = "success"
            stats["duration_seconds"] = duration

            return stats

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"✗ Erro sincronizando: {e}")
            self._log_sync(
                {"created": 0, "updated": 0, "deleted": 0},
                "error",
                str(e),
                duration
            )

            return {
                "created": 0,
                "updated": 0,
                "deleted": 0,
                "total": 0,
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }

    def _parse_sheets_data(self, rows: List) -> List[Dict]:
        """
        Parsear dados do Google Sheets

        Esperado:
        Col A: Nome (REQUIRED)
        Col B: Email
        Col C: Telefone
        Col D: Papel/Cargo
        Col E: Status (ativo/inativo/saída)
        Col F: Data de Entrada (YYYY-MM-DD)
        """
        collaborators = []

        for i, row in enumerate(rows, start=1):
            try:
                # Skip header or empty rows
                if not row or not row[0]:
                    continue

                # Parse columns
                name = str(row[0]).strip() if len(row) > 0 else None
                email = str(row[1]).strip() if len(row) > 1 and row[1] else None
                phone = str(row[2]).strip() if len(row) > 2 and row[2] else None
                role = str(row[3]).strip() if len(row) > 3 and row[3] else None
                status = str(row[4]).strip().lower() if len(row) > 4 and row[4] else "ativo"
                entry_date = str(row[5]).strip() if len(row) > 5 and row[5] else None

                # Validate required fields
                if not name:
                    logger.debug(f"Skipping row {i}: missing name")
                    continue

                # Validate status
                if status not in ["ativo", "inativo", "saída"]:
                    status = "ativo"

                collaborators.append({
                    "name": name,
                    "email": email if email else None,
                    "phone": phone if phone else None,
                    "role": role if role else None,
                    "status": status,
                    "entry_date": entry_date,
                    "sheets_row_id": i
                })

            except Exception as e:
                logger.warning(f"Erro parseando linha {i}: {e}")
                continue

        return collaborators

    def _upsert_collaborators(self, collaborators: List[Dict]) -> Dict:
        """
        Inserir ou atualizar colaboradores no PostgreSQL

        Returns:
            {
                "created": 5,
                "updated": 3,
                "deleted": 1,
                "total": 9
            }
        """
        stats = {"created": 0, "updated": 0, "deleted": 0, "total": 0}

        try:
            with self.engine.begin() as conn:
                sheets_names = [c["name"] for c in collaborators]

                # 1. Insert/update cada colaborador
                for collab in collaborators:
                    # Check if exists
                    check_query = text("""
                        SELECT id FROM app.collaborators WHERE name = :name
                    """)
                    result = conn.execute(check_query, {"name": collab["name"]})
                    existing_id = result.scalar()

                    if existing_id:
                        # Update
                        update_query = text("""
                            UPDATE app.collaborators
                            SET email = :email,
                                phone = :phone,
                                role = :role,
                                status = :status,
                                entry_date = :entry_date,
                                last_synced = NOW(),
                                sheets_row_id = :sheets_row_id,
                                updated_at = NOW()
                            WHERE name = :name
                        """)
                        conn.execute(update_query, collab)
                        stats["updated"] += 1
                        logger.debug(f"Updated: {collab['name']}")

                    else:
                        # Insert
                        insert_query = text("""
                            INSERT INTO app.collaborators
                            (name, email, phone, role, status, entry_date, sheets_row_id, created_at, updated_at)
                            VALUES (:name, :email, :phone, :role, :status, :entry_date, :sheets_row_id, NOW(), NOW())
                        """)
                        conn.execute(insert_query, collab)
                        stats["created"] += 1
                        logger.debug(f"Created: {collab['name']}")

                # 2. Mark departed collaborators (not in sheets anymore)
                if sheets_names:
                    # Build IN clause safely
                    placeholders = ", ".join([f"'{name.replace(chr(39), chr(39)+chr(39))}'" for name in sheets_names])

                    mark_inactive_query = text(f"""
                        UPDATE app.collaborators
                        SET status = 'saída', updated_at = NOW()
                        WHERE name NOT IN ({placeholders})
                        AND status IN ('ativo', 'inativo')
                    """)
                    conn.execute(mark_inactive_query)

                # 3. Count total active
                count_query = text("""
                    SELECT COUNT(*) FROM app.collaborators WHERE status = 'ativo'
                """)
                result = conn.execute(count_query)
                stats["total"] = result.scalar()

                # Count saida (deleted)
                saida_query = text("""
                    SELECT COUNT(*) FROM app.collaborators WHERE status = 'saída'
                """)
                result = conn.execute(saida_query)
                stats["deleted"] = result.scalar()

        except Exception as e:
            logger.error(f"Erro no upsert: {e}")
            raise

        return stats

    def get_active_collaborators(self) -> List[Dict]:
        """Retornar todos os colaboradores ativos"""
        try:
            query = text("""
                SELECT id, name, email, phone, role, status, entry_date
                FROM app.collaborators
                WHERE status = 'ativo'
                ORDER BY name
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [dict(row._mapping) for row in result]

        except Exception as e:
            logger.error(f"Erro ao buscar colaboradores ativos: {e}")
            return []

    def get_by_role(self, role: str) -> List[Dict]:
        """Retornar colaboradores por papel"""
        try:
            query = text("""
                SELECT id, name, email, phone, role, status, entry_date
                FROM app.collaborators
                WHERE role = :role AND status = 'ativo'
                ORDER BY name
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query, {"role": role})
                return [dict(row._mapping) for row in result]

        except Exception as e:
            logger.error(f"Erro ao buscar por papel: {e}")
            return []

    def get_all_collaborators(self) -> List[Dict]:
        """Retornar todos os colaboradores (inclusive inativos)"""
        try:
            query = text("""
                SELECT id, name, email, phone, role, status, entry_date
                FROM app.collaborators
                ORDER BY status DESC, name
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query)
                return [dict(row._mapping) for row in result]

        except Exception as e:
            logger.error(f"Erro ao buscar todos: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Obter estatísticas de colaboradores"""
        try:
            query = text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'ativo' THEN 1 END) as ativos,
                    COUNT(CASE WHEN status = 'inativo' THEN 1 END) as inativos,
                    COUNT(CASE WHEN status = 'saída' THEN 1 END) as saida,
                    COUNT(DISTINCT role) as total_roles
                FROM app.collaborators
            """)

            with self.engine.connect() as conn:
                result = conn.execute(query)
                row = result.fetchone()
                return {
                    "total": row[0],
                    "ativos": row[1],
                    "inativos": row[2],
                    "saida": row[3],
                    "total_roles": row[4]
                }

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}

    def _log_sync(
        self,
        stats: Dict,
        status: str,
        error_message: Optional[str],
        duration_seconds: float
    ) -> None:
        """Registrar log de sincronização"""
        try:
            query = text("""
                INSERT INTO app.sync_logs
                (table_name, records_created, records_updated, records_deleted, status, error_message, started_at, ended_at, duration_seconds, created_at)
                VALUES ('collaborators', :created, :updated, :deleted, :status, :error, NOW() - INTERVAL '1 second' * :duration, NOW(), :duration, NOW())
            """)

            with self.engine.begin() as conn:
                conn.execute(query, {
                    "created": stats.get("created", 0),
                    "updated": stats.get("updated", 0),
                    "deleted": stats.get("deleted", 0),
                    "status": status,
                    "error": error_message,
                    "duration": int(duration_seconds)
                })

        except Exception as e:
            logger.warning(f"Erro ao registrar log: {e}")


# Instância global
_sync_instance: Optional[CollaboratorsSync] = None


def get_collaborators_sync(database_url: Optional[str] = None, sheets_client=None) -> CollaboratorsSync:
    """
    Get or create collaborators sync instance (singleton)

    Args:
        database_url: PostgreSQL connection URL (if None, uses DATABASE_URL env var)
        sheets_client: Google Sheets client

    Returns:
        CollaboratorsSync instance
    """
    global _sync_instance

    if _sync_instance is None:
        db_url = database_url or os.getenv("DATABASE_URL")

        if not db_url:
            raise ValueError(
                "DATABASE_URL must be set either as parameter or environment variable. "
                "For development, use: postgresql://evolution:evolution123@localhost:5432/evolution"
            )

        _sync_instance = CollaboratorsSync(db_url, sheets_client)

    return _sync_instance
