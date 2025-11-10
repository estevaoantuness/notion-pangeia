"""
Fallback Clarification System - When NLP is uncertain, ask user for clarification

Quando a confiança está abaixo do threshold (0.75), o sistema oferece opções
para o usuário selecionar a intenção correta.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


INTENT_DESCRIPTIONS = {
    "create_task": "📝 Criar uma nova tarefa",
    "list_tasks": "📋 Ver minhas tarefas",
    "done_task": "✅ Marcar uma tarefa como concluída",
    "in_progress_task": "🔄 Iniciar uma tarefa",
    "progress": "📊 Ver meu progresso",
    "help": "💬 Ver ajuda e comandos",
    "show_more": "➕ Ver mais opções",
    "show_task": "🔍 Ver detalhes de uma tarefa",
    "greet": "👋 Saudação",
    "thanks": "🙏 Agradecimento",
    "tutorial_complete": "📚 Tutorial completo",
    "tutorial_quick": "⚡ Tutorial rápido",
    "start_from_scratch": "🚀 Como começar",
    "show_tips": "💡 Dicas e macetes",
    "show_examples": "📖 Ver exemplos",
    "goodbye": "👋 Despedida",
    "confirm_yes": "✓ Confirmação (Sim)",
    "confirm_no": "✗ Confirmação (Não)",
}


@dataclass
class ClarificationOption:
    """Opção de esclarecimento para o usuário"""
    intent: str
    emoji: str
    description: str
    confidence: float


class FallbackClarification:
    """
    Sistema de esclarecimento para quando NLP não tem certeza

    Exemplo:
        clarifier = FallbackClarification()
        options = clarifier.generate_options("qual comando", confidence=0.45, top_n=2)

        # Retorna:
        # [
        #   ClarificationOption("help", "💬", "Ver ajuda e comandos", 0.55),
        #   ClarificationOption("list_tasks", "📋", "Ver minhas tarefas", 0.42),
        # ]

        message = clarifier.format_clarification_message(options)
        # "🤔 Não entendi bem. Você quis dizer:\n1️⃣ 💬 Ver ajuda e comandos\n2️⃣ 📋 Ver minhas tarefas\n3️⃣ Outra coisa"
    """

    def __init__(self, confidence_threshold: float = 0.75):
        """
        Inicializar sistema de clarificação

        Args:
            confidence_threshold: Mínimo de confiança (abaixo disso, pedir clarificação)
        """
        self.confidence_threshold = confidence_threshold

    def should_ask_for_clarification(self, confidence: float) -> bool:
        """Verificar se deve pedir clarificação"""
        return confidence < self.confidence_threshold

    def generate_options(
        self,
        text: str,
        detected_intent: str,
        confidence: float,
        top_n: int = 2
    ) -> List[ClarificationOption]:
        """
        Gerar opções de esclarecimento baseado no texto

        Args:
            text: Texto original
            detected_intent: Intent que foi detectado
            confidence: Confiança do resultado
            top_n: Número de opções a gerar

        Returns:
            Lista de opções ordenadas por relevância
        """
        # Implementar heurísticas simples para sugerir intents relacionados
        similar_intents = self._find_similar_intents(text, detected_intent)

        options = []
        for intent, score in similar_intents[:top_n]:
            option = ClarificationOption(
                intent=intent,
                emoji=self._get_emoji(intent),
                description=INTENT_DESCRIPTIONS.get(intent, intent),
                confidence=score
            )
            options.append(option)

        return options

    def _find_similar_intents(
        self,
        text: str,
        current_intent: str
    ) -> List[Tuple[str, float]]:
        """
        Encontrar intents similares baseado no texto

        Usa heurísticas simples:
        - Se tem "tarefa" → likely list_tasks, done_task, create_task
        - Se tem "progresso" → likely progress, show_more
        - Se tem "ajuda" → likely help, tutorial
        """
        text_lower = text.lower()
        scores: Dict[str, float] = {}

        # Heurísticas por palavra-chave
        keyword_patterns = {
            "tarefa": ["list_tasks", "done_task", "create_task", "in_progress_task"],
            "progresso": ["progress", "show_more"],
            "ajuda": ["help", "tutorial_complete", "tutorial_quick"],
            "comando": ["help", "tutorial_quick"],
            "começar": ["start_from_scratch", "tutorial_complete"],
            "exemplo": ["show_examples"],
            "dica": ["show_tips"],
            "feito": ["done_task"],
            "pronto": ["done_task"],
            "fazendo": ["in_progress_task"],
            "ver": ["list_tasks", "show_more", "show_task"],
            "listar": ["list_tasks", "show_more"],
            "mais": ["show_more"],
        }

        for keyword, intents in keyword_patterns.items():
            if keyword in text_lower:
                for intent in intents:
                    scores[intent] = scores.get(intent, 0) + 0.3

        # Se nenhuma palavra-chave, sugerir intents gerais
        if not scores:
            scores = {
                "help": 0.4,
                "list_tasks": 0.35,
                "create_task": 0.3,
            }

        # Ordenar por score (descendente) e converter para lista
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents

    def _get_emoji(self, intent: str) -> str:
        """Obter emoji para um intent"""
        emojis = {
            "create_task": "📝",
            "list_tasks": "📋",
            "done_task": "✅",
            "in_progress_task": "🔄",
            "progress": "📊",
            "help": "💬",
            "show_more": "➕",
            "show_task": "🔍",
            "greet": "👋",
            "thanks": "🙏",
            "tutorial_complete": "📚",
            "tutorial_quick": "⚡",
            "start_from_scratch": "🚀",
            "show_tips": "💡",
            "show_examples": "📖",
            "goodbye": "👋",
        }
        return emojis.get(intent, "❓")

    def format_clarification_message(self, options: List[ClarificationOption]) -> str:
        """
        Formatar mensagem de clarificação para o usuário

        Args:
            options: Opções para apresentar

        Returns:
            Mensagem formatada
        """
        if not options:
            return "🤔 Desculpa, não entendi. Pode reformular?"

        lines = ["🤔 Não entendi bem. Você quis dizer:"]

        for i, option in enumerate(options, 1):
            emoji_num = f"{i}️⃣" if i <= 3 else f"{i}."
            line = f"{emoji_num} {option.description}"  # Removido option.emoji pois está duplicado
            lines.append(line)

        # Número 3 para "Outra coisa"
        next_num = len(options) + 1
        emoji_num = f"{next_num}️⃣" if next_num <= 3 else f"{next_num}."
        lines.append(f"{emoji_num} 🔄 Outra coisa")

        return "\n".join(lines)

    def get_intent_from_response(self, response: str, options: List[ClarificationOption]) -> str:
        """
        Extrair intent da resposta do usuário

        Args:
            response: Resposta do usuário (número ou texto)
            options: Opções que foram apresentadas

        Returns:
            Intent selecionado ou None se inválido
        """
        response = response.strip().lower()

        # Tentar mapear número para opção
        try:
            idx = int(response.replace(".", "").replace("️⃣", "")) - 1
            if 0 <= idx < len(options):
                return options[idx].intent
        except ValueError:
            pass

        # Tentar encontrar por nome/descrição
        response_lower = response.lower()
        for option in options:
            if response_lower in option.intent.lower() or response_lower in option.description.lower():
                return option.intent

        return None


# Instância global
_clarifier: FallbackClarification = None


def get_clarifier(threshold: float = 0.75) -> FallbackClarification:
    """Obter instância global do clarifier"""
    global _clarifier
    if _clarifier is None:
        _clarifier = FallbackClarification(confidence_threshold=threshold)
    return _clarifier


def should_clarify(confidence: float, threshold: float = 0.75) -> bool:
    """Verificar se deve pedir clarificação"""
    return get_clarifier(threshold).should_ask_for_clarification(confidence)


def generate_clarification(
    text: str,
    detected_intent: str,
    confidence: float,
    top_n: int = 2,
    threshold: float = 0.75
) -> str:
    """
    Gerar mensagem de clarificação se necessário

    Args:
        text: Texto original
        detected_intent: Intent detectado
        confidence: Confiança
        top_n: Número de opções
        threshold: Threshold de confiança

    Returns:
        Mensagem de clarificação (vazia se confidence >= threshold)
    """
    clarifier = get_clarifier(threshold)

    if not clarifier.should_ask_for_clarification(confidence):
        return ""

    options = clarifier.generate_options(text, detected_intent, confidence, top_n)
    return clarifier.format_clarification_message(options)
