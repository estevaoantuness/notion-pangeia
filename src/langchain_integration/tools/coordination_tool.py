"""
Team Coordination Tool - LangChain Tool para coordenação de time.

Este tool encapsula todo o sistema de coordenação:
- TeamCoordinator (sync de todos)
- ConnectionDetector (detecta conexões)
- CollaborationRecommender (sugestões)
- MessageFragmenter (mensagens naturais)
"""

import logging
import json
from typing import Optional

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from src.notion.tasks import TasksManager
from src.coordination import (
    TeamCoordinator,
    ConnectionDetector,
    CollaborationRecommender,
    MessageFragmenter
)

logger = logging.getLogger(__name__)


class CoordinationInput(BaseModel):
    """Input schema para CoordinationTool."""

    action: str = Field(
        description=(
            "Ação de coordenação: "
            "'detect_blockers' (quem tá bloqueado), "
            "'suggest_collaboration' (sugestões de ajuda), "
            "'team_summary' (resumo do time), "
            "'workload_analysis' (análise de carga), "
            "'person_insights' (insights de alguém específico)"
        )
    )
    person_name: Optional[str] = Field(
        default=None,
        description="Nome da pessoa (necessário para person_insights e suggest_collaboration)"
    )


class CoordinationTool(BaseTool):
    """
    Tool para coordenação inteligente de time.

    Usa sistema completo de coordenação para:
    - Detectar bloqueios e dependências
    - Sugerir colaborações e pair programming
    - Analisar workload do time
    - Gerar insights de pessoas
    - Resumir estado do time

    Examples:
        detect_blockers: {"action": "detect_blockers"}
        team_summary: {"action": "team_summary"}
        person_insights: {"action": "person_insights", "person_name": "Saraiva"}
    """

    name = "team_coordination"
    description = (
        "Coordena o time completo. Use para detectar bloqueios, sugerir colaborações, "
        "analisar workload, ou obter resumo do time. "
        "Actions: 'detect_blockers', 'suggest_collaboration', 'team_summary', "
        "'workload_analysis', 'person_insights'."
    )
    args_schema = CoordinationInput

    # Componentes de coordenação
    tasks_manager: TasksManager = None
    team_coordinator: TeamCoordinator = None
    connection_detector: ConnectionDetector = None
    collab_recommender: CollaborationRecommender = None
    message_fragmenter: MessageFragmenter = None

    def __init__(self):
        """Inicializa tool com sistema de coordenação."""
        super().__init__()

        # Inicializa componentes
        self.tasks_manager = TasksManager()
        self.team_coordinator = TeamCoordinator(tasks_manager=self.tasks_manager)
        self.connection_detector = ConnectionDetector(self.team_coordinator)
        self.collab_recommender = CollaborationRecommender(self.connection_detector)
        self.message_fragmenter = MessageFragmenter()

        logger.info("CoordinationTool inicializado com todos os componentes")

    def _run(
        self,
        action: str,
        person_name: Optional[str] = None
    ) -> str:
        """
        Executa ação de coordenação.

        Args:
            action: Tipo de ação
            person_name: Nome da pessoa (opcional, depende da ação)

        Returns:
            JSON string com resultado
        """
        try:
            logger.info(f"CoordinationTool: {action}" + (f" para {person_name}" if person_name else ""))

            # Sync completo do time (necessário para todas as ações)
            self.team_coordinator.sync_all()

            if action == "detect_blockers":
                return self._detect_blockers()

            elif action == "suggest_collaboration":
                return self._suggest_collaboration(person_name)

            elif action == "team_summary":
                return self._team_summary()

            elif action == "workload_analysis":
                return self._workload_analysis()

            elif action == "person_insights":
                return self._person_insights(person_name)

            else:
                return json.dumps({
                    "error": f"Ação inválida: {action}",
                    "valid_actions": [
                        "detect_blockers",
                        "suggest_collaboration",
                        "team_summary",
                        "workload_analysis",
                        "person_insights"
                    ]
                })

        except Exception as e:
            logger.error(f"Erro em CoordinationTool: {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "action": action
            })

    def _detect_blockers(self) -> str:
        """Detecta todos os bloqueios no time."""
        # Gera todas as recomendações
        all_recs = self.collab_recommender.generate_all_recommendations()

        # Filtra apenas bloqueios críticos
        blockers = [
            r for r in all_recs
            if r.action_type == "unblock"
        ]

        if not blockers:
            return json.dumps({
                "blockers_found": 0,
                "message": "Nenhum bloqueio detectado! Time tá fluindo bem 🎉"
            }, ensure_ascii=False)

        # Formata bloqueios
        blocker_list = []
        for rec in blockers[:5]:  # Top 5
            blocker_list.append({
                "bloqueador": rec.target_person,
                "bloqueado": rec.involves[0] if rec.involves else "Unknown",
                "prioridade": rec.priority.value,
                "detalhes": rec.message[:100]
            })

        return json.dumps({
            "blockers_found": len(blockers),
            "critical_blockers": blocker_list,
            "message": f"🚨 {len(blockers)} bloqueio(s) detectado(s)"
        }, ensure_ascii=False)

    def _suggest_collaboration(self, person_name: Optional[str]) -> str:
        """Sugere colaborações para uma pessoa ou para todo o time."""
        all_recs = self.collab_recommender.generate_all_recommendations()

        if person_name:
            # Filtra recomendações para essa pessoa
            person_recs = [
                r for r in all_recs
                if r.target_person == person_name and r.action_type in ["pair", "coordinate"]
            ]

            if not person_recs:
                return json.dumps({
                    "person": person_name,
                    "suggestions": 0,
                    "message": f"{person_name} não tem sugestões de colaboração no momento"
                }, ensure_ascii=False)

            suggestions = []
            for rec in person_recs[:3]:  # Top 3
                suggestions.append({
                    "tipo": rec.action_type,
                    "com_quem": rec.involves[0] if rec.involves else "Unknown",
                    "razao": rec.connection.reason[:100] if rec.connection else "N/A",
                    "prioridade": rec.priority.value
                })

            return json.dumps({
                "person": person_name,
                "suggestions": suggestions,
                "total": len(person_recs)
            }, ensure_ascii=False)

        else:
            # Sugestões para todo o time
            collab_recs = [
                r for r in all_recs
                if r.action_type in ["pair", "coordinate"]
            ]

            return json.dumps({
                "team_wide": True,
                "total_suggestions": len(collab_recs),
                "message": f"💡 {len(collab_recs)} oportunidade(s) de colaboração no time"
            }, ensure_ascii=False)

    def _team_summary(self) -> str:
        """Gera resumo completo do time."""
        summary = self.team_coordinator.get_team_summary()

        return json.dumps({
            "total_pessoas": summary['total_people'],
            "total_projetos": summary['total_projects'],
            "tasks": {
                "em_andamento": summary['tasks_em_andamento'],
                "a_fazer": summary['tasks_a_fazer'],
                "concluidas": summary['tasks_concluidas']
            },
            "workload": {
                "media": f"{int(summary['avg_workload']*100)}%",
                "sobrecarregados": summary['overloaded_count']
            },
            "message": f"📊 Time: {summary['total_people']} pessoas, {summary['total_projects']} projetos, {summary['tasks_em_andamento']} tasks ativas"
        }, ensure_ascii=False)

    def _workload_analysis(self) -> str:
        """Analisa workload detalhado do time."""
        team_map = self.team_coordinator.team_map

        # Ordena pessoas por workload (maior → menor)
        people_by_workload = sorted(
            team_map.people.values(),
            key=lambda p: p.workload_score,
            reverse=True
        )

        workload_list = []
        for person in people_by_workload[:10]:  # Top 10
            status = "🔴 SOBRECARGA" if person.workload_score >= 0.7 else \
                     "🟡 ALTO" if person.workload_score >= 0.5 else \
                     "🟢 OK"

            workload_list.append({
                "nome": person.name,
                "workload": f"{int(person.workload_score * 100)}%",
                "status": status,
                "tasks_ativas": person.tasks_em_andamento
            })

        return json.dumps({
            "total_analisados": len(team_map.people),
            "workload_distribution": workload_list,
            "sobrecarregados": len([p for p in team_map.people.values() if p.workload_score >= 0.7])
        }, ensure_ascii=False)

    def _person_insights(self, person_name: Optional[str]) -> str:
        """Gera insights profundos de uma pessoa específica."""
        if not person_name:
            return json.dumps({
                "error": "person_name é obrigatório para person_insights"
            })

        # Overview da pessoa
        person = self.team_coordinator.get_person_overview(person_name)

        if not person:
            return json.dumps({
                "error": f"Pessoa não encontrada: {person_name}"
            })

        # Recomendações para essa pessoa
        person_recs = self.collab_recommender.get_recommendations_for_person(person_name)

        # Agrupa por tipo
        recs_by_type = {}
        for rec in person_recs:
            rec_type = rec.action_type
            if rec_type not in recs_by_type:
                recs_by_type[rec_type] = 0
            recs_by_type[rec_type] += 1

        # Formata insights
        insights = {
            "pessoa": person_name,
            "workload": {
                "percentual": f"{int(person.workload_score * 100)}%",
                "status": "🔴 Alto" if person.workload_score >= 0.7 else "🟢 OK"
            },
            "tasks": {
                "em_andamento": person.tasks_em_andamento,
                "a_fazer": person.tasks_a_fazer,
                "concluidas": person.tasks_concluidas
            },
            "projetos": list(person.projects) if person.projects else [],
            "colaboradores": list(person.collaborators) if person.collaborators else [],
            "recomendacoes": recs_by_type,
            "total_recomendacoes": len(person_recs)
        }

        return json.dumps(insights, ensure_ascii=False)

    async def _arun(self, *args, **kwargs):
        """Async version (não implementado)."""
        raise NotImplementedError("CoordinationTool não suporta async ainda")
