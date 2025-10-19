"""
Connection Detector - Detector de Conexões entre Pessoas.

Identifica quem pode ajudar quem baseado em:
- Projetos em comum
- Tasks relacionadas
- Padrões de colaboração
- Habilidades complementares
"""

import logging
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Tipos de conexão entre pessoas."""
    SAME_PROJECT = "same_project"  # Trabalham no mesmo projeto
    RELATED_TASKS = "related_tasks"  # Tasks relacionadas
    BLOCKER_DEPENDENCY = "blocker_dependency"  # Um bloqueia o outro
    COMPLEMENTARY_SKILLS = "complementary_skills"  # Habilidades complementares
    HISTORICAL_COLLABORATION = "historical_collaboration"  # Já colaboraram antes


@dataclass
class Connection:
    """Conexão detectada entre duas pessoas."""
    person_a: str
    person_b: str
    connection_type: ConnectionType
    strength: float  # 0-1, força da conexão
    reason: str  # Explicação humanizada
    suggested_action: str  # O que fazer com essa conexão


class ConnectionDetector:
    """
    Detector de conexões entre pessoas.

    Identifica padrões de colaboração e sugere
    quem pode ajudar quem.
    """

    def __init__(self, team_coordinator=None):
        """
        Inicializa detector.

        Args:
            team_coordinator: TeamCoordinator
        """
        self.team_coordinator = team_coordinator
        logger.info("ConnectionDetector inicializado")

    def detect_all_connections(self) -> List[Connection]:
        """
        Detecta TODAS as conexões possíveis no time.

        Returns:
            Lista de Connection ordenadas por força
        """
        if not self.team_coordinator:
            logger.error("TeamCoordinator não configurado")
            return []

        # Garante sync
        team_map = self.team_coordinator.sync_all()

        connections = []

        # Detecta conexões por projeto
        connections.extend(self._detect_project_connections(team_map))

        # Detecta conexões por tasks relacionadas
        connections.extend(self._detect_related_task_connections(team_map))

        # Detecta dependências de bloqueio
        connections.extend(self._detect_blocker_dependencies(team_map))

        # Ordena por força
        connections.sort(key=lambda c: c.strength, reverse=True)

        logger.info(f"Detectadas {len(connections)} conexões no time")
        return connections

    def get_connections_for_person(self, person_name: str) -> List[Connection]:
        """
        Pega conexões de uma pessoa específica.

        Args:
            person_name: Nome da pessoa

        Returns:
            Lista de conexões envolvendo essa pessoa
        """
        all_connections = self.detect_all_connections()

        return [
            conn for conn in all_connections
            if conn.person_a == person_name or conn.person_b == person_name
        ]

    def get_collaboration_suggestions(
        self,
        person_name: str,
        limit: int = 5
    ) -> List[Connection]:
        """
        Sugere com quem a pessoa deveria colaborar.

        Args:
            person_name: Nome da pessoa
            limit: Máximo de sugestões

        Returns:
            Top N conexões mais fortes
        """
        connections = self.get_connections_for_person(person_name)
        return connections[:limit]

    def _detect_project_connections(self, team_map) -> List[Connection]:
        """Detecta conexões por projeto em comum."""
        connections = []

        # Para cada projeto, conecta todas as pessoas
        for project in team_map.projects.values():
            people_list = list(project.people)

            # Conecta cada par de pessoas
            for i, person_a in enumerate(people_list):
                for person_b in people_list[i+1:]:
                    # Força da conexão baseada em completion rate do projeto
                    strength = 0.3 + (project.completion_rate * 0.4)  # 0.3 a 0.7

                    reason = (
                        f"Ambos trabalham no projeto '{project.name}' "
                        f"({project.completion_rate*100:.0f}% concluído)"
                    )

                    suggested_action = (
                        f"Coordenar esforços no '{project.name}' - "
                        f"{project.tasks_pending} tasks pendentes"
                    )

                    connections.append(Connection(
                        person_a=person_a,
                        person_b=person_b,
                        connection_type=ConnectionType.SAME_PROJECT,
                        strength=strength,
                        reason=reason,
                        suggested_action=suggested_action
                    ))

        return connections

    def _detect_related_task_connections(self, team_map) -> List[Connection]:
        """Detecta conexões por tasks relacionadas."""
        connections = []

        # Agrupa tasks por projeto
        tasks_by_project: Dict[str, List] = {}

        for task in team_map.tasks.values():
            if task.project not in tasks_by_project:
                tasks_by_project[task.project] = []
            tasks_by_project[task.project].append(task)

        # Para cada projeto, busca tasks relacionadas
        for project_name, tasks in tasks_by_project.items():
            # Detecta tasks com palavras-chave relacionadas
            for i, task_a in enumerate(tasks):
                for task_b in tasks[i+1:]:
                    # Check se tasks são relacionadas por keywords
                    if self._are_tasks_related(task_a.title, task_b.title):
                        # Conecta assignees
                        for person_a in task_a.assignees:
                            for person_b in task_b.assignees:
                                if person_a != person_b:
                                    strength = 0.6  # Tasks relacionadas = conexão forte

                                    reason = (
                                        f"Tasks relacionadas no '{project_name}':\n"
                                        f"• {person_a}: '{task_a.title}'\n"
                                        f"• {person_b}: '{task_b.title}'"
                                    )

                                    suggested_action = (
                                        f"Fazer pair/review - tasks complementares"
                                    )

                                    connections.append(Connection(
                                        person_a=person_a,
                                        person_b=person_b,
                                        connection_type=ConnectionType.RELATED_TASKS,
                                        strength=strength,
                                        reason=reason,
                                        suggested_action=suggested_action
                                    ))

        return connections

    def _detect_blocker_dependencies(self, team_map) -> List[Connection]:
        """Detecta dependências de bloqueio entre tasks."""
        connections = []

        # Heurística: Se task A deve vir antes de task B (baseado em keywords)
        blocker_keywords = {
            "agente": ["interface", "painel", "ux", "ui"],
            "api": ["frontend", "interface"],
            "backend": ["frontend"],
            "design": ["implementar", "desenvolver"],
            "ux": ["ui", "frontend"],
        }

        for task_a in team_map.tasks.values():
            for task_b in team_map.tasks.values():
                if task_a.id == task_b.id:
                    continue

                # Mesmo projeto?
                if task_a.project != task_b.project:
                    continue

                # Task A bloqueia Task B?
                if self._task_blocks_other(task_a.title, task_b.title, blocker_keywords):
                    # Conecta assignees
                    for person_a in task_a.assignees:
                        for person_b in task_b.assignees:
                            if person_a != person_b:
                                # Força depende do status
                                if task_a.status != "Concluído":
                                    strength = 0.9  # Bloqueio ativo = URGENTE
                                else:
                                    strength = 0.3  # Já resolvido

                                reason = (
                                    f"⚠️ DEPENDÊNCIA DETECTADA:\n"
                                    f"'{task_b.title}' ({person_b})\n"
                                    f"DEPENDE DE:\n"
                                    f"'{task_a.title}' ({person_a})\n"
                                    f"Status do bloqueador: {task_a.status}"
                                )

                                if task_a.status != "Concluído":
                                    suggested_action = (
                                        f"🚨 {person_b} está BLOQUEADO esperando {person_a} concluir '{task_a.title}'"
                                    )
                                else:
                                    suggested_action = (
                                        f"✅ Bloqueio resolvido - {person_b} pode continuar"
                                    )

                                connections.append(Connection(
                                    person_a=person_a,
                                    person_b=person_b,
                                    connection_type=ConnectionType.BLOCKER_DEPENDENCY,
                                    strength=strength,
                                    reason=reason,
                                    suggested_action=suggested_action
                                ))

        return connections

    def _are_tasks_related(self, title_a: str, title_b: str) -> bool:
        """
        Verifica se duas tasks são relacionadas por keywords.

        Args:
            title_a: Título da task A
            title_b: Título da task B

        Returns:
            True se relacionadas
        """
        # Keywords relacionadas
        related_keywords = [
            {"agente", "oxy", "atendimento"},
            {"ux", "ui", "interface", "painel"},
            {"bug", "correção", "fix", "estável"},
            {"auzap", "onboarding", "plataforma"},
        ]

        title_a_lower = title_a.lower()
        title_b_lower = title_b.lower()

        for keyword_set in related_keywords:
            # Se ambos titles têm palavras do mesmo set, são relacionadas
            if any(kw in title_a_lower for kw in keyword_set) and \
               any(kw in title_b_lower for kw in keyword_set):
                return True

        return False

    def _task_blocks_other(
        self,
        blocker_title: str,
        blocked_title: str,
        blocker_keywords: Dict[str, List[str]]
    ) -> bool:
        """
        Verifica se uma task bloqueia outra.

        Args:
            blocker_title: Título da task bloqueadora
            blocked_title: Título da task bloqueada
            blocker_keywords: Dict de keywords de bloqueio

        Returns:
            True se task A bloqueia task B
        """
        blocker_lower = blocker_title.lower()
        blocked_lower = blocked_title.lower()

        for blocker_kw, blocked_kws in blocker_keywords.items():
            # Se blocker tem keyword e blocked tem keyword dependente
            if blocker_kw in blocker_lower:
                if any(bkw in blocked_lower for bkw in blocked_kws):
                    return True

        return False
