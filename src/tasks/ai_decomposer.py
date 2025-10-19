"""
AI Task Decomposer - Decomposição Inteligente de Tarefas.

Sistema que usa GPT-4 para quebrar tasks grandes e complexas em
micro-tasks acionáveis, com estimativas de tempo e dificuldade.
"""

import logging
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import timedelta

from config.openai_config import client, GPT_MODEL

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Níveis de complexidade de uma task."""
    TRIVIAL = "trivial"  # < 10 min
    EASY = "easy"  # 10-30 min
    MEDIUM = "medium"  # 30min-2h
    HARD = "hard"  # 2h-8h
    VERY_HARD = "very_hard"  # > 1 dia


@dataclass
class SubTask:
    """Representa uma subtask decomposta."""
    title: str
    description: str
    estimated_minutes: int
    complexity: TaskComplexity
    order: int  # Ordem de execução (1, 2, 3...)
    dependencies: List[int] = field(default_factory=list)  # Índices de subtasks que devem vir antes
    tips: List[str] = field(default_factory=list)  # Dicas para completar
    potential_blockers: List[str] = field(default_factory=list)  # Possíveis bloqueios


class AITaskDecomposer:
    """
    Decompositor inteligente de tasks usando GPT-4.

    Quebra tasks complexas em subtasks acionáveis com:
    - Estimativa de tempo
    - Classificação de dificuldade
    - Mapeamento de dependências
    - Dicas e alertas
    """

    DECOMPOSITION_PROMPT = """Você é um expert em decomposição de tarefas e gerenciamento de projetos.

Sua missão: Pegar uma tarefa grande e complexa e quebrá-la em subtarefas pequenas e acionáveis.

REGRAS:
1. Cada subtask deve ser CONCRETA e ACIONÁVEL (não vaga)
2. Subtasks devem seguir ordem lógica
3. Estimar tempo REALISTICAMENTE (não otimista demais)
4. Identificar DEPENDÊNCIAS entre subtasks
5. Alertar sobre POSSÍVEIS BLOQUEIOS
6. Dar DICAS práticas para completar cada subtask

TAREFA A DECOMPOR:
"{task_description}"

CONTEXTO ADICIONAL (se houver):
{context}

Retorne um JSON com este formato EXATO:

{{
  "subtasks": [
    {{
      "title": "Título curto da subtask",
      "description": "Descrição detalhada do que fazer",
      "estimated_minutes": 30,
      "complexity": "easy|medium|hard",
      "order": 1,
      "dependencies": [],
      "tips": ["Dica 1", "Dica 2"],
      "potential_blockers": ["Possível bloqueio 1"]
    }}
  ],
  "total_estimated_hours": 5.5,
  "critical_path": [1, 3, 5],
  "parallel_opportunities": [[2, 4]],
  "overall_complexity": "medium|hard|very_hard"
}}

IMPORTANTE:
- Mínimo 3 subtasks, máximo 12
- Seja REALISTA com estimativas
- Dependencies são array de números (order de outras subtasks)
- critical_path são as subtasks no caminho crítico
- parallel_opportunities são subtasks que podem ser feitas em paralelo

Retorne APENAS o JSON, sem texto adicional."""

    def __init__(self):
        """Inicializa o decompositor."""
        self.decomposition_cache: Dict[str, Dict] = {}
        logger.info("AITaskDecomposer inicializado")

    def decompose_task(
        self,
        task_description: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Decompõe task usando GPT-4.

        Args:
            task_description: Descrição da task a decompor
            context: Contexto adicional (projeto, recursos, prazos, etc.)

        Returns:
            Dict com subtasks e metadata
        """
        try:
            # Verificar cache
            cache_key = f"{task_description}:{json.dumps(context or {})}"
            if cache_key in self.decomposition_cache:
                logger.info("Decomposição encontrada em cache")
                return self.decomposition_cache[cache_key]

            # Preparar contexto
            context_str = ""
            if context:
                context_str = "\n".join(
                    f"- {key}: {value}"
                    for key, value in context.items()
                )

            # Montar prompt
            prompt = self.DECOMPOSITION_PROMPT.format(
                task_description=task_description,
                context=context_str or "Nenhum contexto adicional"
            )

            logger.info(f"Decomondo task: '{task_description[:50]}...'")

            # Chamar GPT-4
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Usar GPT-4 para melhor qualidade
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um expert em decomposição de tarefas. Retorna apenas JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Baixa para ser consistente
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Extrair resposta
            result_text = response.choices[0].message.content.strip()

            # Parse JSON
            result = json.loads(result_text)

            # Validar estrutura
            if "subtasks" not in result:
                raise ValueError("Resposta não contém 'subtasks'")

            # Converter complexidades para enum
            for subtask in result["subtasks"]:
                complexity_str = subtask.get("complexity", "medium")
                subtask["complexity"] = TaskComplexity(complexity_str)

            # Cache resultado
            self.decomposition_cache[cache_key] = result

            logger.info(
                f"Task decomposta em {len(result['subtasks'])} subtasks "
                f"(~{result.get('total_estimated_hours', 0):.1f}h)"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da resposta GPT-4: {e}")
            logger.error(f"Resposta recebida: {result_text}")
            return self._fallback_decomposition(task_description)

        except Exception as e:
            logger.error(f"Erro ao decompor task: {e}")
            return self._fallback_decomposition(task_description)

    def _fallback_decomposition(self, task_description: str) -> Dict:
        """Fallback se GPT-4 falhar."""
        return {
            "subtasks": [
                {
                    "title": "Planejar abordagem",
                    "description": f"Planejar como executar: {task_description}",
                    "estimated_minutes": 15,
                    "complexity": TaskComplexity.EASY,
                    "order": 1,
                    "dependencies": [],
                    "tips": ["Quebrar em partes menores"],
                    "potential_blockers": []
                },
                {
                    "title": "Executar tarefa",
                    "description": task_description,
                    "estimated_minutes": 60,
                    "complexity": TaskComplexity.MEDIUM,
                    "order": 2,
                    "dependencies": [1],
                    "tips": ["Focar em fazer, não em perfeccionar"],
                    "potential_blockers": []
                },
                {
                    "title": "Revisar resultado",
                    "description": "Revisar e validar o trabalho feito",
                    "estimated_minutes": 15,
                    "complexity": TaskComplexity.EASY,
                    "order": 3,
                    "dependencies": [2],
                    "tips": ["Verificar se atende requisitos"],
                    "potential_blockers": []
                }
            ],
            "total_estimated_hours": 1.5,
            "critical_path": [1, 2, 3],
            "parallel_opportunities": [],
            "overall_complexity": "medium"
        }

    def format_decomposition_for_display(
        self,
        decomposition: Dict,
        show_details: bool = True
    ) -> str:
        """
        Formata decomposição para exibição legível.

        Args:
            decomposition: Resultado de decompose_task()
            show_details: Se True, mostra detalhes completos

        Returns:
            String formatada para exibir
        """
        subtasks = decomposition.get("subtasks", [])
        total_hours = decomposition.get("total_estimated_hours", 0)

        # Cabeçalho
        lines = [
            f"📋 **DECOMPOSIÇÃO DA TAREFA**",
            f"🕐 Tempo total estimado: **{total_hours:.1f}h**",
            f"📊 Complexidade: **{decomposition.get('overall_complexity', 'medium')}**",
            f"📝 {len(subtasks)} subtarefas",
            ""
        ]

        # Subtasks
        for idx, subtask in enumerate(subtasks, 1):
            complexity = subtask.get("complexity")
            if isinstance(complexity, TaskComplexity):
                complexity_str = complexity.value
            else:
                complexity_str = str(complexity)

            # Emoji de complexidade
            complexity_emoji = {
                "trivial": "⚪",
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🟠",
                "very_hard": "🔴"
            }.get(complexity_str, "⚪")

            lines.append(
                f"{idx}. {complexity_emoji} **{subtask['title']}** "
                f"({subtask.get('estimated_minutes', 0)}min)"
            )

            if show_details:
                lines.append(f"   💬 {subtask.get('description', '')}")

                # Dependencies
                deps = subtask.get("dependencies", [])
                if deps:
                    dep_titles = [
                        subtasks[d - 1]["title"]
                        for d in deps
                        if 0 < d <= len(subtasks)
                    ]
                    lines.append(f"   🔗 Depende de: {', '.join(dep_titles)}")

                # Tips
                tips = subtask.get("tips", [])
                if tips:
                    lines.append(f"   💡 Dica: {tips[0]}")

                # Blockers
                blockers = subtask.get("potential_blockers", [])
                if blockers:
                    lines.append(f"   ⚠️ Atenção: {blockers[0]}")

                lines.append("")

        # Oportunidades de paralelização
        parallel = decomposition.get("parallel_opportunities", [])
        if parallel:
            lines.append("⚡ **Oportunidades de paralelização:**")
            for group in parallel:
                group_titles = [
                    subtasks[i - 1]["title"]
                    for i in group
                    if 0 < i <= len(subtasks)
                ]
                lines.append(f"   • {' + '.join(group_titles)}")

        return "\n".join(lines)

    def get_next_actionable_subtask(
        self,
        decomposition: Dict,
        completed_subtasks: List[int]
    ) -> Optional[Dict]:
        """
        Retorna próxima subtask acionável (sem dependências pendentes).

        Args:
            decomposition: Resultado de decompose_task()
            completed_subtasks: Lista de order das subtasks já concluídas

        Returns:
            Subtask ou None se todas foram concluídas
        """
        subtasks = decomposition.get("subtasks", [])

        for subtask in subtasks:
            order = subtask.get("order")

            # Já foi concluída?
            if order in completed_subtasks:
                continue

            # Todas as dependências foram concluídas?
            dependencies = subtask.get("dependencies", [])
            all_deps_done = all(dep in completed_subtasks for dep in dependencies)

            if all_deps_done:
                return subtask

        return None  # Todas concluídas

    def calculate_progress(
        self,
        decomposition: Dict,
        completed_subtasks: List[int]
    ) -> Dict:
        """
        Calcula progresso da decomposição.

        Args:
            decomposition: Resultado de decompose_task()
            completed_subtasks: Lista de order das subtasks já concluídas

        Returns:
            Dict com estatísticas de progresso
        """
        subtasks = decomposition.get("subtasks", [])
        total = len(subtasks)
        completed = len(completed_subtasks)

        # Calcular tempo restante
        remaining_minutes = sum(
            subtask.get("estimated_minutes", 0)
            for subtask in subtasks
            if subtask.get("order") not in completed_subtasks
        )

        return {
            "total_subtasks": total,
            "completed_subtasks": completed,
            "remaining_subtasks": total - completed,
            "percentage_complete": int((completed / total * 100)) if total > 0 else 0,
            "estimated_hours_remaining": remaining_minutes / 60,
            "is_complete": completed == total
        }
