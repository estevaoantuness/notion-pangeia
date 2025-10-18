"""
Perfis de Pessoas - Person Profiles.

Define estrutura de dados para perfis psicológicos e
padrões de comportamento de colaboradores.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class PersonalityTrait(Enum):
    """Traços de personalidade observáveis."""
    MORNING_PERSON = "morning_person"
    NIGHT_OWL = "night_owl"
    PREFERS_SMALL_TASKS = "prefers_small_tasks"
    PREFERS_BIG_CHALLENGES = "prefers_big_challenges"
    NEEDS_ENCOURAGEMENT = "needs_encouragement"
    SELF_MOTIVATED = "self_motivated"
    RESPONDS_TO_CHALLENGES = "responds_to_challenges"
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"


class ProductivityPattern(Enum):
    """Padrões de produtividade."""
    MORNING_PEAK = "morning_peak"  # Pico de manhã
    AFTERNOON_PEAK = "afternoon_peak"  # Pico de tarde
    EVENING_PEAK = "evening_peak"  # Pico de noite
    CONSISTENT = "consistent"  # Consistente o dia todo
    IRREGULAR = "irregular"  # Irregular


class CommunicationStyle(Enum):
    """Estilos de comunicação preferidos."""
    BRIEF = "brief"  # Mensagens curtas
    DETAILED = "detailed"  # Mensagens detalhadas
    EMOJI_RICH = "emoji_rich"  # Usa muitos emojis
    FORMAL = "formal"  # Formal
    CASUAL = "casual"  # Casual


@dataclass
class ProductivityStats:
    """Estatísticas de produtividade."""
    avg_tasks_per_day: float = 0.0
    best_hours: List[str] = field(default_factory=list)
    worst_hours: List[str] = field(default_factory=list)
    peak_day_of_week: Optional[str] = None
    avg_completion_rate: float = 0.0
    avg_response_time_hours: float = 0.0


@dataclass
class EmotionalProfile:
    """Perfil emocional ao longo do tempo."""
    current_state: str = "balanced"
    trend: str = "stable"  # improving, stable, declining
    risk_burnout: bool = False
    last_intervention: Optional[datetime] = None
    positive_ratio: float = 0.5  # Ratio positivo/negativo


@dataclass
class PersonProfile:
    """
    Perfil completo de uma pessoa.

    Agrupa todos os dados psicológicos, padrões e preferências
    de um colaborador.
    """

    # Identificação
    name: str
    phone: str
    role: str = ""

    # Traços de personalidade
    personality_traits: Dict[PersonalityTrait, bool] = field(default_factory=dict)

    # Padrões de produtividade
    productivity_pattern: ProductivityPattern = ProductivityPattern.CONSISTENT
    productivity_stats: ProductivityStats = field(default_factory=ProductivityStats)

    # Perfil emocional
    emotional_profile: EmotionalProfile = field(default_factory=EmotionalProfile)

    # Estilo de comunicação
    communication_style: CommunicationStyle = CommunicationStyle.CASUAL

    # Preferências
    preferences: Dict[str, any] = field(default_factory=dict)

    # Pontos fortes identificados
    strengths: List[str] = field(default_factory=list)

    # Áreas de desenvolvimento
    improvement_areas: List[str] = field(default_factory=list)

    # Histórico de conquistas
    milestones: List[Dict[str, any]] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_strength(self, strength: str) -> None:
        """Adiciona um ponto forte."""
        if strength not in self.strengths:
            self.strengths.append(strength)
            self.updated_at = datetime.now()

    def add_improvement_area(self, area: str) -> None:
        """Adiciona área de desenvolvimento."""
        if area not in self.improvement_areas:
            self.improvement_areas.append(area)
            self.updated_at = datetime.now()

    def add_milestone(self, milestone: str, description: str = "") -> None:
        """Adiciona um marco/conquista."""
        self.milestones.append({
            "title": milestone,
            "description": description,
            "achieved_at": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def set_personality_trait(self, trait: PersonalityTrait, value: bool) -> None:
        """Define um traço de personalidade."""
        self.personality_traits[trait] = value
        self.updated_at = datetime.now()

    def has_trait(self, trait: PersonalityTrait) -> bool:
        """Verifica se pessoa tem um traço."""
        return self.personality_traits.get(trait, False)

    def update_emotional_state(
        self,
        state: str,
        trend: str = "stable",
        risk_burnout: bool = False
    ) -> None:
        """Atualiza estado emocional."""
        self.emotional_profile.current_state = state
        self.emotional_profile.trend = trend
        self.emotional_profile.risk_burnout = risk_burnout
        self.updated_at = datetime.now()

    def record_intervention(self) -> None:
        """Registra que houve uma intervenção."""
        self.emotional_profile.last_intervention = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """Converte perfil para dicionário."""
        return {
            "name": self.name,
            "phone": self.phone,
            "role": self.role,
            "personality_traits": {
                trait.value: value
                for trait, value in self.personality_traits.items()
            },
            "productivity_pattern": self.productivity_pattern.value,
            "productivity_stats": {
                "avg_tasks_per_day": self.productivity_stats.avg_tasks_per_day,
                "best_hours": self.productivity_stats.best_hours,
                "worst_hours": self.productivity_stats.worst_hours,
                "peak_day_of_week": self.productivity_stats.peak_day_of_week,
                "avg_completion_rate": self.productivity_stats.avg_completion_rate,
                "avg_response_time_hours": self.productivity_stats.avg_response_time_hours
            },
            "emotional_profile": {
                "current_state": self.emotional_profile.current_state,
                "trend": self.emotional_profile.trend,
                "risk_burnout": self.emotional_profile.risk_burnout,
                "last_intervention": (
                    self.emotional_profile.last_intervention.isoformat()
                    if self.emotional_profile.last_intervention
                    else None
                ),
                "positive_ratio": self.emotional_profile.positive_ratio
            },
            "communication_style": self.communication_style.value,
            "preferences": self.preferences,
            "strengths": self.strengths,
            "improvement_areas": self.improvement_areas,
            "milestones": self.milestones,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonProfile":
        """Cria perfil a partir de dicionário."""
        profile = cls(
            name=data["name"],
            phone=data["phone"],
            role=data.get("role", "")
        )

        # Restaurar traços de personalidade
        if "personality_traits" in data:
            for trait_str, value in data["personality_traits"].items():
                trait = PersonalityTrait(trait_str)
                profile.personality_traits[trait] = value

        # Restaurar padrão de produtividade
        if "productivity_pattern" in data:
            profile.productivity_pattern = ProductivityPattern(
                data["productivity_pattern"]
            )

        # Restaurar stats de produtividade
        if "productivity_stats" in data:
            stats_data = data["productivity_stats"]
            profile.productivity_stats = ProductivityStats(
                avg_tasks_per_day=stats_data.get("avg_tasks_per_day", 0.0),
                best_hours=stats_data.get("best_hours", []),
                worst_hours=stats_data.get("worst_hours", []),
                peak_day_of_week=stats_data.get("peak_day_of_week"),
                avg_completion_rate=stats_data.get("avg_completion_rate", 0.0),
                avg_response_time_hours=stats_data.get("avg_response_time_hours", 0.0)
            )

        # Restaurar perfil emocional
        if "emotional_profile" in data:
            emot_data = data["emotional_profile"]
            profile.emotional_profile = EmotionalProfile(
                current_state=emot_data.get("current_state", "balanced"),
                trend=emot_data.get("trend", "stable"),
                risk_burnout=emot_data.get("risk_burnout", False),
                last_intervention=(
                    datetime.fromisoformat(emot_data["last_intervention"])
                    if emot_data.get("last_intervention")
                    else None
                ),
                positive_ratio=emot_data.get("positive_ratio", 0.5)
            )

        # Restaurar estilo de comunicação
        if "communication_style" in data:
            profile.communication_style = CommunicationStyle(
                data["communication_style"]
            )

        # Restaurar outras propriedades
        profile.preferences = data.get("preferences", {})
        profile.strengths = data.get("strengths", [])
        profile.improvement_areas = data.get("improvement_areas", [])
        profile.milestones = data.get("milestones", [])

        if "created_at" in data:
            profile.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            profile.updated_at = datetime.fromisoformat(data["updated_at"])

        return profile
