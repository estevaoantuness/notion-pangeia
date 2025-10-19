"""
Complexity Estimator - Estimador de Complexidade de Tarefas.

Analisa tarefas e estima complexidade baseado em múltiplos fatores.
"""

import logging
import re
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class ComplexityFactor(Enum):
    """Fatores que influenciam complexidade."""
    LENGTH = "length"  # Tamanho da descrição
    TECHNICAL_TERMS = "technical_terms"  # Termos técnicos
    DEPENDENCIES = "dependencies"  # Menções a dependências
    UNCERTAINTY = "uncertainty"  # Palavras de incerteza
    SCOPE = "scope"  # Amplitude (palavras como "todos", "sistema completo")


class ComplexityEstimator:
    """
    Estima complexidade de uma tarefa baseado em análise de texto.
    """

    # Termos técnicos que indicam complexidade
    TECHNICAL_TERMS = {
        # Backend
        "api", "database", "migration", "query", "schema", "orm",
        "authentication", "authorization", "jwt", "oauth", "encryption",
        "websocket", "microservice", "serverless", "cache", "redis",

        # Frontend
        "component", "state", "redux", "context", "hooks", "rendering",
        "responsive", "accessibility", "seo", "webpack", "bundle",

        # DevOps
        "deploy", "ci/cd", "docker", "kubernetes", "terraform",
        "monitoring", "logging", "metrics", "scaling",

        # Data
        "etl", "pipeline", "analytics", "machine learning", "model",
        "training", "inference", "feature engineering",

        # Arquitetura
        "architecture", "design pattern", "refactoring", "optimization",
        "performance", "scalability", "distributed", "concurrent"
    }

    # Palavras que indicam incerteza/complexidade
    UNCERTAINTY_WORDS = {
        "investigar", "pesquisar", "explorar", "descobrir", "avaliar",
        "analisar", "estudar", "entender", "aprender", "definir",
        "pode", "talvez", "possivelmente", "eventualmente", "se necessário"
    }

    # Palavras que indicam escopo amplo
    SCOPE_WORDS = {
        "completo", "todo", "todos", "inteiro", "sistema", "plataforma",
        "aplicação", "produto", "end-to-end", "full", "comprehensive",
        "multiple", "vários", "diversos"
    }

    # Palavras que indicam dependências
    DEPENDENCY_WORDS = {
        "depende", "requer", "precisa", "necessita", "aguardar",
        "após", "antes", "junto com", "em conjunto", "integrar",
        "conectar", "vincular", "combinar"
    }

    def __init__(self):
        """Inicializa o estimador."""
        logger.info("ComplexityEstimator inicializado")

    def estimate_complexity(
        self,
        task_description: str,
        context: Dict = None
    ) -> Dict:
        """
        Estima complexidade de uma tarefa.

        Args:
            task_description: Descrição da tarefa
            context: Contexto adicional (opcional)

        Returns:
            Dict com análise de complexidade
        """
        context = context or {}

        # Normalizar texto
        text = task_description.lower()

        # Analisar fatores
        factors = {}

        # Fator 1: Tamanho
        word_count = len(text.split())
        factors[ComplexityFactor.LENGTH] = min(word_count / 50, 1.0)  # Normalizado 0-1

        # Fator 2: Termos técnicos
        technical_count = sum(
            1 for term in self.TECHNICAL_TERMS
            if term in text
        )
        factors[ComplexityFactor.TECHNICAL_TERMS] = min(technical_count / 5, 1.0)

        # Fator 3: Incerteza
        uncertainty_count = sum(
            1 for word in self.UNCERTAINTY_WORDS
            if word in text
        )
        factors[ComplexityFactor.UNCERTAINTY] = min(uncertainty_count / 3, 1.0)

        # Fator 4: Escopo
        scope_count = sum(
            1 for word in self.SCOPE_WORDS
            if word in text
        )
        factors[ComplexityFactor.SCOPE] = min(scope_count / 2, 1.0)

        # Fator 5: Dependências
        dependency_count = sum(
            1 for word in self.DEPENDENCY_WORDS
            if word in text
        )
        factors[ComplexityFactor.DEPENDENCIES] = min(dependency_count / 2, 1.0)

        # Calcular score final (média ponderada)
        weights = {
            ComplexityFactor.LENGTH: 0.15,
            ComplexityFactor.TECHNICAL_TERMS: 0.30,
            ComplexityFactor.UNCERTAINTY: 0.20,
            ComplexityFactor.SCOPE: 0.20,
            ComplexityFactor.DEPENDENCIES: 0.15
        }

        total_score = sum(
            factors[factor] * weights[factor]
            for factor in factors
        )

        # Classificar complexidade
        if total_score < 0.2:
            complexity = "trivial"
            estimated_hours = 0.25  # 15min
        elif total_score < 0.4:
            complexity = "easy"
            estimated_hours = 0.5  # 30min
        elif total_score < 0.6:
            complexity = "medium"
            estimated_hours = 2.0  # 2h
        elif total_score < 0.8:
            complexity = "hard"
            estimated_hours = 6.0  # 6h
        else:
            complexity = "very_hard"
            estimated_hours = 16.0  # 2 dias

        return {
            "complexity": complexity,
            "confidence_score": total_score,
            "estimated_hours": estimated_hours,
            "factors": {
                factor.value: score
                for factor, score in factors.items()
            },
            "signals": {
                "technical_terms_found": technical_count,
                "uncertainty_indicators": uncertainty_count,
                "scope_indicators": scope_count,
                "dependency_indicators": dependency_count,
                "word_count": word_count
            }
        }

    def compare_tasks(
        self,
        task_descriptions: List[str]
    ) -> List[Dict]:
        """
        Compara complexidade de múltiplas tarefas.

        Args:
            task_descriptions: Lista de descrições

        Returns:
            Lista de análises ordenadas por complexidade (mais fácil primeiro)
        """
        analyses = [
            {
                "description": desc,
                **self.estimate_complexity(desc)
            }
            for desc in task_descriptions
        ]

        # Ordenar por score (mais fácil primeiro)
        analyses.sort(key=lambda x: x["confidence_score"])

        return analyses

    def suggest_simplification(
        self,
        task_description: str
    ) -> List[str]:
        """
        Sugere formas de simplificar uma tarefa complexa.

        Args:
            task_description: Descrição da tarefa

        Returns:
            Lista de sugestões
        """
        analysis = self.estimate_complexity(task_description)
        suggestions = []

        # Sugestões baseadas em fatores
        factors = analysis["factors"]

        if factors.get("scope", 0) > 0.5:
            suggestions.append(
                "Escopo muito amplo. Considere quebrar em fases ou módulos menores."
            )

        if factors.get("uncertainty", 0) > 0.5:
            suggestions.append(
                "Muita incerteza detectada. Faça uma spike/pesquisa inicial antes."
            )

        if factors.get("technical_terms", 0) > 0.7:
            suggestions.append(
                "Muita complexidade técnica. Considere protótipo ou POC primeiro."
            )

        if factors.get("dependencies", 0) > 0.5:
            suggestions.append(
                "Muitas dependências. Mapeie dependências críticas e resolva primeiro."
            )

        if analysis["confidence_score"] > 0.7:
            suggestions.append(
                "Task muito complexa. Quebre em 3-5 subtarefas menores."
            )

        if not suggestions:
            suggestions.append("Task parece bem definida. Pode seguir em frente!")

        return suggestions
