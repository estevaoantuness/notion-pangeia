"""
Team Coordinator - Coordenador Central do Time.

Mapeia TODAS as pessoas × tasks × projetos em tempo real.
Cria visão global para coordenação inteligente.
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Person:
    """Pessoa no time."""
    name: str
    tasks_total: int = 0
    tasks_em_andamento: int = 0
    tasks_a_fazer: int = 0
    tasks_concluidas: int = 0
    projects: Set[str] = field(default_factory=set)
    collaborators: Set[str] = field(default_factory=set)  # Pessoas que trabalham nos mesmos projetos
    workload_score: float = 0.0  # 0-1, quanto mais alto mais sobrecarregado


@dataclass
class Project:
    """Projeto sendo desenvolvido."""
    name: str
    people: Set[str] = field(default_factory=set)
    tasks_total: int = 0
    tasks_pending: int = 0
    tasks_completed: int = 0
    completion_rate: float = 0.0


@dataclass
class TaskNode:
    """Task no grafo de coordenação."""
    id: str
    title: str
    assignees: List[str]
    project: str
    status: str
    related_tasks: List[str] = field(default_factory=list)  # Tasks relacionadas
    blockers: List[str] = field(default_factory=list)  # Tasks que bloqueiam essa
    blocking: List[str] = field(default_factory=list)  # Tasks que essa task bloqueia


@dataclass
class TeamMap:
    """Mapa completo do time."""
    people: Dict[str, Person]
    projects: Dict[str, Project]
    tasks: Dict[str, TaskNode]
    last_sync: datetime


class TeamCoordinator:
    """
    Coordenador Central do Time.

    Mapeia TODAS as pessoas e tasks em tempo real,
    criando visão global para coordenação inteligente.
    """

    def __init__(self, tasks_manager=None):
        """
        Inicializa coordenador.

        Args:
            tasks_manager: TasksManager do Notion
        """
        self.tasks_manager = tasks_manager
        self._team_map: Optional[TeamMap] = None
        logger.info("TeamCoordinator inicializado")

    def sync_all(self) -> TeamMap:
        """
        Sincroniza TUDO: todas pessoas, tasks e projetos.

        Returns:
            TeamMap com visão global completa
        """
        logger.info("🔄 Iniciando sync completo do time...")

        if not self.tasks_manager:
            logger.error("TasksManager não configurado")
            return self._empty_team_map()

        try:
            # Busca TODAS as tasks do database
            all_tasks_raw = self.tasks_manager.notion_client.query_database(
                database_id=self.tasks_manager.database_id
            )

            logger.info(f"📋 Encontradas {len(all_tasks_raw)} tasks no total")

            # Inicializa estruturas
            people_dict: Dict[str, Person] = {}
            projects_dict: Dict[str, Project] = {}
            tasks_dict: Dict[str, TaskNode] = {}

            # Processa cada task
            for task_raw in all_tasks_raw:
                task_id = task_raw.get("id", "")
                props = task_raw.get("properties", {})

                # Extrai dados da task
                title = self._extract_title(props)
                assignees = self._extract_assignees(props)
                project = self._extract_project(props)
                status = self._extract_status(props)

                # Cria TaskNode
                task_node = TaskNode(
                    id=task_id,
                    title=title,
                    assignees=assignees,
                    project=project,
                    status=status
                )
                tasks_dict[task_id] = task_node

                # Atualiza pessoas
                for assignee in assignees:
                    if assignee not in people_dict:
                        people_dict[assignee] = Person(name=assignee)

                    person = people_dict[assignee]
                    person.tasks_total += 1

                    if status == "Em Andamento":
                        person.tasks_em_andamento += 1
                    elif status == "A Fazer":
                        person.tasks_a_fazer += 1
                    elif status == "Concluído":
                        person.tasks_concluidas += 1

                    if project:
                        person.projects.add(project)

                # Atualiza projetos
                if project:
                    if project not in projects_dict:
                        projects_dict[project] = Project(name=project)

                    proj = projects_dict[project]
                    proj.people.update(assignees)
                    proj.tasks_total += 1

                    if status == "Concluído":
                        proj.tasks_completed += 1
                    else:
                        proj.tasks_pending += 1

            # Calcula workload scores
            for person in people_dict.values():
                # Workload = tasks ativas (em andamento + a fazer) / 10
                active_tasks = person.tasks_em_andamento + person.tasks_a_fazer
                person.workload_score = min(1.0, active_tasks / 10)

            # Calcula completion rates de projetos
            for project in projects_dict.values():
                if project.tasks_total > 0:
                    project.completion_rate = project.tasks_completed / project.tasks_total

            # Detecta colaboradores (pessoas que trabalham nos mesmos projetos)
            for person_name, person in people_dict.items():
                for project_name in person.projects:
                    if project_name in projects_dict:
                        # Adiciona todas as outras pessoas desse projeto como colaboradores
                        other_people = projects_dict[project_name].people - {person_name}
                        person.collaborators.update(other_people)

            # Cria TeamMap
            team_map = TeamMap(
                people=people_dict,
                projects=projects_dict,
                tasks=tasks_dict,
                last_sync=datetime.now()
            )

            self._team_map = team_map

            logger.info(f"✅ Sync completo: {len(people_dict)} pessoas, {len(projects_dict)} projetos, {len(tasks_dict)} tasks")
            return team_map

        except Exception as e:
            logger.error(f"Erro ao sincronizar time: {e}", exc_info=True)
            return self._empty_team_map()

    def get_person_overview(self, person_name: str) -> Optional[Person]:
        """
        Pega visão geral de uma pessoa.

        Args:
            person_name: Nome da pessoa

        Returns:
            Person ou None
        """
        if not self._team_map:
            self.sync_all()

        return self._team_map.people.get(person_name)

    def get_project_overview(self, project_name: str) -> Optional[Project]:
        """
        Pega visão geral de um projeto.

        Args:
            project_name: Nome do projeto

        Returns:
            Project ou None
        """
        if not self._team_map:
            self.sync_all()

        return self._team_map.projects.get(project_name)

    def get_all_people(self) -> List[Person]:
        """
        Retorna lista de todas as pessoas.

        Returns:
            Lista de Person ordenada por workload
        """
        if not self._team_map:
            self.sync_all()

        return sorted(
            self._team_map.people.values(),
            key=lambda p: p.workload_score,
            reverse=True
        )

    def get_all_projects(self) -> List[Project]:
        """
        Retorna lista de todos os projetos.

        Returns:
            Lista de Project ordenada por completion rate
        """
        if not self._team_map:
            self.sync_all()

        return sorted(
            self._team_map.projects.values(),
            key=lambda p: p.completion_rate
        )

    def get_overloaded_people(self, threshold: float = 0.7) -> List[Person]:
        """
        Identifica pessoas sobrecarregadas.

        Args:
            threshold: Limiar de workload (0-1)

        Returns:
            Lista de pessoas com workload > threshold
        """
        if not self._team_map:
            self.sync_all()

        return [
            person for person in self._team_map.people.values()
            if person.workload_score >= threshold
        ]

    def get_underutilized_people(self, threshold: float = 0.3) -> List[Person]:
        """
        Identifica pessoas subutilizadas.

        Args:
            threshold: Limiar de workload (0-1)

        Returns:
            Lista de pessoas com workload < threshold
        """
        if not self._team_map:
            self.sync_all()

        return [
            person for person in self._team_map.people.values()
            if person.workload_score < threshold and person.tasks_total > 0
        ]

    def get_team_summary(self) -> Dict:
        """
        Retorna resumo geral do time.

        Returns:
            Dict com estatísticas gerais
        """
        if not self._team_map:
            self.sync_all()

        total_people = len(self._team_map.people)
        total_projects = len(self._team_map.projects)
        total_tasks = len(self._team_map.tasks)

        tasks_by_status = defaultdict(int)
        for task in self._team_map.tasks.values():
            tasks_by_status[task.status] += 1

        avg_workload = (
            sum(p.workload_score for p in self._team_map.people.values()) / total_people
            if total_people > 0 else 0
        )

        return {
            "total_people": total_people,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "tasks_em_andamento": tasks_by_status.get("Em Andamento", 0),
            "tasks_a_fazer": tasks_by_status.get("A Fazer", 0),
            "tasks_concluidas": tasks_by_status.get("Concluído", 0),
            "avg_workload": avg_workload,
            "overloaded_count": len(self.get_overloaded_people()),
            "underutilized_count": len(self.get_underutilized_people()),
            "last_sync": self._team_map.last_sync.isoformat()
        }

    # Helper methods

    def _extract_title(self, props: Dict) -> str:
        """Extrai título da task."""
        task_prop = props.get("Task", {})
        if task_prop:
            title_data = task_prop.get("title", [])
            if title_data:
                return title_data[0].get("plain_text", "Sem título")
        return "Sem título"

    def _extract_assignees(self, props: Dict) -> List[str]:
        """Extrai assignees da task."""
        assignees_prop = props.get("Assignees", {})
        assignees = assignees_prop.get("multi_select", [])
        return [a.get("name", "") for a in assignees if a.get("name")]

    def _extract_project(self, props: Dict) -> str:
        """Extrai projeto da task."""
        project_prop = props.get("Project", {})
        projects = project_prop.get("multi_select", [])
        if projects:
            return projects[0].get("name", "Sem projeto")
        return "Sem projeto"

    def _extract_status(self, props: Dict) -> str:
        """Extrai status da task."""
        status_prop = props.get("Status", {})
        status_data = status_prop.get("status")
        if status_data:
            return status_data.get("name", "A Fazer")
        return "A Fazer"

    def _empty_team_map(self) -> TeamMap:
        """Retorna TeamMap vazio."""
        return TeamMap(
            people={},
            projects={},
            tasks={},
            last_sync=datetime.now()
        )
