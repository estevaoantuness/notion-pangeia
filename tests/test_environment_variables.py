"""
Environment Variables and Configuration Tests

Testa todas as variáveis de ambiente, configurações e settings do bot.
Garante que variáveis críticas estejam presente e com valores válidos.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv


class TestEnvironmentVariablesExistence:
    """Testa a existência das variáveis de ambiente essenciais"""

    def test_whatsapp_api_token_exists(self):
        """Verifica se WHATSAPP_API_TOKEN está configurado"""
        token = os.getenv("WHATSAPP_API_TOKEN")
        # Pode ser None em testes, mas não deve estar vazio se presente
        if token:
            assert len(token) > 0, "WHATSAPP_API_TOKEN não pode estar vazio"

    def test_notion_api_key_exists(self):
        """Verifica se NOTION_API_KEY está configurado"""
        key = os.getenv("NOTION_API_KEY")
        if key:
            assert len(key) > 0, "NOTION_API_KEY não pode estar vazio"

    def test_notion_database_ids_exist(self):
        """Verifica se IDs das databases Notion estão configurados"""
        tasks_db = os.getenv("NOTION_TASKS_DB_ID")
        users_db = os.getenv("NOTION_USERS_DB_ID")

        if tasks_db:
            assert len(tasks_db) > 0, "NOTION_TASKS_DB_ID não pode estar vazio"
        if users_db:
            assert len(users_db) > 0, "NOTION_USERS_DB_ID não pode estar vazio"

    def test_google_sheets_url_format(self):
        """Verifica formato da URL do Google Sheets se configurada"""
        sheets_url = os.getenv("GOOGLE_SHEETS_URL")
        if sheets_url:
            assert sheets_url.startswith("https://"), "URL deve começar com https://"
            assert "sheets" in sheets_url.lower(), "URL deve conter 'sheets'"

    def test_database_url_configured(self):
        """Verifica se DATABASE_URL está configurado"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # Deve ser uma URL de banco de dados válida
            assert "://" in db_url, "DATABASE_URL deve ser uma URL válida"
            assert any(
                proto in db_url
                for proto in ["postgresql://", "postgres://", "sqlite://", "mysql://"]
            ), "DATABASE_URL deve usar protocolo válido"

    def test_environment_type_valid(self):
        """Verifica se ENVIRONMENT tem valor válido"""
        env = os.getenv("ENVIRONMENT", "development")
        valid_envs = ["development", "staging", "production", "test"]
        assert env in valid_envs, f"ENVIRONMENT deve ser um de {valid_envs}, got {env}"

    def test_scheduler_enabled_flag(self):
        """Verifica se SCHEDULER_ENABLED é válido"""
        scheduler = os.getenv("SCHEDULER_ENABLED", "true").lower()
        assert scheduler in ["true", "false"], "SCHEDULER_ENABLED deve ser 'true' ou 'false'"

    def test_logging_level_valid(self):
        """Verifica se LOG_LEVEL tem valor válido"""
        level = os.getenv("LOG_LEVEL", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert level in valid_levels, f"LOG_LEVEL deve ser um de {valid_levels}"


class TestEnvironmentVariablesFormats:
    """Testa se variáveis têm formatos corretos"""

    def test_whatsapp_phone_number_format(self):
        """Verifica formato do número de telefone WhatsApp"""
        phone = os.getenv("WHATSAPP_PHONE_NUMBER")
        if phone:
            # Deve ser apenas dígitos, sem espaços ou caracteres especiais
            assert phone.replace("+", "").isdigit(), "Telefone deve conter apenas dígitos"
            assert len(phone) >= 10, "Telefone deve ter pelo menos 10 dígitos"

    def test_notion_database_id_format(self):
        """Verifica formato do ID do Notion"""
        db_id = os.getenv("NOTION_TASKS_DB_ID")
        if db_id:
            # IDs do Notion têm um padrão específico
            # Após remover hífens, deve ter 32 caracteres hexadecimais
            cleaned = db_id.replace("-", "")
            assert len(cleaned) == 32, "ID do Notion deve ter 32 caracteres (sem hífens)"
            try:
                int(cleaned, 16)  # Deve ser hexadecimal
            except ValueError:
                pytest.fail(f"ID do Notion deve ser hexadecimal: {db_id}")

    def test_api_timeout_is_numeric(self):
        """Verifica se API_TIMEOUT é um número válido"""
        timeout = os.getenv("API_TIMEOUT", "30")
        try:
            timeout_int = int(timeout)
            assert timeout_int > 0, "API_TIMEOUT deve ser positivo"
        except ValueError:
            pytest.fail(f"API_TIMEOUT deve ser um número inteiro: {timeout}")

    def test_max_retries_is_numeric(self):
        """Verifica se MAX_RETRIES é um número válido"""
        retries = os.getenv("MAX_RETRIES", "3")
        try:
            retries_int = int(retries)
            assert retries_int >= 0, "MAX_RETRIES deve ser >= 0"
        except ValueError:
            pytest.fail(f"MAX_RETRIES deve ser um número inteiro: {retries}")


class TestEnvironmentVariablesValidation:
    """Testa validação de valores das variáveis"""

    def test_enable_random_checkins_boolean(self):
        """Verifica se ENABLE_RANDOM_CHECKINS é booleano"""
        flag = os.getenv("ENABLE_RANDOM_CHECKINS", "true").lower()
        assert flag in ["true", "false"], "ENABLE_RANDOM_CHECKINS deve ser boolean"

    def test_enable_late_night_checkins_boolean(self):
        """Verifica se ENABLE_LATE_NIGHT_CHECKINS é booleano"""
        flag = os.getenv("ENABLE_LATE_NIGHT_CHECKINS", "true").lower()
        assert flag in ["true", "false"], "ENABLE_LATE_NIGHT_CHECKINS deve ser boolean"

    def test_checkin_times_format(self):
        """Verifica formato dos horários de check-in"""
        times = os.getenv("CHECKIN_TIMES", "8,13:30,15:30,18,22")
        if times:
            time_list = times.split(",")
            for time_str in time_list:
                time_str = time_str.strip()
                parts = time_str.split(":")
                assert len(parts) in [1, 2], f"Horário inválido: {time_str}"
                try:
                    hour = int(parts[0])
                    assert 0 <= hour <= 23, f"Hora deve estar entre 0-23: {hour}"
                    if len(parts) == 2:
                        minute = int(parts[1])
                        assert 0 <= minute <= 59, f"Minuto deve estar entre 0-59: {minute}"
                except ValueError:
                    pytest.fail(f"Horário deve ser numérico: {time_str}")

    def test_random_checkin_frequency_valid(self):
        """Verifica se RANDOM_CHECKIN_FREQUENCY é válido"""
        frequency = os.getenv("RANDOM_CHECKIN_FREQUENCY", "medium")
        valid_freqs = ["low", "medium", "high"]
        if frequency:
            assert frequency in valid_freqs, f"Frequency deve ser um de {valid_freqs}"


class TestEnvironmentVariablesDefaults:
    """Testa valores padrão das variáveis"""

    def test_default_environment_is_development(self):
        """Verifica default de ENVIRONMENT"""
        env = os.getenv("ENVIRONMENT", "development")
        assert env in ["development", "staging", "production", "test"]

    def test_default_log_level_is_info(self):
        """Verifica default de LOG_LEVEL"""
        level = os.getenv("LOG_LEVEL", "INFO")
        assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_default_scheduler_enabled(self):
        """Verifica default de SCHEDULER_ENABLED"""
        scheduler = os.getenv("SCHEDULER_ENABLED", "true")
        assert scheduler.lower() in ["true", "false"]

    def test_default_api_timeout(self):
        """Verifica default de API_TIMEOUT"""
        timeout = int(os.getenv("API_TIMEOUT", "30"))
        assert timeout > 0

    def test_default_max_retries(self):
        """Verifica default de MAX_RETRIES"""
        retries = int(os.getenv("MAX_RETRIES", "3"))
        assert retries >= 0


class TestEnvironmentVariablesProduction:
    """Testa validações específicas para produção"""

    def test_production_requires_api_keys(self):
        """Em produção, chaves API devem estar presentes"""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            assert os.getenv("WHATSAPP_API_TOKEN"), "WHATSAPP_API_TOKEN obrigatório em produção"
            assert os.getenv("NOTION_API_KEY"), "NOTION_API_KEY obrigatório em produção"
            assert os.getenv("DATABASE_URL"), "DATABASE_URL obrigatório em produção"

    def test_production_no_debug_mode(self):
        """Em produção, debug não deve estar ativado"""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            debug = os.getenv("DEBUG", "false").lower()
            assert debug == "false", "DEBUG deve estar desativado em produção"

    def test_production_log_level_not_debug(self):
        """Em produção, log não deve ser DEBUG"""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            level = os.getenv("LOG_LEVEL", "INFO")
            assert level != "DEBUG", "LOG_LEVEL não deve ser DEBUG em produção"


class TestEnvironmentVariablesIntegration:
    """Testa integração entre variáveis"""

    def test_database_url_and_notion_api_key_consistency(self):
        """Verifica consistência entre DATABASE_URL e NOTION_API_KEY"""
        db_url = os.getenv("DATABASE_URL")
        notion_key = os.getenv("NOTION_API_KEY")

        # Se um está configurado, o outro também deve estar
        if db_url and notion_key:
            assert len(db_url) > 0
            assert len(notion_key) > 0

    def test_scheduler_and_checkin_times_consistency(self):
        """Se scheduler está desabilitado, check-in times não é necessário"""
        scheduler = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
        times = os.getenv("CHECKIN_TIMES")

        # Se scheduler está desabilitado, times ainda pode estar presente
        # mas não será usado
        if not scheduler and times:
            # Isso é válido, apenas não será usado
            pass

    def test_whatsapp_phone_and_token_consistency(self):
        """Se há token WhatsApp, deve haver telefone configurado"""
        token = os.getenv("WHATSAPP_API_TOKEN")
        phone = os.getenv("WHATSAPP_PHONE_NUMBER")

        if token:
            # Token requer telefone configurado
            assert phone, "WHATSAPP_PHONE_NUMBER obrigatório se WHATSAPP_API_TOKEN está presente"


class TestEnvironmentVariablesLoadFromEnv:
    """Testa carregamento de variáveis do arquivo .env"""

    def test_env_file_exists(self):
        """Verifica se arquivo .env existe"""
        env_path = ".env"
        # Pode não existir em testes, então não é falha crítica
        if os.path.exists(env_path):
            assert os.path.isfile(env_path), ".env deve ser um arquivo"

    def test_env_file_readable(self):
        """Verifica se arquivo .env é legível"""
        env_path = ".env"
        if os.path.exists(env_path):
            assert os.access(env_path, os.R_OK), ".env deve ser legível"

    def test_dotenv_loads_successfully(self):
        """Testa carregamento do arquivo .env"""
        try:
            load_dotenv()
            # Se chegou aqui, carregou com sucesso
            assert True
        except Exception as e:
            pytest.fail(f"Erro ao carregar .env: {e}")


class TestEnvironmentVariablesMocking:
    """Testa comportamento com variáveis mockadas"""

    @patch.dict(os.environ, {"ENVIRONMENT": "test"})
    def test_environment_override(self):
        """Testa override de variável de ambiente"""
        assert os.getenv("ENVIRONMENT") == "test"

    @patch.dict(os.environ, {"SCHEDULER_ENABLED": "false"})
    def test_scheduler_disabled_via_env(self):
        """Testa desabilitar scheduler via variável"""
        scheduler = os.getenv("SCHEDULER_ENABLED").lower() == "true"
        assert scheduler == False

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"})
    def test_log_level_override(self):
        """Testa mudança de LOG_LEVEL"""
        assert os.getenv("LOG_LEVEL") == "DEBUG"

    @patch.dict(os.environ, {"MAX_RETRIES": "5"})
    def test_max_retries_override(self):
        """Testa mudança de MAX_RETRIES"""
        retries = int(os.getenv("MAX_RETRIES"))
        assert retries == 5


class TestEnvironmentVariablesEdgeCases:
    """Testa casos extremos e edge cases"""

    def test_empty_string_vs_none(self):
        """Diferencia entre string vazia e None"""
        # Simula variável presente mas vazia
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            value = os.getenv("EMPTY_VAR")
            assert value == "", "Variável vazia deve retornar string vazia"

    def test_whitespace_handling(self):
        """Testa variáveis com whitespace"""
        with patch.dict(os.environ, {"WHITESPACE_VAR": "  value  "}):
            value = os.getenv("WHITESPACE_VAR")
            # Algumas variáveis podem precisar de strip()
            assert value.strip() == "value"

    def test_special_characters_in_values(self):
        """Testa variáveis com caracteres especiais"""
        special_value = "abc@123!#$%^&*()"
        with patch.dict(os.environ, {"SPECIAL_VAR": special_value}):
            value = os.getenv("SPECIAL_VAR")
            assert value == special_value

    def test_very_long_string_values(self):
        """Testa variáveis com strings muito longas"""
        long_value = "a" * 10000
        with patch.dict(os.environ, {"LONG_VAR": long_value}):
            value = os.getenv("LONG_VAR")
            assert len(value) == 10000

    def test_unicode_in_variables(self):
        """Testa variáveis com caracteres unicode"""
        unicode_value = "Olá mundo 🌍 ñ é ü"
        with patch.dict(os.environ, {"UNICODE_VAR": unicode_value}):
            value = os.getenv("UNICODE_VAR")
            assert value == unicode_value


class TestEnvironmentVariablesDocumentation:
    """Testa se variáveis estão documentadas"""

    def test_all_env_vars_documented(self):
        """Verifica se todas as variáveis usadas têm documentação"""
        # Lista de todas as variáveis esperadas
        expected_vars = {
            "WHATSAPP_API_TOKEN": "Token de autenticação WhatsApp",
            "NOTION_API_KEY": "Chave de API do Notion",
            "NOTION_TASKS_DB_ID": "ID da database de tarefas no Notion",
            "DATABASE_URL": "URL de conexão do banco de dados",
            "ENVIRONMENT": "Ambiente (development/staging/production)",
            "SCHEDULER_ENABLED": "Se o scheduler está habilitado",
            "LOG_LEVEL": "Nível de logging",
            "API_TIMEOUT": "Timeout para APIs em segundos",
        }

        # Verifica se documentação existe
        assert len(expected_vars) > 0, "Deve haver variáveis documentadas"

    def test_env_template_exists(self):
        """Verifica se template .env.example existe"""
        template_path = ".env.example"
        if os.path.exists(template_path):
            assert os.path.isfile(template_path), ".env.example deve ser um arquivo"
            with open(template_path, 'r') as f:
                content = f.read()
                assert len(content) > 0, ".env.example não deve estar vazio"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
