# ✅ Post-Deploy Verification Checklist

## 🚀 Após Redeploy no Render

### 1. Verificar Logs do Render

Acesse: https://dashboard.render.com/services

1. Clique no serviço `pangeia-bot`
2. Abra a aba **Logs**
3. Procure por estas mensagens (em ordem):

```
[INFO] Flask app initialized
[INFO] Scheduler initialized
[INFO] Random check-ins enabled: true
[INFO] Late-night check-ins enabled: true
[INFO] Scheduling for: Estevao Antunes
[INFO] Total of X random check-ins agendados
[INFO] Scheduler started successfully
```

✅ **Esperado**: Todas as 7 mensagens presentes, sem erros

❌ **Se falhar**:
- Verificar variáveis de ambiente no Render
- Verificar conectividade Redis
- Verificar permissões de arquivo

---

### 2. Verificar Configuração Ativa

```bash
# 2.1 - Colaboradores ativos (deve retornar apenas Estevão)
python3 -c "from config.colaboradores import get_colaboradores_ativos; print(list(get_colaboradores_ativos().keys()))"

# Resultado esperado:
# ['Estevao Antunes']

# 2.2 - Variáveis de ambiente
grep "ENABLE_RANDOM\|ENABLE_LATE" .env

# Resultado esperado:
# ENABLE_RANDOM_CHECKINS=true
# ENABLE_LATE_NIGHT_CHECKINS=true

# 2.3 - Preferências do Estevão no Redis
redis-cli GET "checkins:prefs:estevao"

# Resultado esperado:
# {
#   "enable_late_night": true,
#   "preferred_frequency": 3,
#   "quiet_hours_start": "23:00",
#   "quiet_hours_end": "08:00",
#   "enabled": true
# }
```

---

### 3. Testar Disparos Manualmente

#### 3.1 - Ativar Scheduler para Hoje

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from src.scheduler.scheduler import get_scheduler
from datetime import datetime

scheduler = get_scheduler()

# Forçar agendamento de hoje
today = datetime.now().date()
print(f"Agendando jobs para {today}...")

scheduler.schedule_today()

# Listar jobs agendados
jobs = scheduler.scheduler.get_jobs()
print(f"\nTotal de jobs agendados: {len(jobs)}\n")

for job in jobs:
    print(f"- {job.name} @ {job.next_run_time}")
EOF
```

✅ **Esperado**:
- 8-15 jobs agendados
- Nomes incluindo "Estevao"
- Check-ins aleatórios listados
- Tempos no intervalo correto

---

### 4. Verificar Feedback de Check-ins

```bash
# Ver últimas respostas
python3 scripts/view_checkin_feedback.py estevao

# Ver estatísticas
python3 scripts/view_checkin_feedback.py estevao --stats

# Filtrar por janela de tempo
python3 scripts/view_checkin_feedback.py estevao --window morning

# Filtrar por tipo de resposta
python3 scripts/view_checkin_feedback.py estevao --intent progressing
```

---

### 5. Testar Bot Responsividade

Envie mensagens de teste para o bot:

```
/help
Mostrar meu dia
Criar tarefa: Teste de deploy
```

✅ **Esperado**: Bot responde normalmente a todos os comandos

---

### 6. Checklist Completo

- [ ] Logs do Render mostram sucesso
- [ ] `get_colaboradores_ativos()` retorna apenas Estevão
- [ ] `.env` tem `ENABLE_RANDOM_CHECKINS=true`
- [ ] `.env` tem `ENABLE_LATE_NIGHT_CHECKINS=true`
- [ ] Redis conectado e preferências carregadas
- [ ] Scheduler agendou 8-15 jobs para hoje
- [ ] Check-ins aleatórios presentes no agendamento
- [ ] Late-night check-ins inclusos
- [ ] Bot responde a comandos básicos
- [ ] Nenhum erro nos logs do Render

---

## 🔧 Troubleshooting

### Erro: "No module named 'src'"

**Solução**: Execute scripts do diretório raiz do projeto
```bash
cd /Users/estevaoantunes/notion-pangeia
python3 scripts/configure_estevao_checkins.py
```

---

### Erro: "Redis connection failed"

**Causa**: Redis não está rodando no Render

**Solução**:
1. Verificar se `REDIS_URL` está configurado no Render
2. Se usar Redis local, garantir que está rodando:
   ```bash
   brew services start redis
   redis-cli ping  # Deve retornar PONG
   ```

---

### Erro: "Scheduler failed to initialize"

**Causa**: Erro ao carregar colaboradores ou preferências

**Solução**:
1. Verificar logs do Render detalhadamente
2. Verificar se `config/colaboradores.py` está válido:
   ```bash
   python3 -c "from config.colaboradores import COLABORADORES; print('OK')"
   ```
3. Verificar permissões de arquivo:
   ```bash
   ls -la config/colaboradores.py
   ```

---

### Erro: "Only Estevão was scheduled but others got messages"

**Causa**: Cache ou GitHub não atualizou corretamente

**Solução**:
1. Fazer hard reset:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```
2. Redeployer manualmente no Render
3. Esperar 2-3 minutos para inicialização

---

### Erro: "Late-night check-ins not sending"

**Causa**: Variável de ambiente não sincronizada

**Solução**:
1. Verificar Render environment variables:
   - Dashboard → Service → Environment
   - Procurar por `ENABLE_LATE_NIGHT_CHECKINS`
   - Deve ser `true`
2. Se não existir, adicionar manualmente
3. Redeployer serviço

---

## 📊 Monitoramento Contínuo

### Logs Importantes

```bash
# Tail dos logs (requer terminal Render)
# Via dashboard: Serviço → Logs (live stream)

# Procurar por:
tail -f /var/log/pangeia.log | grep -i "checkin\|dispatch\|scheduler"
```

### Métricas para Acompanhar

- **Hora do próximo job**: Check-in + 5min
- **Número de jobs**: 8-15 por dia
- **Response time do bot**: < 2 segundos
- **Feedback de check-ins**: Mínimo 1/dia esperado

---

## ✅ Status Atual

**Deploy Date**: 10 de Novembro de 2025
**Version**: 3.0.0 (Dispatch reconfiguration)
**Active Users**: Estevão Antunes apenas
**Random Check-ins**: ATIVADOS
**Late-Night Check-ins**: ATIVADOS ✨
**Status**: Aguardando confirmação pós-deploy

---

## 📞 Próximas Etapas

1. ✅ Verificar logs do Render
2. ✅ Confirmar apenas Estevão recebendo mensagens
3. ✅ Testar resposta aos check-ins
4. ✅ Monitorar feedback por 24h
5. ⏳ Se tudo ok → Deploy para produção completa

---

**Última atualização**: 10 de Novembro de 2025
**Próxima revisão**: Após 24h de produção
