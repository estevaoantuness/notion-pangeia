#!/usr/bin/env python3
"""
Teste dos comandos de tutoriais diretos.

Testa:
- tutorial_complete (tutorial, guia, manual)
- tutorial_quick (básico, resumo, rápido)
- start_from_scratch (começar, primeira vez)
- show_examples (exemplos, na prática)
- show_tips (dicas, truques)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.commands.normalizer import parse

def test_tutorial_commands():
    """Testa parsing de comandos de tutoriais"""

    print("=" * 80)
    print("TESTE DE COMANDOS DE TUTORIAIS DIRETOS")
    print("=" * 80)
    print()

    test_cases = [
        # Tutorial completo
        ("tutorial", "tutorial_complete", 0.98),
        ("guia", "tutorial_complete", 0.98),
        ("manual", "tutorial_complete", 0.98),
        ("como funciona", "tutorial_complete", 0.98),
        ("passo a passo", "tutorial_complete", 0.98),
        ("lista de comandos", "tutorial_complete", 0.98),

        # Tutorial básico
        ("básico", "tutorial_quick", 0.98),
        ("resumo", "tutorial_quick", 0.98),
        ("rápido", "tutorial_quick", 0.98),
        ("quick", "tutorial_quick", 0.98),
        ("tldr", "tutorial_quick", 0.98),
        ("essencial", "tutorial_quick", 0.98),

        # Começar do zero
        ("começar", "start_from_scratch", 0.98),
        ("início", "start_from_scratch", 0.98),
        ("primeira vez", "start_from_scratch", 0.98),
        ("como começar", "start_from_scratch", 0.98),
        ("do zero", "start_from_scratch", 0.98),

        # Exemplos
        ("exemplos", "show_examples", 0.98),
        ("exemplo", "show_examples", 0.98),
        ("na prática", "show_examples", 0.98),
        ("casos de uso", "show_examples", 0.98),

        # Dicas
        ("dicas", "show_tips", 0.98),
        ("truques", "show_tips", 0.98),
        ("macetes", "show_tips", 0.98),
        ("tips", "show_tips", 0.98),
        ("sugestões", "show_tips", 0.98),
    ]

    passed = 0
    failed = 0

    for text, expected_intent, expected_confidence in test_cases:
        result = parse(text, log_result=False)

        # Verificar intent
        if result.intent == expected_intent:
            # Verificar confiança
            if result.confidence >= expected_confidence:
                status = "✅ PASS"
                passed += 1
            else:
                status = f"⚠️  LOW CONFIDENCE ({result.confidence:.2f})"
                failed += 1
        else:
            status = f"❌ FAIL (got {result.intent})"
            failed += 1

        print(f"{status:<30} | '{text}' → {result.intent} (conf: {result.confidence:.2f})")

    print()
    print("=" * 80)
    print(f"RESULTADOS: {passed} PASS, {failed} FAIL")
    print("=" * 80)
    print()

    return failed == 0


if __name__ == "__main__":
    success = test_tutorial_commands()
    sys.exit(0 if success else 1)
