# 📋 Plano: Sincronizar Google Sheets → PostgreSQL

## 🎯 Objetivo

Manter a lista de colaboradores (papéis, status) sincronizada entre Google Sheets e PostgreSQL, para que o bot sempre tenha dados atualizados sem redeploy.

---

## 📊 Arquitetura Proposta

```
Google Sheets
(fonte de verdade)
    ↓ (a cada 1h ou manual)
    ↓ Sincroniza mudanças
    ↓
PostgreSQL Database
(cache + histórico)
    ↓ (lê daqui 99% das vezes)
    ↓
Bot em Produção
```

---

## ⚙️ Opções de Implementação

### **Opção 1: PostgreSQL Local (Desenvolvimen
to)**
- **Custo**: Grátis
- **Setup**: 5 min (brew install postgres)
- **Vantagem**: Testa tudo antes de ir para Render
- **Desvantagem**: Precisa manter rodando localmente

### **Opção 2: PostgreSQL no Render (Produção)**
- **Custo**: R$15-20/mês (plano gratuito existe)
- **Setup**: 2 min no dashboard Render
- **Vantagem**: Pronto para produção, escalável
- **Desvantagem**: Precisa de carta de crédito

### **Opção 3: SQLite (Mais Simples)**
- **Custo**: Grátis (arquivo local)
- **Setup**: 2 min (pip install sqlite3)
- **Vantagem**: Zero configuração, funciona em localhost
- **Desvantagem**: Não escalável, não ideal para múltiplas instâncias

---

## 📋 Dados a Sincronizar

Da Google Sheets esperamos ter:

```
Coluna A: Nome
Coluna B: Email
Coluna C: Telefone
Coluna D: Papel/Cargo
Coluna E: Status (Ativo/Inativo)
Coluna F: Data de Entrada
...
```

---

## 🔧 Implementação Recomendada

### **Fase 1: Setup do Banco (1 dia)**

**Opção A: PostgreSQL no Render** (RECOMENDADO)
```bash
1. Acessar https://dashboard.render.com
2. Criar novo PostgreSQL (Free tier ou pagável)
3. Copiar DATABASE_URL
4. Adicionar ao .env do projeto
```

**Opção B: PostgreSQL Local** (para testar)
```bash
brew install postgresql@15
brew services start postgresql@15
createdb notion_pangeia
```

**Opção C: SQLite** (mais fácil para começar)
```bash
# Nada a instalar, usa arquivo .db no projeto
touch db/members.db
```

---

### **Fase 2: Criação do Schema** (30 min)

**Tabela de Colaboradores:**
```sql
CREATE TABLE collaborators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(100),           -- "Desenvolvedor", "Product Manager", etc
    status VARCHAR(20),          -- "ativo", "inativo", "saída"
    entry_date DATE,
    last_synced TIMESTAMP,
    sheets_row_id INTEGER,       -- referência para Google Sheets
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_collaborators_status ON collaborators(status);
CREATE INDEX idx_collaborators_email ON collaborators(email);
```

---

### **Fase 3: Sync automático** (2-3 horas)

**Componentes a Criar:**

1. **GoogleSheetsClient** (já existe?)
   ```python
   class GoogleSheetsClient:
       def get_all_collaborators(self) -> List[Dict]
       def get_updated_since(timestamp) -> List[Dict]
   ```

2. **CollaboratorsRepository**
   ```python
   class CollaboratorsRepository:
       def sync_from_sheets(sheets_data) -> int  # retorna qtd sincronizada
       def get_active() -> List[Collaborator]
       def get_by_role(role) -> List[Collaborator]
       def get_by_status(status) -> List[Collaborator]
   ```

3. **Sync Job** (rodar a cada 1h)
   ```python
   @scheduler.scheduled_job('interval', hours=1)
   def sync_collaborators_from_sheets():
       sheets_data = sheets_client.get_all_collaborators()
       count = repository.sync_from_sheets(sheets_data)
       logger.info(f"✓ Sincronizados {count} colaboradores")
   ```

4. **Web Hook** (sincronização sob demanda)
   ```python
   @app.route('/api/sync/collaborators', methods=['POST'])
   def trigger_sync():
       # Pode ser chamado manualmente para sync imediato
   ```

---

## 📊 Benefícios Esperados

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Atualizar lista** | Edit código + redeploy | Edit sheets + pronto |
| **Performance** | API Google (lento) | PostgreSQL (rápido) |
| **Histórico** | Nenhum | Guardado no DB |
| **Sincronização** | Manual | Automática (1h) |
| **Fallback** | Nenhum | Tenta Google se DB falhar |
| **Escalabilidade** | Hardcoded lista | Dinâmica e flexível |

---

## 💾 Opção Recomendada: **SQLite (COMECE AQUI)**

**Vantagem**: Não precisa de PostgreSQL instalado, não precisa de servidor externo.

### **Implementação SQLite (30 min):**

```python
# 1. Instalar dependência
pip install sqlalchemy sqlite

# 2. Criar schema
# db/schema.sql

# 3. Criar sync job
# src/sync/sheets_to_db.py

# 4. Executar no startup
# src/scheduler/scheduler.py → adicionar job de sync
```

**Depois, quando escalar, migrar para PostgreSQL é trivial (SQLAlchemy abstrai tudo).**

---

## 🚀 Plano de Ação (Recomendado)

### **Semana 1: Setup & Teste**
- [ ] Escolher banco (SQLite = mais fácil)
- [ ] Criar schema de colaboradores
- [ ] Criar GoogleSheetsClient (se não existir)
- [ ] Criar CollaboratorsRepository
- [ ] Testar sync manualmente

### **Semana 2: Automação**
- [ ] Criar sync job (rodar a cada 1h)
- [ ] Testar em desenvolvimento
- [ ] Criar web hook para sync manual
- [ ] Documentar

### **Semana 3: Integração**
- [ ] Integrar ao scheduler existente
- [ ] Usar dados na lógica do bot
- [ ] Monitorar logs
- [ ] Deploy em produção

---

## ⚡ Próximos Passos Imediatos

1. **Responda estas perguntas:**
   - Qual banco você prefere? (SQLite, PostgreSQL local, Render)
   - Você quer testar localmente ou já direto em produção?
   - Qual a frequência de sync? (a cada 1h, 6h, 24h?)

2. **Acesse a Google Sheets:**
   - Confirme quais colunas tem exatamente
   - Veja quantas linhas (colaboradores)
   - Confirme se está realmente atualizada

3. **Eu posso criar:**
   - [ ] Schema do banco
   - [ ] GoogleSheetsClient robusto
   - [ ] Sync automático
   - [ ] Testes

---

## 📌 Nota Importante

Se você usa **SQLite**, o arquivo `.db` fica local e não sobe ao Render. Para produção, você teria que:

**Opção A**: Usar PostgreSQL no Render (recomendado)
**Opção B**: Exportar SQLite como seed file toda semana

Qual você prefere? 🎯

---

**Status**: Aguardando decisão
**Estimativa**: 1-2 dias para implementação completa
**Risco**: Baixo (Google Sheets é fallback sempre disponível)
