# 📖 Guia de Uso - Sistema de Gestão Humanizada

## 🎯 Visão Geral

Este sistema combina gestão de tarefas com inteligência psicológica para **incentivar** pessoas em vez de apenas **cobrar** resultados.

---

## 🚀 Como Começar

### 1. Instalar Dependências

```bash
cd notion-pangeia
pip install -r requirements.txt
pip install pyyaml  # Se ainda não estiver instalado
```

### 2. Configurar WAHA API

Adicione ao seu `.env`:

```bash
# WAHA Configuration
WAHA_API_URL=https://pange-waha.u5qiqp.easypanel.host
WAHA_API_KEY=460cf6f80f8c4599a6276acbf1cabc71
WAHA_SESSION=default
```

---

## 💡 Uso Básico

### Enviar Mensagem com WAHA

```python
from src.whatsapp.waha_client import get_waha_client

# Obter cliente
waha = get_waha_client()

# Enviar mensagem
waha.send_message(
    phone="+5511999999999",
    message="Olá! Como você está?"
)
```

### Analisar Estado Psicológico

```python
from src.psychology.engine import PsychologicalEngine

# Criar engine
psych_engine = PsychologicalEngine()

# Dados da pessoa
tasks_data = {
    "total": 10,
    "completed": 7,
    "pending": 2,
    "blocked": 1
}

communication_data = {
    "recent_messages": [
        {"text": "Obrigado! Consegui terminar a tarefa 😊"},
        {"text": "Estou meio travado na task 5..."}
    ],
    "response_times": [2.5, 3.0],  # horas
    "checkins_sent": 5,
    "checkins_answered": 4
}

# Analisar
metrics = psych_engine.analyze_person(tasks_data, communication_data)

print(f"Estado emocional: {metrics.emotional_state.value}")
print(f"Energia: {metrics.energy_level.value}")
print(f"Risco burnout: {metrics.burnout_risk.value}")
```

### Gerar Mensagem Empática

```python
from src.psychology.communicator import EmpatheticCommunicator

# Criar comunicador
communicator = EmpatheticCommunicator()

# Gerar mensagem de conclusão
message = communicator.generate_task_completion_message(
    name="Arthur",
    task_name="Implementar login OAuth",
    metrics=metrics,
    is_first_today=True
)

print(message)
# Output:
# 🎉 Incrível, Arthur! Você concluiu 'Implementar login OAuth'!
#
# ☀️ Que começo fantástico de dia, Arthur!
```

### Gerenciar Perfis de Pessoas

```python
from src.people.analytics import PeopleAnalytics

# Criar analytics
analytics = PeopleAnalytics()

# Criar ou obter perfil
profile = analytics.get_or_create_profile(
    name="Arthur Leuzzi",
    phone="+554888428246",
    role="Desenvolvedor"
)

# Atualizar perfil com métricas
analytics.update_profile_from_metrics(
    phone="+554888428246",
    metrics=metrics
)

# Obter insights
insights = analytics.generate_person_insights("+554888428246")
for insight in insights:
    print(f"- {insight}")
```

---

## 🎭 Cenários de Uso

### Cenário 1: Check-in Matinal Humanizado

```python
from src.psychology.engine import PsychologicalEngine
from src.psychology.communicator import EmpatheticCommunicator
from src.whatsapp.waha_client import get_waha_client

# Setup
psych_engine = PsychologicalEngine()
communicator = EmpatheticCommunicator()
waha = get_waha_client()

# Dados da pessoa
tasks_data = {"total": 5, "completed": 0, "pending": 5, "blocked": 0}
communication_data = {
    "recent_messages": [],
    "response_times": [],
    "checkins_sent": 20,
    "checkins_answered": 18
}

# Analisar
metrics = psych_engine.analyze_person(tasks_data, communication_data)

# Gerar check-in empático
tasks_list = [
    "Revisar PRs pendentes",
    "Implementar autenticação",
    "Escrever testes unitários",
    "Atualizar documentação",
    "Deploy em staging"
]

message = communicator.generate_check_in_message(
    name="Arthur",
    period="morning",
    metrics=metrics,
    tasks=tasks_list
)

# Enviar
waha.send_message(
    phone="+554888428246",
    message=message
)
```

**Exemplo de mensagem gerada:**

```
Bom dia, Arthur! ☀️

Como está sua energia hoje?

Aqui estão suas tarefas para hoje:

1. Revisar PRs pendentes
2. Implementar autenticação
3. Escrever testes unitários
4. Atualizar documentação
5. Deploy em staging

Você tem 5 tarefas hoje, Arthur. Por qual quer começar?
```

### Cenário 2: Detectar e Intervir em Burnout

```python
# Dados indicando burnout
tasks_data = {
    "total": 15,
    "completed": 2,
    "pending": 10,
    "blocked": 3
}

communication_data = {
    "recent_messages": [
        {"text": "Estou exausto, não consigo mais..."},
        {"text": "Isso está impossível"},
        {"text": "Muito cansado"}
    ],
    "response_times": [12, 15, 18],  # Muito alto
    "checkins_sent": 10,
    "checkins_answered": 3  # Baixo engajamento
}

# Analisar
metrics = psych_engine.analyze_person(tasks_data, communication_data)

# Verificar se precisa intervir
if psych_engine.should_intervene(metrics):
    print("⚠️ INTERVENÇÃO NECESSÁRIA!")

    # Gerar sugestões
    suggestions = psych_engine.get_intervention_suggestions(metrics)
    print("\nSugestões:")
    for suggestion in suggestions:
        print(f"- {suggestion}")

    # Gerar mensagem de intervenção
    intervention_msg = communicator.generate_intervention_message(
        name="Arthur",
        metrics=metrics,
        intervention_type="burnout"
    )

    # Enviar
    waha.send_message(
        phone="+554888428246",
        message=intervention_msg
    )
```

**Exemplo de mensagem de intervenção:**

```
⚠️ Arthur, percebi alguns sinais de sobrecarga. Vamos conversar?

Posso ajudar você a:
1. Priorizar só as 3 tarefas mais importantes
2. Desbloquear algumas tarefas
3. Reorganizar sua semana
4. Redistribuir algumas tarefas

Arthur, você não precisa carregar tudo sozinho(a). Como posso ajudar?
```

### Cenário 3: Celebrar Conquistas (Reforço Positivo)

```python
# Pessoa com alta performance
tasks_data = {
    "total": 8,
    "completed": 8,  # 100%!
    "pending": 0,
    "blocked": 0
}

communication_data = {
    "recent_messages": [
        {"text": "Consegui! 🎉"},
        {"text": "Terminei todas!"},
        {"text": "Show de bola! ✨"}
    ],
    "response_times": [1.5, 2.0],
    "checkins_sent": 5,
    "checkins_answered": 5
}

# Analisar
metrics = psych_engine.analyze_person(tasks_data, communication_data)

# Gerar celebração
celebration = communicator.generate_task_completion_message(
    name="Arthur",
    task_name="Deploy em produção",
    metrics=metrics,
    is_last_today=True
)

# Adicionar reforço extra
reinforcement = communicator.generate_positive_reinforcement(
    name="Arthur",
    metrics=metrics,
    achievement_type="consistency"
)

message = f"{celebration}\n\n{reinforcement}"

waha.send_message(
    phone="+554888428246",
    message=message
)
```

**Exemplo de mensagem:**

```
🎉 Incrível, Arthur! Você concluiu 'Deploy em produção'!

🎊 Arthur, você completou TODAS as tarefas! Isso merece comemoração!

Sua consistência é admirável, Arthur!

Você está em uma sequência de 7 dias!
```

### Cenário 4: Relatório da Equipe

```python
from src.people.analytics import PeopleAnalytics

analytics = PeopleAnalytics()

# Resumo da equipe
summary = analytics.get_team_summary()
print(f"Total de pessoas: {summary['total_people']}")
print(f"Motivadas: {summary['motivated']}")
print(f"Em risco: {summary['at_risk']}")
print(f"% Saudável: {summary['healthy_percentage']:.1f}%")

# Pessoas que precisam de atenção
at_risk = analytics.get_people_needing_attention()
if at_risk:
    print("\n⚠️ Pessoas que precisam de atenção:")
    for person in at_risk:
        print(f"- {person.name}: {person.emotional_profile.current_state}")

# Top performers
top = analytics.get_top_performers(limit=3)
print("\n🏆 Top Performers:")
for person in top:
    completion = person.productivity_stats.avg_completion_rate
    print(f"- {person.name}: {completion * 100:.0f}% de conclusão")
```

---

## 🛠️ Integração com Sistema Existente

### Atualizar Comandos para Usar Motor Psicológico

Edite `src/commands/handlers.py`:

```python
from src.psychology.engine import PsychologicalEngine
from src.psychology.communicator import EmpatheticCommunicator
from src.people.analytics import PeopleAnalytics

class CommandHandler:
    def __init__(self):
        self.psych_engine = PsychologicalEngine()
        self.communicator = EmpatheticCommunicator()
        self.people_analytics = PeopleAnalytics()

    def handle_task_completed(self, user_phone, task_name, user_name):
        """Handler quando usuário completa tarefa."""

        # Obter/criar perfil
        profile = self.people_analytics.get_or_create_profile(
            name=user_name,
            phone=user_phone
        )

        # Obter dados de tarefas e comunicação
        tasks_data = self._get_user_tasks(user_phone)
        communication_data = self._get_user_communication(user_phone)

        # Analisar estado psicológico
        metrics = self.psych_engine.analyze_person(
            tasks_data,
            communication_data
        )

        # Atualizar perfil
        self.people_analytics.update_profile_from_metrics(
            user_phone,
            metrics
        )

        # Verificar se é primeira ou última do dia
        is_first = tasks_data["completed"] == 1
        is_last = tasks_data["pending"] == 0

        # Gerar mensagem empática
        message = self.communicator.generate_task_completion_message(
            name=user_name,
            task_name=task_name,
            metrics=metrics,
            is_first_today=is_first,
            is_last_today=is_last
        )

        # Adaptar tom à energia
        message = self.communicator.adapt_tone_to_energy(
            message,
            metrics.energy_level
        )

        return message
```

### Atualizar Scheduler de Check-ins

Edite `src/scheduler/jobs.py`:

```python
from src.psychology.engine import PsychologicalEngine
from src.psychology.communicator import EmpatheticCommunicator
from src.people.analytics import PeopleAnalytics
from src.whatsapp.waha_client import get_waha_client

def send_morning_checkin():
    """Envia check-in matinal empático."""

    psych_engine = PsychologicalEngine()
    communicator = EmpatheticCommunicator()
    analytics = PeopleAnalytics()
    waha = get_waha_client()

    # Para cada colaborador
    for phone, profile in analytics.profiles.items():

        # Obter tarefas do dia
        tasks = get_daily_tasks_for_user(phone)

        # Obter dados para análise
        tasks_data = get_tasks_metrics(phone)
        communication_data = get_communication_metrics(phone)

        # Analisar
        metrics = psych_engine.analyze_person(
            tasks_data,
            communication_data
        )

        # Atualizar perfil
        analytics.update_profile_from_metrics(phone, metrics)

        # Gerar mensagem empática
        message = communicator.generate_check_in_message(
            name=profile.name,
            period="morning",
            metrics=metrics,
            tasks=tasks
        )

        # Enviar via WAHA
        waha.send_message(
            phone=phone,
            message=message
        )

        # Se pessoa está em risco, alertar liderança
        if psych_engine.should_intervene(metrics):
            notify_leadership(profile, metrics)
```

---

## 📊 Monitoramento e Insights

### Dashboard Simples em Terminal

```python
from src.people.analytics import PeopleAnalytics

def show_team_dashboard():
    """Mostra dashboard da equipe no terminal."""

    analytics = PeopleAnalytics()

    print("\n" + "="*50)
    print("📊 DASHBOARD DA EQUIPE")
    print("="*50 + "\n")

    # Resumo geral
    summary = analytics.get_team_summary()
    print(f"Total de pessoas: {summary['total_people']}")
    print(f"✅ Motivadas: {summary['motivated']}")
    print(f"⚠️  Em risco: {summary['at_risk']}")
    print(f"💚 % Saudável: {summary['healthy_percentage']:.1f}%\n")

    # Pessoas em risco
    at_risk = analytics.get_people_needing_attention()
    if at_risk:
        print("🚨 ATENÇÃO NECESSÁRIA:")
        print("-" * 50)
        for person in at_risk:
            state = person.emotional_profile.current_state
            trend = person.emotional_profile.trend
            print(f"\n{person.name}")
            print(f"  Estado: {state} ({trend})")

            insights = analytics.generate_person_insights(person.phone)
            for insight in insights[:3]:
                print(f"  • {insight}")
        print()

    # Top performers
    top = analytics.get_top_performers(3)
    print("\n🏆 TOP PERFORMERS:")
    print("-" * 50)
    for i, person in enumerate(top, 1):
        rate = person.productivity_stats.avg_completion_rate
        print(f"{i}. {person.name} - {rate * 100:.0f}% conclusão")

    print("\n" + "="*50 + "\n")

# Executar
show_team_dashboard()
```

---

## 🎯 Boas Práticas

### 1. Sempre Dar Autonomia

❌ **Errado:**
```python
message = "Você TEM que fazer essas 3 tarefas até 18h."
```

✅ **Correto:**
```python
message = communicator.generate_autonomy_message(
    name="Arthur",
    context="task_order"
)
# "Você tem 3 tarefas. Por qual quer começar?"
```

### 2. Reconhecer Esforço, Não Só Resultado

❌ **Errado:**
```python
if tasks_completed < 5:
    message = "Você não atingiu a meta."
```

✅ **Correto:**
```python
message = "Vejo seu esforço, Arthur. Mesmo que não tenha concluído tudo, você tentou. Isso conta muito!"
```

### 3. Intervir Cedo

```python
# Monitorar diariamente
metrics = psych_engine.analyze_person(tasks_data, communication_data)

# Intervir antes de virar burnout
if metrics.burnout_risk.value in ["medium", "high"]:
    send_intervention_message()
```

### 4. Adaptar Comunicação ao Estado Emocional

```python
# Se pessoa está stressed, usar tom mais suave
if metrics.emotional_state.value in ["stressed", "overwhelmed"]:
    # Evitar cobranças
    # Oferecer suporte
    # Reduzir carga
    pass
else:
    # Pode ser mais direto
    # Pode desafiar mais
    pass
```

---

## 📚 Próximos Passos

1. **Integrar com Notion**: Buscar dados reais de tarefas
2. **Criar Webhook WAHA**: Receber mensagens em tempo real
3. **Machine Learning**: Melhorar detecção de padrões
4. **Dashboard Web**: Visualizar métricas graficamente
5. **Alertas Proativos**: Notificar liderança automaticamente

---

## 🆘 Troubleshooting

### WAHA não conecta

```python
# Testar conexão
from src.whatsapp.waha_client import get_waha_client

waha = get_waha_client()
try:
    status = waha.get_session_status()
    print(f"Status: {status}")
except Exception as e:
    print(f"Erro: {e}")
    # Verificar API_URL e API_KEY
```

### Perfis não salvam

```python
# Verificar permissões de diretório
from pathlib import Path

storage_path = Path.home() / ".pangeia"
storage_path.mkdir(parents=True, exist_ok=True)

# Verificar se consegue escrever
test_file = storage_path / "test.txt"
test_file.write_text("test")
print(f"✅ Diretório acessível: {storage_path}")
```

### Respostas YAML não carregam

```python
# Verificar caminho
from pathlib import Path

yaml_path = Path(__file__).parent / "config" / "psychology" / "psychological_responses.yaml"
print(f"YAML path: {yaml_path}")
print(f"Exists: {yaml_path.exists()}")

if yaml_path.exists():
    import yaml
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    print(f"✅ YAML carregado: {len(data)} categorias")
```

---

## 📞 Suporte

Se precisar de ajuda, abra uma issue ou entre em contato com a equipe!

---

**Desenvolvido com ❤️ e 🧠 Psicologia**
