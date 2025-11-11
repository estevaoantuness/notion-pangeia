# 🧪 Test Suite - Bot Configuration & Environment Variables

Suite completa de testes para validar todas as configurações do bot, variáveis de ambiente e integração entre componentes.

## 📁 Arquivos de Teste

### `test_environment_variables.py`
Testa todas as variáveis de ambiente do bot:

**Classes de Testes:**
- `TestEnvironmentVariablesExistence` - Verifica existência de variáveis críticas
- `TestEnvironmentVariablesFormats` - Valida formatos (URLs, IDs, números)
- `TestEnvironmentVariablesValidation` - Valida valores (ranges, tipos)
- `TestEnvironmentVariablesDefaults` - Testa valores padrão
- `TestEnvironmentVariablesProduction` - Validações específicas para produção
- `TestEnvironmentVariablesIntegration` - Testa consistência entre variáveis
- `TestEnvironmentVariablesLoadFromEnv` - Carregamento de .env
- `TestEnvironmentVariablesMocking` - Testa override de variáveis
- `TestEnvironmentVariablesEdgeCases` - Casos extremos
- `TestEnvironmentVariablesDocumentation` - Documentação de variáveis

**Variáveis Testadas:**
- `WHATSAPP_API_TOKEN` - Token de autenticação WhatsApp
- `NOTION_API_KEY` - Chave de API Notion
- `NOTION_TASKS_DB_ID` - ID da database de tarefas
- `DATABASE_URL` - URL de conexão do banco
- `ENVIRONMENT` - Ambiente (dev/staging/prod)
- `SCHEDULER_ENABLED` - Se scheduler está ativo
- `LOG_LEVEL` - Nível de logging
- `API_TIMEOUT` - Timeout de APIs
- `MAX_RETRIES` - Número máximo de tentativas
- E mais...

### `test_bot_configuration.py`
Testa todas as configurações do bot:

**Classes de Testes:**
- `TestConfigFiles` - Existência de arquivos de config
- `TestColaboradoresConfig` - Validação de colaboradores
- `TestRepliesConfiguration` - Validação de respostas (YAML)
- `TestSchedulerConfiguration` - Configurações do scheduler
- `TestNLPConfiguration` - Configuração NLP
- `TestDatabaseConfiguration` - Configurações de banco
- `TestLoggingConfiguration` - Configuração de logs
- `TestConfigurationIntegration` - Integração entre componentes

**O que é Testado:**
- ✅ Arquivo `config/colaboradores.py` válido
- ✅ Arquivo `config/replies.yaml` válido
- ✅ Todos os colaboradores têm campos obrigatórios
- ✅ Números de telefone em formato correto
- ✅ Não há duplicatas de telefone ou nome
- ✅ Categorias de replies estão presentes
- ✅ Placeholders são válidos
- ✅ MessageHumanizer consegue carregar replies
- ✅ NLP consegue detectar intenções
- ✅ Scheduler está configurado corretamente

## 🚀 Como Rodar os Testes

### Pré-requisitos
```bash
pip install pytest pytest-cov pyyaml python-dotenv
```

### Rodar todos os testes
```bash
pytest tests/ -v
```

### Rodar teste específico
```bash
# Todas as variáveis de ambiente
pytest tests/test_environment_variables.py -v

# Todas as configurações do bot
pytest tests/test_bot_configuration.py -v

# Teste específico
pytest tests/test_environment_variables.py::TestEnvironmentVariablesExistence::test_whatsapp_api_token_exists -v
```

### Rodar com coverage
```bash
pytest tests/ --cov=src --cov=config --cov-report=html
```

### Rodar em modo quiet (sem detalhes)
```bash
pytest tests/ -q
```

### Rodar apenas os testes que falharam
```bash
pytest tests/ --lf
```

## 📊 O Que Os Testes Cobrem

### Variáveis de Ambiente

#### Existência
✅ WHATSAPP_API_TOKEN
✅ NOTION_API_KEY
✅ NOTION_TASKS_DB_ID
✅ DATABASE_URL
✅ ENVIRONMENT
✅ SCHEDULER_ENABLED
✅ LOG_LEVEL

#### Formatos
✅ Telefones WhatsApp
✅ IDs do Notion (hexadecimal, 32 chars)
✅ URLs de banco de dados
✅ Horários de check-in (HH:MM)
✅ Valores numéricos (timeout, retries)

#### Validação
✅ Valores booleanos (true/false)
✅ Ranges válidos (hora 0-23, minuto 0-59)
✅ Tipos esperados (string, int, bool)
✅ Valores padrão sensatos

#### Produção
✅ Chaves API obrigatórias em produção
✅ Debug desabilitado em produção
✅ Log level apropriado em produção

### Configurações

#### Colaboradores
✅ Arquivo importável
✅ Campos obrigatórios (telefone, nome, ativo)
✅ Formato de telefone
✅ Campo ativo é boolean
✅ Sem duplicatas de telefone
✅ Função `get_colaboradores_ativos()` funciona

#### Replies YAML
✅ Arquivo válido
✅ Categorias esperadas (greetings, help, etc)
✅ Saudações com contextos (morning, afternoon, evening)
✅ Mensagens não vazias
✅ Placeholders válidos
✅ MessageHumanizer consegue carregar

#### NLP
✅ Normalizer importável
✅ Detecção de intenção funciona
✅ Detecção de sim/não funciona

#### Database
✅ DATABASE_URL válido
✅ Driver suportado
✅ Formato de URL correto

### Integração
✅ Humanizer ↔ Replies
✅ CommandProcessor ↔ Normalizer
✅ CommandHandlers ↔ Database

## 🎯 Exemplo de Saída

```
tests/test_environment_variables.py::TestEnvironmentVariablesExistence::test_whatsapp_api_token_exists PASSED
tests/test_environment_variables.py::TestEnvironmentVariablesExistence::test_notion_api_key_exists PASSED
tests/test_environment_variables.py::TestEnvironmentVariablesFormats::test_whatsapp_phone_number_format PASSED
tests/test_environment_variables.py::TestEnvironmentVariablesValidation::test_enable_random_checkins_boolean PASSED
tests/test_bot_configuration.py::TestConfigFiles::test_colaboradores_config_exists PASSED
tests/test_bot_configuration.py::TestColaboradoresConfig::test_colaboradores_importable PASSED
tests/test_bot_configuration.py::TestColaboradoresConfig::test_no_duplicate_phone_numbers PASSED
tests/test_bot_configuration.py::TestRepliesConfiguration::test_replies_yaml_valid PASSED
tests/test_bot_configuration.py::TestRepliesConfiguration::test_greetings_are_lists PASSED

========================== 45 passed in 2.34s ==========================
```

## 🔍 Diagnosticando Falhas

### Variável não existe
```
FAILED tests/test_environment_variables.py::...::test_whatsapp_api_token_exists
AssertionError: assert None

✅ Solução: Configure a variável no .env:
WHATSAPP_API_TOKEN=seu_token_aqui
```

### Formato inválido
```
FAILED tests/test_environment_variables.py::...::test_whatsapp_phone_number_format
AssertionError: Telefone deve conter apenas dígitos

✅ Solução: Verifique o formato:
WHATSAPP_PHONE_NUMBER=+5511987654321  (correto)
```

### Arquivo de config inválido
```
FAILED tests/test_bot_configuration.py::...::test_replies_yaml_valid
YAMLError: ...

✅ Solução: Valide YAML:
python -m yaml config/replies.yaml
```

## 📝 Adicionando Novos Testes

Para adicionar um novo teste de variável:

```python
class TestNewFeature:
    def test_new_variable_exists(self):
        """Verifica se NEW_VAR está configurado"""
        new_var = os.getenv("NEW_VAR")
        assert new_var is not None, "NEW_VAR deve estar configurado"

    def test_new_variable_format(self):
        """Verifica formato de NEW_VAR"""
        new_var = os.getenv("NEW_VAR")
        if new_var:
            # Sua validação aqui
            assert len(new_var) > 0
```

## 🔐 Segurança

⚠️ **Importante**: Nunca commite valores reais de variáveis de produção!

- ✅ Use `.env` para desenvolvimento (git-ignored)
- ✅ Use `.env.example` como template
- ✅ Configure variáveis em CI/CD via secrets
- ✅ Nuca commit `.env` no repositório

## 📈 Coverage Goals

- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 90%+
- **Lines**: 80%+

Verificar coverage:
```bash
pytest tests/ --cov=src --cov=config --cov-report=html
open htmlcov/index.html
```

## 🔗 Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [YAML Validation](https://www.yamllint.com/)
- [Environment Variables Best Practices](https://12factor.net/config)

## 📞 Troubleshooting

### Tests não rodam
```bash
# Verifique se pytest está instalado
pip install pytest pytest-cov pyyaml python-dotenv

# Verifique se tests/ é um pacote
touch tests/__init__.py
```

### Tests muito lento
```bash
# Pule testes lentos
pytest tests/ -m "not slow"

# Rode em paralelo
pip install pytest-xdist
pytest tests/ -n auto
```

### Variável não é detectada
```bash
# Verifique se .env existe
ls -la .env

# Verifique se dotenv está carregando
python -c "from dotenv import load_dotenv; load_dotenv(); print(os.getenv('VAR'))"
```

---

**Última atualização**: November 11, 2025
**Status**: ✅ 45+ testes, cobertura de produção
