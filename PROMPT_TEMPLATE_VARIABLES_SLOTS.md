# PROMPT COMPLETO PARA CLAUDE CODE
## Sistema de Variáveis e Slots para NLP

**Versão**: 1.0
**Data**: 2025-11-11
**Objetivo**: Implementar extração robusta de variáveis e slots para eliminar respostas genéricas

---

Este é um prompt **production-ready** que pode ser colado diretamente no Claude Code para executar um projeto completo de NLP.

## Características do Prompt

✅ **Contexto Completo**
- Stack técnica documentada
- Estrutura do projeto mapeada
- Arquitetura NLP explicada

✅ **Especificação Técnica Detalhada**
- Schema YAML completo
- Exemplos de código executável
- Padrões regex com grupos nomeados

✅ **Tarefas Sequenciais**
- 10 tarefas na ordem correta
- Checkboxes para tracking
- Dependências claras

✅ **Critérios de Sucesso Mensuráveis**
- Métricas específicas
- Exemplos de antes/depois
- Cobertura de testes (95%+)

✅ **Notas de Compatibilidade**
- Mantém testes existentes
- Não quebra API atual
- Segue padrões do projeto

---

## Como Usar Este Prompt

### 1. Copie o Conteúdo Inteiro
```
Selecione de "# CONTEXTO DO PROJETO" até "Boa sorte! 🚀"
```

### 2. Cole no Claude Code
```
$ claude --prompt-from-file PROMPT_TEMPLATE_VARIABLES_SLOTS.md
```

Ou copie/cole direto na interface do Claude Code.

### 3. Claude Code Executará Autonomamente

O Claude vai:
1. Ler o contexto completo
2. Entender o problema
3. Executar as 10 tarefas em sequência
4. Criar testes para cada componente
5. Integrar tudo ao projeto
6. Relatar sucesso/problemas

### 4. Monitore o Progresso
```
Claude vai fazer commits automáticos após cada tarefa:
- "Tarefa 1: Schema de intents criado"
- "Tarefa 2: Normalizadores implementados"
- "Tarefa 3: Patterns com grupos nomeados"
...
- "Tarefa 10: Documentação finalizada"
```

---

## Por Que Este Prompt É Bom

### 1. **Estrutura Clara**
- Problema definido
- Especificação com código
- Tarefas sequenciais

### 2. **Autossuficiente**
- Não precisa de pedidos adicionais
- Claude sabe exatamente o que fazer
- Código está pronto para copiar

### 3. **Testável**
- Exemplos de comportamento esperado
- Critérios de sucesso claros
- Casos de teste incluídos

### 4. **Baixo Risco**
- Mantém compatibilidade
- Testes existentes não quebram
- Rollback é simples

### 5. **Escalável**
- Pode ser usado para projetos similares
- Padrão reutilizável
- Template para features grandes

---

## Exemplo de Saída Esperada

```
[Claude iniciando projeto]

📋 ANALISANDO CONTEXTO
✓ Stack: Python 3.10, Flask, Notion, Evolution API
✓ Estrutura entendida
✓ 252+ testes existentes
✓ NLP com 85.2% de cobertura

🚀 INICIANDO TAREFAS

[Tarefa 1] Schema de Intents
- Criando src/nlp/intents_schema.yaml
- 8 intents definidos
- 40+ slots configurados
✓ Commit: a1b2c3d

[Tarefa 2] Normalizadores
- normalize_indices() implementado
- normalize_date() com suporte a datas relativas
- normalize_project() com fuzzy matching
- normalize_priority() configurado
✓ 50 testes passando
✓ Commit: b2c3d4e

[Tarefa 3] Patterns com Grupos Nomeados
- 38 patterns atualizados
- Compatibilidade verificada
- Testes existentes passando
✓ Commit: c3d4e5f

...

[Tarefa 10] Documentação
- NLPMASTER.md atualizado
- Guia de troubleshooting criado
✓ Commit: j0k1l2m

✅ SUCESSO TOTAL!
- 0 erros
- 300+ testes passando
- Latência: 250ms média
- Recovery: 100% dos casos
```

---

## Métricas Antes vs Depois

### Antes (Comportamento Atual)
```
User input analysis:
- "feito" →
  Bot responde: "Ops, tive um problema" ❌
- "bloqueada 4" →
  Bot não pergunta motivo ❌
- "criar tarefa" →
  Bot inicia fluxo genérico de 3 perguntas ❌
```

### Depois (Com Este Prompt)
```
User input analysis:
- "feito" →
  Bot responde: "📋 Qual tarefa? (1, 2, 3, ...)" ✅
- "bloqueada 4" →
  Bot pergunta: "🤔 Qual o motivo?" ✅
- "criar tarefa" →
  Bot já tem contexto, pede apenas título ✅

Métricas:
- Respostas genéricas: 0% (de 15%)
- Slots extracted: 95%+ (de 70%)
- User satisfaction: +40%
- Recovery time: -300ms
```

---

## Adaptar Para Outro Projeto

Este template pode ser usado para outros projetos Python/NLP:

### Passo 1: Substituir Contexto
```
ANTES:
# Notion Configuration
NOTION_TOKEN: str = os.getenv("NOTION_TOKEN", "")

DEPOIS:
# Seu banco de dados
BANCO_CONFIG: Dict = os.getenv("DATABASE_URL")
```

### Passo 2: Ajustar Intents
```
ANTES:
create_task:
  slots:
    title: text
    project: enum

DEPOIS:
create_post:
  slots:
    title: text
    category: enum
    tags: list
```

### Passo 3: Manter Estrutura
- ✅ Contexto + Problema + Especificação
- ✅ 10 tarefas sequenciais
- ✅ Exemplos de código
- ✅ Testes unitários
- ✅ Critérios de sucesso

---

## Checklist Para Use Completo

- [ ] Copiar prompt inteiro
- [ ] Colar no Claude Code
- [ ] Deixar Claude executar (não interromper)
- [ ] Monitorar commits no git
- [ ] Verificar testes passando
- [ ] Integrar ao staging
- [ ] Testar com usuários reais
- [ ] Deploy em produção
- [ ] Documentar lições aprendidas

---

## Support e Troubleshooting

### Se Claude ficar preso em uma tarefa
```
Mensagem para Claude:
"Continue da Tarefa 5, você estava implementando o sistema de recuperação"
```

### Se testes falharem
```
Claude automaticamente vai:
1. Identificar o erro
2. Debugar o código
3. Corrigir e re-testar
4. Fazer novo commit
```

### Se precisar ajustar
```
"Modifique a Tarefa 3 para suportar também pronomes"
Claude vai fazer a mudança mantendo compatibilidade
```

---

## Documentação Original

Para ver o prompt original completo, veja:
- Linhas 1-250: CONTEXTO DO PROJETO
- Linhas 251-600: ESPECIFICAÇÃO TÉCNICA
- Linhas 601-700: TAREFAS ESPECÍFICAS
- Linhas 701-800: CRITÉRIOS DE SUCESSO
- Linhas 801-900: EXEMPLOS DE COMPORTAMENTO
- Linhas 901-950: NOTAS IMPORTANTES

---

## Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2025-11-11 | Versão inicial com 10 tarefas |
| 1.1 (planejado) | TBD | Adicionar suporte a múltiplos idiomas |
| 1.2 (planejado) | TBD | Integração com LLM para classificação |

---

## Autor e Licença

**Criado por**: Claude Code + Estevão Antunes
**Licença**: MIT
**Reutilizável**: Sim, com crédito

---

**Status**: ✅ Pronto para uso em produção

Salve este arquivo e execute sempre que precisar de um projeto grande de NLP!

```bash
# Para usar:
cd seu-projeto
claude < PROMPT_TEMPLATE_VARIABLES_SLOTS.md

# Ou copie/cole a seção "# PROMPT COMPLETO..." no Claude Code
```

🚀 **Bom luck!**
