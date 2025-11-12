import pytest

from src.commands.processor import CommandProcessor
from src.commands.normalizer import ParseResult


class FakeHandlers:
    def __init__(self):
        self.done_calls = []
        self.in_progress_calls = []
        self.show_calls = []
        self.list_called = False
        self.progress_called = False

    def handle_done(self, person_name, task_number):
        self.done_calls.append(task_number)
        return True, ""

    def handle_in_progress(self, person_name, task_number):
        self.in_progress_calls.append(task_number)
        return True, ""

    def handle_show_task(self, person_name, task_number):
        self.show_calls.append(task_number)
        return True, f"detalhes {task_number}"

    def handle_list(self, person_name):
        self.list_called = True
        return True, "lista enviada"

    def handle_progress(self, person_name):
        self.progress_called = True
        return True, "progresso enviado"


class DummyHumanizer:
    def __init__(self):
        self.error_calls = []

    def get_error_message(self, key, **kwargs):
        self.error_calls.append((key, kwargs))
        return f"msg:{key}"

    def pick(self, *args, **kwargs):
        return "👍"

    def __getattr__(self, name):
        return lambda *args, **kwargs: ""


@pytest.fixture
def processor():
    handlers = FakeHandlers()
    proc = CommandProcessor(handlers=handlers)
    proc.humanizer = DummyHumanizer()
    return proc, handlers


def test_execute_intent_without_indices_starts_slot_filling(processor):
    proc, _ = processor
    result = ParseResult("done_task", {}, 0.95, "feito", "feito")

    success, message = proc._execute_intent("Joao", result)

    assert success is True
    assert message == "msg:missing_index_done"
    assert proc.user_states["Joao"]["intent"] == "done_task"


def test_slot_filling_processes_multiple_indices(processor):
    proc, handlers = processor
    proc._set_user_state("Joao", {"intent": "done_task", "expected": "indices"})
    pending = proc._get_user_state("Joao")

    success, message = proc._handle_slot_filling("Joao", "1 2", pending)

    assert success is True
    assert "Tarefa 1" in message
    assert "Tarefa 2" in message
    assert handlers.done_calls == [1, 2]
    assert proc._get_user_state("Joao") is None


def test_show_task_slot_filling_uses_first_index(processor):
    proc, handlers = processor
    proc._set_user_state("Joao", {"intent": "show_task", "expected": "index"})
    pending = proc._get_user_state("Joao")

    success, message = proc._handle_slot_filling("Joao", "5", pending)

    assert success is True
    assert message == "detalhes 5"
    assert handlers.show_calls == [5]
    assert proc._get_user_state("Joao") is None


def test_pending_question_handles_neutral_choice(processor):
    proc, handlers = processor
    proc._set_user_state("Joao", {
        "pending_confirm": {
            "action": "ask_task_or_progress",
            "question": "ask_task_or_progress"
        }
    })
    pending = proc._get_user_state("Joao")

    success, message = proc._handle_slot_filling("Joao", "quero por favor", pending)

    assert success is True
    assert "tarefas" in message.lower()
    assert handlers.list_called is False
    assert handlers.progress_called is False


def test_pending_question_routes_to_progress(processor):
    proc, handlers = processor
    proc._set_user_state("Joao", {
        "pending_confirm": {
            "action": "ask_task_or_progress",
            "question": "ask_task_or_progress"
        }
    })
    pending = proc._get_user_state("Joao")

    success, message = proc._handle_slot_filling("Joao", "quero ver o progresso", pending)

    assert success is True
    assert handlers.progress_called is True
    assert proc._get_user_state("Joao") is None
