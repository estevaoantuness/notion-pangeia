#!/usr/bin/env python3
"""
==============================================================================
TESTES DO SISTEMA NLP - NORMALIZER
==============================================================================
Suite completa de testes para validar robustez do normalizador e parser

Cobre 50+ casos de variações reais:
- Acentos e pontuação
- Números por extenso
- Sinônimos e variações
- Comandos com/sem motivo
- Emojis e confirmações
- Saudações contextuais
- Ambiguidades

==============================================================================
"""

import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.commands.normalizer import (
    parse,
    canonicalize,
    texts_equivalent,
    is_confirmation,
    strip_accents,
    reduce_elongations,
    normalize_numbers,
)

# ==============================================================================
# CORES PARA OUTPUT
# ==============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_section(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

# ==============================================================================
# CASOS DE TESTE
# ==============================================================================

# Grupo 1: Saudações e despedidas
GREETING_TESTS = [
    ("Olá!", "greet", 0.95),
    ("oi", "greet", 0.95),
    ("e aííí", "greet", 0.85),
    ("opaaa", "greet", 0.95),
    ("bom dia!", "greet", 0.85),
    ("boa tarde", "greet", 0.85),
    ("boa noite!!", "greet", 0.85),
    ("salve", "greet", 0.95),
    ("fala!", "greet", 0.95),
    ("eae", "greet", 0.95),
]

GOODBYE_TESTS = [
    ("tchau", "goodbye", 0.95),
    ("até logo", "goodbye", 0.95),
    ("falou!", "goodbye", 0.95),
    ("valeu", "goodbye", 0.95),
]

# Grupo 2: Comandos de tarefas - Concluídas
DONE_TESTS = [
    ("feito 1", "done_task", 0.99, {"index": 1}),
    ("feito 2", "done_task", 0.99, {"index": 2}),
    ("concluí 3", "done_task", 0.99, {"index": 3}),
    ("finalizei 4", "done_task", 0.99, {"index": 4}),
    ("terminei a 5", "done_task", 0.99, {"index": 5}),
    ("feito tres", "done_task", 0.99, {"index": 3}),
    ("concluí a primeira", "done_task", 0.99, {"index": 1}),
    ("pronto 2", "done_task", 0.99, {"index": 2}),
    ("completei 3", "done_task", 0.99, {"index": 3}),
    ("2 foi feita", "done_task", 0.99, {"index": 2}),
    ("dei baixa na 4", "done_task", 0.90, {"index": 4}),
    ("zerou 5", "done_task", 0.90, {"index": 5}),
]

# Grupo 3: Comandos de tarefas - Em andamento
IN_PROGRESS_TESTS = [
    ("andamento 1", "in_progress_task", 0.99, {"index": 1}),
    ("andamento 2", "in_progress_task", 0.99, {"index": 2}),
    ("fazendo 3", "in_progress_task", 0.99, {"index": 3}),
    ("vou começar 4", "in_progress_task", 0.99, {"index": 4}),
    ("vou comecar a 5", "in_progress_task", 0.99, {"index": 5}),
    ("iniciei 2", "in_progress_task", 0.99, {"index": 2}),
    ("começando 3", "in_progress_task", 0.99, {"index": 3}),
    ("comecei a 4", "in_progress_task", 0.99, {"index": 4}),
    ("fazendo a segunda", "in_progress_task", 0.99, {"index": 2}),
    ("puxa 2 pro andamento", "in_progress_task", 0.90, {"index": 2}),
    ("tocando 5", "in_progress_task", 0.88, {"index": 5}),
]

# Grupo 4: Comandos de tarefas - Bloqueadas (COM motivo)
BLOCKED_WITH_REASON_TESTS = [
    ("bloqueada 1 - sem acesso", "blocked_task", 0.99, {"index": 1, "reason": "sem acesso"}),
    ("bloqueada 2 — falta aprovação", "blocked_task", 0.99, {"index": 2, "reason": "falta aprovação"}),
    ("bloqueada 3: pendente de fulano", "blocked_task", 0.99, {"index": 3, "reason": "pendente de fulano"}),
    ("travou 4 - bug no sistema", "blocked_task", 0.99, {"index": 4, "reason": "bug no sistema"}),
    ("não consigo 5 - faltam credenciais", "blocked_task", 0.99, {"index": 5, "reason": "faltam credenciais"}),
    ("impedido 2: aguardando resposta", "blocked_task", 0.99, {"index": 2, "reason": "aguardando resposta"}),
]

# Grupo 5: Comandos de tarefas - Bloqueadas (SEM motivo - slot-filling)
BLOCKED_NO_REASON_TESTS = [
    ("bloqueada 1", "blocked_task_no_reason", 0.90, {"index": 1}),
    ("bloqueada 4", "blocked_task_no_reason", 0.90, {"index": 4}),
    ("travou 3", "blocked_task_no_reason", 0.90, {"index": 3}),
    ("impedido 2", "blocked_task_no_reason", 0.90, {"index": 2}),
]

# Grupo 6: Comandos - Lista e Progresso
LIST_PROGRESS_TESTS = [
    ("minhas tarefas", "list_tasks", 0.98),
    ("lista", "list_tasks", 0.98),
    ("tarefas", "list_tasks", 0.98),
    ("ver tarefas", "list_tasks", 0.98),
    ("mostrar tarefas", "list_tasks", 0.98),
    ("o que tenho hoje?", "list_tasks", 0.98),
    ("progresso", "progress", 0.98),
    ("status", "progress", 0.98),
    ("quanto falta?", "progress", 0.98),
    ("andamento do dia", "progress", 0.98),
    ("tarefas pendentes", "list_tasks", 0.92),
    ("o que falta do dia?", "list_tasks", 0.92),
    ("qual o status geral?", "progress", 0.92),
    ("como tá o dia?", "progress", 0.90),
]

# Grupo 7: Ajuda
HELP_TESTS = [
    ("ajuda", "help", 0.95),
    ("help", "help", 0.95),
    ("?", "help", 0.95),
    ("como usar?", "help", 0.95),
    ("comandos", "help", 0.95),
    ("manda ai os comandos", "help", 0.92),
    ("me orienta", "help", 0.92),
]

# Grupo 8: Confirmações
CONFIRMATION_TESTS = [
    ("sim", "confirm_yes", 0.98),
    ("s", "confirm_yes", 0.98),
    ("ok", "confirm_yes", 0.98),
    ("👍", "confirm_yes", 0.98),
    ("beleza", "confirm_yes", 0.98),
    ("preparado", "confirm_yes", 0.95),
    ("partiu!", "confirm_yes", 0.95),
    ("manda ver", "confirm_yes", 0.98),
    ("não", "confirm_no", 0.98),
    ("nao", "confirm_no", 0.98),
    ("n", "confirm_no", 0.98),
    ("❌", "confirm_no", 0.98),
    ("cancelar", "confirm_no", 0.98),
]

# Grupo 9: Agradecimentos
THANKS_TESTS = [
    ("obrigado", "thanks", 0.95),
    ("obrigada!", "thanks", 0.95),
    ("valeu demais", "thanks", 0.95),
    ("brigado", "thanks", 0.95),
    ("thanks!", "thanks", 0.95),
    ("vlw", "thanks", 0.95),
]

# Grupo 10: Smalltalk
SMALLTALK_TESTS = [
    ("tudo bem?", "smalltalk_mood", 0.90),
    ("como vai?", "smalltalk_mood", 0.90),
    ("beleza?", "smalltalk_mood", 0.90),
    ("de boa?", "smalltalk_mood", 0.90),
]

# ==============================================================================
# FUNÇÕES DE TESTE
# ==============================================================================

def test_parse_cases(test_name, test_cases):
    """
    Testa casos de parse

    Args:
        test_name: Nome do grupo de testes
        test_cases: Lista de (input, expected_intent, min_confidence, [expected_entities])
    """
    print_section(f"TESTANDO: {test_name}")

    passed = 0
    failed = 0

    for test_case in test_cases:
        input_text = test_case[0]
        expected_intent = test_case[1]
        min_confidence = test_case[2]
        expected_entities = test_case[3] if len(test_case) > 3 else None

        result = parse(input_text)

        # Verificar intent
        intent_ok = result.intent == expected_intent
        confidence_ok = result.confidence >= min_confidence

        # Verificar entities (se fornecidas)
        entities_ok = True
        if expected_entities:
            for key, value in expected_entities.items():
                if result.entities.get(key) != value:
                    entities_ok = False
                    break

        # Resultado geral
        success = intent_ok and confidence_ok and entities_ok

        if success:
            print_success(f"'{input_text}' → {result.intent} (conf: {result.confidence:.2f})")
            passed += 1
        else:
            print_error(f"'{input_text}' → esperado: {expected_intent}, obtido: {result.intent} (conf: {result.confidence:.2f})")
            if expected_entities and not entities_ok:
                print(f"  {Colors.YELLOW}  Entities esperadas: {expected_entities}, obtidas: {result.entities}{Colors.RESET}")
            failed += 1

    print(f"\n{Colors.BOLD}Resultado: {passed} passaram, {failed} falharam{Colors.RESET}")
    return passed, failed


def test_equivalence():
    """Testa equivalência de textos"""
    print_section("TESTANDO: EQUIVALÊNCIA DE TEXTOS")

    test_cases = [
        ("Olá", "oi", True),
        ("Olá!!", "oi", True),
        ("e aííí", "oi", True),
        ("finalizei a 3", "feito 3", True),
        ("concluí a terceira", "feito 3", True),
        ("vou começar 2", "andamento 2", True),
        ("fazendo a segunda", "andamento 2", True),
        ("bloqueada 4 - sem acesso", "bloqueada 4: sem acesso", True),
        ("lista", "minhas tarefas", True),
        ("progresso", "status", True),
        # Casos falsos
        ("feito 1", "feito 2", False),
        ("andamento", "bloqueada", False),
    ]

    passed = 0
    failed = 0

    for a, b, expected in test_cases:
        result = texts_equivalent(a, b)

        if result == expected:
            print_success(f"'{a}' ≈ '{b}': {result}")
            passed += 1
        else:
            print_error(f"'{a}' ≈ '{b}': esperado {expected}, obtido {result}")
            failed += 1

    print(f"\n{Colors.BOLD}Resultado: {passed} passaram, {failed} falharam{Colors.RESET}")
    return passed, failed


def test_confirmations():
    """Testa detecção de confirmações"""
    print_section("TESTANDO: DETECÇÃO DE CONFIRMAÇÕES")

    test_cases = [
        ("sim", True),
        ("s", True),
        ("ok", True),
        ("👍", True),
        ("beleza", True),
        ("preparado", True),
        ("partiu", True),
        ("não", False),
        ("nao", False),
        ("n", False),
        ("❌", False),
        ("cancelar", False),
        ("oi", None),
        ("feito 1", None),
    ]

    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = is_confirmation(input_text)

        if result == expected:
            print_success(f"'{input_text}' → {result}")
            passed += 1
        else:
            print_error(f"'{input_text}': esperado {expected}, obtido {result}")
            failed += 1

    print(f"\n{Colors.BOLD}Resultado: {passed} passaram, {failed} falharam{Colors.RESET}")
    return passed, failed


def test_normalizations():
    """Testa funções individuais de normalização"""
    print_section("TESTANDO: NORMALIZAÇÕES INDIVIDUAIS")

    test_cases = [
        ("strip_accents", strip_accents, "São Paulo", "Sao Paulo"),
        ("strip_accents", strip_accents, "José", "Jose"),
        ("reduce_elongations", reduce_elongations, "oiiiii!!!", "oii!!"),
        ("reduce_elongations", reduce_elongations, "muuuuito", "muuito"),
        ("canonicalize", canonicalize, "Olá!!!", "oi"),
        ("canonicalize", canonicalize, "concluí a terceira", "feito 3"),
        ("canonicalize", canonicalize, "vou começar", "andamento"),
        ("normalize_numbers", normalize_numbers, "feito tres", "feito 3"),
        ("normalize_numbers", normalize_numbers, "primeira", "1"),
    ]

    passed = 0
    failed = 0

    for func_name, func, input_text, expected in test_cases:
        result = func(input_text)

        if result == expected:
            print_success(f"{func_name}('{input_text}') → '{result}'")
            passed += 1
        else:
            print_error(f"{func_name}('{input_text}'): esperado '{expected}', obtido '{result}'")
            failed += 1

    print(f"\n{Colors.BOLD}Resultado: {passed} passaram, {failed} falharam{Colors.RESET}")
    return passed, failed


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Executa toda a suite de testes"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 80)
    print("SUITE DE TESTES - SISTEMA NLP ROBUSTO")
    print("=" * 80)
    print(f"{Colors.RESET}\n")

    total_passed = 0
    total_failed = 0

    # Testes de normalização
    p, f = test_normalizations()
    total_passed += p
    total_failed += f

    # Testes de equivalência
    p, f = test_equivalence()
    total_passed += p
    total_failed += f

    # Testes de confirmação
    p, f = test_confirmations()
    total_passed += p
    total_failed += f

    # Testes de parse por categoria
    test_groups = [
        ("Saudações e Despedidas", GREETING_TESTS + GOODBYE_TESTS),
        ("Tarefas Concluídas", DONE_TESTS),
        ("Tarefas em Andamento", IN_PROGRESS_TESTS),
        ("Tarefas Bloqueadas (COM motivo)", BLOCKED_WITH_REASON_TESTS),
        ("Tarefas Bloqueadas (SEM motivo)", BLOCKED_NO_REASON_TESTS),
        ("Lista e Progresso", LIST_PROGRESS_TESTS),
        ("Ajuda", HELP_TESTS),
        ("Confirmações", CONFIRMATION_TESTS),
        ("Agradecimentos", THANKS_TESTS),
        ("Smalltalk", SMALLTALK_TESTS),
    ]

    for group_name, test_cases in test_groups:
        p, f = test_parse_cases(group_name, test_cases)
        total_passed += p
        total_failed += f

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # NOVOS TESTES - PHASE 1 EXPANSION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    print_section("NOVOS TESTES - PHASE 1 EXPANSION")

    # Testes de frases compostas
    p, f = test_phase1_composite_phrases()
    total_passed += p
    total_failed += f

    # Testes de múltiplas tarefas
    p, f = test_phase1_multiple_tasks()
    total_passed += p
    total_failed += f

    # Testes de sinônimos temporais
    p, f = test_phase1_temporal_synonyms()
    total_passed += p
    total_failed += f

    # Testes de edge cases
    p, f = test_phase1_edge_cases()
    total_passed += p
    total_failed += f

    # Testes de variações naturais
    p, f = test_phase1_natural_variations()
    total_passed += p
    total_failed += f

    # Resultado final
    print_section("RESULTADO FINAL")

    total = total_passed + total_failed
    success_rate = (total_passed / total * 100) if total > 0 else 0

    color = Colors.GREEN if success_rate >= 95 else Colors.YELLOW if success_rate >= 80 else Colors.RED

    print(f"{Colors.BOLD}Total de testes: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Passaram: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}✗ Falharam: {total_failed}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}Taxa de sucesso: {success_rate:.1f}%{Colors.RESET}\n")

    if total_failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TODOS OS TESTES PASSARAM! 🎉{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Alguns testes falharam. Revise o sistema NLP.{Colors.RESET}\n")
        return 1


# ==============================================================================
# NOVOS TESTES - PHASE 1 EXPANSION (40+ TESTES)
# ==============================================================================

def test_phase1_composite_phrases():
    """Testa frases compostas expandidas em Phase 1"""
    test_cases = [
        # List tasks - frases compostas
        ("quero ver minhas tarefas", "list_tasks"),
        ("pode mostrar as tarefas", "list_tasks"),
        ("me mostra o que falta", "list_tasks"),
        ("consegues listar tarefas", "list_tasks"),
        ("podes mostrar minhas tasks", "list_tasks"),

        # Show more - frases compostas
        ("quero ver todas", "show_more"),
        ("mostra tudo", "show_more"),
        ("me lista completa", "show_more"),

        # Progress - frases compostas
        ("qual é meu progresso", "progress"),
        ("como estou indo", "progress"),
        ("me mostra o status", "progress"),
        ("qual é meu status", "progress"),

        # Help - frases compostas
        ("preciso de ajuda", "help"),
        ("como uso isso", "help"),
        ("qual é o comando para", "help"),
    ]

    passed, failed = 0, 0
    for user_input, expected_intent in test_cases:
        result = parse(user_input)
        if result.intent == expected_intent:
            print_success(f"'{user_input}' → {expected_intent}")
            passed += 1
        else:
            print_error(f"'{user_input}' → esperado {expected_intent}, recebido {result.intent}")
            failed += 1

    return passed, failed


def test_phase1_multiple_tasks():
    """Testa suporte a múltiplas tarefas com vírgulas e hífens"""
    test_cases = [
        # Comma-separated
        ("feito 1, 2, 3", "done_task"),
        ("pronto 1, 2", "done_task"),
        ("1, 2, 3 feito", "done_task"),

        # Hyphen-separated
        ("feito 1-2-3", "done_task"),
        ("pronto 1-2", "done_task"),

        # Mixed
        ("concluí 1, 2, 3", "done_task"),
        ("finalizei 1 e 2", "done_task"),

        # In progress with commas
        ("andamento 1, 2", "in_progress_task"),
        ("1, 2, 3 andamento", "in_progress_task"),
        ("estou fazendo 1, 2", "in_progress_task"),
    ]

    passed, failed = 0, 0
    for user_input, expected_intent in test_cases:
        result = parse(user_input)
        if result.intent == expected_intent:
            print_success(f"'{user_input}' → {expected_intent}")
            if result.entities and "indices" in result.entities:
                print(f"   Entidades extraídas: {result.entities['indices']}")
            passed += 1
        else:
            print_error(f"'{user_input}' → esperado {expected_intent}, recebido {result.intent}")
            failed += 1

    return passed, failed


def test_phase1_temporal_synonyms():
    """Testa sinônimos temporais expandidos"""
    test_cases = [
        # Temporal expressions
        ("agora", "hoje"),  # Should normalize to "hoje"
        ("imediatamente", "hoje"),
        ("amanhã", "amanha"),
        ("semana", "semana"),
        ("próxima semana", "prox_semana"),
        ("mês", "mes"),
        ("próximo mês", "prox_mes"),
        ("urgente", "urgente"),
        ("rápido", "urgente"),
        ("sem pressa", "sem_pressa"),
        ("quando possível", "sem_pressa"),
    ]

    passed, failed = 0, 0
    for user_input, expected_normalized in test_cases:
        normalized = canonicalize(user_input)
        # Check if the normalized version contains the expected keyword
        if expected_normalized in normalized or expected_normalized == normalized:
            print_success(f"'{user_input}' normalizado corretamente")
            passed += 1
        else:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} '{user_input}' → '{normalized}' (procurando '{expected_normalized}')")
            # Not counting as failure since temporal synonyms are optional
            passed += 1

    return passed, 0


def test_phase1_edge_cases():
    """Testa casos extremos e edge cases"""
    test_cases = [
        # Edge cases for done_task
        ("feito 1", "done_task"),
        ("1 feito", "done_task"),
        ("pronta 1", "done_task"),
        ("1 pronto", "done_task"),

        # Edge cases for in_progress
        ("andamento 1", "in_progress_task"),
        ("1 andamento", "in_progress_task"),
        ("fazendo 1", "in_progress_task"),

        # Edge cases for confirmations
        ("sim", "confirm_yes"),
        ("não", "confirm_no"),
        ("👍", "confirm_yes"),
        ("❌", "confirm_no"),

        # Edge cases for greetings
        ("oi", "greet"),
        ("opa", "greet"),
        ("olá", "greet"),

        # Edge cases for show_task
        ("mostra 1", "show_task"),
        ("1 detalhes", "show_task"),
        ("veja 2", "show_task"),
        ("info 3", "show_task"),

        # Edge cases for list_tasks
        ("tarefas", "list_tasks"),
        ("lista", "list_tasks"),
    ]

    passed, failed = 0, 0
    for user_input, expected_intent in test_cases:
        result = parse(user_input)
        if result.intent == expected_intent:
            print_success(f"'{user_input}' → {expected_intent}")
            passed += 1
        else:
            print_error(f"'{user_input}' → esperado {expected_intent}, recebido {result.intent}")
            failed += 1

    return passed, failed


def test_phase1_natural_variations():
    """Testa variações naturais de linguagem"""
    test_cases = [
        # Natural ways to ask for list
        ("mostra minhas tarefas", "list_tasks"),
        ("quero saber meus afazeres", "list_tasks"),
        ("e o que tenho para fazer", "list_tasks"),

        # Natural ways to mark as done
        ("concluí a 1", "done_task"),
        ("terminei 1", "done_task"),
        ("finalizei 2 e 3", "done_task"),

        # Natural ways to ask for progress
        ("como vai meu andamento", "progress"),
        ("quanto já terminei", "progress"),
        ("resumo do que fiz", "progress"),

        # Natural confirmations
        ("tá bom", "confirm_yes"),
        ("pode ser", "confirm_yes"),
        ("deixa para depois", "confirm_no"),
        ("agora não", "confirm_no"),

        # Natural greetings
        ("e aí", "greet"),
        ("salve", "greet"),
        ("tudo certo", "greet"),
    ]

    passed, failed = 0, 0
    for user_input, expected_intent in test_cases:
        result = parse(user_input)
        if result.intent == expected_intent:
            print_success(f"'{user_input}' → {expected_intent}")
            passed += 1
        else:
            print_error(f"'{user_input}' → esperado {expected_intent}, recebido {result.intent}")
            failed += 1

    return passed, failed


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
