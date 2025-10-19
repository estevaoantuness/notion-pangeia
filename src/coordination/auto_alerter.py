"""
Auto Alerter - Alertas Automáticos de Coordenação.

Envia mensagens automáticas sobre:
- Bloqueios detectados
- Sugestões de colaboração
- Avisos de sobrecarga

Usa message_fragmenter para enviar 2-5 mensagens naturais.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import time

from .team_coordinator import TeamCoordinator
from .connection_detector import ConnectionDetector
from .collaboration_recommender import CollaborationRecommender, RecommendationPriority
from .message_fragmenter import MessageFragmenter

logger = logging.getLogger(__name__)


class AutoAlerter:
    """
    Sistema de alertas automáticos.

    Verifica bloqueios e envia mensagens via WhatsApp
    de forma natural e fracionada.
    """

    def __init__(
        self,
        team_coordinator: TeamCoordinator,
        whatsapp_sender=None
    ):
        """
        Inicializa alerter.

        Args:
            team_coordinator: TeamCoordinator
            whatsapp_sender: WhatsAppSender (opcional, para envio real)
        """
        self.team_coordinator = team_coordinator
        self.connection_detector = ConnectionDetector(team_coordinator)
        self.collab_recommender = CollaborationRecommender(self.connection_detector)
        self.message_fragmenter = MessageFragmenter()
        self.whatsapp_sender = whatsapp_sender

        # Tracking de alertas enviados (evita spam)
        self.sent_alerts: Dict[str, datetime] = {}

        logger.info("AutoAlerter inicializado")

    def check_and_send_alerts(
        self,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Verifica e envia todos os alertas necessários.

        Args:
            dry_run: Se True, não envia de verdade (só loga)

        Returns:
            Dict com estatísticas {critical: N, high: N, sent: N}
        """
        logger.info("🔍 Verificando alertas...")

        # Sync completo
        self.team_coordinator.sync_all()

        # Gera todas as recomendações
        recommendations = self.collab_recommender.generate_all_recommendations()

        # Filtra por prioridade e horário
        current_hour = datetime.now().hour

        to_send = []
        for rec in recommendations:
            # Check se deve enviar agora
            if not self.message_fragmenter.should_send_now(rec, current_hour):
                continue

            # Check se já enviou recentemente (evita spam)
            alert_key = f"{rec.target_person}:{rec.action_type}:{','.join(rec.involves)}"
            if alert_key in self.sent_alerts:
                last_sent = self.sent_alerts[alert_key]
                hours_since = (datetime.now() - last_sent).total_seconds() / 3600

                # Critical: pode reenviar após 2h
                # High: pode reenviar após 6h
                # Medium: pode reenviar após 24h
                if rec.priority == RecommendationPriority.CRITICAL and hours_since < 2:
                    continue
                elif rec.priority == RecommendationPriority.HIGH and hours_since < 6:
                    continue
                elif hours_since < 24:
                    continue

            to_send.append(rec)

        # Agrupa por pessoa
        by_person = self.message_fragmenter.batch_recommendations_by_person(to_send)

        stats = {
            "critical": len([r for r in to_send if r.priority == RecommendationPriority.CRITICAL]),
            "high": len([r for r in to_send if r.priority == RecommendationPriority.HIGH]),
            "medium": len([r for r in to_send if r.priority == RecommendationPriority.MEDIUM]),
            "people": len(by_person),
            "sent": 0
        }

        logger.info(f"📊 Alertas a enviar: {stats['critical']} críticos, {stats['high']} importantes, {stats['medium']} médios")
        logger.info(f"👥 Para {stats['people']} pessoas")

        # Envia alertas por pessoa
        for person_name, person_recs in by_person.items():
            # Prioriza críticos
            person_recs.sort(key=lambda r: 0 if r.priority == RecommendationPriority.CRITICAL else 1)

            # Envia no máximo 3 alertas por pessoa por vez (evita bombardeio)
            for rec in person_recs[:3]:
                success = self._send_recommendation(
                    recommendation=rec,
                    dry_run=dry_run
                )

                if success:
                    stats["sent"] += 1

                    # Marca como enviado
                    alert_key = f"{rec.target_person}:{rec.action_type}:{','.join(rec.involves)}"
                    self.sent_alerts[alert_key] = datetime.now()

        logger.info(f"✅ Enviados {stats['sent']} alertas")
        return stats

    def _send_recommendation(
        self,
        recommendation,
        dry_run: bool = False
    ) -> bool:
        """
        Envia uma recomendação via WhatsApp (fracionada).

        Args:
            recommendation: Recommendation
            dry_run: Se True, só loga (não envia)

        Returns:
            True se enviou com sucesso
        """
        try:
            # Fragmenta em 2-5 mensagens
            messages = self.message_fragmenter.fragment_recommendation(recommendation)

            # Adiciona delays
            messages_with_delay = self.message_fragmenter.add_delays_between_messages(messages)

            person_name = recommendation.target_person
            priority = recommendation.priority.value

            logger.info(f"📤 Enviando alerta [{priority}] para {person_name}: {len(messages)} mensagens")

            if dry_run:
                # Modo de teste: só loga
                for i, msg_data in enumerate(messages_with_delay, 1):
                    logger.info(f"  Msg {i} (delay: {msg_data['delay_seconds']}s): {msg_data['text']}")
                return True

            # Envia de verdade
            if not self.whatsapp_sender:
                logger.warning("WhatsAppSender não configurado - mensagens não enviadas")
                return False

            for i, msg_data in enumerate(messages_with_delay):
                # Espera antes de enviar (exceto primeira)
                if msg_data['delay_seconds'] > 0:
                    time.sleep(msg_data['delay_seconds'])

                # Envia mensagem
                success, sid, error = self.whatsapp_sender.send_message(
                    person_name=person_name,
                    message=msg_data['text']
                )

                if not success:
                    logger.error(f"Erro ao enviar mensagem {i+1}/{len(messages)}: {error}")
                    return False

                logger.info(f"  ✅ Msg {i+1}/{len(messages)} enviada (SID: {sid})")

            return True

        except Exception as e:
            logger.error(f"Erro ao enviar recomendação: {e}", exc_info=True)
            return False

    def send_team_summary(
        self,
        target_person: str,
        dry_run: bool = False
    ) -> bool:
        """
        Envia resumo geral do time para alguém específico.

        Args:
            target_person: Para quem enviar
            dry_run: Se True, só loga

        Returns:
            True se enviou
        """
        try:
            # Sync
            self.team_coordinator.sync_all()

            # Gera resumo
            summary = self.team_coordinator.get_team_summary()

            # Fragmenta em mensagens naturais
            messages = []

            messages.append(f"Oi {target_person}! Aqui vai um resumo do time 📊")

            messages.append(
                f"Temos {summary['total_people']} pessoas trabalhando em "
                f"{summary['total_projects']} projetos"
            )

            messages.append(
                f"Tasks: {summary['tasks_em_andamento']} em andamento, "
                f"{summary['tasks_a_fazer']} a fazer, "
                f"{summary['tasks_concluidas']} concluídas"
            )

            if summary['overloaded_count'] > 0:
                messages.append(
                    f"⚠️ {summary['overloaded_count']} pessoas tão sobrecarregadas "
                    f"(workload >70%)"
                )

            messages.append(f"Workload médio do time: {int(summary['avg_workload']*100)}%")

            # Adiciona delays
            messages_with_delay = self.message_fragmenter.add_delays_between_messages(messages)

            if dry_run:
                for i, msg_data in enumerate(messages_with_delay, 1):
                    logger.info(f"  Msg {i}: {msg_data['text']}")
                return True

            # Envia
            if not self.whatsapp_sender:
                return False

            for msg_data in messages_with_delay:
                if msg_data['delay_seconds'] > 0:
                    time.sleep(msg_data['delay_seconds'])

                success, _, _ = self.whatsapp_sender.send_message(
                    person_name=target_person,
                    message=msg_data['text']
                )

                if not success:
                    return False

            return True

        except Exception as e:
            logger.error(f"Erro ao enviar resumo: {e}", exc_info=True)
            return False

    def send_person_insights(
        self,
        target_person: str,
        about_person: Optional[str] = None,
        dry_run: bool = False
    ) -> bool:
        """
        Envia insights sobre uma pessoa específica.

        Args:
            target_person: Para quem enviar
            about_person: Sobre quem são os insights (se None, sobre target_person)
            dry_run: Se True, só loga

        Returns:
            True se enviou
        """
        if not about_person:
            about_person = target_person

        try:
            # Sync
            self.team_coordinator.sync_all()

            # Pega overview da pessoa
            person = self.team_coordinator.get_person_overview(about_person)

            if not person:
                logger.warning(f"Pessoa não encontrada: {about_person}")
                return False

            # Pega recomendações
            recs = self.collab_recommender.get_recommendations_for_person(about_person)

            # Fragmenta em mensagens
            messages = []

            if about_person == target_person:
                messages.append(f"Oi {target_person}! Aqui vão seus insights 🎯")
            else:
                messages.append(f"Oi {target_person}! Aqui vai sobre o {about_person}")

            # Workload
            workload_pct = int(person.workload_score * 100)
            if workload_pct >= 70:
                messages.append(f"⚠️ Workload em {workload_pct}% (tá pesado!)")
            elif workload_pct >= 50:
                messages.append(f"Workload em {workload_pct}% (na medida)")
            else:
                messages.append(f"Workload em {workload_pct}% (tranquilo)")

            # Tasks
            messages.append(
                f"{person.tasks_em_andamento} tasks em andamento, "
                f"{person.tasks_a_fazer} a fazer"
            )

            # Projetos
            if person.projects:
                projects_list = ', '.join(list(person.projects)[:3])
                messages.append(f"Projetos: {projects_list}")

            # Recomendações
            critical_recs = [r for r in recs if r.priority == RecommendationPriority.CRITICAL]
            if critical_recs:
                messages.append(f"🚨 {len(critical_recs)} alerta(s) crítico(s)!")

            # Adiciona delays e envia
            messages_with_delay = self.message_fragmenter.add_delays_between_messages(messages)

            if dry_run:
                for i, msg_data in enumerate(messages_with_delay, 1):
                    logger.info(f"  Msg {i}: {msg_data['text']}")
                return True

            if not self.whatsapp_sender:
                return False

            for msg_data in messages_with_delay:
                if msg_data['delay_seconds'] > 0:
                    time.sleep(msg_data['delay_seconds'])

                success, _, _ = self.whatsapp_sender.send_message(
                    person_name=target_person,
                    message=msg_data['text']
                )

                if not success:
                    return False

            return True

        except Exception as e:
            logger.error(f"Erro ao enviar insights: {e}", exc_info=True)
            return False
