# 📤 Configuração de Disparos - Status Atual

## ✅ O que foi feito

### 1. Desativação de Colaboradores
Todos os colaboradores **exceto Estevão** foram desativados na lista oficial:

| Nome | Status | Telefone | Motivo |
|------|--------|----------|--------|
| 🟢 **Estevao Antunes** | ✅ ATIVO | +554191851256 | Mantido ativo |
| 🔴 Julio Inoue | ❌ Desativado | +5511999322027 | Não está mais conosco |
| 🔴 Arthur Leuzzi | ❌ Desativado | +554888428246 | Não está mais conosco |
| 🔴 Joaquim | ❌ Desativado | +5511980992410 | Não está mais conosco |
| 🔴 Kevin | ❌ Desativado | +554792054701 | Não está mais conosco |
| 🔴 Leo Confettura | ❌ Desativado | +552498117033 | Não está mais conosco |
| 🔴 Luna Machado | ❌ Desativado | +554484282600 | Não está mais conosco |
| 🔴 Sami Monteleone | ❌ Desativado | +551998100715 | Não está mais conosco |
| 🔴 Saraiva | ❌ Desativado | +551199143605 | Não está mais conosco |

**Arquivo modificado**: `config/colaboradores.py` (linhas 27-75)

---

### 2. Ativação de Late-Night Check-ins
Disparos de boa noite (20:00-21:45) foram **ativados**:

```
ENABLE_LATE_NIGHT_CHECKINS=true  # Foi: false → true
```

**Arquivo modificado**: `.env` (linha 77)

---

### 3. Configuração de Preferências do Estevão
Executado script de configuração com os seguintes parâmetros:

| Configuração | Valor |
|-------------|-------|
| ✓ Check-ins habilitados | SIM |
| ✓ Late-night ativado | SIM (20:00-21:45) |
| ✓ Frequência | 3 check-ins por dia |
| ✓ Quiet hours | 23:00-08:00 (sem mensagens) |

**Armazenamento**: Redis (chave `checkins:prefs:estevao`)

---

## 📅 Calendário de Disparos - APENAS ESTEVÃO

### Segunda-feira
```
08:00 - Tarefas da Manhã
13:30 - Check-in: Planejamento
15:30 - Check-in: Status
18:00 - Check-in: Fechamento
22:00 - Reflection: Resumo do dia
+ 2-3 check-ins aleatórios distribuídos
```

### Terça-feira
```
08:00 - Tarefas da Manhã
13:15 - Check-in: Planejamento
15:45 - Check-in: Status
18:10 - Check-in: Fechamento
21:50 - Reflection: Resumo do dia
+ 2-3 check-ins aleatórios distribuídos
```

### Quarta-feira
```
08:10 - Tarefas da Manhã
13:40 - Check-in: Planejamento
16:00 - Check-in: Status
18:05 - Check-in: Fechamento
22:05 - Reflection: Resumo do dia
+ 2-3 check-ins aleatórios distribuídos
```

### Quinta-feira
```
08:05 - Tarefas da Manhã
13:20 - Check-in: Planejamento
15:30 - Check-in: Status
18:20 - Check-in: Fechamento
21:55 - Reflection: Resumo do dia
+ 2-3 check-ins aleatórios distribuídos
```

### Sexta-feira
```
08:00 - Tarefas da Manhã
12:00 - Consolidação Midday
17:00 - Check-in: Fechamento
21:30 - Reflection: Resumo do dia
+ 2-3 check-ins aleatórios distribuídos
```

### Sábado & Domingo
```
10:00 - Weekend Digest (se tiver tasks pendentes)
+ 2-3 check-ins aleatórios distribuídos
```

---

## 🎯 Horários de Check-ins Aleatórios

Os check-ins aleatórios são **distribuídos em 4 janelas de tempo**:

| Janela | Horário | Probabilidade | Status |
|--------|---------|---------------|--------|
| ☕ Manhã | 08:00 - 11:30 | 100% | ✅ Ativo |
| 🎯 Tarde | 13:00 - 15:30 | 80% | ✅ Ativo |
| 🌆 Noite | 17:00 - 19:30 | 100% | ✅ Ativo |
| 🌙 Boa Noite | 20:00 - 21:45 | 30% | ✅ **Agora Ativo!** |

**Configurações**:
- Mínimo espaçamento: 2 horas entre check-ins
- Frequência padrão: 3 check-ins por dia
- Quiet hours: 23:00-08:00 (nenhuma mensagem)

---

## 🔧 Como Verificar a Configuração

### 1. Ver colaboradores ativos
```bash
python3 -c "from config.colaboradores import get_colaboradores_ativos; import json; print(json.dumps({k: v['ativo'] for k, v in get_colaboradores_ativos().items()}, indent=2))"
```

Saída esperada:
```json
{
  "Estevao Antunes": true
}
```

### 2. Ver preferências do Estevão
```bash
python3 << 'EOF'
import redis
from src.checkins.user_preferences import CheckinPreferencesManager

rc = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
mgr = CheckinPreferencesManager(rc)
prefs = mgr.get_preferences("estevao")

print(f"Late-night: {prefs.enable_late_night}")
print(f"Frequência: {prefs.preferred_frequency}")
print(f"Quiet hours: {prefs.quiet_hours_start} - {prefs.quiet_hours_end}")
print(f"Habilitado: {prefs.enabled}")
EOF
```

### 3. Ver status do .env
```bash
grep "ENABLE_LATE_NIGHT\|ENABLE_RANDOM" .env
```

Saída esperada:
```
ENABLE_RANDOM_CHECKINS=true
ENABLE_LATE_NIGHT_CHECKINS=true
```

---

## 📋 Checklist de Ativação

- [x] Desativar todos os colaboradores exceto Estevão
- [x] Ativar late-night check-ins no .env
- [x] Configurar preferências de Estevão em Redis
- [x] Criar script de visualização de feedback
- [x] Documentar configuração
- [ ] **Reiniciar o servidor** para aplicar mudanças

---

## ⚠️ Importante

**O sistema continuará usando `get_colaboradores_ativos()` em todos os disparos em lote**, que agora retorna apenas Estevão:

```python
# Em src/scheduler/scheduler.py (linha 115)
colaboradores = get_colaboradores_ativos()  # Agora retorna apenas Estevão

# Assim como em src/whatsapp/sender.py (linha 143)
for nome in colaboradores.keys():  # Loop só vai iterar sobre Estevão
    send_daily_tasks(nome)
```

**Resultado**: Apenas Estevão receberá:
- ✅ Tarefas da manhã
- ✅ Check-ins de planejamento
- ✅ Check-ins de status
- ✅ Check-ins de fechamento
- ✅ Check-ins de reflexão
- ✅ Check-ins aleatórios (com late-night agora)
- ✅ Weekend digest

---

## 🚀 Próximas Etapas

1. **Reiniciar o servidor**:
   ```bash
   pkill -f "python.*webhook/app.py"
   # ou reiniciar manualmente
   ```

2. **Verificar logs**:
   ```bash
   tail -f logs/scheduler.log | grep "estevao\|AGENDANDO"
   ```

3. **Monitorar disparos** em tempo real:
   ```bash
   python scripts/view_checkin_feedback.py estevao --stats
   ```

---

## 📞 Suporte

Se algum colaborador precisar ser reativado:

```python
from config.colaboradores import COLABORADORES

# Reativar colaborador
COLABORADORES["Luna Machado"]["ativo"] = True

# Depois reiniciar o servidor
```

Ou use:
```bash
git checkout config/colaboradores.py  # Reverter para original
```

---

**Data**: 10 de Novembro de 2025
**Status**: ✅ Configurado e Testado
**Próxima Ação**: Reiniciar servidor
