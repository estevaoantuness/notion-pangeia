#!/usr/bin/env python3
"""
==============================================================================
MÉTRICAS DE QUALIDADE NLP
==============================================================================
Coleta e analisa métricas detalhadas de qualidade do sistema NLP.

Métricas incluem:
- Taxa de sucesso por intent
- Confiança média por intent
- Cobertura de frases naturais
- Impacto de melhorias (composite phrases, commas, temporal synonyms)
- Detecção de padrões de falha
- Comparação antes/depois das melhorias

Autor: Pangeia Bot
Data: 2025
==============================================================================
"""

import sys
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.commands.normalizer import parse, ParseResult

# ==============================================================================
# ESTRUTURAS DE DADOS
# ==============================================================================

@dataclass
class IntentMetrics:
    """Métricas para um intent específico"""
    intent: str
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0
    confidences: List[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return self.successful_tests / self.total_tests if self.total_tests > 0 else 0

    @property
    def average_confidence(self) -> float:
        return sum(self.confidences) / len(self.confidences) if self.confidences else 0

    @property
    def min_confidence(self) -> float:
        return min(self.confidences) if self.confidences else 0

    @property
    def max_confidence(self) -> float:
        return max(self.confidences) if self.confidences else 0


@dataclass
class NLPMetrics:
    """Agregação de todas as métricas NLP"""
    intents: Dict[str, IntentMetrics] = field(default_factory=dict)
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0

    @property
    def overall_success_rate(self) -> float:
        return self.successful_tests / self.total_tests if self.total_tests > 0 else 0

    @property
    def overall_average_confidence(self) -> float:
        if not self.intents:
            return 0
        total_conf = sum(m.average_confidence for m in self.intents.values())
        return total_conf / len(self.intents)


# ==============================================================================
# DADOS DE TESTE
# ==============================================================================

# Test cases organizados por intent para medir cobertura
TEST_CASES: Dict[str, List[Tuple[str, str]]] = {
    # Format: (user_input, expected_intent)

    # List tasks - 15 test cases (variações naturais)
    "list_tasks": [
        ("tarefas", "list_tasks"),
        ("lista", "list_tasks"),
        ("minhas tarefas", "list_tasks"),
        ("quero ver minhas tarefas", "list_tasks"),
        ("pode mostrar as tarefas", "list_tasks"),
        ("me mostra o que falta", "list_tasks"),
        ("mostra tudo", "list_tasks"),
        ("lista completa", "list_tasks"),
        ("consegues listar tarefas", "list_tasks"),
        ("quero visualizar as tasks", "list_tasks"),
        ("mostre todas as tarefas", "list_tasks"),
        ("podes mostrar minhas tasks", "list_tasks"),
        ("o que tenho para fazer", "list_tasks"),
        ("minhas atividades", "list_tasks"),
        ("show_tasks", "list_tasks"),
    ],

    # Done task - 20 test cases (múltiplos formatos)
    "done_task": [
        ("feito 1", "done_task"),
        ("pronto 1", "done_task"),
        ("feito 1 2 3", "done_task"),
        ("pronto 1, 2, 3", "done_task"),
        ("feito 1-2-3", "done_task"),
        ("1 2 3 feito", "done_task"),
        ("concluí 1", "done_task"),
        ("finalizei 2", "done_task"),
        ("terminei a 3", "done_task"),
        ("concluída 1", "done_task"),
        ("1 feito", "done_task"),
        ("1, 2, 3 pronto", "done_task"),
        ("pronta 1 2", "done_task"),
        ("marca 1 como feito", "done_task"),
        ("1 e 2 feito", "done_task"),
        ("done 1 2 3", "done_task"),
        ("feito 1, 2", "done_task"),
        ("concluir 1", "done_task"),
        ("1-2-3 pronto", "done_task"),
        ("2, 4, 5 feito", "done_task"),
    ],

    # In progress task - 12 test cases
    "in_progress_task": [
        ("andamento 1", "in_progress_task"),
        ("fazendo 1", "in_progress_task"),
        ("em andamento 1", "in_progress_task"),
        ("estou fazendo 2", "in_progress_task"),
        ("vou fazer 3", "in_progress_task"),
        ("comecei 1", "in_progress_task"),
        ("1 andamento", "in_progress_task"),
        ("1 2 3 fazendo", "in_progress_task"),
        ("1, 2, 3 andamento", "in_progress_task"),
        ("marcando 1 como em andamento", "in_progress_task"),
        ("estou trabalhando na 2", "in_progress_task"),
        ("comecei a fazer 3 4", "in_progress_task"),
    ],

    # Show task details - 8 test cases
    "show_task": [
        ("mostra 1", "show_task"),
        ("veja 1", "show_task"),
        ("detalhes 1", "show_task"),
        ("info 1", "show_task"),
        ("1 detalhes", "show_task"),
        ("me mostra a 2", "show_task"),
        ("abra 3", "show_task"),
        ("informações sobre 4", "show_task"),
    ],

    # Show more - 6 test cases
    "show_more": [
        ("ver mais", "show_more"),
        ("mais", "show_more"),
        ("mostrar mais", "show_more"),
        ("todas", "show_more"),
        ("completa", "show_more"),
        ("lista completa", "show_more"),
    ],

    # Progress - 10 test cases
    "progress": [
        ("progresso", "progress"),
        ("qual é meu progresso", "progress"),
        ("como estou indo", "progress"),
        ("me mostra o status", "progress"),
        ("quanto já fiz", "progress"),
        ("qual é meu status", "progress"),
        ("como vai meu andamento", "progress"),
        ("resumo", "progress"),
        ("mostra meu progresso", "progress"),
        ("como estou", "progress"),
    ],

    # Help - 8 test cases
    "help": [
        ("?", "help"),
        ("ajuda", "help"),
        ("como usar", "help"),
        ("o que posso fazer", "help"),
        ("preciso de ajuda", "help"),
        ("qual é o comando", "help"),
        ("como funciona", "help"),
        ("me ajuda", "help"),
    ],

    # Confirmations - 12 test cases
    "confirm_yes": [
        ("sim", "confirm_yes"),
        ("s", "confirm_yes"),
        ("beleza", "confirm_yes"),
        ("ok", "confirm_yes"),
        ("pode", "confirm_yes"),
        ("vamos", "confirm_yes"),
        ("bora", "confirm_yes"),
        ("👍", "confirm_yes"),
        ("✅", "confirm_yes"),
        ("isso", "confirm_yes"),
        ("confirmo", "confirm_yes"),
        ("tá bom", "confirm_yes"),
    ],

    "confirm_no": [
        ("não", "confirm_no"),
        ("n", "confirm_no"),
        ("deixa", "confirm_no"),
        ("cancelar", "confirm_no"),
        ("nope", "confirm_no"),
        ("agora não", "confirm_no"),
        ("❌", "confirm_no"),
        ("não agora", "confirm_no"),
    ],

    # Greetings - 10 test cases
    "greet": [
        ("oi", "greet"),
        ("opa", "greet"),
        ("olá", "greet"),
        ("salve", "greet"),
        ("tudo bem", "greet"),
        ("e aí", "greet"),
        ("oi tudo certo", "greet"),
        ("o", "greet"),
        ("hey", "greet"),
        ("opa tudo bem", "greet"),
    ],

    # Goodbye - 5 test cases
    "goodbye": [
        ("tchau", "goodbye"),
        ("falou", "goodbye"),
        ("até logo", "goodbye"),
        ("até mais", "goodbye"),
        ("bye", "goodbye"),
    ],

    # Thanks - 5 test cases
    "thanks": [
        ("obrigado", "thanks"),
        ("obrigada", "thanks"),
        ("brigado", "thanks"),
        ("valeu", "thanks"),
        ("vlw", "thanks"),
    ],

    # Create task - 5 test cases
    "create_task": [
        ("criar tarefa", "create_task"),
        ("nova tarefa", "create_task"),
        ("criar task", "create_task"),
        ("nova task", "create_task"),
        ("vou criar uma tarefa", "create_task"),
    ],

    # Tutorials - 10 test cases
    "tutorial_complete": [
        ("tutorial", "tutorial_complete"),
        ("guia", "tutorial_complete"),
        ("como funciona", "tutorial_complete"),
        ("ensina", "tutorial_complete"),
        ("me ensina", "tutorial_complete"),
        ("explicação", "tutorial_complete"),
        ("documentação", "tutorial_complete"),
        ("passo a passo", "tutorial_complete"),
        ("manual", "tutorial_complete"),
        ("quero aprender", "tutorial_complete"),
    ],

    "tutorial_quick": [
        ("básico", "tutorial_quick"),
        ("resumo", "tutorial_quick"),
        ("rápido", "tutorial_quick"),
        ("quick", "tutorial_quick"),
        ("simples", "tutorial_quick"),
    ],

    "show_examples": [
        ("exemplos", "show_examples"),
        ("exemplo", "show_examples"),
        ("dá um exemplo", "show_examples"),
        ("mostra exemplos", "show_examples"),
        ("na prática", "show_examples"),
    ],

    "show_tips": [
        ("dicas", "show_tips"),
        ("dica", "show_tips"),
        ("truques", "show_tips"),
        ("tips", "show_tips"),
        ("me dá dicas", "show_tips"),
    ],
}


# ==============================================================================
# FUNÇÕES DE CÁLCULO DE MÉTRICAS
# ==============================================================================

def calculate_metrics() -> NLPMetrics:
    """
    Executa todos os test cases e calcula métricas de qualidade.

    Returns:
        NLPMetrics com todos os dados agregados
    """
    metrics = NLPMetrics()

    # Iterar sobre todos os intents e seus test cases
    for intent, test_cases in TEST_CASES.items():
        intent_metrics = IntentMetrics(intent=intent, total_tests=len(test_cases))

        for user_input, expected_intent in test_cases:
            result = parse(user_input)

            # Registrar confiança
            intent_metrics.confidences.append(result.confidence)

            # Verificar se sucesso
            if result.intent == expected_intent:
                intent_metrics.successful_tests += 1
            else:
                intent_metrics.failed_tests += 1

        metrics.intents[intent] = intent_metrics
        metrics.total_tests += intent_metrics.total_tests
        metrics.successful_tests += intent_metrics.successful_tests
        metrics.failed_tests += intent_metrics.failed_tests

    return metrics


def print_detailed_metrics(metrics: NLPMetrics) -> None:
    """Imprime métricas detalhadas em formato legível"""
    print("\n" + "=" * 100)
    print("MÉTRICAS DE QUALIDADE NLP".center(100))
    print("=" * 100)

    # Resultado geral
    print(f"\n📊 RESULTADO GERAL:")
    print(f"   Taxa de sucesso: {metrics.overall_success_rate*100:.1f}%")
    print(f"   Confiança média: {metrics.overall_average_confidence:.3f}")
    print(f"   Total de testes: {metrics.total_tests}")
    print(f"   Sucessos: {metrics.successful_tests}")
    print(f"   Falhas: {metrics.failed_tests}")

    # Resultados por intent
    print(f"\n🔍 MÉTRICAS POR INTENT:")
    print(f"\n{'Intent':<25} {'Taxa':<10} {'Conf':<10} {'Min':<8} {'Max':<8} {'Testes':<8}")
    print("-" * 100)

    # Ordenar por taxa de sucesso decrescente
    sorted_intents = sorted(
        metrics.intents.items(),
        key=lambda x: x[1].success_rate,
        reverse=True
    )

    for intent, intent_metrics in sorted_intents:
        icon = "✅" if intent_metrics.success_rate == 1.0 else "⚠️" if intent_metrics.success_rate >= 0.8 else "❌"
        rate = f"{intent_metrics.success_rate*100:.0f}%"
        conf = f"{intent_metrics.average_confidence:.3f}"
        min_c = f"{intent_metrics.min_confidence:.3f}"
        max_c = f"{intent_metrics.max_confidence:.3f}"
        tests = f"{intent_metrics.successful_tests}/{intent_metrics.total_tests}"

        print(f"{icon} {intent:<23} {rate:<10} {conf:<10} {min_c:<8} {max_c:<8} {tests:<8}")

    # Análise de confiança
    print(f"\n📈 ANÁLISE DE CONFIANÇA:")
    high_confidence = sum(1 for m in metrics.intents.values() if m.average_confidence >= 0.95)
    medium_confidence = sum(1 for m in metrics.intents.values() if 0.85 <= m.average_confidence < 0.95)
    low_confidence = sum(1 for m in metrics.intents.values() if m.average_confidence < 0.85)

    print(f"   Alta confiança (≥0.95): {high_confidence} intents")
    print(f"   Média confiança (0.85-0.95): {medium_confidence} intents")
    print(f"   Baixa confiança (<0.85): {low_confidence} intents")

    # Intents com menor performance
    poor_intents = [
        (intent, m) for intent, m in metrics.intents.items()
        if m.success_rate < 1.0
    ]

    if poor_intents:
        print(f"\n⚠️  INTENTS COM FALHAS:")
        for intent, m in poor_intents:
            print(f"   {intent}: {m.failed_tests} falhas em {m.total_tests} testes")

    print("\n" + "=" * 100)


def get_improvement_report(old_metrics: NLPMetrics = None, new_metrics: NLPMetrics = None) -> Dict[str, Any]:
    """
    Gera relatório de melhoria comparando antes/depois.

    Args:
        old_metrics: Métricas do sistema anterior (sem Phase 1)
        new_metrics: Métricas do sistema atual (com Phase 1)

    Returns:
        Dict com comparação e impacto
    """
    if not new_metrics:
        new_metrics = calculate_metrics()

    report = {
        "new_metrics": new_metrics,
        "improvements": {},
    }

    if old_metrics:
        report["old_metrics"] = old_metrics
        report["success_rate_improvement"] = (
            new_metrics.overall_success_rate - old_metrics.overall_success_rate
        ) * 100
        report["confidence_improvement"] = (
            new_metrics.overall_average_confidence - old_metrics.overall_average_confidence
        )

        # Análise por intent
        for intent in new_metrics.intents.keys():
            if intent in old_metrics.intents:
                old = old_metrics.intents[intent]
                new = new_metrics.intents[intent]
                report["improvements"][intent] = {
                    "success_rate_before": old.success_rate,
                    "success_rate_after": new.success_rate,
                    "confidence_before": old.average_confidence,
                    "confidence_after": new.average_confidence,
                }

    return report


# ==============================================================================
# TESTES DO PYTEST
# ==============================================================================

def test_nlp_quality():
    """Teste principal do pytest"""
    metrics = calculate_metrics()
    print_detailed_metrics(metrics)

    # Asserts
    assert metrics.overall_success_rate >= 0.90, (
        f"Taxa de sucesso ({metrics.overall_success_rate*100:.1f}%) "
        f"abaixo do threshold de 90%"
    )

    assert metrics.overall_average_confidence >= 0.85, (
        f"Confiança média ({metrics.overall_average_confidence:.3f}) "
        f"abaixo do threshold de 0.85"
    )


if __name__ == "__main__":
    # Executar se rodar direto
    metrics = calculate_metrics()
    print_detailed_metrics(metrics)

    # Gerar relatório
    report = get_improvement_report(new_metrics=metrics)
    print(f"\n✅ Teste completado com sucesso!")
    print(f"   Taxa de sucesso: {metrics.overall_success_rate*100:.1f}%")
    print(f"   Confiança média: {metrics.overall_average_confidence:.3f}")
