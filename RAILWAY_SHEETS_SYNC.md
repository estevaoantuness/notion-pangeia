# 🚂 Railway + Google Sheets Sync

## 🎯 Objetivo

Sincronizar lista de colaboradores (papéis, status) da Google Sheets para PostgreSQL no Railway, para o bot sempre ter dados atualizados.

---

## ✅ Checklist: O que você JÁ tem

- ✅ Railway configurado (você fez redeploy)
- ✅ Projeto em git
- ✅ Redis rodando
- ✅ Google Sheets atualizada (com lista de membros)
- ❌ PostgreSQL no Railway (PRECISA CRIAR)
- ❌ Sync automático (PRECISA IMPLEMENTAR)

---

## 🚀 Implementação em 3 Passos

### **PASSO 1: Criar PostgreSQL no Railway (2 min)**

1. Acesse: https://railway.app/dashboard
2. Clique em **+ New Project**
3. Selecione **PostgreSQL**
4. Copie a `DATABASE_URL` gerada
5. Adicione ao `.env` do projeto:
   ```bash
   DATABASE_URL=postgresql://...
   ```

**Resultado**: Banco PostgreSQL rodando, pronto para usar.

---

### **PASSO 2: Criar Schema de Colaboradores (5 min)**

**Arquivo**: `migrations/003_create_collaborators_table.sql`

```sql
CREATE TABLE collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(100),           -- "Desenvolvedor", "Founder", etc
    status VARCHAR(20),          -- "ativo", "inativo", "saída"
    entry_date DATE,
    last_synced TIMESTAMP DEFAULT NOW(),
    sheets_row_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_collaborators_status ON collaborators(status);
CREATE INDEX idx_collaborators_name ON collaborators(name);
CREATE INDEX idx_collaborators_sheets_id ON collaborators(sheets_row_id);
```

**Executar**:
```bash
psql $DATABASE_URL -f migrations/003_create_collaborators_table.sql
```

---

### **PASSO 3: Criar Sync automático (30 min)**

**Arquivo**: `src/sync/sheets_collaborators.py`

```python
"""
Sincroniza lista de colaboradores de Google Sheets para PostgreSQL
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)


class CollaboratorsSync:
    """Sincroniza colaboradores do Google Sheets para PostgreSQL"""

    def __init__(self, db_connection, sheets_url: str):
        """
        Args:
            db_connection: Conexão SQLAlchemy com PostgreSQL
            sheets_url: URL da Google Sheets
        """
        self.db = db_connection
        self.sheets_url = sheets_url

    def sync_from_sheets(self) -> Dict[str, int]:
        """
        Sincronizar colaboradores da Google Sheets para PostgreSQL

        Returns:
            {
                "created": 5,      # Novos colaboradores adicionados
                "updated": 3,      # Colaboradores atualizados
                "deleted": 1,      # Marcados como inativo
                "total": 9         # Total no banco
            }
        """
        try:
            from src.api.google_sheets import GoogleSheetsClient

            # 1. Buscar dados do Google Sheets
            sheets_client = GoogleSheetsClient(self.sheets_url)
            sheets_data = sheets_client.get_sheet_data("Tab")  # Adjust sheet name if needed

            logger.info(f"Fetched {len(sheets_data)} rows from Google Sheets")

            # 2. Transformar dados
            collaborators = self._parse_sheets_data(sheets_data)

            # 3. Sincronizar com banco
            stats = self._upsert_collaborators(collaborators)

            logger.info(
                f"✓ Sync completo: {stats['created']} criados, "
                f"{stats['updated']} atualizados, {stats['deleted']} inativos"
            )

            return stats

        except Exception as e:
            logger.error(f"✗ Erro sincronizando colaboradores: {e}")
            return {"created": 0, "updated": 0, "deleted": 0, "total": 0, "error": str(e)}

    def _parse_sheets_data(self, rows: List[List[str]]) -> List[Dict]:
        """
        Parsear dados do Google Sheets

        Esperado:
        Col A: Nome
        Col B: Email
        Col C: Telefone
        Col D: Papel/Cargo
        Col E: Status (ativo/inativo/saída)
        Col F: Data de Entrada
        """
        collaborators = []

        for i, row in enumerate(rows[1:], start=2):  # Skip header
            if not row or not row[0]:  # Skip empty rows
                continue

            try:
                name = row[0].strip() if len(row) > 0 else None
                email = row[1].strip() if len(row) > 1 else None
                phone = row[2].strip() if len(row) > 2 else None
                role = row[3].strip() if len(row) > 3 else None
                status = row[4].strip().lower() if len(row) > 4 else "ativo"
                entry_date = row[5].strip() if len(row) > 5 else None

                if not name:
                    continue

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

    def _upsert_collaborators(self, collaborators: List[Dict]) -> Dict[str, int]:
        """
        Inserir ou atualizar colaboradores no PostgreSQL
        """
        from sqlalchemy import text

        stats = {"created": 0, "updated": 0, "deleted": 0, "total": 0}

        try:
            with self.db.begin() as conn:
                # 1. Marcar todos como "potencialmente inativos"
                # (será revertido para os que estão na sheets)
                sheets_names = [c["name"] for c in collaborators]

                # 2. Inserir/atualizar cada colaborador
                for collab in collaborators:
                    # Checar se existe
                    check_query = text(
                        "SELECT id FROM collaborators WHERE name = :name"
                    )
                    result = conn.execute(check_query, {"name": collab["name"]})
                    existing = result.scalar()

                    if existing:
                        # Atualizar
                        update_query = text("""
                            UPDATE collaborators
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

                    else:
                        # Inserir
                        insert_query = text("""
                            INSERT INTO collaborators
                            (name, email, phone, role, status, entry_date, sheets_row_id, created_at, updated_at)
                            VALUES (:name, :email, :phone, :role, :status, :entry_date, :sheets_row_id, NOW(), NOW())
                        """)
                        conn.execute(insert_query, collab)
                        stats["created"] += 1

                # 3. Marcar como "saída" os que não estão mais na sheets
                mark_inactive_query = text("""
                    UPDATE collaborators
                    SET status = 'saída', updated_at = NOW()
                    WHERE name NOT IN ({})
                    AND status != 'saída'
                """.format(", ".join([f"'{n}'" for n in sheets_names])))

                if sheets_names:
                    conn.execute(mark_inactive_query)
                    result = conn.execute(
                        text("SELECT COUNT(*) FROM collaborators WHERE status = 'saída'")
                    )
                    stats["deleted"] = result.scalar()

        except Exception as e:
            logger.error(f"Erro ao upsert: {e}")
            raise

        # Total
        with self.db.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM collaborators WHERE status = 'ativo'"))
            stats["total"] = result.scalar()

        return stats

    def get_active_collaborators(self) -> List[Dict]:
        """Retornar todos os colaboradores ativos"""
        from sqlalchemy import text

        query = text("""
            SELECT id, name, email, phone, role, status
            FROM collaborators
            WHERE status = 'ativo'
            ORDER BY name
        """)

        with self.db.connect() as conn:
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]

    def get_by_role(self, role: str) -> List[Dict]:
        """Retornar colaboradores por papel"""
        from sqlalchemy import text

        query = text("""
            SELECT id, name, email, phone, role, status
            FROM collaborators
            WHERE role = :role AND status = 'ativo'
            ORDER BY name
        """)

        with self.db.connect() as conn:
            result = conn.execute(query, {"role": role})
            return [dict(row._mapping) for row in result]


# Instância global
_sync_instance: Optional[CollaboratorsSync] = None


def get_collaborators_sync(db_connection, sheets_url: str) -> CollaboratorsSync:
    """Get or create collaborators sync instance"""
    global _sync_instance
    if _sync_instance is None:
        _sync_instance = CollaboratorsSync(db_connection, sheets_url)
    return _sync_instance
```

---

## 🔄 Integração ao Scheduler

**Arquivo**: `src/scheduler/scheduler.py`

Adicionar ao `__init__()`:

```python
from src.sync.sheets_collaborators import get_collaborators_sync

# Após inicializar other components:
self.collaborators_sync = get_collaborators_sync(
    db_connection,
    os.getenv("GOOGLE_SHEETS_URL")
)

logger.info("Collaborators sync initialized")
```

Adicionar job de sincronização:

```python
def setup_jobs(self):
    """... existing code ..."""

    # Sincronizar colaboradores a cada 6 horas
    self.scheduler.add_job(
        func=self.sync_collaborators,
        trigger="interval",
        hours=6,
        id="sync_collaborators_from_sheets",
        name="Sync Collaborators from Sheets",
        replace_existing=True
    )

def sync_collaborators(self):
    """Sincronizar colaboradores da Google Sheets"""
    try:
        stats = self.collaborators_sync.sync_from_sheets()
        logger.info(f"✓ Colaboradores sincronizados: {stats}")
    except Exception as e:
        logger.error(f"✗ Erro ao sincronizar colaboradores: {e}")
```

---

## 📊 Usar Dados no Bot

Agora o bot pode consultar colaboradores ativos:

```python
# Em qualquer handler de comando
collaborators = self.collaborators_sync.get_active_collaborators()

# Ou por papel
developers = self.collaborators_sync.get_by_role("Desenvolvedor")

# Usar na lógica
for collab in developers:
    logger.info(f"Dev: {collab['name']} ({collab['email']})")
```

---

## 🔧 Setup Final (Railway)

### **1. Adicionar DATABASE_URL ao Railway**

```bash
railway variables set DATABASE_URL=postgresql://...
```

### **2. Adicionar GOOGLE_SHEETS_URL**

```bash
railway variables set GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1UOo3kKlNCdNJwIVJqMDlnJdtxGLjlGmi9vuctU44324/edit
```

### **3. Executar migração**

```bash
railway run python -m alembic upgrade head
# Ou manualmente:
railway run psql $DATABASE_URL -f migrations/003_create_collaborators_table.sql
```

### **4. Redeploy**

```bash
git push  # Railway faz deploy automático
```

---

## ✅ Verificação Pós-Deploy

```bash
# Ver colaboradores sincronizados
railway run python << 'EOF'
from src.sync.sheets_collaborators import get_collaborators_sync
from src.database import get_db_connection

db = get_db_connection()
sync = get_collaborators_sync(db, os.getenv("GOOGLE_SHEETS_URL"))
collaborators = sync.get_active_collaborators()

for c in collaborators:
    print(f"✓ {c['name']} - {c['role']} ({c['status']})")
EOF
```

---

## 📋 Checklist de Implementação

- [ ] Criar PostgreSQL no Railway
- [ ] Adicionar DATABASE_URL ao .env e Railway
- [ ] Criar tabela `collaborators` (migration)
- [ ] Criar `src/sync/sheets_collaborators.py`
- [ ] Integrar ao scheduler
- [ ] Adicionar GOOGLE_SHEETS_URL
- [ ] Testar sync manualmente
- [ ] Deploy em Railway
- [ ] Verificar logs de sincronização
- [ ] Usar dados no bot

---

## 🎯 Resultado Final

```
Google Sheets (Membros Pangeia)
    ↓ Sync a cada 6h
PostgreSQL no Railway
    ↓ Lê daqui
Bot em Produção
    ✓ Dados sempre atualizados
    ✓ Sem redeploy necessário
    ✓ Performance de banco de dados
```

---

**Tempo estimado**: 1-2 horas de implementação
**Custo**: R$0 (Railway PostgreSQL free tier + Google API gratuita)
**Risco**: Baixo (fallback para hardcoded sempre existe)
