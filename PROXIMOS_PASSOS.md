# 🚀 Próximos Passos - Roadmap do Pangeia Bot

**Data:** 13 de Novembro de 2025
**Status Atual:** ✅ Sistema de Checkins implementado e funcionando
**Ambiente:** Railway (Produção) + Dashboard Local

---

## 📋 Resumo do Status Atual

### ✅ Completo

- [x] Sistema de checkins diários (3x por dia)
- [x] Scheduler automático
- [x] Webhook com detecção de respostas
- [x] Armazenamento em PostgreSQL (Railway)
- [x] Dashboard web em tempo real
- [x] Bug fix: "Ops, tive um problema"
- [x] Testes simulados e end-to-end
- [x] README atualizado
- [x] Deploy em Railway

### ⏳ Próximos (Recomendados)

1. **Ativar para todos os usuários**
2. **Customizar perguntas**
3. **Notificações inteligentes**
4. **Relatórios e exportação**
5. **Dashboard melhorado (dark mode)**

### 💡 Opcionais (Futuro)

- Sincronizar com Supabase
- Análise de padrões
- Google Sheets backup
- Integrações extras

---

## 🎯 Fase 1: Produção Imediata (1-2 semanas)

### 1️⃣ Ativar Checkins para Todos os Usuários

**Objetivo:** Todos os 6 usuários receberem checkins automáticos

**O que fazer:**

1. **Atualizar `config/colaboradores.py`**
   ```python
   # Mudar de:
   "ativo": False  # Apenas Estevão está ativo

   # Para:
   "ativo": True   # Todos os usuários
   ```

2. **Testar com cada usuário**
   ```bash
   # Simular checkin para cada um
   python3 test_send_checkin_simulated.py  # Já funciona

   # Ou chamar manualmente
   from src.database.checkins_integration import get_checkins_integration
   integration = get_checkins_integration()
   for nome in ["Joaquim", "Kevin", "Leo", "Arthur", "Julio"]:
       integration.create_daily_checkin(nome)
   ```

3. **Verificar logs**
   ```bash
   railway logs -f | grep "checkin"
   ```

**Tempo Estimado:** 30 minutos
**Complexidade:** Baixa
**Impacto:** Alto ✅

---

### 2️⃣ Customizar Perguntas de Checkin

**Objetivo:** Perguntas específicas por projeto/time

**O que fazer:**

1. **Editar `config/replies.yaml`**
   ```yaml
   checkins:
     metas:
       - "🎯 Qual é a meta de hoje?"
       - "🚀 O que você quer conquistar hoje?"

     status:
       - "🌤️ Como está o dia?"
       - "⚡ Qual é a velocidade?"

     closing:
       - "🌙 Resumo do dia?"
       - "📊 O que aprendeu?"
   ```

2. **Ou customizar por usuário**
   ```python
   # Criar tabela: user_custom_questions
   # user_id | question_type | custom_question | active

   # Depois atualizar humanizer para consultar
   ```

3. **Testar perguntas novas**
   ```bash
   python3 view_postgres_history.py
   # Verificar se as perguntas mudaram
   ```

**Tempo Estimado:** 45 minutos
**Complexidade:** Média
**Impacto:** Médio ⭐

---

## 🔔 Fase 2: Notificações Inteligentes (2-3 semanas)

### 3️⃣ Notificações para Checkins Atrasados

**Objetivo:** Alertar usuário se não responder em 30-60 min

**O que fazer:**

1. **Criar job no scheduler**
   ```python
   # src/scheduler/scheduler.py

   def _check_overdue_checkins(self):
       """Envia notificação para checkins não respondidos"""
       tracker = get_pending_checkin_tracker()
       pending = tracker.get_all_pending()

       for checkin in pending:
           if checkin.time_elapsed > 30_minutes:
               sender.send_message(
                   person_name=checkin.user_id,
                   message=f"⏰ Não esqueci que você não respondeu: {checkin.question}"
               )
   ```

2. **Agendar execução**
   ```python
   # A cada 30 minutos, checar pending
   self.scheduler.add_job(
       self._check_overdue_checkins,
       trigger="interval",
       minutes=30,
       id="check_overdue_checkins"
   )
   ```

3. **Testar**
   ```bash
   # Enviar checkin
   # Esperar 31 minutos
   # Verificar se notificação foi enviada
   ```

**Tempo Estimado:** 1-2 horas
**Complexidade:** Média
**Impacto:** Alto ✅

---

### 4️⃣ Relatórios e Exportação

**Objetivo:** Gerar relatórios em PDF/CSV

**O que fazer:**

1. **Criar endpoint no dashboard**
   ```python
   # dashboard.py - adicionar rotas

   @app.route('/api/export/csv')
   def export_csv():
       """Exporta checkins em CSV"""
       from io import StringIO
       import csv

       output = StringIO()
       writer = csv.writer(output)
       writer.writerow(['User', 'Date', 'Morning', 'Afternoon', 'Evening'])

       # Query e escrever dados

       return output.getvalue()

   @app.route('/api/export/pdf')
   def export_pdf():
       """Exporta relatório em PDF"""
       # Usar biblioteca: reportlab ou weasyprint
   ```

2. **Adicionar botões no dashboard**
   ```html
   <!-- dashboard.html -->
   <button onclick="downloadCSV()">📥 Exportar CSV</button>
   <button onclick="downloadPDF()">📄 Exportar PDF</button>
   ```

3. **Testar downloads**
   ```bash
   # Acessar dashboard
   # Clicar em "Exportar CSV"
   # Verificar arquivo
   ```

**Tempo Estimado:** 2 horas
**Complexidade:** Média-Alta
**Impacto:** Alto ✅

---

## 🎨 Fase 3: Dashboard Melhorado (2-3 semanas)

### 5️⃣ Dark Mode

**Objetivo:** Tema escuro no dashboard

**O que fazer:**

1. **Adicionar toggle no dashboard**
   ```javascript
   // dashboard.py - TEMPLATE

   <button onclick="toggleDarkMode()" class="dark-mode-toggle">
       🌙 Dark Mode
   </button>

   <script>
   function toggleDarkMode() {
       document.body.classList.toggle('dark-mode');
       localStorage.setItem('darkMode',
           document.body.classList.contains('dark-mode'));
   }

   // Carregar preferência salva
   if (localStorage.getItem('darkMode') === 'true') {
       document.body.classList.add('dark-mode');
   }
   </script>
   ```

2. **Adicionar CSS dark mode**
   ```css
   body.dark-mode {
       background: #1a1a1a;
       color: #e0e0e0;
   }

   body.dark-mode .card {
       background: #2d2d2d;
       border-color: #444;
   }
   ```

**Tempo Estimado:** 1 hora
**Complexidade:** Baixa
**Impacto:** Médio ⭐

---

### 6️⃣ Gráficos Avançados

**Objetivo:** Mais insights no dashboard

**O que fazer:**

1. **Adicionar novos gráficos**
   - 📈 Tendência de resposta (7 dias)
   - 📊 Distribuição por hora
   - 👥 Comparação entre usuários
   - 🕐 Tempo médio de resposta

2. **Implementar**
   ```python
   # dashboard.py - nova rota

   @app.route('/api/analytics')
   def analytics():
       # Calcular tendências
       # Agregações por hora
       # Comparações
       return jsonify({
           'trend': [...],
           'distribution': [...],
           'comparison': [...]
       })
   ```

**Tempo Estimado:** 2-3 horas
**Complexidade:** Média
**Impacto:** Alto ✅

---

## 🔄 Fase 4: Integrações Avançadas (3-4 semanas)

### 7️⃣ Sincronizar com Supabase

**Objetivo:** Dados em Supabase para web UI visual

**O que fazer:**

```python
# Novo arquivo: src/integrations/supabase_sync.py

from supabase import create_client

def sync_to_supabase():
    """Sincroniza Railway → Supabase"""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Sincronizar users
    # 2. Sincronizar daily_checkins
    # 3. Atualizar em tempo real
```

**Tempo Estimado:** 3-4 horas
**Complexidade:** Alta
**Impacto:** Médio ⭐

---

### 8️⃣ Análise de Padrões

**Objetivo:** Insights automáticos (ex: melhor hora de responder)

**O que fazer:**

```python
# src/analytics/patterns.py

def analyze_patterns():
    """Analisa padrões nos checkins"""

    # Melhor hora para responder
    # Usuários mais produtivos
    # Tendências de humor
    # Previsões
```

**Tempo Estimado:** 4-5 horas
**Complexidade:** Alta
**Impacto:** Alto ✅

---

### 9️⃣ Google Sheets Backup

**Objetivo:** Dados em Google Sheets automaticamente

**O que fazer:**

```python
# src/integrations/google_sheets_sync.py

def sync_to_sheets():
    """Copia checkins para Google Sheets"""
    sheets_client = GoogleSheetsClient()

    # Lê dados do PostgreSQL
    # Escreve em Sheets em tempo real
```

**Tempo Estimado:** 2-3 horas
**Complexidade:** Média
**Impacto:** Médio ⭐

---

## 📊 Plano de Execução Recomendado

### Semana 1: Fundação (CRÍTICO)
```
✅ Segunda: Ativar para todos usuários (30 min)
✅ Terça: Customizar perguntas (1 hora)
✅ Quarta: Notificações de atraso (2 horas)
✅ Quinta: Relatórios CSV/PDF (2 horas)
✅ Sexta: Testar tudo em produção
```

### Semana 2: Dashboard (IMPORTANTE)
```
✅ Segunda: Dark mode (1 hora)
✅ Terça-Quarta: Gráficos avançados (3 horas)
✅ Quinta-Sexta: Polir e testar
```

### Semana 3+: Avançado (OPCIONAL)
```
⭐ Supabase sync (4 horas)
⭐ Análise de padrões (5 horas)
⭐ Google Sheets (3 horas)
⭐ Novas features
```

---

## ✅ Checklist de Verificação

Antes de cada release:

- [ ] Todos os testes passam
- [ ] Logs verificados em produção
- [ ] README atualizado
- [ ] Documentação de mudanças
- [ ] Nenhum erro no webhook
- [ ] Dashboard exibindo dados corretos
- [ ] Comitted e pushed para Railway

---

## 🛠️ Tecnologias Úteis para Próximas Features

| Feature | Tech Stack | Tempo |
|---------|-----------|-------|
| **Notificações** | APScheduler (já temos) | 2h |
| **Exportar PDF** | reportlab ou weasyprint | 3h |
| **Gráficos avançados** | Plotly ou D3.js | 4h |
| **Sincronização Supabase** | Supabase Python client | 3h |
| **Google Sheets** | Google Sheets API | 2h |
| **Análise ML** | scikit-learn ou TensorFlow | 6h |
| **Mobile App** | React Native ou Flutter | 20h |

---

## 📞 Dúvidas Frequentes

**P: Por onde começar?**
R: Comece pela **Fase 1** (Ativar para todos). É rápido e de alto impacto.

**P: Qual é mais importante?**
R: Na ordem: 1 → 2 → 3 → 4 → 5. Depois fica a seu critério.

**P: Posso fazer em paralelo?**
R: Sim! Tasks 3 e 4 podem ser feitas simultaneamente com 1 e 2.

**P: E se algo quebrar?**
R: Todos os testes simulados estão em `test_*.py`. Use para validar.

---

## 🎯 Resultado Esperado (Após todas as fases)

```
📊 Dashboard Super Completo
├── 📈 Gráficos avançados em tempo real
├── 🌙 Dark mode automático
├── 📥 Exportar para PDF/CSV
├── 🔔 Notificações inteligentes
├── 📊 Análise de padrões
├── 📱 Sincronizado com Supabase
└── 💾 Backup em Google Sheets

🤖 Bot Potente
├── ✅ 6 usuários com checkins automáticos
├── 🎯 Perguntas customizadas
├── 📊 Análise de tendências
└── 🚀 Escalável e maintível

📈 Métricas
├── ✅ 100% de uptime
├── 📊 Respostas rastreadas
├── 📈 Tendências claras
└── 🎯 Insights acionáveis
```

---

**Status:** ✅ **PRONTO PARA PRÓXIMA FASE**

**Recomendação:** Comece pela **Fase 1** segunda-feira!