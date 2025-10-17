# 📚 Setup do Database de Usuários (Notion)

Este documento explica como criar o database de usuários no Notion para persistir o estado de onboarding.

## 🎯 Por que este database?

Sem persistência, o bot:
- ❌ Esquece usuários quando reinicia
- ❌ Repete tutorial para usuários antigos
- ❌ Não rastreia histórico de interações

Com persistência:
- ✅ Lembra conversas anteriores
- ✅ Reconhece usuários que já fizeram onboarding
- ✅ Rastreia última interação de cada pessoa

## 🏗️ Estrutura do Database

Crie um database no Notion com as seguintes properties:

### Properties Obrigatórias:

| Property | Type | Description |
|----------|------|-------------|
| **Nome** | Title | Nome completo do colaborador (ex: "Estevao Antunes") |
| **Telefone** | Phone Number | Número do WhatsApp (ex: +5511999999999) |
| **Onboarding Completo** | Checkbox | ✅ se completou, ❌ se não |
| **Data Primeiro Acesso** | Date | Quando usou o bot pela primeira vez |
| **Data Último Acesso** | Date | Última interação com o bot |
| **Tipo Onboarding** | Select | "completo", "básico", ou "nenhum" |

### Properties Opcionais (Recomendadas):

| Property | Type | Description |
|----------|------|-------------|
| **Status** | Select | "ativo", "inativo", etc |
| **Cargo** | Text | Cargo do colaborador |
| **Email** | Email | Email (se quiser integrar futuramente) |

## 📝 Passos para Setup:

### 1. Criar Database no Notion

1. Abra o Notion
2. Crie uma nova página
3. Digite `/database` e selecione "Database - Full page"
4. Nomeie: "Usuários Pangeia Bot"

### 2. Adicionar Properties

Para cada property da tabela acima:

1. Clique em "+" no header
2. Selecione o tipo correto
3. Nomeie exatamente como especificado
4. Configure options (para Select):
   - **Tipo Onboarding**: "completo", "básico", "nenhum"

### 3. Configurar Visualização

Recomenda-se criar as seguintes views:

- **Todos** (default): Mostra todos os usuários
- **Onboarding Pendente**: Filter = Onboarding Completo ☐ (unchecked)
- **Ativos Hoje**: Filter = Data Último Acesso = Today
- **Novos (7 dias)**: Filter = Data Primeiro Acesso > 7 days ago

### 4. Obter Database ID

1. Abra o database no Notion
2. Copie a URL: `https://notion.so/workspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...`
3. O ID é: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (32 caracteres)

### 5. Adicionar ao .env

```bash
# No arquivo .env
NOTION_USERS_DB_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 🧪 Testar Persistência

Após configurar, teste com:

```python
python3 -c "
from src.onboarding.persistence import get_persistence
p = get_persistence()
print('Persistência habilitada:', p.is_enabled())
print('Teste:', p.mark_onboarding_complete('Teste', onboarding_type='básico'))
"
```

## 🔄 Comportamento

### Primeiro Acesso (Usuário Novo):
1. Bot verifica Notion → Não encontra registro
2. `is_first_time_user()` retorna `True`
3. Bot mostra pergunta de tutorial
4. Usuário responde "sim" ou "não"
5. Bot salva no Notion com `Onboarding Completo = ✅`

### Próximos Acessos (Usuário Antigo):
1. Bot verifica Notion → Encontra registro com `Onboarding Completo = ✅`
2. `is_first_time_user()` retorna `False`
3. Bot NÃO mostra pergunta de tutorial
4. Processa comando normalmente

### Após Reinicialização:
1. Bot inicia → Cache em memória vazio
2. Usuário envia mensagem
3. Bot busca no Notion → Encontra registro
4. Comportamento correto (não repete onboarding)

## ⚙️ Opcional: Fallback sem Persistência

Se `NOTION_USERS_DB_ID` não estiver configurado:
- Bot funciona normalmente
- Usa cache em memória (temporário)
- ⚠️ Estado é perdido ao reiniciar
- Logs mostram: "Persistência desabilitada - usando cache em memória"

## 📊 Exemplo de Registro:

```
Nome: Estevao Antunes
Telefone: +5511987654321
Onboarding Completo: ✅
Data Primeiro Acesso: 2025-10-17
Data Último Acesso: 2025-10-17
Tipo Onboarding: básico
```

## 🔍 Troubleshooting

### "Persistência desabilitada"
- Verifique se `NOTION_USERS_DB_ID` está no `.env`
- Confirme que o ID tem exatamente 32 caracteres
- Reinicie o bot após adicionar

### "Erro ao salvar onboarding"
- Verifique permissões do token Notion
- Confirme que as properties existem com os nomes corretos
- Verifique tipos das properties (Title, Checkbox, Date, Select)

### "Bot não lembra usuários antigos"
- Confirme que registros existem no Notion
- Verifique se `Onboarding Completo` está marcado (✅)
- Confirme que nome do usuário está exatamente igual
