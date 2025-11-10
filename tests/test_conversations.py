#!/usr/bin/env python3
"""
==============================================================================
TESTE DE CONVERSAS REALISTAS (NLP QUALITY VALIDATION)
==============================================================================
Testa 10 conversas realistas para validar cobertura do NLP.
Cada conversa simula um fluxo natural de usuário com várias mensagens.

Métricas coletadas:
- Taxa de sucesso (% intents detectados corretamente)
- Confiança média dos matches
- Tipos de intents melhor/pior cobertos
- Impacto das melhorias (composite phrases, commas, etc)

Autor: Pangeia Bot
Data: 2025
==============================================================================
"""

import sys
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar o parser
from src.commands.normalizer import parse, ParseResult

# ==============================================================================
# ESTRUTURAS DE DADOS
# ==============================================================================

@dataclass
class ConversationStep:
    """Uma mensagem em uma conversa"""
    user_input: str
    expected_intent: str
    description: str = ""
    should_succeed: bool = True


@dataclass
class ConversationTest:
    """Uma conversa completa com múltiplas mensagens"""
    name: str
    description: str
    steps: List[ConversationStep]


# ==============================================================================
# CONVERSAS DE TESTE
# ==============================================================================

CONVERSATIONS: List[ConversationTest] = [
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 1: Usuário quer ver suas tarefas (variações naturais)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Listar Tarefas - Variações Naturais",
        description="Testa múltiplas formas de pedir para ver tarefas",
        steps=[
            ConversationStep("oi bot", "greet"),
            ConversationStep("tarefas", "list_tasks", "Formato simples"),
            ConversationStep("mostra minhas tarefas", "list_tasks", "Composite phrase"),
            ConversationStep("quero ver o que falta", "list_tasks", "Paráfrase natural"),
            ConversationStep("pode mostrar a lista completa", "list_tasks", "Composite com 'lista completa'"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 2: Marcar múltiplas tarefas como feitas
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Múltiplas Tarefas Concluídas",
        description="Testa diferentes formas de marcar múltiplas tarefas",
        steps=[
            ConversationStep("feito 1 2 3", "done_task", "Espaços"),
            ConversationStep("pronto 1, 2, 3", "done_task", "Vírgulas"),
            ConversationStep("feito 1-2-3", "done_task", "Hífens"),
            ConversationStep("concluí 1 2", "done_task", "Verbo 'concluir'"),
            ConversationStep("terminei a 3 e 4", "done_task", "Linguagem natural"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 3: Progresso e status
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Verificar Progresso",
        description="Testa diferentes formas de pedir progresso/status",
        steps=[
            ConversationStep("progresso", "progress", "Formato simples"),
            ConversationStep("qual é meu progresso", "progress", "Pergunta natural"),
            ConversationStep("como estou indo", "progress", "Idioma natural"),
            ConversationStep("me mostra o status", "progress", "Com verbo 'mostrar'"),
            ConversationStep("quanto já fiz", "progress", "Pergunta informal"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 4: Tarefas em andamento
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Iniciar Tarefas",
        description="Testa diferentes formas de marcar tarefas como em andamento",
        steps=[
            ConversationStep("andamento 1", "in_progress_task", "Formato simples"),
            ConversationStep("fazendo 2", "in_progress_task", "Verbo direto"),
            ConversationStep("estou fazendo 3", "in_progress_task", "Frase natural"),
            ConversationStep("comecei a fazer 4 5", "in_progress_task", "Múltiplas tarefas"),
            ConversationStep("vou fazer 1, 2, 3", "in_progress_task", "Com vírgulas"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 5: Confirmações e respostas
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Confirmações",
        description="Testa reconhecimento de sim/não em diferentes formatos",
        steps=[
            ConversationStep("sim", "confirm_yes"),
            ConversationStep("não", "confirm_no"),
            ConversationStep("beleza", "confirm_yes"),
            ConversationStep("deixa", "confirm_no"),
            ConversationStep("👍", "confirm_yes", "Emoji positivo"),
            ConversationStep("❌", "confirm_no", "Emoji negativo"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 6: Saudações e despedidas
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Interações Básicas",
        description="Testa saudações, despedidas e agradecimentos",
        steps=[
            ConversationStep("oi", "greet"),
            ConversationStep("olá", "greet"),
            ConversationStep("e aí", "greet"),
            ConversationStep("obrigado", "thanks"),
            ConversationStep("valeu", "thanks"),
            ConversationStep("tchau", "goodbye"),
            ConversationStep("falou", "goodbye"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 7: Ajuda e tutoriais
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Ajuda e Aprendizado",
        description="Testa solicitações de ajuda e tutoriais",
        steps=[
            ConversationStep("?", "help"),
            ConversationStep("ajuda", "help"),
            ConversationStep("como usar", "help", "Pergunta sobre funcionalidade"),
            ConversationStep("tutorial", "tutorial_complete"),
            ConversationStep("me ensina", "tutorial_complete"),
            ConversationStep("básico", "tutorial_quick"),
            ConversationStep("exemplos", "show_examples"),
            ConversationStep("dicas", "show_tips"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 8: Detalha de tarefa específica
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Detalhes de Tarefa",
        description="Testa diferentes formas de pedir detalhes de uma tarefa",
        steps=[
            ConversationStep("mostra 1", "show_task"),
            ConversationStep("veja 2", "show_task"),
            ConversationStep("detalhes 3", "show_task"),
            ConversationStep("info 4", "show_task"),
            ConversationStep("1 detalhes", "show_task", "Ordem inversa"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 9: Criar tarefa nova
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Criar Tarefa",
        description="Testa diferentes formas de criar nova tarefa",
        steps=[
            ConversationStep("criar tarefa", "create_task"),
            ConversationStep("nova tarefa", "create_task"),
            ConversationStep("criar task", "create_task"),
        ]
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CONVERSA 10: Fluxo completo natural
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ConversationTest(
        name="Fluxo Completo",
        description="Simula um fluxo natural de usuário: saudação → listar → marcar → progresso → despedida",
        steps=[
            ConversationStep("opa tudo bem", "greet"),
            ConversationStep("e minhas tarefas aí", "list_tasks"),
            ConversationStep("feito 1, 2", "done_task"),
            ConversationStep("como estou indo", "progress"),
            ConversationStep("legal obrigado", "thanks"),
            ConversationStep("tchau", "goodbye"),
        ]
    ),
]


# ==============================================================================
# FUNÇÕES DE TESTE
# ==============================================================================

def test_conversation_step(step: ConversationStep) -> Tuple[bool, ParseResult]:
    """
    Testa um passo individual da conversa.

    Returns:
        (sucesso: bool, resultado: ParseResult)
    """
    result = parse(step.user_input)
    sucesso = result.intent == step.expected_intent
    return sucesso, result


def test_conversation(conv: ConversationTest) -> Dict[str, any]:
    """
    Testa uma conversa completa.

    Returns:
        Dict com estatísticas da conversa
    """
    stats = {
        "name": conv.name,
        "total_steps": len(conv.steps),
        "successful_steps": 0,
        "failed_steps": 0,
        "average_confidence": 0.0,
        "success_rate": 0.0,
        "failures": [],
    }

    confidences = []

    for step in conv.steps:
        sucesso, result = test_conversation_step(step)
        confidences.append(result.confidence)

        if sucesso:
            stats["successful_steps"] += 1
        else:
            stats["failed_steps"] += 1
            stats["failures"].append({
                "input": step.user_input,
                "expected": step.expected_intent,
                "got": result.intent,
                "confidence": result.confidence,
                "description": step.description,
            })

    # Calcular média de confiança
    if confidences:
        stats["average_confidence"] = sum(confidences) / len(confidences)

    # Calcular taxa de sucesso
    stats["success_rate"] = stats["successful_steps"] / stats["total_steps"] if stats["total_steps"] > 0 else 0

    return stats


def run_all_conversations() -> Dict[str, any]:
    """
    Executa todos os testes de conversa e coleta estatísticas.

    Returns:
        Dict com resultado agregado
    """
    all_stats = {
        "total_conversations": len(CONVERSATIONS),
        "conversations": [],
        "overall_success_rate": 0.0,
        "overall_average_confidence": 0.0,
        "total_steps": 0,
        "total_successful": 0,
        "total_failures": 0,
    }

    for conv in CONVERSATIONS:
        stats = test_conversation(conv)
        all_stats["conversations"].append(stats)
        all_stats["total_steps"] += stats["total_steps"]
        all_stats["total_successful"] += stats["successful_steps"]
        all_stats["total_failures"] += stats["failed_steps"]

    # Calcular agregados
    if all_stats["total_steps"] > 0:
        all_stats["overall_success_rate"] = all_stats["total_successful"] / all_stats["total_steps"]

    all_stats["overall_average_confidence"] = sum(
        c["average_confidence"] for c in all_stats["conversations"]
    ) / len(all_stats["conversations"]) if all_stats["conversations"] else 0

    return all_stats


def print_results(all_stats: Dict) -> None:
    """Imprime resultados em formato legível"""
    print("\n" + "=" * 80)
    print("RESULTADO DE TESTES DE CONVERSAS REALISTAS".center(80))
    print("=" * 80)

    print(f"\n📊 RESULTADO AGREGADO:")
    print(f"   Taxa de sucesso global: {all_stats['overall_success_rate']*100:.1f}%")
    print(f"   Confiança média: {all_stats['overall_average_confidence']:.2f}")
    print(f"   Total de passos: {all_stats['total_steps']}")
    print(f"   Passos bem-sucedidos: {all_stats['total_successful']}")
    print(f"   Falhas: {all_stats['total_failures']}")

    print(f"\n🔍 RESULTADO POR CONVERSA:")
    for conv_stats in all_stats["conversations"]:
        rate = conv_stats["success_rate"] * 100
        icon = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
        print(f"\n{icon} {conv_stats['name']}")
        print(f"   Taxa de sucesso: {rate:.1f}% ({conv_stats['successful_steps']}/{conv_stats['total_steps']})")
        print(f"   Confiança média: {conv_stats['average_confidence']:.2f}")

        if conv_stats["failures"]:
            print(f"   Falhas:")
            for failure in conv_stats["failures"]:
                print(f"      ❌ '{failure['input']}'")
                print(f"         Esperado: {failure['expected']}, Recebido: {failure['got']} ({failure['confidence']:.2f})")
                if failure["description"]:
                    print(f"         Contexto: {failure['description']}")

    print("\n" + "=" * 80)


# ==============================================================================
# TESTES DO PYTEST
# ==============================================================================

def test_all_conversations():
    """Teste principal do pytest"""
    all_stats = run_all_conversations()
    print_results(all_stats)

    # Assert que taxa de sucesso é no mínimo 80%
    assert all_stats["overall_success_rate"] >= 0.80, (
        f"Taxa de sucesso ({all_stats['overall_success_rate']*100:.1f}%) "
        f"abaixo do threshold de 80%"
    )

    # Assert que confiança média é no mínimo 0.80
    assert all_stats["overall_average_confidence"] >= 0.80, (
        f"Confiança média ({all_stats['overall_average_confidence']:.2f}) "
        f"abaixo do threshold de 0.80"
    )


if __name__ == "__main__":
    # Executar testes se rodar direto (não via pytest)
    all_stats = run_all_conversations()
    print_results(all_stats)
