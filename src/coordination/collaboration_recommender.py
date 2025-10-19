"""
Collaboration Recommender - Recomendador de Colaboração.

Transforma conexões detectadas em insights acionáveis:
- Sugere quem deve falar com quem
- Identifica bloqueios urgentes
- Forma times/squads
- Gera mensagens prontas para envio
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from .connection_detector import Connection, ConnectionType

logger = logging.getLogger(__name__)


class RecommendationPriority(Enum):
    """Prioridade da recomendação."""
    CRITICAL = "critical"  # Bloqueio ativo
    HIGH = "high"  # Colaboração importante
    MEDIUM = "medium"  # Sugestão útil
    LOW = "low"  # Opcional


@dataclass
class Recommendation:
    """Recomendação de colaboração."""
    priority: RecommendationPriority
    target_person: str  # Para quem enviar
    message: str  # Mensagem pronta
    action_type: str  # Tipo de ação (ex: "pair", "unblock", "coordinate")
    involves: List[str]  # Outras pessoas envolvidas
    connection: Connection  # Conexão original


class CollaborationRecommender:
    """
    Recomendador de colaboração.

    Transforma conexões em insights acionáveis
    e mensagens prontas para envio.
    """

    def __init__(self, connection_detector=None):
        """
        Inicializa recomendador.

        Args:
            connection_detector: ConnectionDetector
        """
        self.connection_detector = connection_detector
        logger.info("CollaborationRecommender inicializado")

    def generate_all_recommendations(self) -> List[Recommendation]:
        """
        Gera TODAS as recomendações de colaboração.

        Returns:
            Lista de Recommendation ordenadas por prioridade
        """
        if not self.connection_detector:
            logger.error("ConnectionDetector não configurado")
            return []

        # Detecta todas as conexões
        connections = self.connection_detector.detect_all_connections()

        logger.info(f"Processando {len(connections)} conexões...")

        recommendations = []

        for connection in connections:
            # Gera recomendação baseada no tipo de conexão
            recs = self._generate_recommendations_for_connection(connection)
            recommendations.extend(recs)

        # Ordena por prioridade
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3
        }
        recommendations.sort(key=lambda r: priority_order[r.priority])

        logger.info(f"Geradas {len(recommendations)} recomendações")
        return recommendations

    def get_recommendations_for_person(
        self,
        person_name: str,
        priority_filter: Optional[RecommendationPriority] = None
    ) -> List[Recommendation]:
        """
        Pega recomendações para uma pessoa específica.

        Args:
            person_name: Nome da pessoa
            priority_filter: Filtrar por prioridade (opcional)

        Returns:
            Lista de recomendações para essa pessoa
        """
        all_recs = self.generate_all_recommendations()

        recs = [
            rec for rec in all_recs
            if rec.target_person == person_name
        ]

        if priority_filter:
            recs = [rec for rec in recs if rec.priority == priority_filter]

        return recs

    def get_critical_recommendations(self) -> List[Recommendation]:
        """
        Pega apenas recomendações críticas (bloqueios ativos).

        Returns:
            Lista de recomendações críticas
        """
        all_recs = self.generate_all_recommendations()

        return [
            rec for rec in all_recs
            if rec.priority == RecommendationPriority.CRITICAL
        ]

    def _generate_recommendations_for_connection(
        self,
        connection: Connection
    ) -> List[Recommendation]:
        """
        Gera recomendações para uma conexão específica.

        Args:
            connection: Conexão detectada

        Returns:
            Lista de 1-2 recomendações (uma para cada pessoa)
        """
        recommendations = []

        if connection.connection_type == ConnectionType.BLOCKER_DEPENDENCY:
            # BLOQUEIO: Gera recomendação CRÍTICA
            recommendations.extend(self._gen_blocker_recommendations(connection))

        elif connection.connection_type == ConnectionType.RELATED_TASKS:
            # TASKS RELACIONADAS: Sugere pair/review
            recommendations.extend(self._gen_pair_recommendations(connection))

        elif connection.connection_type == ConnectionType.SAME_PROJECT:
            # MESMO PROJETO: Sugere coordenação
            recommendations.extend(self._gen_coordination_recommendations(connection))

        return recommendations

    def _gen_blocker_recommendations(self, connection: Connection) -> List[Recommendation]:
        """Gera recomendações para bloqueios."""
        recommendations = []

        # Determina quem é bloqueador e quem é bloqueado
        # (connection.reason contém essa info)
        blocker = connection.person_a
        blocked = connection.person_b

        # Detecta se bloqueio ainda está ativo
        is_active_block = "🚨" in connection.suggested_action

        if is_active_block:
            # Recomendação CRÍTICA para o BLOQUEADOR
            message_blocker = (
                f"🚨 URGENTE: Bloqueio Ativo\n\n"
                f"{blocked} está BLOQUEADO esperando você concluir uma task.\n\n"
                f"{connection.reason}\n\n"
                f"Ação: {connection.suggested_action}\n\n"
                f"Priorize isso! O time tá parado."
            )

            recommendations.append(Recommendation(
                priority=RecommendationPriority.CRITICAL,
                target_person=blocker,
                message=message_blocker,
                action_type="unblock",
                involves=[blocked],
                connection=connection
            ))

            # Recomendação HIGH para o BLOQUEADO
            message_blocked = (
                f"⏸️ Você está bloqueado\n\n"
                f"{connection.reason}\n\n"
                f"Enquanto isso, você pode:\n"
                f"• Trabalhar em outras tasks\n"
                f"• Preparar o que vem depois\n"
                f"• Falar com {blocker} pra ajudar\n\n"
                f"Já avisei {blocker} que é urgente! 🚨"
            )

            recommendations.append(Recommendation(
                priority=RecommendationPriority.HIGH,
                target_person=blocked,
                message=message_blocked,
                action_type="wait_or_help",
                involves=[blocker],
                connection=connection
            ))

        else:
            # Bloqueio resolvido - apenas notifica
            message_blocked = (
                f"✅ Bloqueio Resolvido!\n\n"
                f"{blocker} concluiu a task que te bloqueava.\n\n"
                f"Você pode continuar agora! 🚀"
            )

            recommendations.append(Recommendation(
                priority=RecommendationPriority.MEDIUM,
                target_person=blocked,
                message=message_blocked,
                action_type="unblocked",
                involves=[blocker],
                connection=connection
            ))

        return recommendations

    def _gen_pair_recommendations(self, connection: Connection) -> List[Recommendation]:
        """Gera recomendações para pair programming/review."""
        recommendations = []

        person_a = connection.person_a
        person_b = connection.person_b

        # Mensagem para A sugerindo pair com B
        message_a = (
            f"💡 Sugestão: Pair Programming\n\n"
            f"{connection.reason}\n\n"
            f"Vocês dois estão trabalhando em tasks complementares.\n"
            f"Que tal fazer um pair ou review mútuo?\n\n"
            f"Benefícios:\n"
            f"• Acelera ambas tasks\n"
            f"• Compartilha conhecimento\n"
            f"• Evita retrabalho\n\n"
            f"Quer que eu conecte vocês?"
        )

        recommendations.append(Recommendation(
            priority=RecommendationPriority.HIGH,
            target_person=person_a,
            message=message_a,
            action_type="pair",
            involves=[person_b],
            connection=connection
        ))

        # Mesma mensagem para B
        message_b = (
            f"💡 Sugestão: Pair Programming\n\n"
            f"{connection.reason}\n\n"
            f"Vocês dois estão trabalhando em tasks complementares.\n"
            f"Que tal fazer um pair ou review mútuo?\n\n"
            f"Benefícios:\n"
            f"• Acelera ambas tasks\n"
            f"• Compartilha conhecimento\n"
            f"• Evita retrabalho\n\n"
            f"Quer que eu conecte vocês?"
        )

        recommendations.append(Recommendation(
            priority=RecommendationPriority.HIGH,
            target_person=person_b,
            message=message_b,
            action_type="pair",
            involves=[person_a],
            connection=connection
        ))

        return recommendations

    def _gen_coordination_recommendations(self, connection: Connection) -> List[Recommendation]:
        """Gera recomendações para coordenação de projeto."""
        recommendations = []

        person_a = connection.person_a
        person_b = connection.person_b

        # Mensagem sugerindo coordenação
        message = (
            f"🤝 Coordenação de Projeto\n\n"
            f"{connection.reason}\n\n"
            f"Sugestão: Alinhar esforços com {person_b}.\n\n"
            f"• Garantir que não estão fazendo trabalho duplicado\n"
            f"• Dividir tasks de forma eficiente\n"
            f"• Combinar deadlines\n\n"
            f"Ação: {connection.suggested_action}"
        )

        recommendations.append(Recommendation(
            priority=RecommendationPriority.MEDIUM,
            target_person=person_a,
            message=message,
            action_type="coordinate",
            involves=[person_b],
            connection=connection
        ))

        return recommendations

    def generate_team_insights(self) -> str:
        """
        Gera insights gerais sobre o time todo.

        Returns:
            String com resumo geral
        """
        recommendations = self.generate_all_recommendations()

        critical_count = len([r for r in recommendations if r.priority == RecommendationPriority.CRITICAL])
        high_count = len([r for r in recommendations if r.priority == RecommendationPriority.HIGH])

        # Conta pessoas envolvidas
        all_people = set()
        for rec in recommendations:
            all_people.add(rec.target_person)
            all_people.update(rec.involves)

        # Conta tipos de ação
        action_types = {}
        for rec in recommendations:
            action_types[rec.action_type] = action_types.get(rec.action_type, 0) + 1

        insights = (
            f"📊 VISÃO GERAL DO TIME\n"
            f"{'='*50}\n\n"
            f"👥 Pessoas envolvidas: {len(all_people)}\n"
            f"🚨 Bloqueios críticos: {critical_count}\n"
            f"⚡ Colaborações sugeridas: {high_count}\n\n"
            f"📈 Tipos de ação recomendados:\n"
        )

        for action_type, count in sorted(action_types.items(), key=lambda x: x[1], reverse=True):
            insights += f"  • {action_type}: {count}\n"

        return insights
