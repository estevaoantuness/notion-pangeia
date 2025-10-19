"""
Emotional Correlation - Correlação Entre Emoções e Produtividade.

Analisa a relação entre:
- Estado emocional (energia, feelings) × Tasks completadas
- Tipo de task × Reação emocional
- Padrões temporais × Bem-estar

Gera insights como:
"Quando você tá com energia baixa, você completa 60% menos tasks.
Mas tasks de 'código' você faz mesmo cansado. Por quê?"
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class EmotionalCorrelationInsight:
    """Insight de correlação emocional."""
    insight_type: str
    correlation_strength: float  # -1 a 1
    message: str
    evidence: Dict
    person_name: str


class EmotionalCorrelation:
    """
    Motor de correlação emocional.

    Cruza dados emocionais com produtividade para
    identificar padrões profundos de comportamento.
    """

    def __init__(self):
        """Inicializa motor de correlação."""
        self.min_data_points = 7  # Mínimo de dias para correlação válida
        logger.info("EmotionalCorrelation inicializado")

    def analyze_correlations(
        self,
        person_name: str,
        metrics_history: List[Dict],
        tasks_history: List[Dict]
    ) -> List[EmotionalCorrelationInsight]:
        """
        Analisa correlações entre emoções e tasks.

        Args:
            person_name: Nome da pessoa
            metrics_history: Histórico de métricas (energia, feelings)
            tasks_history: Histórico de tasks completadas

        Returns:
            Lista de insights de correlação
        """
        insights = []

        # Correlação 1: Energia × Completion Rate
        energy_insight = self._correlate_energy_completion(
            person_name, metrics_history
        )
        if energy_insight:
            insights.append(energy_insight)

        # Correlação 2: Feelings × Tipo de Task
        feelings_insight = self._correlate_feelings_task_type(
            person_name, metrics_history, tasks_history
        )
        if feelings_insight:
            insights.append(feelings_insight)

        # Correlação 3: Produtividade × Bem-estar
        wellbeing_insight = self._correlate_productivity_wellbeing(
            person_name, metrics_history
        )
        if wellbeing_insight:
            insights.append(wellbeing_insight)

        # Correlação 4: Tipo de Task × Performance
        tasktype_insight = self._correlate_tasktype_performance(
            person_name, tasks_history
        )
        if tasktype_insight:
            insights.append(tasktype_insight)

        logger.info(f"Gerados {len(insights)} insights de correlação para {person_name}")
        return insights

    def _correlate_energy_completion(
        self,
        person_name: str,
        metrics_history: List[Dict]
    ) -> Optional[EmotionalCorrelationInsight]:
        """
        Correlaciona nível de energia com completion rate.

        Ex: "Com energia baixa, você completa 40% menos."
        """
        if len(metrics_history) < self.min_data_points:
            return None

        # Agrupa por nível de energia
        energy_groups = {
            "high": [],  # high + very_high
            "medium": [],
            "low": []  # low + very_low
        }

        for metric in metrics_history:
            energy = metric.get("energy_level", "medium")
            completion_rate = metric.get("completion_rate", 0.5)

            if energy in ["high", "very_high"]:
                energy_groups["high"].append(completion_rate)
            elif energy in ["low", "very_low"]:
                energy_groups["low"].append(completion_rate)
            else:
                energy_groups["medium"].append(completion_rate)

        # Calcula médias
        avg_high = (
            sum(energy_groups["high"]) / len(energy_groups["high"])
            if energy_groups["high"] else None
        )
        avg_low = (
            sum(energy_groups["low"]) / len(energy_groups["low"])
            if energy_groups["low"] else None
        )

        # Precisa de ambos os grupos
        if avg_high is None or avg_low is None:
            return None

        # Diferença significativa? (>20%)
        diff = avg_high - avg_low

        if abs(diff) >= 0.2:
            # Correlação detectada
            correlation_strength = diff  # -1 a 1

            if diff > 0:
                # Energia alta = mais produtividade (esperado)
                pct_diff = ((avg_high - avg_low) / avg_low) * 100

                message = (
                    f"💡 Correlação: Energia × Produtividade\n\n"
                    f"Com energia ALTA: {avg_high*100:.0f}% completion\n"
                    f"Com energia BAIXA: {avg_low*100:.0f}% completion\n\n"
                    f"Diferença brutal: {pct_diff:.0f}%\n\n"
                    f"Isso significa:\n"
                    f"Quando você tá cansado, você REALMENTE produz menos.\n\n"
                    f"Não é falta de disciplina. É FISIOLOGIA.\n\n"
                    f"Hierarquia Pangeia: CUIDAR da sua energia vem PRIMEIRO.\n"
                    f"Produtividade é consequência, não objetivo."
                )
            else:
                # Energia baixa = mais produtividade (paradoxo!)
                message = (
                    f"⚠️ Padrão Preocupante Detectado\n\n"
                    f"Com energia BAIXA: {avg_low*100:.0f}% completion\n"
                    f"Com energia ALTA: {avg_high*100:.0f}% completion\n\n"
                    f"Você produz MAIS quando tá ESGOTADO.\n\n"
                    f"Isso NÃO é bom. É sintoma de:\n"
                    f"• Ansiedade (só trabalha sob pressão)\n"
                    f"• Autosabotagem (se pune trabalhando cansado)\n"
                    f"• Perfeccionismo (não se permite descansar)\n\n"
                    f"Vamos conversar sobre isso com HONESTIDADE?"
                )

            return EmotionalCorrelationInsight(
                insight_type="energy_completion_correlation",
                correlation_strength=correlation_strength,
                message=message,
                evidence={
                    "avg_completion_high_energy": avg_high,
                    "avg_completion_low_energy": avg_low,
                    "difference_pct": diff * 100,
                    "high_energy_days": len(energy_groups["high"]),
                    "low_energy_days": len(energy_groups["low"])
                },
                person_name=person_name
            )

        return None

    def _correlate_feelings_task_type(
        self,
        person_name: str,
        metrics_history: List[Dict],
        tasks_history: List[Dict]
    ) -> Optional[EmotionalCorrelationInsight]:
        """
        Correlaciona feelings com tipos de task completadas.

        Ex: "Você fica feliz depois de tasks de 'código' mas
             ansioso depois de tasks de 'vendas'."
        """
        if len(metrics_history) < self.min_data_points:
            return None

        # Cruza métricas com tasks do mesmo dia
        category_feelings = defaultdict(list)

        for metric in metrics_history:
            date_str = metric.get("date")
            feelings = metric.get("current_feelings", [])

            if not date_str or not feelings:
                continue

            # Encontra tasks completadas nesse dia
            metric_date = datetime.fromisoformat(date_str).date()

            for task in tasks_history:
                completed_at = task.get("completed_at")
                category = task.get("category", "Sem categoria")

                if not completed_at:
                    continue

                try:
                    task_date = datetime.fromisoformat(completed_at).date()

                    if task_date == metric_date:
                        # Task completada nesse dia
                        category_feelings[category].extend(feelings)
                except:
                    continue

        # Identifica categoria com feelings consistentemente positivos/negativos
        positive_feelings = [
            "feliz", "animado", "confiante", "realizado",
            "satisfeito", "orgulhoso", "empolgado"
        ]
        negative_feelings = [
            "ansioso", "estressado", "frustrado", "cansado",
            "sobrecarregado", "inseguro", "desmotivado"
        ]

        category_sentiment = {}

        for category, feelings_list in category_feelings.items():
            if len(feelings_list) < 3:  # Precisa de amostra mínima
                continue

            positive_count = sum(
                1 for f in feelings_list
                if any(pos in f.lower() for pos in positive_feelings)
            )
            negative_count = sum(
                1 for f in feelings_list
                if any(neg in f.lower() for neg in negative_feelings)
            )

            total = positive_count + negative_count

            if total == 0:
                continue

            sentiment_score = (positive_count - negative_count) / total
            category_sentiment[category] = {
                "score": sentiment_score,
                "positive": positive_count,
                "negative": negative_count,
                "total": len(feelings_list)
            }

        # Identifica categoria muito positiva ou muito negativa
        for category, sentiment in category_sentiment.items():
            if abs(sentiment["score"]) >= 0.5:  # 50%+ tendência
                if sentiment["score"] > 0:
                    # Categoria positiva
                    message = (
                        f"✨ Descoberta: Trabalho que te Energiza\n\n"
                        f"Tasks de '{category}' te deixam FELIZ.\n\n"
                        f"{sentiment['positive']} vezes você se sentiu bem depois.\n"
                        f"{sentiment['negative']} vezes se sentiu mal.\n\n"
                        f"Esse tipo de trabalho te DÁ energia, não tira.\n\n"
                        f"Pergunta: Como fazer MAIS disso?\n"
                        f"E MENOS das coisas que te drenam?"
                    )
                else:
                    # Categoria negativa
                    message = (
                        f"⚠️ Descoberta: Trabalho que te Drena\n\n"
                        f"Tasks de '{category}' te deixam MAL.\n\n"
                        f"{sentiment['negative']} vezes você se sentiu ansioso/estressado.\n"
                        f"{sentiment['positive']} vezes se sentiu bem.\n\n"
                        f"Isso não é sobre competência.\n"
                        f"É sobre ALINHAMENTO.\n\n"
                        f"Opções:\n"
                        f"• Delegar esse tipo de work\n"
                        f"• Encontrar um jeito diferente de fazer\n"
                        f"• Aceitar que não é pra você\n\n"
                        f"Vamos falar sobre isso?"
                    )

                return EmotionalCorrelationInsight(
                    insight_type="feelings_tasktype_correlation",
                    correlation_strength=sentiment["score"],
                    message=message,
                    evidence={
                        "category": category,
                        "sentiment_score": sentiment["score"],
                        "positive_count": sentiment["positive"],
                        "negative_count": sentiment["negative"],
                        "total_observations": sentiment["total"]
                    },
                    person_name=person_name
                )

        return None

    def _correlate_productivity_wellbeing(
        self,
        person_name: str,
        metrics_history: List[Dict]
    ) -> Optional[EmotionalCorrelationInsight]:
        """
        Correlaciona produtividade com bem-estar geral.

        Detecta se alta produtividade = baixo bem-estar (red flag!)
        """
        if len(metrics_history) < self.min_data_points:
            return None

        # Calcula wellbeing score (energia + feelings positivos)
        wellbeing_productivity = []

        for metric in metrics_history:
            completion_rate = metric.get("completion_rate", 0.5)
            energy = metric.get("energy_level", "medium")
            feelings = metric.get("current_feelings", [])

            # Wellbeing score simplificado
            energy_score = {
                "very_high": 1.0,
                "high": 0.75,
                "medium": 0.5,
                "low": 0.25,
                "very_low": 0.0
            }.get(energy, 0.5)

            # Conta feelings positivos
            positive_feelings = [
                "feliz", "animado", "confiante", "realizado", "satisfeito"
            ]
            positive_count = sum(
                1 for f in feelings
                if any(pos in f.lower() for pos in positive_feelings)
            )
            feelings_score = min(1.0, positive_count / 3)  # Normaliza

            wellbeing = (energy_score + feelings_score) / 2

            wellbeing_productivity.append((wellbeing, completion_rate))

        # Calcula correlação de Pearson (simplificada)
        if len(wellbeing_productivity) < 5:
            return None

        # Separa em quartis
        sorted_by_wellbeing = sorted(wellbeing_productivity, key=lambda x: x[0])
        bottom_quartile = sorted_by_wellbeing[:len(sorted_by_wellbeing)//4]
        top_quartile = sorted_by_wellbeing[-len(sorted_by_wellbeing)//4:]

        avg_productivity_low_wellbeing = sum(p[1] for p in bottom_quartile) / len(bottom_quartile)
        avg_productivity_high_wellbeing = sum(p[1] for p in top_quartile) / len(top_quartile)

        diff = avg_productivity_high_wellbeing - avg_productivity_low_wellbeing

        # Correlação negativa (red flag!)
        if diff < -0.15:
            message = (
                f"🚨 RED FLAG: Produtividade × Bem-estar\n\n"
                f"Quando você tá BEM: {avg_productivity_high_wellbeing*100:.0f}% produtivo\n"
                f"Quando você tá MAL: {avg_productivity_low_wellbeing*100:.0f}% produtivo\n\n"
                f"Você produz MAIS quando tá se sentindo PIOR.\n\n"
                f"Isso é AUTOSSABOTAGEM.\n\n"
                f"Possíveis causas:\n"
                f"• Você se pune trabalhando quando tá mal\n"
                f"• Trabalho é fuga de sentimentos\n"
                f"• Perfeccionismo/culpa te impede de descansar\n\n"
                f"Isso NÃO é sustentável.\n"
                f"Caminho direto pro burnout.\n\n"
                f"Vamos parar e conversar sobre isso AGORA?"
            )

            return EmotionalCorrelationInsight(
                insight_type="productivity_wellbeing_negative_correlation",
                correlation_strength=diff,
                message=message,
                evidence={
                    "avg_productivity_high_wellbeing": avg_productivity_high_wellbeing,
                    "avg_productivity_low_wellbeing": avg_productivity_low_wellbeing,
                    "difference": diff,
                    "sample_size": len(wellbeing_productivity)
                },
                person_name=person_name
            )

        return None

    def _correlate_tasktype_performance(
        self,
        person_name: str,
        tasks_history: List[Dict]
    ) -> Optional[EmotionalCorrelationInsight]:
        """
        Identifica tipos de task onde pessoa performa melhor.

        Ex: "Tasks pequenas você faz em 1 dia. Tasks grandes param."
        """
        if len(tasks_history) < 10:
            return None

        # Classifica tasks por "tamanho" (heurística simples)
        small_tasks = []
        large_tasks = []

        for task in tasks_history:
            title = task.get("title", "")
            description = task.get("description", "")
            days_to_complete = task.get("days_to_complete", 0)

            # Considera "grande" se:
            is_large = (
                len(title) > 50 or
                len(description) > 200 or
                any(word in title.lower() for word in [
                    "migrar", "refatorar", "implementar", "desenvolver"
                ])
            )

            if is_large:
                large_tasks.append(days_to_complete)
            else:
                small_tasks.append(days_to_complete)

        # Precisa de amostra mínima
        if len(small_tasks) < 3 or len(large_tasks) < 3:
            return None

        avg_small = sum(small_tasks) / len(small_tasks)
        avg_large = sum(large_tasks) / len(large_tasks)

        # Tasks grandes demoram >2x tasks pequenas?
        if avg_large > avg_small * 2:
            ratio = avg_large / avg_small

            message = (
                f"📊 Padrão: Tamanho de Task × Performance\n\n"
                f"Tasks PEQUENAS: {avg_small:.1f} dias em média\n"
                f"Tasks GRANDES: {avg_large:.1f} dias em média\n\n"
                f"Tasks grandes demoram {ratio:.1f}x mais.\n\n"
                f"Isso não é procrastinação.\n"
                f"É PARALISIA POR COMPLEXIDADE.\n\n"
                f"Quando a task é grande:\n"
                f"• Seu cérebro não sabe por onde começar\n"
                f"• Você adia porque parece impossível\n"
                f"• A ansiedade te trava\n\n"
                f"Solução: SEMPRE quebrar em pedaços <1 dia.\n\n"
                f"Quer que eu faça isso automaticamente pra você?"
            )

            return EmotionalCorrelationInsight(
                insight_type="tasksize_performance_correlation",
                correlation_strength=ratio,
                message=message,
                evidence={
                    "avg_days_small_tasks": avg_small,
                    "avg_days_large_tasks": avg_large,
                    "ratio": ratio,
                    "small_tasks_count": len(small_tasks),
                    "large_tasks_count": len(large_tasks)
                },
                person_name=person_name
            )

        return None
