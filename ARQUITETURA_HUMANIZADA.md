# 🧠 Arquitetura do Sistema de Gestão Humanizada de Tarefas e Pessoas

## 🎯 Visão Geral

Sistema de gestão de tarefas e pessoas que aplica princípios da psicologia moderna para **incentivar** em vez de **cobrar**, promovendo motivação intrínseca e bem-estar da equipe.

---

## 📚 Fundamentos Psicológicos

### 1. Teoria da Autodeterminação (Self-Determination Theory)

**3 Necessidades Básicas:**
- **Autonomia**: Dar escolhas, não impor
- **Competência**: Celebrar progresso, reconhecer habilidades
- **Relacionamento**: Criar conexão emocional e pertencimento

### 2. Entrevista Motivacional (OARS)

- **O**pen-ended questions: Perguntas abertas ("Como você está se sentindo com essa tarefa?")
- **A**ffirming: Afirmações positivas ("Você tem feito um ótimo trabalho!")
- **R**eflections: Reflexões ("Parece que você está sobrecarregado...")
- **S**ummaries: Resumos ("Então você concluiu 3 tarefas hoje, ótimo!")

### 3. Comunicação Não-Violenta (OFNR)

- **O**bservação: Descrever fatos sem julgamento
- **F**eeling: Reconhecer sentimentos
- **N**eed: Identificar necessidades
- **R**equest: Fazer pedidos claros e respeitosos

### 4. Reforço Positivo

- Quanto mais você recompensa um comportamento, mais ele se repete
- Feedback construtivo > Crítica
- Celebrar pequenas vitórias
- Reconhecimento público e privado

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp (Interface)                      │
│                           ↕                                  │
│                      WAHA API                                │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                    Flask Webhook Server                      │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                   NLP Processor (Atual)                      │
│              Compreensão de Comandos e Intenções             │
└─────────────────────────────────────────────────────────────┘
                           ↕
        ┌──────────────────┴───────────────────┐
        ↓                                      ↓
┌──────────────────────┐          ┌──────────────────────┐
│  Command Handler     │          │  Psychological       │
│  (Atual)             │←────────→│  Engine (NOVO)       │
│                      │          │                      │
│  - Lista tarefas     │          │  - Análise emocional │
│  - Marca concluída   │          │  - Geração de        │
│  - Inicia tarefa     │          │    mensagens         │
│  - Bloqueia          │          │    empáticas         │
│  - Progresso         │          │  - Reforço positivo  │
└──────────────────────┘          │  - Detecção burnout  │
        ↓                         │  - Sugestões         │
┌──────────────────────┐          │    personalizadas    │
│  Notion API          │          └──────────────────────┘
│  (Atual)             │                     ↓
│                      │          ┌──────────────────────┐
│  - Tasks DB          │          │  People Analytics    │
│  - Users DB          │←────────→│  (NOVO)              │
│  - Check-ins DB      │          │                      │
│  - Insights DB       │          │  - Perfil emocional  │
└──────────────────────┘          │  - Histórico         │
        ↓                         │  - Padrões           │
┌──────────────────────┐          │  - Preferências      │
│  Humanizer           │          └──────────────────────┘
│  (Aprimorado)        │
│                      │
│  - Mensagens         │
│    empáticas         │
│  - Tom personalizado │
│  - Timing adequado   │
└──────────────────────┘
```

---

## 🆕 Componentes Novos

### 1. **Psychological Engine** (Motor Psicológico)

**Localização:** `src/psychology/engine.py`

**Responsabilidades:**
- Analisar estado emocional baseado em padrões de mensagens
- Detectar sinais de burnout, sobrecarga ou desmotivação
- Gerar mensagens empáticas usando OARS e OFNR
- Aplicar reforço positivo estratégico
- Personalizar comunicação para cada pessoa

**Métricas rastreadas:**
```python
{
    "completion_rate": 0.85,  # Taxa de conclusão
    "response_time": 2.5,      # Tempo médio de resposta (horas)
    "energy_level": "medium",  # low/medium/high
    "stress_signals": 2,       # Indicadores de stress
    "positive_words": 15,      # Palavras positivas usadas
    "negative_words": 3,       # Palavras negativas usadas
    "last_checkin_mood": "motivated"
}
```

### 2. **People Analytics** (Análise de Pessoas)

**Localização:** `src/people/analytics.py`

**Responsabilidades:**
- Criar perfil psicológico de cada colaborador
- Identificar padrões de produtividade
- Detectar momentos de alta/baixa energia
- Sugerir intervenções personalizadas
- Gerar insights para liderança

**Perfil de Pessoa:**
```python
{
    "name": "Arthur Leuzzi",
    "personality_traits": {
        "morning_person": True,
        "prefers_small_tasks": False,
        "needs_encouragement": True,
        "responds_to_challenges": True
    },
    "productivity_pattern": {
        "best_hours": ["09:00-12:00", "14:00-17:00"],
        "worst_hours": ["13:00-14:00", "18:00+"],
        "avg_tasks_per_day": 4.2
    },
    "emotional_state": {
        "current": "balanced",
        "trend": "improving",
        "risk_burnout": False
    }
}
```

### 3. **Empathic Communicator** (Comunicador Empático)

**Localização:** `src/psychology/communicator.py`

**Responsabilidades:**
- Gerar mensagens usando técnicas de MI e NVC
- Adaptar tom baseado no estado emocional
- Escolher timing adequado para comunicação
- Evitar linguagem de cobrança

**Exemplo de transformação:**

**Antes (Cobrança):**
```
"Você tem 5 tarefas pendentes. Por favor, atualize o status."
```

**Depois (Incentivo):**
```
"Oi Arthur! 👋

Vi que você tem 5 tarefas em andamento. Como você está se sentindo com relação a elas?

Ontem você concluiu 3 tarefas - isso foi incrível! 🚀

Há algo em que eu possa ajudar hoje?"
```

### 4. **WAHA Integration** (Integração WAHA)

**Localização:** `src/whatsapp/waha_client.py`

**Substituir:** Evolution API atual

**Configuração:**
```python
WAHA_CONFIG = {
    "api_url": "https://pange-waha.u5qiqp.easypanel.host",
    "api_key": "460cf6f80f8c4599a6276acbf1cabc71",
    "session": "pangeia_bot"
}
```

**Funcionalidades WAHA a usar:**
- Envio de mensagens (texto, imagem, áudio)
- Recebimento via webhook
- Marcar mensagens como lidas
- Status do WhatsApp
- Eventos de edição

---

## 🎭 Estratégias de Comunicação Humanizada

### 1. **Check-ins Empáticos**

**Manhã (08:00):**
```
Bom dia, [Nome]! ☀️

Como você dormiu? Como está sua energia hoje?

Aqui estão suas tarefas para hoje:
[lista de tarefas]

Qual você gostaria de começar? (Autonomia)
```

**Tarde (13:30):**
```
E aí, [Nome]!

Como está indo sua manhã? Você já fez muita coisa!

📊 Progresso: X/Y tarefas concluídas

Como você está se sentindo? Precisa de ajuda com algo?
```

**Noite (22:00):**
```
Oi [Nome]!

Antes de encerrar o dia, que tal refletir um pouco?

1. Qual foi sua maior vitória hoje? 🏆
2. O que você aprendeu?
3. Como você quer se sentir amanhã?

Não precisa ser perfeito, só honesto 💙
```

### 2. **Reforço Positivo Estratégico**

**Quando completar tarefa:**
```
🎉 Incrível, [Nome]!

Você concluiu "[tarefa]"!

Isso mostra [competência específica]. Continue assim! 💪

[Se for 1ª tarefa do dia]
Que começo fantástico de dia!

[Se for última tarefa]
Você completou todas as tarefas! Isso merece uma comemoração! 🎊
```

**Quando travar em tarefa:**
```
Ei [Nome],

Vi que a tarefa "[tarefa]" está em andamento há [X] dias.

Não é cobrança! Só queria saber:
- Como você está se sentindo com ela?
- Há algum bloqueio que eu possa ajudar?
- Quer dividir ela em partes menores?

Estou aqui pra ajudar 🤝
```

### 3. **Detecção e Intervenção em Burnout**

**Sinais detectados:**
- Taxa de conclusão < 30% por 3+ dias
- Mensagens negativas frequentes
- Tempo de resposta > 8 horas
- Ausência em check-ins

**Mensagem de intervenção:**
```
Oi [Nome],

Percebi que você está com muita coisa nas mãos ultimamente.

Não é pra cobrar - é pra cuidar de você 💙

Que tal a gente:
1. Priorizar só as 3 tarefas mais importantes?
2. Adiar algumas para semana que vem?
3. Pedir ajuda para a equipe?

Você não precisa fazer tudo sozinho(a). Como posso ajudar?
```

### 4. **Autonomia nas Escolhas**

**Ao invés de impor:**
```
❌ "Complete essas tarefas até 18h"
```

**Dar escolha:**
```
✅ "Você tem 4 tarefas hoje. Qual ordem faz mais sentido pra você?

   A) Começar pelas mais difíceis
   B) Começar pelas mais rápidas
   C) Fazer a que você está mais animado(a)

   Você escolhe! 😊"
```

---

## 📊 Métricas de Sucesso

### Métricas Psicológicas (NOVO)

1. **Índice de Bem-Estar da Equipe**
   - Média de respostas positivas nos check-ins
   - Taxa de palavras positivas vs negativas
   - Nível de energia reportado

2. **Engajamento**
   - Taxa de resposta aos check-ins
   - Tempo médio de resposta
   - Participação em reflexões

3. **Autonomia**
   - % de vezes que escolheu ordem de tarefas
   - % de tarefas auto-iniciadas vs atribuídas

4. **Competência**
   - Taxa de conclusão ao longo do tempo
   - Diversidade de tarefas completadas
   - Feedback positivo recebido

5. **Relacionamento**
   - Qualidade das interações (NLP sentiment)
   - Abertura em compartilhar dificuldades
   - Pedidos de ajuda (sinal de confiança)

### Métricas de Produtividade (Manter)

- Taxa de conclusão de tarefas
- Tempo médio por tarefa
- Bloqueios identificados e resolvidos

---

## 🛠️ Plano de Implementação

### Fase 1: Infraestrutura (1-2 dias)

1. ✅ Migrar Evolution API → WAHA API
2. ✅ Criar módulo `src/psychology/`
3. ✅ Criar módulo `src/people/`
4. ✅ Adicionar banco de dados de perfis

### Fase 2: Motor Psicológico (2-3 dias)

1. ✅ Implementar análise de sentimento
2. ✅ Criar gerador de mensagens empáticas
3. ✅ Implementar detecção de burnout
4. ✅ Sistema de reforço positivo

### Fase 3: Analytics de Pessoas (2-3 dias)

1. ✅ Criar perfis de colaboradores
2. ✅ Rastrear padrões de produtividade
3. ✅ Dashboard de métricas psicológicas
4. ✅ Sistema de alertas para liderança

### Fase 4: Integração e Testes (1-2 dias)

1. ✅ Integrar motor psicológico com commands
2. ✅ Atualizar check-ins com abordagem empática
3. ✅ Testes com colaboradores
4. ✅ Ajustes baseados em feedback

---

## 🎯 Exemplos de Uso Real

### Cenário 1: Pessoa Desmotivada

**Sistema detecta:**
- Taxa de conclusão caiu de 80% → 30%
- Mensagens curtas e negativas
- Não responde check-ins

**Intervenção:**
```
Oi [Nome],

Tudo bem com você? Percebi que você anda mais quieto(a) ultimamente.

Não é pra cobrar nada - só queria saber como você está se sentindo.

Às vezes a gente fica sobrecarregado e tudo bem admitir isso.

Quer conversar sobre suas tarefas? Posso ajudar a:
- Reduzir a carga
- Reorganizar prioridades
- Encontrar bloqueios

Você não está sozinho(a) nisso 💙
```

### Cenário 2: Pessoa em Alta Performance

**Sistema detecta:**
- 95% de conclusão
- Mensagens positivas
- Rápida resposta

**Reforço:**
```
[Nome], você está ARRASANDO! 🚀

Nos últimos 7 dias você:
✅ Concluiu 28 tarefas (média: 4/dia)
✅ Zero bloqueios
✅ Ajudou 2 colegas

Seu trabalho está fazendo diferença real na equipe!

Como você está se sentindo? Está sustentável esse ritmo ou quer ajustar algo?
```

### Cenário 3: Pessoa com Bloqueio

**Usuário:** "bloqueada 3 - não sei por onde começar"

**Bot (com empatia):**
```
Entendo, [Nome]. Tarefas grandes podem ser intimidantes mesmo.

Vamos quebrar essa tarefa em pedaços menores?

"[Nome da tarefa]" poderia ser:
1. [sub-tarefa 1]
2. [sub-tarefa 2]
3. [sub-tarefa 3]

Qual dessas você se sente mais confortável começando?

E lembre: progresso > perfeição 💪
```

---

## 📋 Configuração YAML Expandida

**Novo arquivo:** `config/psychological_responses.yaml`

```yaml
encouragement:
  task_completed:
    - "🎉 Incrível! Você concluiu '{task_name}'!"
    - "👏 Parabéns! Mais uma vitória para você!"
    - "💪 Você é incrível! '{task_name}' concluída!"

  first_task_of_day:
    - "☀️ Que começo fantástico de dia!"
    - "🚀 Já começou com o pé direito!"
    - "⚡ Essa energia matinal é tudo!"

empathy:
  task_blocked:
    - "Ei {name}, vi que '{task}' está travada. Como posso ajudar?"
    - "Bloqueios acontecem, {name}. Vamos resolver juntos?"
    - "{name}, sem pressão! Que tal conversarmos sobre '{task}'?"

  low_energy:
    - "Percebi que você está mais quieto hoje. Tudo bem?"
    - "Dias difíceis acontecem. Como você está se sentindo?"
    - "Não precisa ser produtivo todo dia. Como posso ajudar?"

autonomy:
  task_order:
    - "Você tem {n} tarefas. Por qual quer começar?"
    - "Qual tarefa faz mais sentido pra você agora?"
    - "Você escolhe: começar pela mais difícil ou mais fácil?"

  timing:
    - "Quando você acha melhor fazer '{task}'?"
    - "Você se sente mais produtivo de manhã ou tarde?"
```

---

## 🔒 Considerações Éticas

1. **Privacidade**: Dados emocionais são sensíveis
2. **Transparência**: Usuário sabe que está interagindo com bot
3. **Consentimento**: Opt-in para análise psicológica
4. **Limite**: Bot sugere ajuda humana quando necessário
5. **Não-julgamento**: Nunca culpar ou envergonhar

---

## 📚 Referências

1. **Teoria da Autodeterminação**: Deci & Ryan (1985, 2000)
2. **Entrevista Motivacional**: Miller & Rollnick (1991, 2025)
3. **Comunicação Não-Violenta**: Marshall Rosenberg (1963-2015)
4. **Reforço Positivo**: B.F. Skinner (Behaviorism)
5. **Psicologia Positiva**: Martin Seligman

---

**Status**: Arquitetura aprovada ✅
**Próximo Passo**: Implementação do Motor Psicológico
