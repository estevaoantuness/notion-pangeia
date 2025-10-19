"""
Pattern Detector - Detecção de Padrões Comportamentais.

Analisa histórico de tasks e comportamentos para detectar:
- Procrastinação seletiva (tipos de task que sempre param)
- Padrões temporais (dias/horários problemáticos)
- Complexidade paralisante (tasks grandes que travam)
- Burnout silencioso (queda de performance)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Tipos de padrões detectáveis."""
    SELECTIVE_PROCRASTINATION = "selective_procrastination"  # Adia categoria específica
    TEMPORAL_PATTERN = "temporal_pattern"  # Problema em dia/horário específico
    COMPLEXITY_PARALYSIS = "complexity_paralysis"  # Task grande parada
    SILENT_BURNOUT = "silent_burnout"  # Performance caindo
    CATEGORY_AVERSION = "category_aversion"  # Evita tipo de task
    ENERGY_MISMATCH = "energy_mismatch"  # Tasks vs energia disponível


@dataclass
class DetectedPattern:
    """Padrão comportamental detectado."""
    pattern_type: PatternType
    confidence: float  # 0-1
    evidence: Dict  # Dados que suportam o padrão
    insight: str  # Insight humanizado
    suggested_action: str  # O que fazer
    person_name: str


class PatternDetector:
    """
    Detector de padrões comportamentais.

    Analisa histórico de tasks + métricas psicológicas para
    identificar padrões que revelam bloqueios emocionais ou
    problemas sistêmicos.
    """

    def __init__(self):
        """Inicializa detector de padrões."""
        self.min_data_points = 7  # Mínimo de dias para detectar padrão
        logger.info("PatternDetector inicializado")

    def detect_all_patterns(
        self,
        person_name: str,
        tasks_history: List[Dict],
        metrics_history: List[Dict]
    ) -> List[DetectedPattern]:
        """
        Detecta todos os padrões possíveis.

        Args:
            person_name: Nome da pessoa
            tasks_history: Histórico de tasks (últimos 30 dias)
            metrics_history: Métricas psicológicas históricas

        Returns:
            Lista de padrões detectados
        """
        patterns = []

        # Pattern 1: Procrastinação Seletiva
        selective_pattern = self._detect_selective_procrastination(
            person_name, tasks_history
        )
        if selective_pattern:
            patterns.append(selective_pattern)

        # Pattern 2: Padrões Temporais
        temporal_pattern = self._detect_temporal_pattern(
            person_name, tasks_history, metrics_history
        )
        if temporal_pattern:
            patterns.append(temporal_pattern)

        # Pattern 3: Complexidade Paralisante
        complexity_pattern = self._detect_complexity_paralysis(
            person_name, tasks_history
        )
        if complexity_pattern:
            patterns.append(complexity_pattern)

        # Pattern 4: Burnout Silencioso
        burnout_pattern = self._detect_silent_burnout(
            person_name, metrics_history
        )
        if burnout_pattern:
            patterns.append(burnout_pattern)

        # Pattern 5: Aversão a Categoria
        category_pattern = self._detect_category_aversion(
            person_name, tasks_history
        )
        if category_pattern:
            patterns.append(category_pattern)

        logger.info(f"Detectados {len(patterns)} padrões para {person_name}")
        return patterns

    def _detect_selective_procrastination(
        self,
        person_name: str,
        tasks_history: List[Dict]
    ) -> Optional[DetectedPattern]:
        """
        Detecta procrastinação seletiva por categoria de task.

        Se tasks de uma categoria sempre demoram >2x a média,
        há um padrão de procrastinação seletiva.
        """
        if len(tasks_history) < self.min_data_points:
            return None

        # Agrupa por categoria e calcula tempo médio
        category_times = {}

        for task in tasks_history:
            category = task.get("category", "Sem categoria")
            days_to_complete = task.get("days_to_complete", 0)

            if category not in category_times:
                category_times[category] = []

            if days_to_complete > 0:
                category_times[category].append(days_to_complete)

        # Calcula média global
        all_times = [t for times in category_times.values() for t in times]
        if not all_times:
            return None

        global_avg = sum(all_times) / len(all_times)

        # Identifica categoria problemática (>2x a média)
        for category, times in category_times.items():
            if len(times) < 3:  # Precisa de pelo menos 3 amostras
                continue

            category_avg = sum(times) / len(times)

            if category_avg > global_avg * 2:
                # Padrão detectado!
                confidence = min(1.0, (category_avg / global_avg) / 4)

                insight = (
                    f"Padrão detectado 📊\n\n"
                    f"Tasks de '{category}' demoram {category_avg:.1f} dias em média.\n"
                    f"Suas outras tasks: {global_avg:.1f} dias.\n\n"
                    f"Você demora {category_avg/global_avg:.1f}x mais nesse tipo de work.\n\n"
                    f"Isso aconteceu {len(times)} vezes nos últimos 30 dias.\n\n"
                    f"Hipóteses:\n"
                    f"• Essas tasks são chatas mas necessárias?\n"
                    f"• Você não se sente confortável com esse tipo de trabalho?\n"
                    f"• Tem algo emocional rolando?\n\n"
                    f"Vamos conversar sobre isso? Pangeia não julga, só quer entender."
                )

                suggested_action = (
                    f"Conversar sobre aversão a tasks de '{category}' e "
                    f"encontrar estratégias para lidar (delegar, simplificar, ou aceitar e fazer rápido)"
                )

                return DetectedPattern(
                    pattern_type=PatternType.SELECTIVE_PROCRASTINATION,
                    confidence=confidence,
                    evidence={
                        "category": category,
                        "category_avg_days": category_avg,
                        "global_avg_days": global_avg,
                        "ratio": category_avg / global_avg,
                        "occurrences": len(times)
                    },
                    insight=insight,
                    suggested_action=suggested_action,
                    person_name=person_name
                )

        return None

    def _detect_temporal_pattern(
        self,
        person_name: str,
        tasks_history: List[Dict],
        metrics_history: List[Dict]
    ) -> Optional[DetectedPattern]:
        """
        Detecta padrões temporais (ex: toda segunda é ruim).

        Analisa completion rate por dia da semana.
        """
        if len(metrics_history) < self.min_data_points:
            return None

        # Agrupa por dia da semana
        weekday_rates = {i: [] for i in range(7)}  # 0=Monday

        for metric in metrics_history:
            date_str = metric.get("date")
            completion_rate = metric.get("completion_rate", 0.5)

            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str)
                    weekday = dt.weekday()
                    weekday_rates[weekday].append(completion_rate)
                except:
                    continue

        # Calcula média por dia
        weekday_avgs = {}
        for weekday, rates in weekday_rates.items():
            if rates:
                weekday_avgs[weekday] = sum(rates) / len(rates)

        if not weekday_avgs:
            return None

        global_avg = sum(weekday_avgs.values()) / len(weekday_avgs)

        # Identifica dia problemático (<70% da média)
        weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

        for weekday, avg_rate in weekday_avgs.items():
            if avg_rate < global_avg * 0.7:
                confidence = 1.0 - (avg_rate / global_avg)

                insight = (
                    f"Padrão temporal detectado 📅\n\n"
                    f"Toda {weekday_names[weekday]} você tem performance mais baixa.\n\n"
                    f"{weekday_names[weekday]}: {avg_rate*100:.0f}% de completion\n"
                    f"Outros dias: {global_avg*100:.0f}% em média\n\n"
                    f"Isso não é coincidência.\n\n"
                    f"Hipóteses:\n"
                    f"• Final de semana te deixa cansado?\n"
                    f"• Você agenda coisas pesadas demais pra {weekday_names[weekday]}?\n"
                    f"• Tem algum padrão na vida pessoal?\n\n"
                    f"Vamos ajustar como você planeja {weekday_names[weekday]}s?"
                )

                suggested_action = (
                    f"Reduzir carga em {weekday_names[weekday]}s ou "
                    f"investigar o que deixa esse dia mais difícil"
                )

                return DetectedPattern(
                    pattern_type=PatternType.TEMPORAL_PATTERN,
                    confidence=confidence,
                    evidence={
                        "problematic_weekday": weekday,
                        "weekday_name": weekday_names[weekday],
                        "weekday_rate": avg_rate,
                        "global_rate": global_avg
                    },
                    insight=insight,
                    suggested_action=suggested_action,
                    person_name=person_name
                )

        return None

    def _detect_complexity_paralysis(
        self,
        person_name: str,
        tasks_history: List[Dict]
    ) -> Optional[DetectedPattern]:
        """
        Detecta tasks grandes que param por serem complexas demais.

        Task com >1 descrição longa parada >5 dias = paralisia.
        """
        for task in tasks_history:
            title = task.get("title", "")
            description = task.get("description", "")
            days_stalled = task.get("days_stalled", 0)
            status = task.get("status", "")

            # Critérios de complexidade:
            is_complex = (
                len(title) > 50 or  # Título longo
                len(description) > 200 or  # Descrição detalhada
                "migrar" in title.lower() or
                "refatorar" in title.lower() or
                "implementar" in title.lower()
            )

            is_stalled = days_stalled >= 5 and status != "Concluída"

            if is_complex and is_stalled:
                confidence = min(1.0, days_stalled / 10)

                insight = (
                    f"Paralisia por complexidade detectada 🧠\n\n"
                    f"'{title}' tá parada há {days_stalled} dias.\n\n"
                    f"Achei o problema: ela é GRANDE demais.\n\n"
                    f"Você não tá procrastinando por preguiça.\n"
                    f"Você tá paralisado porque não sabe por onde começar.\n\n"
                    f"Quando a task é muito grande, o cérebro trava.\n\n"
                    f"Vamos quebrar em passos pequenos AGORA?"
                )

                suggested_action = (
                    f"Decompor '{title}' em 3-5 subtasks menores "
                    f"e começar pela mais fácil HOJE"
                )

                return DetectedPattern(
                    pattern_type=PatternType.COMPLEXITY_PARALYSIS,
                    confidence=confidence,
                    evidence={
                        "task_title": title,
                        "days_stalled": days_stalled,
                        "is_complex": is_complex
                    },
                    insight=insight,
                    suggested_action=suggested_action,
                    person_name=person_name
                )

        return None

    def _detect_silent_burnout(
        self,
        person_name: str,
        metrics_history: List[Dict]
    ) -> Optional[DetectedPattern]:
        """
        Detecta burnout silencioso (completion rate caindo + energia baixa).
        """
        if len(metrics_history) < 7:
            return None

        # Últimos 7 dias vs 7 dias anteriores
        recent = metrics_history[-7:]
        previous = metrics_history[-14:-7] if len(metrics_history) >= 14 else []

        if not previous:
            return None

        recent_avg = sum(m.get("completion_rate", 0.5) for m in recent) / len(recent)
        previous_avg = sum(m.get("completion_rate", 0.5) for m in previous) / len(previous)

        # Queda >30% = alerta
        if recent_avg < previous_avg * 0.7:
            drop_pct = ((previous_avg - recent_avg) / previous_avg) * 100
            confidence = min(1.0, drop_pct / 50)

            # Check energia também
            recent_energy = [m.get("energy_level", "medium") for m in recent]
            low_energy_count = sum(1 for e in recent_energy if e in ["low", "very_low"])

            insight = (
                f"ALERTA: Burnout silencioso detectado 🚨\n\n"
                f"Seu completion rate caiu {drop_pct:.0f}% essa semana.\n\n"
                f"Semana passada: {previous_avg*100:.0f}%\n"
                f"Esta semana: {recent_avg*100:.0f}%\n\n"
            )

            if low_energy_count >= 4:
                insight += (
                    f"E {low_energy_count} de 7 dias com energia baixa.\n\n"
                    f"Isso NÃO é sobre organização.\n"
                    f"Isso NÃO é sobre disciplina.\n\n"
                    f"Você tá ESGOTADO.\n\n"
                )
            else:
                insight += (
                    f"Sua energia não caiu tanto, então o problema pode ser:\n"
                    f"• Sobrecarga de tasks\n"
                    f"• Tasks muito complexas\n"
                    f"• Falta de clareza sobre prioridades\n\n"
                )

            insight += (
                f"Pangeia hierarquia: CUIDAR vem PRIMEIRO.\n\n"
                f"Vamos reduzir sua carga AGORA antes que vire burnout de verdade."
            )

            suggested_action = (
                "Cortar 50% das tasks imediatamente e "
                "focar só no absolutamente essencial"
            )

            return DetectedPattern(
                pattern_type=PatternType.SILENT_BURNOUT,
                confidence=confidence,
                evidence={
                    "recent_rate": recent_avg,
                    "previous_rate": previous_avg,
                    "drop_percentage": drop_pct,
                    "low_energy_days": low_energy_count
                },
                insight=insight,
                suggested_action=suggested_action,
                person_name=person_name
            )

        return None

    def _detect_category_aversion(
        self,
        person_name: str,
        tasks_history: List[Dict]
    ) -> Optional[DetectedPattern]:
        """
        Detecta aversão específica a categoria (ex: sempre adia vendas).
        Similar a selective procrastination mas mais específico.
        """
        # Conta quantas tasks de cada categoria estão paradas >3 dias
        category_stalled = {}

        for task in tasks_history:
            category = task.get("category", "Sem categoria")
            days_stalled = task.get("days_stalled", 0)

            if category not in category_stalled:
                category_stalled[category] = {"total": 0, "stalled": 0}

            category_stalled[category]["total"] += 1

            if days_stalled >= 3:
                category_stalled[category]["stalled"] += 1

        # Identifica categoria com >70% paradas
        for category, counts in category_stalled.items():
            if counts["total"] < 3:  # Precisa de amostra mínima
                continue

            stalled_rate = counts["stalled"] / counts["total"]

            if stalled_rate >= 0.7:
                confidence = stalled_rate

                insight = (
                    f"Aversão detectada 😰\n\n"
                    f"{counts['stalled']} de {counts['total']} tasks de '{category}' estão paradas.\n\n"
                    f"Isso é {stalled_rate*100:.0f}% de taxa de paralisia.\n\n"
                    f"Você claramente TEM algo com esse tipo de work.\n\n"
                    f"Não é falta de tempo. Não é falta de skill.\n"
                    f"É AVERSÃO.\n\n"
                    f"Hipóteses:\n"
                    f"• Te deixa ansioso?\n"
                    f"• Você não vê sentido nisso?\n"
                    f"• Conflito de valores?\n\n"
                    f"Vamos falar sobre isso com honestidade?"
                )

                suggested_action = (
                    f"Conversa profunda sobre por que '{category}' te trava tanto"
                )

                return DetectedPattern(
                    pattern_type=PatternType.CATEGORY_AVERSION,
                    confidence=confidence,
                    evidence={
                        "category": category,
                        "total_tasks": counts["total"],
                        "stalled_tasks": counts["stalled"],
                        "stalled_rate": stalled_rate
                    },
                    insight=insight,
                    suggested_action=suggested_action,
                    person_name=person_name
                )

        return None
