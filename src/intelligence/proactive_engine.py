"""
Proactive Engine - Motor de Inteligência Proativa.

Sistema que MONITORA automaticamente e ENVIA insights sem ser solicitado:
- Alertas de tasks esquecidas/paradas
- Insights de padrões detectados
- Sugestões de corte/cancelamento
- Decomposição automática de tasks complexas

NÃO espera comando do usuário. Age proativamente.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from enum import Enum

from .pattern_detector import PatternDetector, DetectedPattern, PatternType

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Tipos de triggers proativos."""
    STALLED_TASK = "stalled_task"  # Task parada >3 dias
    PATTERN_DETECTED = "pattern_detected"  # Padrão comportamental detectado
    OVERLOAD_WARNING = "overload_warning"  # Sobrecarga detectada
    AUTO_DECOMPOSE = "auto_decompose"  # Task grande precisa ser quebrada
    BURNOUT_ALERT = "burnout_alert"  # Alerta de burnout
    CATEGORY_INSIGHT = "category_insight"  # Insight sobre categoria


@dataclass
class ProactiveInsight:
    """Insight proativo gerado pelo sistema."""
    trigger_type: TriggerType
    priority: str  # "urgent", "high", "medium", "low"
    message: str  # Mensagem para enviar ao usuário
    suggested_action: str  # O que fazer
    metadata: Dict  # Dados adicionais
    person_name: str


class ProactiveEngine:
    """
    Motor de Inteligência Proativa.

    Analisa tasks e métricas automaticamente e gera insights
    sem precisar ser solicitado pelo usuário.

    Funciona como um "terapeuta vigilante" que observa
    padrões e intervém quando necessário.
    """

    def __init__(self):
        """Inicializa motor proativo."""
        self.pattern_detector = PatternDetector()

        # Thresholds configuráveis
        self.stalled_days_threshold = 3
        self.overload_task_count = 15
        self.complexity_paralysis_days = 5

        logger.info("ProactiveEngine inicializado")

    def analyze_and_generate_insights(
        self,
        person_name: str,
        current_tasks: List[Dict],
        tasks_history: List[Dict],
        metrics_history: List[Dict]
    ) -> List[ProactiveInsight]:
        """
        Analisa tudo e gera insights proativos.

        Args:
            person_name: Nome da pessoa
            current_tasks: Tasks atuais (não concluídas)
            tasks_history: Histórico completo (últimos 30 dias)
            metrics_history: Métricas psicológicas históricas

        Returns:
            Lista de insights proativos ordenados por prioridade
        """
        insights = []

        # Trigger 1: Tasks Paradas/Esquecidas
        stalled_insights = self._check_stalled_tasks(person_name, current_tasks)
        insights.extend(stalled_insights)

        # Trigger 2: Padrões Comportamentais
        pattern_insights = self._check_behavioral_patterns(
            person_name, tasks_history, metrics_history
        )
        insights.extend(pattern_insights)

        # Trigger 3: Sobrecarga
        overload_insight = self._check_overload(person_name, current_tasks)
        if overload_insight:
            insights.append(overload_insight)

        # Trigger 4: Auto-Decomposição
        decompose_insights = self._check_auto_decompose(person_name, current_tasks)
        insights.extend(decompose_insights)

        # Trigger 5: Category Insights
        category_insight = self._check_category_patterns(person_name, tasks_history)
        if category_insight:
            insights.append(category_insight)

        # Ordena por prioridade
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        insights.sort(key=lambda x: priority_order.get(x.priority, 4))

        logger.info(f"Gerados {len(insights)} insights proativos para {person_name}")
        return insights

    def _check_stalled_tasks(
        self,
        person_name: str,
        current_tasks: List[Dict]
    ) -> List[ProactiveInsight]:
        """
        Detecta tasks paradas >3 dias.

        Alerta proativo: "Essa task tá esquecida, vamos resolver?"
        """
        insights = []

        for task in current_tasks:
            days_stalled = task.get("days_stalled", 0)
            title = task.get("title", "Task sem nome")
            status = task.get("status", "")

            # Ignora tasks já concluídas
            if status == "Concluída":
                continue

            # Task parada há >3 dias
            if days_stalled >= self.stalled_days_threshold:
                priority = "high" if days_stalled >= 7 else "medium"

                message = (
                    f"🔔 Alerta: Task parada\n\n"
                    f"'{title}' tá parada há {days_stalled} dias.\n\n"
                )

                if days_stalled >= 7:
                    message += (
                        f"Isso não é coincidência. Algo tá te travando.\n\n"
                        f"Opções:\n"
                        f"1️⃣ Cancelar - Essa task importa mesmo?\n"
                        f"2️⃣ Decompor - Tá grande demais?\n"
                        f"3️⃣ Delegar - Alguém pode fazer?\n"
                        f"4️⃣ Fazer agora - Bora resolver de vez?\n\n"
                        f"O que você quer fazer?"
                    )
                else:
                    message += (
                        f"Tá tudo bem se essa task não importa.\n"
                        f"Mas se importa, vamos resolver?\n\n"
                        f"Quer que eu quebre em passos menores?"
                    )

                suggested_action = (
                    f"Perguntar se task '{title}' ainda importa ou se pode cancelar"
                )

                insights.append(ProactiveInsight(
                    trigger_type=TriggerType.STALLED_TASK,
                    priority=priority,
                    message=message,
                    suggested_action=suggested_action,
                    metadata={
                        "task_title": title,
                        "days_stalled": days_stalled,
                        "task_id": task.get("id")
                    },
                    person_name=person_name
                ))

        return insights

    def _check_behavioral_patterns(
        self,
        person_name: str,
        tasks_history: List[Dict],
        metrics_history: List[Dict]
    ) -> List[ProactiveInsight]:
        """
        Detecta padrões comportamentais e gera insights.

        Ex: "Toda segunda você procrastina, por quê?"
        """
        insights = []

        # Usa o Pattern Detector
        patterns = self.pattern_detector.detect_all_patterns(
            person_name, tasks_history, metrics_history
        )

        for pattern in patterns:
            # Mapeia tipo de padrão para prioridade
            if pattern.pattern_type == PatternType.SILENT_BURNOUT:
                priority = "urgent"
            elif pattern.pattern_type in [
                PatternType.COMPLEXITY_PARALYSIS,
                PatternType.CATEGORY_AVERSION
            ]:
                priority = "high"
            else:
                priority = "medium"

            insights.append(ProactiveInsight(
                trigger_type=TriggerType.PATTERN_DETECTED,
                priority=priority,
                message=pattern.insight,
                suggested_action=pattern.suggested_action,
                metadata={
                    "pattern_type": pattern.pattern_type.value,
                    "confidence": pattern.confidence,
                    "evidence": pattern.evidence
                },
                person_name=person_name
            ))

        return insights

    def _check_overload(
        self,
        person_name: str,
        current_tasks: List[Dict]
    ) -> Optional[ProactiveInsight]:
        """
        Detecta sobrecarga (>15 tasks ativas).

        Alerta: "Você tem tasks demais. Vamos cortar?"
        """
        active_tasks = [
            t for t in current_tasks
            if t.get("status") not in ["Concluída", "Cancelada"]
        ]

        task_count = len(active_tasks)

        if task_count >= self.overload_task_count:
            # Agrupa por categoria
            categories = {}
            for task in active_tasks:
                category = task.get("category", "Sem categoria")
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1

            # Formata top categorias
            top_categories = sorted(
                categories.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            category_text = "\n".join([
                f"• {cat}: {count} tasks"
                for cat, count in top_categories
            ])

            message = (
                f"🚨 SOBRECARGA DETECTADA\n\n"
                f"Você tem {task_count} tasks ativas.\n"
                f"Isso não é produtividade. É autossabotagem.\n\n"
                f"Distribuição:\n{category_text}\n\n"
                f"Hierarquia Pangeia: CUIDAR vem PRIMEIRO.\n\n"
                f"Regra brutal: Se você tem 15 tasks, 10 são lixo.\n"
                f"Vamos cortar AGORA as que não importam?\n\n"
                f"Me diz: qual dessas categorias você pode IGNORAR essa semana?"
            )

            suggested_action = (
                f"Reduzir carga de {task_count} para <10 tasks, cortando impiedosamente"
            )

            return ProactiveInsight(
                trigger_type=TriggerType.OVERLOAD_WARNING,
                priority="urgent",
                message=message,
                suggested_action=suggested_action,
                metadata={
                    "task_count": task_count,
                    "categories": categories
                },
                person_name=person_name
            )

        return None

    def _check_auto_decompose(
        self,
        person_name: str,
        current_tasks: List[Dict]
    ) -> List[ProactiveInsight]:
        """
        Detecta tasks grandes paradas que precisam ser quebradas.

        Alerta: "Quebrei essa task em 4 passos. Vamos começar?"
        """
        insights = []

        for task in current_tasks:
            title = task.get("title", "")
            description = task.get("description", "")
            days_stalled = task.get("days_stalled", 0)
            status = task.get("status", "")

            # Ignora concluídas
            if status == "Concluída":
                continue

            # Critérios para auto-decomposição:
            is_complex = (
                len(title) > 50 or
                len(description) > 200 or
                any(word in title.lower() for word in [
                    "migrar", "refatorar", "implementar", "desenvolver",
                    "criar sistema", "integrar", "automatizar"
                ])
            )

            is_stalled = days_stalled >= self.complexity_paralysis_days

            if is_complex and is_stalled:
                # Sugere decomposição automática
                suggested_subtasks = self._generate_subtasks_suggestion(
                    title, description
                )

                subtasks_text = "\n".join([
                    f"{i+1}. {subtask}"
                    for i, subtask in enumerate(suggested_subtasks)
                ])

                message = (
                    f"💡 Sugestão: Decomposição Automática\n\n"
                    f"'{title}' tá parada há {days_stalled} dias.\n\n"
                    f"Eu sei o problema: ela é GRANDE demais.\n"
                    f"Seu cérebro trava quando a task não tem começo claro.\n\n"
                    f"Quebrei em passos menores:\n\n{subtasks_text}\n\n"
                    f"Quer que eu crie essas subtasks pra você?\n"
                    f"Você só precisa começar pela #1 HOJE."
                )

                suggested_action = (
                    f"Decompor '{title}' automaticamente e marcar primeira subtask como prioritária"
                )

                insights.append(ProactiveInsight(
                    trigger_type=TriggerType.AUTO_DECOMPOSE,
                    priority="high",
                    message=message,
                    suggested_action=suggested_action,
                    metadata={
                        "task_title": title,
                        "task_id": task.get("id"),
                        "suggested_subtasks": suggested_subtasks,
                        "days_stalled": days_stalled
                    },
                    person_name=person_name
                ))

        return insights

    def _check_category_patterns(
        self,
        person_name: str,
        tasks_history: List[Dict]
    ) -> Optional[ProactiveInsight]:
        """
        Detecta padrões de categoria ao longo do tempo.

        Ex: "Você completa muito mais tasks de 'código' que 'vendas'. Por quê?"
        """
        if len(tasks_history) < 10:
            return None

        # Agrupa por categoria
        category_stats = {}

        for task in tasks_history:
            category = task.get("category", "Sem categoria")
            status = task.get("status", "")

            if category not in category_stats:
                category_stats[category] = {"total": 0, "completed": 0}

            category_stats[category]["total"] += 1

            if status == "Concluída":
                category_stats[category]["completed"] += 1

        # Calcula completion rate por categoria
        category_rates = {}
        for category, stats in category_stats.items():
            if stats["total"] >= 3:  # Mínimo 3 amostras
                rate = stats["completed"] / stats["total"]
                category_rates[category] = {
                    "rate": rate,
                    "total": stats["total"],
                    "completed": stats["completed"]
                }

        if len(category_rates) < 2:
            return None

        # Identifica categoria muito superior
        sorted_categories = sorted(
            category_rates.items(),
            key=lambda x: x[1]["rate"],
            reverse=True
        )

        best_category, best_stats = sorted_categories[0]
        worst_category, worst_stats = sorted_categories[-1]

        # Diferença significativa? (>40%)
        if best_stats["rate"] - worst_stats["rate"] >= 0.4:
            message = (
                f"📊 Insight: Padrão de Performance\n\n"
                f"Tasks de '{best_category}': {best_stats['rate']*100:.0f}% concluídas\n"
                f"Tasks de '{worst_category}': {worst_stats['rate']*100:.0f}% concluídas\n\n"
                f"Diferença brutal de {(best_stats['rate'] - worst_stats['rate'])*100:.0f}%.\n\n"
                f"Isso revela algo:\n"
                f"• '{best_category}' te dá energia?\n"
                f"• '{worst_category}' te drena?\n\n"
                f"Não é sobre disciplina. É sobre ALINHAMENTO.\n\n"
                f"Quer conversar sobre isso?"
            )

            suggested_action = (
                f"Explorar por que '{best_category}' funciona e '{worst_category}' não"
            )

            return ProactiveInsight(
                trigger_type=TriggerType.CATEGORY_INSIGHT,
                priority="medium",
                message=message,
                suggested_action=suggested_action,
                metadata={
                    "best_category": best_category,
                    "best_rate": best_stats["rate"],
                    "worst_category": worst_category,
                    "worst_rate": worst_stats["rate"]
                },
                person_name=person_name
            )

        return None

    def _generate_subtasks_suggestion(
        self,
        title: str,
        description: str
    ) -> List[str]:
        """
        Gera sugestões de subtasks baseado em heurísticas.

        Em produção, isso poderia usar GPT-4 para ser mais inteligente.
        Por ora, usa regras simples.
        """
        title_lower = title.lower()

        # Heurísticas por tipo de task
        if "migrar" in title_lower or "migração" in title_lower:
            return [
                "Fazer backup dos dados atuais",
                "Preparar ambiente de destino",
                "Migrar dados em lote pequeno (teste)",
                "Validar integridade dos dados migrados",
                "Executar migração completa"
            ]

        elif "refatorar" in title_lower or "refatoração" in title_lower:
            return [
                "Identificar código a ser refatorado",
                "Escrever testes para código existente",
                "Refatorar mantendo testes passando",
                "Code review e ajustes finais"
            ]

        elif "implementar" in title_lower or "desenvolver" in title_lower:
            return [
                "Definir requisitos e escopo exato",
                "Criar estrutura básica/esqueleto",
                "Implementar funcionalidade core",
                "Adicionar validações e tratamento de erros",
                "Testar e documentar"
            ]

        elif "integrar" in title_lower or "integração" in title_lower:
            return [
                "Estudar documentação da API/serviço",
                "Configurar credenciais e ambiente",
                "Implementar chamada básica (teste)",
                "Integrar com sistema existente",
                "Testar edge cases e erros"
            ]

        else:
            # Decomposição genérica
            return [
                f"Planejar: definir escopo e requisitos de '{title}'",
                f"Preparar: reunir recursos necessários",
                f"Executar: fazer parte core",
                f"Validar: testar e ajustar",
                f"Finalizar: documentar e concluir"
            ]
