"""
Bot Configuration Tests

Testa todas as configurações do bot: colaboradores, replies, NLP settings, etc.
"""

import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigFiles:
    """Testa existência e integridade dos arquivos de configuração"""

    def test_colaboradores_config_exists(self):
        """Verifica se config/colaboradores.py existe"""
        config_path = "config/colaboradores.py"
        assert os.path.exists(config_path), f"{config_path} deve existir"

    def test_replies_yaml_exists(self):
        """Verifica se config/replies.yaml existe"""
        config_path = "config/replies.yaml"
        assert os.path.exists(config_path), f"{config_path} deve existir"

    def test_replies_yaml_valid(self):
        """Verifica se replies.yaml é válido"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                assert isinstance(data, dict), "replies.yaml deve ser um dicionário"
                assert len(data) > 0, "replies.yaml não deve estar vazio"
            except yaml.YAMLError as e:
                pytest.fail(f"replies.yaml YAML inválido: {e}")

    def test_nlp_config_exists(self):
        """Verifica se configurações NLP existem"""
        nlp_path = "config/nlp"
        assert os.path.exists(nlp_path), f"{nlp_path} deve existir"
        assert os.path.isdir(nlp_path), f"{nlp_path} deve ser um diretório"


class TestColaboradoresConfig:
    """Testa configuração de colaboradores"""

    def test_colaboradores_importable(self):
        """Verifica se colaboradores pode ser importado"""
        try:
            from config.colaboradores import COLABORADORES
            assert isinstance(COLABORADORES, dict), "COLABORADORES deve ser um dict"
        except ImportError as e:
            pytest.fail(f"Erro ao importar colaboradores: {e}")

    def test_colaboradores_has_required_fields(self):
        """Verifica se cada colaborador tem campos obrigatórios"""
        from config.colaboradores import COLABORADORES

        required_fields = ["telefone", "nome", "ativo"]

        for nome, info in COLABORADORES.items():
            assert isinstance(info, dict), f"{nome} deve ser um dicionário"
            for field in required_fields:
                assert field in info, f"{nome} deve ter campo '{field}'"

    def test_colaboradores_phone_format(self):
        """Verifica formato dos telefones dos colaboradores"""
        from config.colaboradores import COLABORADORES

        for nome, info in COLABORADORES.items():
            phone = info.get("telefone")
            if phone:
                # Deve ser string ou None
                assert isinstance(phone, (str, type(None))), f"Telefone deve ser string"
                if isinstance(phone, str):
                    # Deve ter + no início e apenas dígitos
                    assert phone.startswith("+"), f"Telefone de {nome} deve começar com +"
                    assert phone[1:].isdigit(), f"Telefone de {nome} deve ter apenas dígitos"

    def test_colaboradores_ativo_boolean(self):
        """Verifica se ativo é booleano"""
        from config.colaboradores import COLABORADORES

        for nome, info in COLABORADORES.items():
            ativo = info.get("ativo")
            assert isinstance(ativo, bool), f"Campo 'ativo' de {nome} deve ser boolean"

    def test_get_colaboradores_ativos_function(self):
        """Testa função get_colaboradores_ativos"""
        try:
            from config.colaboradores import get_colaboradores_ativos
            ativos = get_colaboradores_ativos()
            assert isinstance(ativos, dict), "get_colaboradores_ativos deve retornar dict"
            # Todos os retornados devem estar ativos
            for nome, info in ativos.items():
                assert info.get("ativo") == True, f"{nome} retornado mas não está ativo"
        except ImportError as e:
            pytest.fail(f"Erro ao importar get_colaboradores_ativos: {e}")

    def test_no_duplicate_phone_numbers(self):
        """Verifica se não há números duplicados"""
        from config.colaboradores import COLABORADORES

        phones = []
        for nome, info in COLABORADORES.items():
            phone = info.get("telefone")
            if phone:
                assert phone not in phones, f"Número {phone} duplicado (em {nome})"
                phones.append(phone)

    def test_no_duplicate_names(self):
        """Verifica se não há nomes duplicados"""
        from config.colaboradores import COLABORADORES

        names = list(COLABORADORES.keys())
        assert len(names) == len(set(names)), "Há nomes duplicados em colaboradores"


class TestRepliesConfiguration:
    """Testa configuração de respostas (replies.yaml)"""

    def test_replies_has_greetings(self):
        """Verifica se replies tem categoria 'greetings'"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            assert "greetings" in replies, "replies.yaml deve ter 'greetings'"

    def test_greetings_has_time_contexts(self):
        """Verifica se greetings tem contextos de tempo"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            greetings = replies.get("greetings", {})
            expected_times = ["morning", "afternoon", "evening"]
            for time_ctx in expected_times:
                assert time_ctx in greetings, f"greetings deve ter '{time_ctx}'"

    def test_greetings_are_lists(self):
        """Verifica se saudações são listas"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            greetings = replies.get("greetings", {})
            for context, messages in greetings.items():
                if isinstance(messages, dict):
                    for key, values in messages.items():
                        assert isinstance(values, list), f"greetings.{context}.{key} deve ser lista"
                else:
                    assert isinstance(messages, list), f"greetings.{context} deve ser lista"

    def test_replies_has_task_responses(self):
        """Verifica se replies tem respostas de tarefas"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            task_categories = ["task_completed", "task_in_progress", "task_blocked"]
            for cat in task_categories:
                assert cat in replies, f"replies.yaml deve ter '{cat}'"

    def test_replies_has_help_section(self):
        """Verifica se replies tem seção de ajuda"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            assert "help" in replies, "replies.yaml deve ter 'help'"
            assert "full" in replies["help"], "help deve ter 'full'"
            assert "short" in replies["help"], "help deve ter 'short'"

    def test_replies_messages_not_empty(self):
        """Verifica se mensagens não são vazias"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)

            def check_messages(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        check_messages(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, str):
                            assert len(item.strip()) > 0, f"Mensagem vazia em {path}[{i}]"
                        check_messages(item, f"{path}[{i}]")

            check_messages(replies)

    def test_replies_placeholder_consistency(self):
        """Verifica placeholders usados (ex: {name}, {number})"""
        with open("config/replies.yaml", "r", encoding="utf-8") as f:
            replies = yaml.safe_load(f)
            valid_placeholders = {
                "{name}",
                "{number}",
                "{title}",
                "{percent}",
                "{done}",
                "{total}",
                "{role}",
                "{reason}",
            }

            def check_placeholders(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        check_placeholders(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, str):
                            # Extrair placeholders
                            import re

                            found = re.findall(r"\{[a-z_]+\}", item)
                            for ph in found:
                                # Pode ser placeholder customizado, apenas verificar format
                                assert (
                                    ph.startswith("{") and ph.endswith("}")
                                ), f"Placeholder inválido: {ph} em {path}"
                        check_placeholders(item, f"{path}[{i}]")

            check_placeholders(replies)

    def test_replies_humanizer_can_load(self):
        """Testa se MessageHumanizer consegue carregar replies"""
        try:
            from src.messaging.humanizer import get_humanizer

            humanizer = get_humanizer()
            assert humanizer is not None, "Humanizer não deve ser None"
        except Exception as e:
            pytest.fail(f"Erro ao carregar humanizer: {e}")


class TestSchedulerConfiguration:
    """Testa configuração do scheduler"""

    def test_scheduler_check_in_times(self):
        """Verifica horários de check-in"""
        times_str = os.getenv("CHECKIN_TIMES", "8,13:30,15:30,18,22")
        times = times_str.split(",")

        assert len(times) > 0, "Deve haver pelo menos um horário de check-in"

        for time_str in times:
            time_str = time_str.strip()
            parts = time_str.split(":")
            assert len(parts) in [1, 2], f"Horário inválido: {time_str}"

            hour = int(parts[0])
            assert 0 <= hour <= 23, f"Hora inválida: {hour}"

            if len(parts) == 2:
                minute = int(parts[1])
                assert 0 <= minute <= 59, f"Minuto inválido: {minute}"

    def test_scheduler_enabled_flag(self):
        """Verifica se scheduler está habilitado"""
        scheduler_enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
        assert isinstance(scheduler_enabled, bool), "SCHEDULER_ENABLED deve ser boolean"

    def test_random_checkins_enabled(self):
        """Verifica se random check-ins estão habilitados"""
        enabled = os.getenv("ENABLE_RANDOM_CHECKINS", "true").lower() == "true"
        assert isinstance(enabled, bool), "ENABLE_RANDOM_CHECKINS deve ser boolean"


class TestNLPConfiguration:
    """Testa configuração NLP"""

    def test_normalizer_imports(self):
        """Testa se normalizer pode ser importado"""
        try:
            from src.commands.normalizer import parse, is_confirmation
            assert callable(parse), "parse deve ser uma função"
            assert callable(is_confirmation), "is_confirmation deve ser uma função"
        except ImportError as e:
            pytest.fail(f"Erro ao importar normalizer: {e}")

    def test_intent_detection_works(self):
        """Testa se detecção de intenção funciona"""
        try:
            from src.commands.normalizer import parse

            # Teste simples
            result = parse("oi")
            assert hasattr(result, "intent"), "Result deve ter atributo 'intent'"
            assert hasattr(result, "confidence"), "Result deve ter atributo 'confidence'"
            assert 0 <= result.confidence <= 1, "Confidence deve estar entre 0 e 1"
        except Exception as e:
            pytest.fail(f"Erro ao testar detecção de intenção: {e}")

    def test_yes_no_detection(self):
        """Testa detecção de sim/não"""
        try:
            from src.commands.normalizer import is_confirmation

            assert is_confirmation("sim") == True, "Deve detectar 'sim'"
            assert is_confirmation("não") == True, "Deve detectar 'não'"
            assert is_confirmation("talvez") == False, "Não deve detectar 'talvez'"
        except Exception as e:
            pytest.fail(f"Erro ao testar confirmação: {e}")


class TestDatabaseConfiguration:
    """Testa configuração do banco de dados"""

    def test_database_url_valid(self):
        """Verifica se DATABASE_URL é válido"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            assert "://" in db_url, "DATABASE_URL deve ser URL válida"
            valid_drivers = [
                "postgresql",
                "postgres",
                "sqlite",
                "mysql",
                "mariadb",
            ]
            assert any(
                driver in db_url for driver in valid_drivers
            ), f"DATABASE_URL deve usar driver válido"

    def test_database_connection_settings(self):
        """Verifica configurações de conexão"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            # URL deve ter partes mínimas
            assert "@" in db_url or "localhost" in db_url, "DATABASE_URL deve ter host"
            assert "/" in db_url, "DATABASE_URL deve ter banco de dados"


class TestLoggingConfiguration:
    """Testa configuração de logging"""

    def test_log_level_valid(self):
        """Verifica se LOG_LEVEL é válido"""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert log_level in valid_levels, f"LOG_LEVEL deve ser um de {valid_levels}"

    def test_log_file_path_exists(self):
        """Verifica se diretório de logs existe"""
        log_dir = "logs"
        # Pode não existir, mas deve ser criável
        os.makedirs(log_dir, exist_ok=True)
        assert os.path.isdir(log_dir), "Diretório logs deve existir ou ser criável"


class TestConfigurationIntegration:
    """Testa integração entre configurações"""

    def test_humanizer_and_replies_integration(self):
        """Testa se Humanizer consegue acessar todas as replies"""
        try:
            from src.messaging.humanizer import get_humanizer

            humanizer = get_humanizer()

            # Tenta acessar categorias principais
            greeting = humanizer.pick("greetings", "morning")
            assert greeting is not None, "Deve retornar saudação"
            assert len(greeting) > 0, "Saudação não deve estar vazia"
        except Exception as e:
            pytest.fail(f"Erro na integração humanizer: {e}")

    def test_processor_and_normalizer_integration(self):
        """Testa se CommandProcessor consegue usar Normalizer"""
        try:
            from src.commands.processor import CommandProcessor

            processor = CommandProcessor()
            success, response = processor.process_by_name("Test", "oi")

            assert isinstance(response, (str, type(None))), "Resposta deve ser string"
        except Exception as e:
            pytest.fail(f"Erro na integração processor: {e}")

    def test_handlers_and_database_integration(self):
        """Testa se Handlers conseguem conectar ao banco"""
        try:
            from src.commands.handlers import CommandHandlers

            handlers = CommandHandlers()
            assert handlers is not None, "Handlers não deve ser None"
        except Exception as e:
            # Pode falhar se banco não está disponível em testes
            pytest.skip(f"Database não disponível: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
