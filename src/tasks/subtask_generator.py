"""
Subtask Generator - Gerador de Subtasks Baseado em Templates.

Gera subtasks comuns para tipos específicos de tarefas usando templates.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class SubtaskGenerator:
    """
    Gera subtasks baseadas em templates para tarefas comuns.

    Útil quando não precisa usar GPT-4 (economia de custo).
    """

    # Templates de subtasks para tipos comuns
    TEMPLATES = {
        "feature": [
            {
                "title": "Definir requisitos e escopo",
                "description": "Definir exatamente o que a feature deve fazer",
                "estimated_minutes": 30,
                "complexity": "easy",
                "order": 1
            },
            {
                "title": "Desenhar arquitetura",
                "description": "Definir componentes, APIs, e fluxo de dados",
                "estimated_minutes": 45,
                "complexity": "medium",
                "order": 2,
                "dependencies": [1]
            },
            {
                "title": "Implementar backend",
                "description": "Criar APIs, modelos, e lógica de negócio",
                "estimated_minutes": 180,
                "complexity": "hard",
                "order": 3,
                "dependencies": [2]
            },
            {
                "title": "Implementar frontend",
                "description": "Criar UI e conectar com backend",
                "estimated_minutes": 120,
                "complexity": "medium",
                "order": 4,
                "dependencies": [3]
            },
            {
                "title": "Escrever testes",
                "description": "Testes unitários e de integração",
                "estimated_minutes": 60,
                "complexity": "medium",
                "order": 5,
                "dependencies": [3, 4]
            },
            {
                "title": "Testar manualmente",
                "description": "Testar fluxos completos e edge cases",
                "estimated_minutes": 30,
                "complexity": "easy",
                "order": 6,
                "dependencies": [5]
            },
            {
                "title": "Documentar",
                "description": "Atualizar README e documentação técnica",
                "estimated_minutes": 20,
                "complexity": "easy",
                "order": 7,
                "dependencies": [6]
            }
        ],

        "bug_fix": [
            {
                "title": "Reproduzir o bug",
                "description": "Criar caso de teste que reproduz o bug consistentemente",
                "estimated_minutes": 30,
                "complexity": "medium",
                "order": 1
            },
            {
                "title": "Investigar causa raiz",
                "description": "Debugar e identificar exatamente onde está o problema",
                "estimated_minutes": 60,
                "complexity": "hard",
                "order": 2,
                "dependencies": [1]
            },
            {
                "title": "Implementar fix",
                "description": "Corrigir o código problemático",
                "estimated_minutes": 45,
                "complexity": "medium",
                "order": 3,
                "dependencies": [2]
            },
            {
                "title": "Adicionar teste de regressão",
                "description": "Garantir que bug não volte",
                "estimated_minutes": 20,
                "complexity": "easy",
                "order": 4,
                "dependencies": [3]
            },
            {
                "title": "Testar em ambiente de staging",
                "description": "Validar fix em ambiente similar a produção",
                "estimated_minutes": 15,
                "complexity": "easy",
                "order": 5,
                "dependencies": [4]
            }
        ],

        "refactoring": [
            {
                "title": "Identificar código a refatorar",
                "description": "Mapear exatamente o que precisa ser refatorado",
                "estimated_minutes": 20,
                "complexity": "easy",
                "order": 1
            },
            {
                "title": "Escrever testes existentes",
                "description": "Garantir cobertura antes de mudar código",
                "estimated_minutes": 45,
                "complexity": "medium",
                "order": 2,
                "dependencies": [1]
            },
            {
                "title": "Refatorar em pequenos passos",
                "description": "Mudanças incrementais, testando após cada uma",
                "estimated_minutes": 120,
                "complexity": "hard",
                "order": 3,
                "dependencies": [2]
            },
            {
                "title": "Validar testes passam",
                "description": "Garantir que funcionalidade não quebrou",
                "estimated_minutes": 15,
                "complexity": "easy",
                "order": 4,
                "dependencies": [3]
            },
            {
                "title": "Code review",
                "description": "Pedir review do time",
                "estimated_minutes": 30,
                "complexity": "easy",
                "order": 5,
                "dependencies": [4]
            }
        ],

        "research": [
            {
                "title": "Definir objetivo da pesquisa",
                "description": "O que exatamente estamos tentando descobrir?",
                "estimated_minutes": 15,
                "complexity": "easy",
                "order": 1
            },
            {
                "title": "Pesquisar documentações oficiais",
                "description": "Ler docs das tecnologias relevantes",
                "estimated_minutes": 60,
                "complexity": "medium",
                "order": 2,
                "dependencies": [1]
            },
            {
                "title": "Buscar artigos e casos de uso",
                "description": "Medium, Dev.to, blogs técnicos",
                "estimated_minutes": 45,
                "complexity": "easy",
                "order": 3,
                "dependencies": [1]
            },
            {
                "title": "Criar POC se necessário",
                "description": "Testar conceitos na prática",
                "estimated_minutes": 90,
                "complexity": "medium",
                "order": 4,
                "dependencies": [2, 3]
            },
            {
                "title": "Documentar findings",
                "description": "Criar documento com descobertas e recomendações",
                "estimated_minutes": 30,
                "complexity": "easy",
                "order": 5,
                "dependencies": [4]
            }
        ],

        "documentation": [
            {
                "title": "Definir estrutura do documento",
                "description": "Outline com seções principais",
                "estimated_minutes": 15,
                "complexity": "easy",
                "order": 1
            },
            {
                "title": "Escrever conteúdo principal",
                "description": "Preencher cada seção",
                "estimated_minutes": 90,
                "complexity": "medium",
                "order": 2,
                "dependencies": [1]
            },
            {
                "title": "Adicionar exemplos de código",
                "description": "Code snippets práticos",
                "estimated_minutes": 30,
                "complexity": "easy",
                "order": 3,
                "dependencies": [2]
            },
            {
                "title": "Revisar e melhorar clareza",
                "description": "Ler como se fosse leitor novo",
                "estimated_minutes": 20,
                "complexity": "easy",
                "order": 4,
                "dependencies": [3]
            },
            {
                "title": "Pedir review do time",
                "description": "Feedback de colegas",
                "estimated_minutes": 15,
                "complexity": "easy",
                "order": 5,
                "dependencies": [4]
            }
        ]
    }

    def __init__(self):
        """Inicializa o gerador."""
        logger.info("SubtaskGenerator inicializado")

    def generate_from_template(
        self,
        task_type: str,
        customize: bool = False
    ) -> List[Dict]:
        """
        Gera subtasks a partir de template.

        Args:
            task_type: Tipo da task (feature, bug_fix, refactoring, etc.)
            customize: Se True, permite customização

        Returns:
            Lista de subtasks
        """
        template = self.TEMPLATES.get(task_type.lower())

        if not template:
            logger.warning(f"Template não encontrado para tipo: {task_type}")
            return []

        # Copiar template
        import copy
        subtasks = copy.deepcopy(template)

        logger.info(f"Geradas {len(subtasks)} subtasks do template '{task_type}'")

        return subtasks

    def get_available_templates(self) -> List[str]:
        """Retorna lista de templates disponíveis."""
        return list(self.TEMPLATES.keys())

    def preview_template(self, task_type: str) -> str:
        """
        Gera preview de um template.

        Args:
            task_type: Tipo da task

        Returns:
            String formatada com preview
        """
        subtasks = self.generate_from_template(task_type)

        if not subtasks:
            return f"Template '{task_type}' não encontrado"

        lines = [
            f"📋 **Template: {task_type.upper()}**",
            f"📝 {len(subtasks)} subtarefas",
            ""
        ]

        total_minutes = sum(st.get("estimated_minutes", 0) for st in subtasks)
        lines.append(f"🕐 Tempo total estimado: **{total_minutes / 60:.1f}h**")
        lines.append("")

        for idx, subtask in enumerate(subtasks, 1):
            complexity_emoji = {
                "easy": "🟢",
                "medium": "🟡",
                "hard": "🔴"
            }.get(subtask.get("complexity", "medium"), "⚪")

            lines.append(
                f"{idx}. {complexity_emoji} **{subtask['title']}** "
                f"({subtask.get('estimated_minutes', 0)}min)"
            )

        return "\n".join(lines)
