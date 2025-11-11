import re

from src.commands.normalizer import (
    extract_task_entities,
    normalize_indices,
)


def test_extract_task_entities_uses_named_indices():
    pattern = re.compile(r"^(feito)\s+(?P<indices>(?:\d+\s*)+)$")
    match = pattern.match("feito 1 3 5")

    entities = extract_task_entities("done_task", match)

    assert entities["indices"] == [1, 3, 5]


def test_extract_task_entities_normalizes_project_scope():
    pattern = re.compile(r"^(tarefas)\s+(?:do|da|de)\s+(?P<project>[\w\s-]+)$")
    match = pattern.match("tarefas do projeto alfa beta")

    entities = extract_task_entities("list_tasks", match)

    assert entities["project"] == "Projeto Alfa Beta"


def test_extract_task_entities_fallback_tuple():
    entities = extract_task_entities("done_task", ("feito", "1 2 3"))

    assert entities["indices"] == [1, 2, 3]


def test_normalize_indices_supports_unicode_dash():
    result = normalize_indices("1—3")

    assert result == [1, 2, 3]
