#!/usr/bin/env python3
"""
==============================================================================
NORMALIZADOR E PARSER DE MENSAGENS (NLP - PT-BR)
==============================================================================
Sistema robusto de normalização e parsing de linguagem natural em português

Funcionalidades:
- Remoção de acentos e normalização Unicode
- Redução de alongamentos (ex: "oiiiii" -> "oii")
- Remoção de emojis (opcional)
- Normalização de pontuação
- Conversão de números por extenso
- Mapeamento de sinônimos
- Parsing de intenções com regex patterns
- Fuzzy matching para equivalência de textos
- Extração de entidades (números, motivos, etc)

Autor: Pangeia Bot
Data: 2025
==============================================================================
"""

import re
import unicodedata
from typing import Dict, Optional, Tuple, Any, List, Set
from dataclasses import dataclass
import logging

# Tentar importar rapidfuzz para melhor fuzzy matching
try:
    from rapidfuzz import fuzz, process
    HAVE_RAPIDFUZZ = True
except ImportError:
    from difflib import SequenceMatcher
    HAVE_RAPIDFUZZ = False

# ==============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ==============================================================================

# Números por extenso (cardinais e ordinais)
NUM_WORDS_PT = {
    # Cardinais
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2,
    "tres": 3, "três": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    # Ordinais
    "primeiro": 1, "primeira": 1, "segundo": 2, "segunda": 2,
    "terceiro": 3, "terceira": 3, "quarto": 4, "quarta": 4,
    "quinto": 5, "quinta": 5, "sexto": 6, "sexta": 6,
    "setimo": 7, "sétimo": 7, "oitavo": 8, "nono": 9,
    "decimo": 10, "décimo": 10,
}

# Confirmações positivas
YES_SET: Set[str] = {
    "sim", "s", "ok", "okay", "okey", "isso", "pode", "manda ver", "beleza", "blz",
    "confirmo", "confirmar", "isso mesmo", "vamos",
    "👍", "✅", "✓"
}

# Confirmações negativas
NO_SET: Set[str] = {
    "nao", "não", "n", "agora nao", "agora não",
    "deixa", "cancelar", "cancela",
    "❌", "🚫", "✗"
}

# Mapa de sinônimos (palavra -> palavra canônica)
SYNONYM_MAP = {
    # Saudações
    "ola": "oi", "olá": "oi", "opa": "oi", "e ai": "oi", "e aii": "oi", "e aiii": "oi",
    "eae": "oi", "salve": "oi", "fala": "oi", "opaaa": "oi",
    "bom dia": "oi", "boa tarde": "oi", "boa noite": "oi",

    # Comandos - Tarefas concluídas
    "conclui": "feito", "concluí": "feito", "concluida": "feito", "concluído": "feito",
    "finalizei": "feito", "finalizado": "feito", "finalizada": "feito",
    "terminei": "feito", "foi feita": "feito", "completei": "feito",
    "completo": "feito", "completa": "feito",
    "pronto": "feito", "pronta": "feito", "feita": "feito",
    "done": "feito", "✓": "feito", "✅": "feito",

    # Comandos - Tarefas em andamento
    "vou comecar": "andamento", "vou começar": "andamento",
    "iniciar": "andamento", "iniciei": "andamento", "iniciado": "andamento", "iniciada": "andamento",
    "comecando": "andamento", "começando": "andamento",
    "comecei": "andamento", "fazendo": "andamento",
    "comecar": "andamento", "começar": "andamento",
    "trabalhando": "andamento", "em progresso": "andamento",
    "progress": "andamento", "wip": "andamento",
    "⏳": "andamento", "🔄": "andamento",

    # Comandos - Tarefas bloqueadas
    "bloqueado": "bloqueada", "travou": "bloqueada", "travado": "bloqueada",
    "travada": "bloqueada", "impedido": "bloqueada", "impedida": "bloqueada",
    "parado": "bloqueada", "parada": "bloqueada",
    "nao consigo": "bloqueada", "não consigo": "bloqueada",
    "bloqueio": "bloqueada", "trava": "bloqueada",
    "blocked": "bloqueada", "⛔": "bloqueada",

    # Comandos - Listar tarefas
    "lista": "tarefas", "tasks": "tarefas",
    "minhas tarefas": "tarefas", "meus itens": "tarefas",
    "ver tarefas": "tarefas", "mostrar tarefas": "tarefas",
    "quais tarefas": "tarefas", "o que tenho": "tarefas",
    "o que falta": "tarefas",

    # Comandos - Ver mais
    "mostrar mais": "ver mais",
    "todas": "ver mais", "completa": "ver mais", "lista completa": "ver mais",

    # Comandos - Progresso
    "status": "progresso",
    "quanto falta": "progresso", "como estou": "progresso",
    "como está": "progresso", "como esta": "progresso",
    "resumo": "progresso",

    # Comandos - Ajuda
    "help": "ajuda", "comandos": "ajuda",
    "comando": "ajuda", "como usar": "ajuda", "como uso": "ajuda",

    # Despedidas
    "tchau": "ate", "falou": "ate", "até logo": "ate",
    "ate logo": "ate", "até mais": "ate", "ate mais": "ate",

    # Agradecimentos
    "obrigado": "thanks", "obrigada": "thanks", "brigado": "thanks",
    "brigada": "thanks", "vlw": "thanks",
}

# Padrões regex para remover/normalizar
PUNCT_PATTERN = re.compile(r"[^\w\s@#:+\-]")  # mantém @ # : + -
MULTISPACE = re.compile(r"\s+")
EMOJI_PATTERN = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map
    u"\U0001F1E0-\U0001F1FF"  # flags
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE
)

# ==============================================================================
# CLASSES DE DADOS
# ==============================================================================

@dataclass
class ParseResult:
    """Resultado do parsing de uma mensagem"""
    intent: str
    entities: Dict[str, Any]
    confidence: float
    normalized_text: str
    original_text: str

    def is_confident(self, threshold: float = 0.75) -> bool:
        """Verifica se a confiança está acima do threshold"""
        return self.confidence >= threshold

    def __repr__(self) -> str:
        return f"ParseResult(intent='{self.intent}', confidence={self.confidence:.2f}, entities={self.entities})"


# ==============================================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ==============================================================================

def strip_accents(text: str) -> str:
    """
    Remove acentos de caracteres Unicode
    Ex: "São Paulo" -> "Sao Paulo"
    """
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def reduce_elongations(text: str, max_repeats: int = 2) -> str:
    """
    Reduz caracteres repetidos para no máximo 2
    Ex: "oiiiii!!!" -> "oii!!"
    """
    return re.sub(r"(.)\1{" + str(max_repeats) + r",}", r"\1" * max_repeats, text)


def remove_emoji(text: str, keep_common: bool = True) -> str:
    """
    Remove emojis do texto
    Se keep_common=True, mantém emojis comuns (👍, ✅, ❌)
    """
    if keep_common:
        # Preservar emojis comuns de confirmação
        preserved_emojis = ["👍", "✅", "❌", "🚫", "✓", "✗"]
        for emoji in preserved_emojis:
            text = text.replace(emoji, f" _EMOJI_{ord(emoji)}_ ")

        # Remover outros emojis
        text = EMOJI_PATTERN.sub(" ", text)

        # Restaurar emojis preservados
        for emoji in preserved_emojis:
            text = text.replace(f"_EMOJI_{ord(emoji)}_", emoji)

        return text
    else:
        return EMOJI_PATTERN.sub(" ", text)


def base_normalize(text: str, remove_emojis: bool = False, keep_special_chars: bool = True) -> str:
    """
    Normalização básica: lowercase, acentos, pontuação, espaços

    Args:
        text: Texto a normalizar
        remove_emojis: Se True, remove emojis (mantém comuns de confirmação)
        keep_special_chars: Se True, preserva "?" antes de remover pontuação
    """
    t = text.strip().lower()

    # Preservar "?" como token especial antes de normalização
    is_question_mark = (t == "?")

    t = strip_accents(t)
    t = reduce_elongations(t, max_repeats=2)

    if remove_emojis:
        t = remove_emoji(t, keep_common=True)

    # Preservar emojis comuns antes de remover pontuação
    preserved_tokens = []
    if "👍" in t:
        preserved_tokens.append("👍")
        t = t.replace("👍", " _THUMBSUP_ ")
    if "✅" in t:
        preserved_tokens.append("✅")
        t = t.replace("✅", " _CHECKMARK_ ")
    if "❌" in t:
        preserved_tokens.append("❌")
        t = t.replace("❌", " _CROSSMARK_ ")

    t = PUNCT_PATTERN.sub(" ", t)  # remove pontuação
    t = MULTISPACE.sub(" ", t).strip()  # normaliza espaços

    # Restaurar tokens preservados
    if is_question_mark:
        return "?"
    t = t.replace("_THUMBSUP_", "👍")
    t = t.replace("_CHECKMARK_", "✅")
    t = t.replace("_CROSSMARK_", "❌")

    return t


def words_to_number(token: str) -> Optional[int]:
    """
    Converte palavra numérica para número
    Ex: "tres" -> 3, "primeiro" -> 1
    """
    return NUM_WORDS_PT.get(token)


def normalize_numbers(text: str) -> str:
    """
    Converte números por extenso em dígitos
    Ex: "feito tres" -> "feito 3"
    """
    tokens = text.split()
    out: List[str] = []

    for tok in tokens:
        if tok.isdigit():
            out.append(tok)
        else:
            n = words_to_number(tok)
            out.append(str(n) if n is not None else tok)

    return " ".join(out)


def apply_synonym_map(text: str) -> str:
    """
    Aplica mapeamento de sinônimos palavra a palavra
    Ex: "lista" -> "minhas tarefas"
    """
    # Primeiro tenta matches multi-palavra (exato)
    for src, tgt in sorted(SYNONYM_MAP.items(), key=lambda x: -len(x[0])):
        # Match de palavra inteira (início/fim ou cercada por espaços)
        if text == src:
            return tgt
        # Match com espaços ao redor
        pattern = f" {src} "
        if pattern in f" {text} ":
            text = f" {text} ".replace(pattern, f" {tgt} ").strip()

    return text


def canonicalize(text: str, remove_emojis: bool = False) -> str:
    """
    Pipeline completo de normalização e canonicalização

    1. Normalização básica (lowercase, acentos, pontuação)
    2. Conversão de números por extenso
    3. Mapeamento de sinônimos

    Ex: "Concluí a terceira!!!" -> "feito 3"
    """
    # 1. Normalização básica
    t = base_normalize(text, remove_emojis=remove_emojis)

    # 2. Números por extenso
    t = normalize_numbers(t)

    # 3. Sinônimos
    t = apply_synonym_map(t)

    return t.strip()


# ==============================================================================
# EQUIVALÊNCIA E FUZZY MATCHING
# ==============================================================================

def texts_equivalent(a: str, b: str, threshold: int = 92) -> bool:
    """
    Verifica se dois textos são equivalentes após normalização

    Args:
        a: Primeiro texto
        b: Segundo texto
        threshold: Threshold de similaridade (0-100)

    Returns:
        True se textos são equivalentes

    Examples:
        >>> texts_equivalent("Olá", "oi")
        True
        >>> texts_equivalent("feito 3", "finalizei a terceira")
        True
    """
    ca, cb = canonicalize(a), canonicalize(b)

    # Match exato
    if ca == cb:
        return True

    # Fuzzy matching
    if HAVE_RAPIDFUZZ:
        return fuzz.token_sort_ratio(ca, cb) >= threshold
    else:
        # Fallback com difflib
        return (SequenceMatcher(None, ca, cb).ratio() * 100) >= threshold


def find_best_match(query: str, choices: List[str], threshold: int = 80) -> Optional[Tuple[str, float]]:
    """
    Encontra o melhor match em uma lista de escolhas

    Returns:
        (melhor_match, score) ou None se nenhum match acima do threshold
    """
    query_norm = canonicalize(query)

    if HAVE_RAPIDFUZZ:
        result = process.extractOne(query_norm, [canonicalize(c) for c in choices])
        if result and result[1] >= threshold:
            idx = [canonicalize(c) for c in choices].index(result[0])
            return choices[idx], result[1]
    else:
        best_match = None
        best_score = 0.0
        for choice in choices:
            score = SequenceMatcher(None, query_norm, canonicalize(choice)).ratio() * 100
            if score > best_score and score >= threshold:
                best_score = score
                best_match = choice

        if best_match:
            return best_match, best_score

    return None


# ==============================================================================
# PATTERNS E PARSING DE INTENÇÕES
# ==============================================================================

CommandPattern = Tuple[str, re.Pattern, float]

# Padrões ordenados por especificidade (mais específico primeiro)
PATTERNS: List[CommandPattern] = [
    # Tarefas com motivo de bloqueio (mais específico)
    ("blocked_task", re.compile(r"^(bloqueada)\s+(\d+)\s*(?:-|—|:|,)+\s*(.+)$"), 0.99),
    ("blocked_task", re.compile(r"^(\d+)\s+(bloqueada)\s*(?:-|—|:|,)+\s*(.+)$"), 0.99),

    # Tarefas - aceita UM ou VÁRIOS números
    # Ex: "feito 1", "feito 1 2 3", "1 2 3 feito"
    ("done_task", re.compile(r"^(feito|pronto|pronta)\s+((?:\d+\s*)+)$"), 0.99),
    ("done_task", re.compile(r"^((?:\d+\s*)+)\s+(feito|pronto|pronta|concluida)$"), 0.99),

    ("in_progress_task", re.compile(r"^(andamento|fazendo)\s+((?:\d+\s*)+)$"), 0.99),
    ("in_progress_task", re.compile(r"^((?:\d+\s*)+)\s+(andamento|fazendo)$"), 0.99),

    ("blocked_task_no_reason", re.compile(r"^(bloqueada)\s+(\d+)$"), 0.90),
    ("blocked_task_no_reason", re.compile(r"^(\d+)\s+(bloqueada)$"), 0.90),

    # Mostrar detalhes de tarefa
    ("show_task", re.compile(r"^(mostre?|mostra|ver|veja|abra?|detalhes?|info)\s+(?:a\s+)?(\d+)$"), 0.99),
    ("show_task", re.compile(r"^(\d+)\s+(detalhes?|info)$"), 0.99),

    # Comandos simples
    ("list_tasks", re.compile(r"^(tarefas)$"), 0.98),
    ("list_tasks", re.compile(r"^(lista|minhas tarefas)$"), 0.98),
    ("show_more", re.compile(r"^(ver mais|mais|mostrar mais|todas|completa|lista completa)$"), 0.98),
    ("progress", re.compile(r"^(progresso)$"), 0.98),
    ("help", re.compile(r"^(ajuda|\?)$"), 0.95),

    # Confirmações (incluindo emojis)
    ("confirm_yes", re.compile(r"^(sim|s|isso|pode|ok|okay|okey|manda ver|beleza|blz|confirmo|vamos|👍|✅)$"), 0.98),
    ("confirm_no", re.compile(r"^(nao|n|agora nao|deixa|cancelar|cancela|❌)$"), 0.98),

    # Saudações e despedidas
    ("greet", re.compile(r"^(oi|opa|opaaa|salve)$"), 0.95),
    ("goodbye", re.compile(r"^(ate|falou)$"), 0.95),
    ("thanks", re.compile(r"^(thanks|valeu)$"), 0.95),

    # Criar tarefa
    ("create_task", re.compile(r"^(criar tarefa|nova tarefa)$"), 0.95),

    # Smalltalk (mas não "beleza" sozinho que é confirmação)
    ("smalltalk_mood", re.compile(r"^(tudo bem|como vai|de boa)$"), 0.90),
]


def extract_task_entities(intent: str, match_groups: tuple) -> Dict[str, Any]:
    """
    Extrai entidades de comandos relacionados a tarefas
    """
    entities: Dict[str, Any] = {}

    # Comandos de tarefas (done_task ou in_progress_task)
    if intent in {"done_task", "in_progress_task"}:
        # Encontra o grupo que contém os números
        for g in match_groups:
            if g and re.match(r"^\d+", g.strip()):
                # Extrai todos os números
                numbers = [int(n) for n in g.split() if n.strip().isdigit()]
                if numbers:
                    # Se for apenas 1 número, usa "index" (mantém compatibilidade)
                    # Se forem vários, usa "indices"
                    if len(numbers) == 1:
                        entities["index"] = numbers[0]
                    else:
                        entities["indices"] = numbers
                break
        return entities

    # Comandos de bloqueio
    if intent in {"blocked_task", "blocked_task_no_reason"}:
        # Extrair índice (número da tarefa)
        nums = [g for g in match_groups if g and g.strip() and g.strip().isdigit()]
        if nums:
            entities["index"] = int(nums[0].strip())

        # Extrair motivo do bloqueio (se presente)
        if intent == "blocked_task":
            # Filtra grupos vazios e remove palavras-chave de comando
            reasons = [
                g for g in match_groups
                if g and g.strip() and not g.strip().isdigit()
                and g.strip() not in {"bloqueada", "bloqueado", "a", "a "}
            ]
            if reasons:
                entities["reason"] = reasons[-1].strip()

    return entities


def parse(text: str, log_result: bool = False) -> ParseResult:
    """
    Parse uma mensagem e retorna a intenção detectada

    Args:
        text: Texto original da mensagem
        log_result: Se True, loga o resultado

    Returns:
        ParseResult com intent, entities, confidence, etc.

    Examples:
        >>> parse("finalizei a terceira")
        ParseResult(intent='done_task', confidence=0.99, entities={'index': 3})

        >>> parse("bloqueada 4 - sem acesso")
        ParseResult(intent='blocked_task', confidence=0.99, entities={'index': 4, 'reason': 'sem acesso'})
    """
    original = text
    normalized = canonicalize(text)

    # 1) Tentar match com padrões regex (alta confiança)
    for intent, rgx, confidence in PATTERNS:
        m = rgx.match(normalized)
        if m:
            groups = m.groups()
            entities = extract_task_entities(intent, groups)

            result = ParseResult(
                intent=intent,
                entities=entities,
                confidence=confidence,
                normalized_text=normalized,
                original_text=original
            )

            if log_result:
                logging.info(f"Parsed: {result}")

            return result

    # 2) Heurísticas para intents por palavras-chave (média confiança)
    tokens = normalized.split()
    if not tokens:
        return ParseResult("unknown", {}, 0.0, normalized, original)

    first_tokens = " ".join(tokens[:2])

    # Saudações
    if any(tok in {"oi", "opa", "salve", "e", "bom", "boa"} for tok in tokens[:2]):
        return ParseResult("greet", {}, 0.85, normalized, original)

    # Agradecimentos
    if any(tok in {"valeu", "brigado", "obrigado", "thanks"} for tok in tokens):
        return ParseResult("thanks", {}, 0.85, normalized, original)

    # Comandos incompletos (baixa confiança)
    if "feito" in first_tokens or "pronto" in first_tokens:
        return ParseResult("done_task", {}, 0.60, normalized, original)

    if "andamento" in first_tokens or "fazendo" in first_tokens:
        return ParseResult("in_progress_task", {}, 0.60, normalized, original)

    if "bloqueada" in first_tokens:
        return ParseResult("blocked_task_no_reason", {}, 0.60, normalized, original)

    # 3) Unknown
    return ParseResult(
        intent="unknown",
        entities={"normalized": normalized},
        confidence=0.3,
        normalized_text=normalized,
        original_text=original
    )


# ==============================================================================
# UTILITÁRIOS DE CONFIRMAÇÃO
# ==============================================================================

def is_confirmation(text: str) -> Optional[bool]:
    """
    Verifica se o texto é uma confirmação sim/não

    Returns:
        True para sim, False para não, None para ambíguo
    """
    norm = canonicalize(text)

    if norm in YES_SET:
        return True

    if norm in NO_SET:
        return False

    # Fuzzy check
    for yes_word in YES_SET:
        if texts_equivalent(norm, yes_word, threshold=90):
            return True

    for no_word in NO_SET:
        if texts_equivalent(norm, no_word, threshold=90):
            return False

    return None


# ==============================================================================
# TESTES RÁPIDOS
# ==============================================================================

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("TESTANDO NORMALIZER")
    print("=" * 80)
    print()

    test_cases = [
        "Olá!!!",
        "e aííí",
        "finalizei a terceira",
        "bloqueada 4 - sem acesso",
        "vou começar a 2",
        "minhas tarefas",
        "progresso",
        "👍",
        "feito tres",
    ]

    for test in test_cases:
        result = parse(test, log_result=False)
        print(f"Input:  '{test}'")
        print(f"Norm:   '{result.normalized_text}'")
        print(f"Intent: {result.intent} (conf: {result.confidence:.2f})")
        print(f"Entities: {result.entities}")
        print()

    print("=" * 80)
    print("TESTANDO EQUIVALÊNCIA")
    print("=" * 80)
    print()

    equiv_tests = [
        ("Olá", "oi"),
        ("finalizei a 3", "feito 3"),
        ("vou começar 2", "andamento 2"),
        ("bloqueada 4 - sem acesso", "bloqueada 4: sem acesso"),
    ]

    for a, b in equiv_tests:
        result = texts_equivalent(a, b)
        print(f"'{a}' ≈ '{b}': {result}")
