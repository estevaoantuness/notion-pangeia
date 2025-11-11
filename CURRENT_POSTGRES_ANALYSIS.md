# 🔍 Análise: PostgreSQL Atual do Projeto

## 📊 Situação Atual

### **PostgreSQL Existente**

**Localização**: `evolution-setup/docker-compose.yml`

**Configuração:**
```yaml
Imagem: postgres:15-alpine
Container: evolution_postgres
User: evolution
Password: evolution123
Database: evolution
Port: 5432
Dados: postgres_data (volume)
```

**Uso Atual**:
- ✅ Dedicado ao **Evolution API** (WhatsApp integration)
- ✅ Armazena instâncias do Evolution
- ❌ NÃO compartilhado com bot (dados de colaboradores)

---

## 🏗️ Arquitetura Atual

```
Bot em Desenvolvimento (localhost:5000)
├─ Notion API → dados de tasks
├─ WhatsApp Evolution API (localhost:8080)
│  └─ PostgreSQL (evolution_postgres) para Evolution
│     └─ Dados de WhatsApp/instâncias
└─ Redis (localhost:6379) → preferências, cache

Bot em Produção (Railway)
├─ Notion API → dados de tasks
├─ WhatsApp Evolution API (Railway)
│  └─ PostgreSQL (Railway) para Evolution
│     └─ Dados de WhatsApp/instâncias
└─ Redis (Railway) → preferências, cache
```

**Problema**: Não tem banco de dados para colaboradores/membros!

---

## ✅ O que Você PODE Fazer

### **Opção 1: Reutilizar PostgreSQL Existente** ⭐ RECOMENDADO

Adicionar tabela `collaborators` **no mesmo PostgreSQL** do Evolution:

```sql
-- Conectar em: postgresql://evolution:evolution123@localhost:5432/evolution
CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE app.collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(100),
    status VARCHAR(20),
    entry_date DATE,
    last_synced TIMESTAMP DEFAULT NOW(),
    sheets_row_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Vantagens:**
- ✅ PostgreSQL já existe
- ✅ Já está no docker-compose
- ✅ Não precisa provisionar novo banco
- ✅ Mesma connection string
- ✅ Mesmo database.yml/Dockerfile

**Desvantagens:**
- ❌ Mistura dados (Evolution + App)
- ❌ Em produção, ambos dependem do mesmo PostgreSQL

---

### **Opção 2: PostgreSQL Separado no Railway** ⭐ MELHOR PARA PRODUÇÃO

Criar banco NOVO dedicado ao app (não Evolution):

```
Evolution PostgreSQL (Railway)
└─ Dados de WhatsApp

App PostgreSQL (Railway) ← NOVO
└─ Colaboradores
└─ Check-in feedback
└─ Histórico
```

**Vantagens:**
- ✅ Isolamento de dados
- ✅ Escalar independentemente
- ✅ Backup separado
- ✅ Performance isolada

**Desvantagens:**
- ❌ Custo adicional (R$15-20/mês)
- ❌ Mais uma conexão para gerenciar

---

### **Opção 3: Criar PostgreSQL Local Separado** ⭐ PARA DESENVOLVIMENTO

Novo docker-compose com PostgreSQL app:

```yaml
services:
  postgres-app:
    image: postgres:15-alpine
    container_name: notion_pangeia_db
    environment:
      POSTGRES_USER: pangeia
      POSTGRES_PASSWORD: pangeia123
      POSTGRES_DB: pangeia
    ports:
      - "5433:5432"  # Diferente do Evolution (5432)
    volumes:
      - pangeia_db:/var/lib/postgresql/data
```

**Vantagens:**
- ✅ Não interfere com Evolution
- ✅ Separação clara
- ✅ Pronta para migrar para Railway

**Desvantagens:**
- ❌ Mais um container pra rodar localmente

---

## 🚀 Minha Recomendação

### **Fase 1: Desenvolvimento (AGORA)**
Use **Opção 1** (reutilizar Evolution PostgreSQL):
- Rápido de implementar
- Testa tudo localmente
- Depois migra para Opção 2 em produção

```bash
# Conectar ao PostgreSQL existente
psql postgresql://evolution:evolution123@localhost:5432/evolution

# Criar schema e tabela (SQL fornecido)
\i migrations/004_create_collaborators_table.sql

# Testar sincronização
python3 scripts/sync_sheets_to_db.py
```

### **Fase 2: Produção (DEPOIS)**
Mude para **Opção 2** (PostgreSQL separado no Railway):
- Banco dedicado para app
- Isola Evolution de dados da app
- Melhor performance
- Melhor para backup/restore

---

## 📋 Implementação Recomendada

### **PASSO 1: Criar Migração SQL** (5 min)

Arquivo: `migrations/004_create_collaborators_table.sql`

```sql
-- Criar schema para app (separar de Evolution)
CREATE SCHEMA IF NOT EXISTS app;

-- Tabela de colaboradores
CREATE TABLE app.collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(100),          -- "Desenvolvedor", "Founder", etc
    status VARCHAR(20),         -- "ativo", "inativo", "saída"
    entry_date DATE,
    last_synced TIMESTAMP DEFAULT NOW(),
    sheets_row_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_collaborators_status ON app.collaborators(status);
CREATE INDEX idx_collaborators_name ON app.collaborators(name);
CREATE INDEX idx_collaborators_email ON app.collaborators(email);
CREATE INDEX idx_collaborators_sheets_id ON app.collaborators(sheets_row_id);

-- Log de sincronizações
CREATE TABLE app.sync_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    records_synced INTEGER,
    status VARCHAR(20),         -- "success", "error"
    error_message TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **PASSO 2: Executar Migração**

```bash
# Desenvolvimento (Evolution existente)
psql postgresql://evolution:evolution123@localhost:5432/evolution < migrations/004_create_collaborators_table.sql

# Ou em produção (Railway)
railway run psql $DATABASE_URL < migrations/004_create_collaborators_table.sql
```

### **PASSO 3: Criar Sync Class**

```python
# src/sync/sheets_to_collaborators.py

from sqlalchemy import create_engine, text
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CollaboratorsSync:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)

    def sync_from_sheets(self, sheets_data: List[Dict]) -> Dict:
        """Sincronizar dados da Sheets para PostgreSQL"""
        stats = {"created": 0, "updated": 0, "deleted": 0}

        with self.engine.begin() as conn:
            for row in sheets_data:
                # Lógica de insert/update
                pass

        return stats
```

### **PASSO 4: Integrar ao Scheduler**

```python
# src/scheduler/scheduler.py

def setup_jobs(self):
    # ... existing jobs ...

    # Sincronizar colaboradores a cada 6h
    self.scheduler.add_job(
        func=self.sync_collaborators_from_sheets,
        trigger="interval",
        hours=6,
        id="sync_collaborators",
        name="Sync Collaborators from Sheets"
    )

def sync_collaborators_from_sheets(self):
    try:
        sheets_data = self.sheets_client.fetch_collaborators()
        stats = self.collaborators_sync.sync_from_sheets(sheets_data)
        logger.info(f"✓ Sincronizados: {stats}")
    except Exception as e:
        logger.error(f"✗ Erro sync: {e}")
```

---

## 🔗 Conexão String

### **Desenvolvimento (Evolution existente)**
```python
DATABASE_URL = "postgresql://evolution:evolution123@localhost:5432/evolution"
```

### **Produção (Railway - novo banco)**
```python
DATABASE_URL = os.getenv("DATABASE_URL")
# Railway injecta automaticamente
```

---

## ✅ Checklist

### **Desenvolvimento (Agora)**
- [ ] Executar migração SQL no Evolution PostgreSQL
- [ ] Testar conexão: `psql postgresql://evolution:evolution123@localhost:5432/evolution`
- [ ] Criar CollaboratorsSync class
- [ ] Testar sync manualmente
- [ ] Integrar ao scheduler

### **Produção (Depois)**
- [ ] Criar novo PostgreSQL no Railway
- [ ] Copiar DATABASE_URL
- [ ] Executar mesma migração
- [ ] Testar em produção

---

## 🎯 Próximos Passos

1. **Você quer usar Evolution PostgreSQL existente?** (Opção 1)
   - Ou criar novo banco separado? (Opção 2)
   - Ou PostgreSQL local novo? (Opção 3)

2. **Você quer que eu implemente TUDO agora?**
   - Migrations SQL
   - CollaboratorsSync class
   - Integração ao scheduler
   - Testes

3. **Ou prefere passo-a-passo?**
   - Passo 1: Criar tabela
   - Passo 2: Testar conexão
   - Passo 3: Implementar sync
   - Passo 4: Deploy

**Responda e a gente continua!** 🚀

---

## 📚 Referências

- Evolution PostgreSQL: `evolution-setup/docker-compose.yml:3-14`
- Dockerfile do bot: `Dockerfile`
- Migrations existentes: `migrations/002_create_checkin_feedback_table.sql`
- Scheduler: `src/scheduler/scheduler.py`

---

**Análise de**: `/Users/estevaoantunes/notion-pangeia`
**Data**: 10 de Novembro de 2025
**Status**: Pronto para implementação
