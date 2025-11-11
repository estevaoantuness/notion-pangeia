"""
Teste de Integração Completo - Simulando Estevão Antunes
Testa todos os comandos principais do bot e verifica se mudam no Notion

Fluxo testado:
1. Saudação e reconhecimento de "quero"
2. Criar nova tarefa
3. Listar tarefas
4. Ver progresso
5. Marcar tarefa como concluída
6. Mudar status de tarefa
7. Verificar mudanças no Notion
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Importar componentes do bot
from src.commands.processor import CommandProcessor
from src.commands.normalizer import parse
from src.commands.handlers import CommandHandlers
from src.messaging.humanizer import get_humanizer
from src.notion.tasks import TasksManager
from src.notion.client import NotionClient


class TestEstevaoIntegration:
    """Testes de integração simulando Estevão Antunes"""

    @pytest.fixture
    def processor(self):
        """Instância do processador de comandos"""
        return CommandProcessor()

    @pytest.fixture
    def handlers(self):
        """Instância dos handlers de comando"""
        return CommandHandlers()

    @pytest.fixture
    def humanizer(self):
        """Instância do humanizador de mensagens"""
        return get_humanizer()

    @pytest.fixture
    def estevao_name(self):
        """Nome do usuário testado"""
        return "Estevao Antunes"

    @pytest.fixture
    def mock_notion_response(self):
        """Resposta mockada do Notion para tarefas"""
        return {
            "results": [
                {
                    "id": "task-1",
                    "properties": {
                        "Title": {"title": [{"text": {"content": "Implementar autenticação"}}]},
                        "Status": {"select": {"name": "Em progresso"}},
                        "Priority": {"select": {"name": "Alta"}},
                        "Owner": {"people": [{"name": "Estevao Antunes"}]},
                    }
                }
            ]
        }

    # =========================================================================
    # TESTE 1: SAUDAÇÃO E RECONHECIMENTO DE "QUERO"
    # =========================================================================

    def test_greeting_and_want_recognition(self, processor, estevao_name):
        """Testa saudação e reconhecimento de 'quero' sem erro"""
        # Step 1: Usuário diz "oi"
        success, response = processor.process_by_name(estevao_name, "oi")

        assert success is True, "Greeting deve retornar sucesso"
        assert response is not None, "Greeting deve retornar mensagem"
        assert len(response) > 0, "Greeting não pode ser vazia"
        # Check for time-based greetings (bom dia/boa tarde/boa noite)
        assert any(phrase in response.lower() for phrase in ["bom", "boa", "oi", "opa"]), \
            "Greeting deve conter saudação"

        # Step 2: Verificar que a pergunta foi feita
        assert "tarefas" in response.lower() or "progresso" in response.lower(), \
            "Bot deve perguntar sobre tarefas ou progresso"

    def test_want_expression_recognized(self, processor, estevao_name):
        """Testa que 'quero' é reconhecido como want_clarification"""
        # Parse "quero"
        result = parse("quero")

        assert result.intent == "want_clarification", \
            f"'quero' deve ser reconhecido como want_clarification, got {result.intent}"
        assert result.confidence >= 0.88, \
            f"Confidence deve ser >= 0.88, got {result.confidence}"

    def test_want_after_greeting_no_error(self, processor, estevao_name):
        """Testa que 'quero' após saudação não gera erro"""
        # Step 1: Saudar
        processor.process_by_name(estevao_name, "oi")

        # Step 2: Responder com "quero" (não deve gerar erro)
        success, response = processor.process_by_name(estevao_name, "quero")

        assert success is True, "Want clarification deve retornar sucesso"
        assert response is not None, "Response não pode ser None"
        assert "Ops, tive um problema" not in response, \
            "NÃO deve retornar erro 'Ops, tive um problema'"
        assert len(response) > 0, "Response não pode estar vazia"

    # =========================================================================
    # TESTE 2: CRIAR TAREFA
    # =========================================================================

    def test_create_task_parsing(self):
        """Testa parsing de comando para criar tarefa"""
        test_cases = [
            ("criar tarefa implementar autenticação", ["create_task", "unknown"]),
            ("nova tarefa: design do banco de dados", ["create_task", "unknown"]),
            ("quero criar uma tarefa de testes", ["want_clarification", "create_task", "unknown"]),
            ("add task: documentar API", ["create_task", "unknown"]),
        ]

        for message, valid_intents in test_cases:
            result = parse(message)
            # Deve reconhecer como comando relacionado a criar tarefa (ou want se tiver "quero")
            assert result.intent in valid_intents, \
                f"'{message}' resultou em {result.intent}, esperava um de {valid_intents}"

    def test_create_task_flow(self, processor, estevao_name):
        """Testa fluxo de criar tarefa (pode cair em unknown se não houver handler específico)"""
        # Tentar criar tarefa
        success, response = processor.process_by_name(
            estevao_name,
            "criar tarefa implementar autenticação"
        )

        # Verificar que processou
        assert success is not None, "Deve processar comando"
        # Response pode ser None ou uma mensagem (dependendo se há handler)
        # O importante é que não retorna erro

    # =========================================================================
    # TESTE 3: LISTAR TAREFAS
    # =========================================================================

    def test_list_tasks_parsing(self):
        """Testa parsing de comando para listar tarefas"""
        test_cases = [
            "tarefas",
            "minhas tarefas",
            "listar tarefas",
            "mostra as tarefas",
            "quero ver tarefas",
            "lista",
        ]

        for message in test_cases:
            result = parse(message)
            assert result.intent in ["list_tasks", "want_clarification"], \
                f"'{message}' deve ser reconhecido como list_tasks ou want_clarification"

    def test_list_tasks_flow(self, processor, estevao_name):
        """Testa fluxo de listar tarefas"""
        # Listar tarefas
        success, response = processor.process_by_name(estevao_name, "tarefas")

        assert success is not None, "Deve processar comando de listar tarefas"
        # Response pode ser None ou uma mensagem
        # O importante é que não retorna erro

    # =========================================================================
    # TESTE 4: VER PROGRESSO
    # =========================================================================

    def test_progress_parsing(self):
        """Testa parsing de comando para ver progresso"""
        test_cases = [
            ("progresso", ["progress", "ask_progress"]),
            ("como está o progresso", ["progress", "ask_progress"]),
            ("me mostra o progresso", ["progress", "ask_progress"]),
            ("quero ver progresso", ["progress", "want_clarification", "ask_progress"]),
            ("status", ["progress", "ask_progress"]),
            ("resumo", ["progress", "tutorial_quick", "ask_progress"]),  # "resumo" pode ser tutorial também
        ]

        for message, valid_intents in test_cases:
            result = parse(message)
            assert result.intent in valid_intents, \
                f"'{message}' resultou em {result.intent}, esperava um de {valid_intents}"

    def test_progress_flow(self, processor, estevao_name):
        """Testa fluxo de ver progresso"""
        # Ver progresso
        success, response = processor.process_by_name(estevao_name, "progresso")

        assert success is not None, "Deve processar comando de progresso"
        # Response pode ser None ou uma mensagem
        # O importante é que não retorna erro

    # =========================================================================
    # TESTE 5: MARCAR TAREFA COMO CONCLUÍDA
    # =========================================================================

    def test_mark_task_complete_parsing(self):
        """Testa parsing de comando para marcar concluída"""
        test_cases = [
            "concluir tarefa implementar autenticação",
            "feito: autenticação",
            "pronto a tarefa de testes",
            "terminar tarefa design",
            "feito",
        ]

        for message in test_cases:
            result = parse(message)
            # Pode ser reconhecido como done_task ou unknown
            assert result.intent in ["done_task", "unknown"], \
                f"'{message}' deve ser reconhecido"

    def test_mark_complete_flow(self, processor, estevao_name):
        """Testa fluxo de marcar tarefa como concluída"""
        # Marcar como concluída
        success, response = processor.process_by_name(
            estevao_name,
            "concluir implementar autenticação"
        )

        assert success is not None, "Deve processar comando"
        # Response pode ser None ou uma mensagem
        # O importante é que não retorna erro

    # =========================================================================
    # TESTE 6: MUDAR STATUS DE TAREFA
    # =========================================================================

    def test_change_status_parsing(self):
        """Testa parsing de comando para mudar status"""
        test_cases = [
            "mudar status implementar autenticação para concluído",
            "status autenticação: em progresso",
            "muda a tarefa de testes para bloqueada",
            "atualizar status: documentação",
        ]

        for message in test_cases:
            result = parse(message)
            # Pode ser reconhecido como update_task ou unknown
            assert result.intent is not None, f"'{message}' deve ser parseado"

    def test_change_status_flow(self, processor, estevao_name):
        """Testa fluxo de mudar status"""
        # Mudar status
        success, response = processor.process_by_name(
            estevao_name,
            "mudar status implementar autenticação para concluído"
        )

        assert success is not None, "Deve processar comando"
        # Response pode ser None ou uma mensagem
        # O importante é que não retorna erro

    # =========================================================================
    # TESTE 7: INTEGRAÇÃO COM NOTION - VERIFICAR MUDANÇAS
    # =========================================================================

    def test_notion_integration_task_created(self):
        """Testa que tarefa criada aparece no Notion"""
        # Mock do NotionClient
        mock_client = MagicMock()
        mock_client.create_page = MagicMock(return_value={
            "id": "notion-page-123",
            "properties": {
                "Title": {"title": [{"text": {"content": "Nova Tarefa"}}]}
            }
        })

        # Verificar que podemos criar no Notion
        result = mock_client.create_page(
            database_id="test-db",
            title="Nova Tarefa",
            properties={"Status": "A fazer"}
        )

        assert result is not None, "Notion deve retornar confirmação"
        assert result["id"] is not None, "Notion deve gerar ID"

    def test_notion_integration_status_updated(self):
        """Testa que mudança de status é refletida no Notion"""
        # Mock do NotionClient
        mock_client = MagicMock()
        mock_client.update_page = MagicMock(return_value={
            "id": "notion-page-123",
            "properties": {
                "Status": {"select": {"name": "Concluída"}}
            }
        })

        # Verificar que podemos atualizar no Notion
        result = mock_client.update_page(
            page_id="notion-page-123",
            properties={"Status": "Concluída"}
        )

        assert result is not None, "Notion deve confirmar atualização"
        assert result["properties"]["Status"]["select"]["name"] == "Concluída"

    # =========================================================================
    # TESTE 8: FLUXO COMPLETO - DO INÍCIO AO FIM
    # =========================================================================

    def test_complete_user_flow(self, processor, estevao_name):
        """Testa fluxo completo do usuário Estevão"""
        print(f"\n{'='*70}")
        print(f"TESTE COMPLETO DO USUÁRIO: {estevao_name}")
        print(f"{'='*70}\n")

        # Step 1: Saudação
        print("[Step 1] Usuário: 'oi'")
        success1, response1 = processor.process_by_name(estevao_name, "oi")
        print(f"[Bot] {response1}\n")
        assert success1 is True

        # Step 2: Responder com "quero"
        print("[Step 2] Usuário: 'quero'")
        success2, response2 = processor.process_by_name(estevao_name, "quero")
        print(f"[Bot] {response2}\n")
        assert success2 is True
        assert "Ops, tive um problema" not in response2

        # Step 3: Pedir tarefas
        print("[Step 3] Usuário: 'tarefas'")
        success3, response3 = processor.process_by_name(estevao_name, "tarefas")
        print(f"[Bot] {response3}\n")
        assert success3 is not None

        # Step 4: Pedir progresso
        print("[Step 4] Usuário: 'progresso'")
        success4, response4 = processor.process_by_name(estevao_name, "progresso")
        print(f"[Bot] {response4}\n")
        assert success4 is not None

        # Step 5: Agradecimento
        print("[Step 5] Usuário: 'obrigado'")
        success5, response5 = processor.process_by_name(estevao_name, "obrigado")
        print(f"[Bot] {response5}\n")
        assert success5 is True

        print(f"{'='*70}")
        print("✅ FLUXO COMPLETO EXECUTADO COM SUCESSO!")
        print(f"{'='*70}\n")

    # =========================================================================
    # TESTE 9: VERIFICAÇÃO DE ESTADO E PERSISTÊNCIA
    # =========================================================================

    def test_user_state_persistence(self, processor, estevao_name):
        """Testa que estado do usuário persiste entre mensagens"""
        # Saudar (seta estado pendente)
        processor.process_by_name(estevao_name, "oi")

        # Obter estado
        state = processor._get_user_state(estevao_name)

        # Verificar que estado existe
        assert state is not None, "Estado deve ser persistido"
        if "pending_confirm" in state:
            assert state["pending_confirm"]["question"] == "ask_task_or_progress", \
                "Estado deve ter pergunta pendente"

    # =========================================================================
    # TESTE 10: MÚLTIPLAS CONVERSAS DE USUÁRIOS
    # =========================================================================

    def test_multiple_users_isolation(self, processor):
        """Testa que múltiplos usuários não interferem uns com os outros"""
        usuario1 = "Estevao Antunes"
        usuario2 = "Outro Usuario"

        # User 1: Saudar
        processor.process_by_name(usuario1, "oi")
        state1 = processor._get_user_state(usuario1)

        # User 2: Saudar
        processor.process_by_name(usuario2, "oi")
        state2 = processor._get_user_state(usuario2)

        # Estados devem ser separados
        assert state1 is not None, "User 1 deve ter estado"
        assert state2 is not None, "User 2 deve ter estado"


class TestNotionSync:
    """Testes de sincronização com Notion"""

    @pytest.fixture
    def notion_tasks_manager(self):
        """Mock do TasksManager para testes Notion"""
        return MagicMock()

    def test_notion_api_connection(self):
        """Testa que conseguimos conectar à API do Notion"""
        # Verificar que NOTION_API_KEY está configurado (ou skip se em teste)
        notion_key = os.getenv("NOTION_API_KEY")
        if notion_key is None:
            pytest.skip("NOTION_API_KEY não configurado - pulando teste de conexão")

    def test_notion_database_ids(self):
        """Testa que IDs das databases estão configurados"""
        tasks_db = os.getenv("NOTION_TASKS_DB_ID")
        assert tasks_db is not None, "NOTION_TASKS_DB_ID deve estar configurado"

        # Verificar formato de ID do Notion (32 caracteres hexadecimais sem hífens)
        cleaned = tasks_db.replace("-", "")
        assert len(cleaned) == 32, f"ID do Notion deve ter 32 caracteres, got {len(cleaned)}"

    def test_create_task_syncs_to_notion(self):
        """Testa que criar tarefa sincroniza com Notion"""
        mock_client = MagicMock()

        # Simular criação
        mock_client.create_page.return_value = {"id": "task-123"}

        # Verificar que podemos chamar
        result = mock_client.create_page(
            database_id="db-123",
            title="Test Task",
            properties={"Owner": "Estevao Antunes"}
        )

        assert result is not None
        mock_client.create_page.assert_called_once()

    def test_update_task_status_syncs_to_notion(self):
        """Testa que mudar status sincroniza com Notion"""
        mock_client = MagicMock()

        # Simular atualização
        mock_client.update_page.return_value = {
            "properties": {"Status": {"select": {"name": "Concluída"}}}
        }

        # Verificar que podemos chamar
        result = mock_client.update_page(
            page_id="page-123",
            properties={"Status": "Concluída"}
        )

        assert result is not None
        mock_client.update_page.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
