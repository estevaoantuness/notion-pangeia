"""
Analytics de Pessoas - People Analytics.

Gerencia perfis, identifica padrões e fornece insights
sobre colaboradores.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .profile import PersonProfile, PersonalityTrait, ProductivityPattern, CommunicationStyle
from ..psychology.engine import PsychologicalEngine, PsychologicalMetrics

logger = logging.getLogger(__name__)


class PeopleAnalytics:
    """
    Gerencia perfis de pessoas e fornece insights.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Inicializa o analytics de pessoas.

        Args:
            storage_path: Caminho para armazenar perfis
        """
        if storage_path is None:
            storage_path = Path.home() / ".pangeia" / "people_profiles.json"
        else:
            storage_path = Path(storage_path)

        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.profiles: Dict[str, PersonProfile] = {}
        self.psych_engine = PsychologicalEngine()

        self._load_profiles()
        logger.info(f"People Analytics inicializado - {len(self.profiles)} perfis carregados")

    def _load_profiles(self) -> None:
        """Carrega perfis do disco."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for phone, profile_data in data.items():
                self.profiles[phone] = PersonProfile.from_dict(profile_data)

            logger.info(f"Carregados {len(self.profiles)} perfis")

        except Exception as e:
            logger.error(f"Erro ao carregar perfis: {e}")

    def _save_profiles(self) -> None:
        """Salva perfis no disco."""
        try:
            data = {
                phone: profile.to_dict()
                for phone, profile in self.profiles.items()
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Salvos {len(self.profiles)} perfis")

        except Exception as e:
            logger.error(f"Erro ao salvar perfis: {e}")

    def get_or_create_profile(
        self,
        name: str,
        phone: str,
        role: str = ""
    ) -> PersonProfile:
        """
        Obtém perfil existente ou cria novo.

        Args:
            name: Nome da pessoa
            phone: Telefone
            role: Cargo/função

        Returns:
            Perfil da pessoa
        """
        if phone not in self.profiles:
            self.profiles[phone] = PersonProfile(
                name=name,
                phone=phone,
                role=role
            )
            self._save_profiles()
            logger.info(f"Novo perfil criado: {name}")

        return self.profiles[phone]

    def update_profile_from_metrics(
        self,
        phone: str,
        metrics: PsychologicalMetrics
    ) -> PersonProfile:
        """
        Atualiza perfil baseado em métricas psicológicas.

        Args:
            phone: Telefone da pessoa
            metrics: Métricas psicológicas

        Returns:
            Perfil atualizado
        """
        if phone not in self.profiles:
            logger.warning(f"Perfil não encontrado para {phone}")
            return None

        profile = self.profiles[phone]

        # Atualizar estado emocional
        profile.update_emotional_state(
            state=metrics.emotional_state.value,
            trend=self._determine_trend(profile, metrics),
            risk_burnout=self.psych_engine.should_intervene(metrics)
        )

        # Atualizar stats de produtividade
        profile.productivity_stats.avg_completion_rate = metrics.completion_rate
        profile.productivity_stats.avg_response_time_hours = metrics.response_time_hours

        # Atualizar ratio positivo/negativo
        total_words = metrics.positive_words_count + metrics.negative_words_count
        if total_words > 0:
            profile.emotional_profile.positive_ratio = (
                metrics.positive_words_count / total_words
            )

        # Identificar traços de personalidade
        self._infer_personality_traits(profile, metrics)

        # Identificar padrão de produtividade
        self._infer_productivity_pattern(profile, metrics)

        # Atualizar pontos fortes e áreas de melhoria
        self._update_strengths_and_improvements(profile, metrics)

        profile.updated_at = datetime.now()
        self._save_profiles()

        return profile

    def _determine_trend(
        self,
        profile: PersonProfile,
        metrics: PsychologicalMetrics
    ) -> str:
        """Determina se a pessoa está melhorando, estável ou piorando."""

        # Comparar com estado anterior
        prev_state = profile.emotional_profile.current_state
        current_state = metrics.emotional_state.value

        # Ranking de estados (pior para melhor)
        state_ranking = {
            "burned_out": 1,
            "overwhelmed": 2,
            "stressed": 3,
            "disengaged": 3,
            "balanced": 4,
            "motivated": 5
        }

        prev_rank = state_ranking.get(prev_state, 4)
        curr_rank = state_ranking.get(current_state, 4)

        if curr_rank > prev_rank:
            return "improving"
        elif curr_rank < prev_rank:
            return "declining"
        else:
            return "stable"

    def _infer_personality_traits(
        self,
        profile: PersonProfile,
        metrics: PsychologicalMetrics
    ) -> None:
        """Infere traços de personalidade baseado em comportamento."""

        # Needs encouragement se tem baixa motivação intrínseca
        if metrics.completion_rate < 0.6 and metrics.checkin_participation > 0.7:
            profile.set_personality_trait(PersonalityTrait.NEEDS_ENCOURAGEMENT, True)

        # Self-motivated se tem alta taxa sem muito engajamento
        if metrics.completion_rate > 0.8 and metrics.checkin_participation < 0.5:
            profile.set_personality_trait(PersonalityTrait.SELF_MOTIVATED, True)

        # Collaborative se usa muitas palavras positivas e participa
        if metrics.positive_words_count > 10 and metrics.checkin_participation > 0.7:
            profile.set_personality_trait(PersonalityTrait.COLLABORATIVE, True)

        # Prefers small tasks se tem muitas tarefas concluídas
        if metrics.tasks_completed_today > 5:
            profile.set_personality_trait(PersonalityTrait.PREFERS_SMALL_TASKS, True)

    def _infer_productivity_pattern(
        self,
        profile: PersonProfile,
        metrics: PsychologicalMetrics
    ) -> None:
        """Infere padrão de produtividade."""

        # Por enquanto, usar padrão consistente como padrão
        # Em uma implementação completa, analisaria timestamps de conclusão
        profile.productivity_pattern = ProductivityPattern.CONSISTENT

    def _update_strengths_and_improvements(
        self,
        profile: PersonProfile,
        metrics: PsychologicalMetrics
    ) -> None:
        """Atualiza pontos fortes e áreas de melhoria."""

        # Identificar pontos fortes
        if metrics.completion_rate > 0.8:
            profile.add_strength("Alta taxa de conclusão")

        if metrics.checkin_participation > 0.8:
            profile.add_strength("Engajamento consistente")

        if metrics.positive_words_count > metrics.negative_words_count * 2:
            profile.add_strength("Comunicação positiva")

        # Identificar áreas de melhoria
        if metrics.tasks_blocked > 3:
            profile.add_improvement_area("Reduzir bloqueios em tarefas")

        if metrics.response_time_hours > 6:
            profile.add_improvement_area("Melhorar tempo de resposta")

    def get_team_summary(self) -> Dict:
        """
        Retorna resumo da equipe.

        Returns:
            Dicionário com métricas da equipe
        """
        if not self.profiles:
            return {}

        total = len(self.profiles)
        motivated = sum(
            1 for p in self.profiles.values()
            if p.emotional_profile.current_state == "motivated"
        )
        at_risk = sum(
            1 for p in self.profiles.values()
            if p.emotional_profile.risk_burnout
        )

        return {
            "total_people": total,
            "motivated": motivated,
            "at_risk": at_risk,
            "healthy_percentage": (total - at_risk) / total * 100 if total > 0 else 0
        }

    def get_people_needing_attention(self) -> List[PersonProfile]:
        """
        Retorna lista de pessoas que precisam de atenção.

        Returns:
            Lista de perfis em risco
        """
        return [
            profile for profile in self.profiles.values()
            if profile.emotional_profile.risk_burnout
            or profile.emotional_profile.current_state in ["burned_out", "overwhelmed"]
        ]

    def get_top_performers(self, limit: int = 5) -> List[PersonProfile]:
        """
        Retorna top performers da equipe.

        Args:
            limit: Número de pessoas a retornar

        Returns:
            Lista de perfis ordenada por performance
        """
        sorted_profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.productivity_stats.avg_completion_rate,
            reverse=True
        )

        return sorted_profiles[:limit]

    def generate_person_insights(self, phone: str) -> List[str]:
        """
        Gera insights sobre uma pessoa específica.

        Args:
            phone: Telefone da pessoa

        Returns:
            Lista de insights
        """
        if phone not in self.profiles:
            return ["Perfil não encontrado"]

        profile = self.profiles[phone]
        insights = []

        # Estado emocional
        state = profile.emotional_profile.current_state
        trend = profile.emotional_profile.trend

        if trend == "improving":
            insights.append(f"Estado emocional está melhorando ({state})")
        elif trend == "declining":
            insights.append(f"⚠️ Estado emocional está piorando ({state})")

        # Risco de burnout
        if profile.emotional_profile.risk_burnout:
            insights.append("🚨 RISCO DE BURNOUT DETECTADO")

        # Produtividade
        comp_rate = profile.productivity_stats.avg_completion_rate
        if comp_rate > 0.8:
            insights.append(f"Excelente taxa de conclusão ({comp_rate * 100:.0f}%)")
        elif comp_rate < 0.5:
            insights.append(f"Taxa de conclusão baixa ({comp_rate * 100:.0f}%)")

        # Traços de personalidade
        if profile.has_trait(PersonalityTrait.NEEDS_ENCOURAGEMENT):
            insights.append("Responde bem a encorajamento")

        if profile.has_trait(PersonalityTrait.COLLABORATIVE):
            insights.append("Perfil colaborativo")

        # Pontos fortes
        if profile.strengths:
            insights.append(f"Pontos fortes: {', '.join(profile.strengths[:3])}")

        return insights

    def record_milestone(
        self,
        phone: str,
        milestone: str,
        description: str = ""
    ) -> None:
        """
        Registra um marco/conquista.

        Args:
            phone: Telefone da pessoa
            milestone: Nome do marco
            description: Descrição
        """
        if phone in self.profiles:
            profile = self.profiles[phone]
            profile.add_milestone(milestone, description)
            self._save_profiles()
            logger.info(f"Marco registrado para {profile.name}: {milestone}")

    def export_team_report(self) -> Dict:
        """
        Exporta relatório completo da equipe.

        Returns:
            Dicionário com relatório completo
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_team_summary(),
            "people_needing_attention": [
                p.to_dict() for p in self.get_people_needing_attention()
            ],
            "top_performers": [
                p.to_dict() for p in self.get_top_performers()
            ],
            "all_profiles": [
                p.to_dict() for p in self.profiles.values()
            ]
        }
