"""
Nudge Engine - Motor de Micro-Interventions Personalizadas.

Sistema de nudges psicológicos que influencia comportamentos de forma
sutil e não invasiva, baseado em behavioral economics e psicologia positiva.
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from src.people.profile import PersonProfile, PersonalityTrait
from src.psychology.engine import PsychologicalMetrics, EmotionalState, EnergyLevel

logger = logging.getLogger(__name__)


class NudgeType(Enum):
    """Tipos de nudges disponíveis."""
    ENCOURAGEMENT = "encouragement"  # Encorajamento
    CHALLENGE = "challenge"  # Desafio
    REMINDER = "reminder"  # Lembrete
    CELEBRATION = "celebration"  # Comemoração
    BREAK_SUGGESTION = "break_suggestion"  # Sugestão de pausa
    FOCUS_PROMPT = "focus_prompt"  # Prompt de foco
    SOCIAL = "social"  # Social (colaboração)
    REFLECTION = "reflection"  # Reflexão
    GRATITUDE = "gratitude"  # Gratidão
    RESET = "reset"  # Reset (após falha)


class NudgeTiming(Enum):
    """Momentos ideais para enviar nudges."""
    MORNING_START = "morning_start"  # Início da manhã (8-9h)
    MID_MORNING = "mid_morning"  # Meio da manhã (10-11h)
    LUNCH_TIME = "lunch_time"  # Almoço (12-13h)
    AFTERNOON_SLUMP = "afternoon_slump"  # Queda da tarde (14-15h)
    END_OF_DAY = "end_of_day"  # Fim do dia (17-18h)
    EVENING = "evening"  # Noite (19-21h)
    WHEN_STRUGGLING = "when_struggling"  # Quando está lutando
    AFTER_WIN = "after_win"  # Após vitória
    ENERGY_DROP = "energy_drop"  # Queda de energia


@dataclass
class Nudge:
    """Representa um nudge individual."""
    message: str
    nudge_type: NudgeType
    timing: NudgeTiming
    personality_match: List[PersonalityTrait]
    emotional_state_match: List[EmotionalState]
    energy_level_match: List[EnergyLevel]
    cooldown_hours: int = 24  # Tempo mínimo entre nudges similares
    priority: int = 1  # 1-5, maior = mais prioritário


class NudgeEngine:
    """
    Motor de nudges psicológicos personalizados.

    Seleciona e envia micro-interventions baseadas em:
    - Perfil da pessoa (traits, padrões)
    - Estado emocional atual
    - Nível de energia
    - Contexto temporal
    - Histórico de nudges
    """

    def __init__(self):
        """Inicializa o motor de nudges."""
        self.nudge_library: Dict[NudgeType, List[Nudge]] = {}
        self.nudge_history: Dict[str, List[Tuple[datetime, NudgeType, str]]] = {}

        self._load_nudge_library()
        logger.info("NudgeEngine inicializado")

    def _load_nudge_library(self) -> None:
        """Carrega biblioteca de nudges pré-definidos."""

        # ENCOURAGEMENT - Encorajamento
        self.nudge_library[NudgeType.ENCOURAGEMENT] = [
            Nudge(
                message="Você consegue! 💪 Já fez coisas muito mais difíceis que isso.",
                nudge_type=NudgeType.ENCOURAGEMENT,
                timing=NudgeTiming.WHEN_STRUGGLING,
                personality_match=[PersonalityTrait.NEEDS_ENCOURAGEMENT],
                emotional_state_match=[EmotionalState.STRESSED, EmotionalState.OVERWHELMED],
                energy_level_match=[EnergyLevel.LOW, EnergyLevel.MEDIUM],
                priority=4
            ),
            Nudge(
                message="Lembre-se: progresso, não perfeição. Cada pequeno passo conta! 🌱",
                nudge_type=NudgeType.ENCOURAGEMENT,
                timing=NudgeTiming.MID_MORNING,
                personality_match=[PersonalityTrait.NEEDS_ENCOURAGEMENT],
                emotional_state_match=[EmotionalState.STRESSED],
                energy_level_match=[EnergyLevel.MEDIUM],
                priority=3
            ),
            Nudge(
                message="Acredite em você! Sua dedicação está fazendo diferença. ✨",
                nudge_type=NudgeType.ENCOURAGEMENT,
                timing=NudgeTiming.AFTERNOON_SLUMP,
                personality_match=[PersonalityTrait.NEEDS_ENCOURAGEMENT],
                emotional_state_match=[EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.MEDIUM],
                priority=2
            ),
        ]

        # CHALLENGE - Desafio
        self.nudge_library[NudgeType.CHALLENGE] = [
            Nudge(
                message="Meta de hoje: 5 tasks concluídas. Seu recorde é 7. Vai tentar quebrar? 👀",
                nudge_type=NudgeType.CHALLENGE,
                timing=NudgeTiming.MORNING_START,
                personality_match=[PersonalityTrait.SELF_MOTIVATED, PersonalityTrait.RESPONDS_TO_CHALLENGES],
                emotional_state_match=[EmotionalState.MOTIVATED, EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.HIGH, EnergyLevel.VERY_HIGH],
                priority=4
            ),
            Nudge(
                message="Você já está indo bem! Mas... será que consegue fazer mais uma? 🎯",
                nudge_type=NudgeType.CHALLENGE,
                timing=NudgeTiming.MID_MORNING,
                personality_match=[PersonalityTrait.RESPONDS_TO_CHALLENGES],
                emotional_state_match=[EmotionalState.MOTIVATED],
                energy_level_match=[EnergyLevel.HIGH],
                priority=3
            ),
        ]

        # BREAK_SUGGESTION - Sugestão de pausa
        self.nudge_library[NudgeType.BREAK_SUGGESTION] = [
            Nudge(
                message="Você tá firme há 3 horas! ⏰ Que tal 10 minutos de pausa? Seu cérebro agradece! ☕",
                nudge_type=NudgeType.BREAK_SUGGESTION,
                timing=NudgeTiming.WHEN_STRUGGLING,
                personality_match=[],  # Aplica a todos
                emotional_state_match=[EmotionalState.STRESSED, EmotionalState.OVERWHELMED],
                energy_level_match=[EnergyLevel.LOW, EnergyLevel.VERY_LOW],
                priority=5
            ),
            Nudge(
                message="Respira fundo por 2 minutos. Sério, funciona! 🧘‍♀️",
                nudge_type=NudgeType.BREAK_SUGGESTION,
                timing=NudgeTiming.AFTERNOON_SLUMP,
                personality_match=[],
                emotional_state_match=[EmotionalState.STRESSED],
                energy_level_match=[EnergyLevel.LOW],
                priority=4
            ),
        ]

        # CELEBRATION - Comemoração
        self.nudge_library[NudgeType.CELEBRATION] = [
            Nudge(
                message="BOAAA! 🎉 Mais uma concluída! Você tá voando hoje!",
                nudge_type=NudgeType.CELEBRATION,
                timing=NudgeTiming.AFTER_WIN,
                personality_match=[],
                emotional_state_match=[EmotionalState.MOTIVATED, EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.HIGH, EnergyLevel.VERY_HIGH],
                priority=3
            ),
            Nudge(
                message="🏆 Arrasou! Olha só o que você já fez hoje. Continue assim!",
                nudge_type=NudgeType.CELEBRATION,
                timing=NudgeTiming.AFTER_WIN,
                personality_match=[PersonalityTrait.NEEDS_ENCOURAGEMENT],
                emotional_state_match=[EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.MEDIUM, EnergyLevel.HIGH],
                priority=4
            ),
        ]

        # SOCIAL - Colaboração
        self.nudge_library[NudgeType.SOCIAL] = [
            Nudge(
                message="3 pessoas do time precisam de ajuda. Quer dar uma força? 🤝",
                nudge_type=NudgeType.SOCIAL,
                timing=NudgeTiming.MID_MORNING,
                personality_match=[PersonalityTrait.COLLABORATIVE],
                emotional_state_match=[EmotionalState.MOTIVATED, EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.HIGH, EnergyLevel.MEDIUM],
                priority=3
            ),
            Nudge(
                message="Você tem expertise nisso! Que tal compartilhar com o time? 💡",
                nudge_type=NudgeType.SOCIAL,
                timing=NudgeTiming.AFTERNOON_SLUMP,
                personality_match=[PersonalityTrait.COLLABORATIVE],
                emotional_state_match=[EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.MEDIUM],
                priority=2
            ),
        ]

        # FOCUS_PROMPT - Prompt de foco
        self.nudge_library[NudgeType.FOCUS_PROMPT] = [
            Nudge(
                message="Uma task de cada vez. Qual é a MAIS importante agora? 🎯",
                nudge_type=NudgeType.FOCUS_PROMPT,
                timing=NudgeTiming.WHEN_STRUGGLING,
                personality_match=[],
                emotional_state_match=[EmotionalState.OVERWHELMED, EmotionalState.STRESSED],
                energy_level_match=[EnergyLevel.LOW, EnergyLevel.MEDIUM],
                priority=5
            ),
            Nudge(
                message="Deep work mode: 25 minutos focado, sem distrações. Topa? ⏱️",
                nudge_type=NudgeType.FOCUS_PROMPT,
                timing=NudgeTiming.MORNING_START,
                personality_match=[PersonalityTrait.SELF_MOTIVATED],
                emotional_state_match=[EmotionalState.BALANCED],
                energy_level_match=[EnergyLevel.HIGH],
                priority=3
            ),
        ]

        # REFLECTION - Reflexão
        self.nudge_library[NudgeType.REFLECTION] = [
            Nudge(
                message="O que você aprendeu hoje? 🤔 Pequenas reflexões fazem grande diferença.",
                nudge_type=NudgeType.REFLECTION,
                timing=NudgeTiming.END_OF_DAY,
                personality_match=[],
                emotional_state_match=[EmotionalState.BALANCED, EmotionalState.MOTIVATED],
                energy_level_match=[EnergyLevel.MEDIUM],
                priority=2
            ),
        ]

        # GRATITUDE - Gratidão
        self.nudge_library[NudgeType.GRATITUDE] = [
            Nudge(
                message="Pelo que você é grato hoje? 💙 Lembrar coisas boas muda tudo.",
                nudge_type=NudgeType.GRATITUDE,
                timing=NudgeTiming.EVENING,
                personality_match=[],
                emotional_state_match=[EmotionalState.STRESSED, EmotionalState.OVERWHELMED],
                energy_level_match=[EnergyLevel.LOW],
                priority=3
            ),
        ]

        # RESET - Reset após falha
        self.nudge_library[NudgeType.RESET] = [
            Nudge(
                message="Tudo bem ter dias difíceis. Amanhã é um novo começo! 🌅",
                nudge_type=NudgeType.RESET,
                timing=NudgeTiming.EVENING,
                personality_match=[PersonalityTrait.NEEDS_ENCOURAGEMENT],
                emotional_state_match=[EmotionalState.OVERWHELMED, EmotionalState.STRESSED],
                energy_level_match=[EnergyLevel.VERY_LOW, EnergyLevel.LOW],
                priority=5
            ),
        ]

        logger.info(f"Biblioteca de nudges carregada: {sum(len(v) for v in self.nudge_library.values())} nudges")

    def select_best_nudge(
        self,
        person_name: str,
        profile: PersonProfile,
        metrics: PsychologicalMetrics,
        context: Optional[Dict] = None
    ) -> Optional[Nudge]:
        """
        Seleciona o melhor nudge para a pessoa no momento atual.

        Args:
            person_name: Nome da pessoa
            profile: Perfil da pessoa
            metrics: Métricas psicológicas atuais
            context: Contexto adicional (opcional)

        Returns:
            Nudge selecionado ou None se nenhum adequado
        """
        context = context or {}

        # Determinar timing atual
        current_timing = self._determine_current_timing(metrics, context)

        # Candidatos de nudges
        candidates: List[Tuple[Nudge, float]] = []

        for nudge_type, nudges in self.nudge_library.items():
            for nudge in nudges:
                # Verificar cooldown
                if self._is_in_cooldown(person_name, nudge):
                    continue

                # Calcular score de match
                score = self._calculate_match_score(
                    nudge, profile, metrics, current_timing
                )

                if score > 0:
                    candidates.append((nudge, score))

        if not candidates:
            logger.debug(f"Nenhum nudge adequado para {person_name} no momento")
            return None

        # Ordenar por score (maior primeiro)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Selecionar top 3 e randomizar (evitar previsibilidade)
        top_candidates = candidates[:3]
        selected_nudge, score = random.choice(top_candidates)

        # Registrar no histórico
        self._record_nudge(person_name, selected_nudge)

        logger.info(
            f"Nudge selecionado para {person_name}: {selected_nudge.nudge_type.value} "
            f"(score: {score:.2f})"
        )

        return selected_nudge

    def _determine_current_timing(
        self,
        metrics: PsychologicalMetrics,
        context: Dict
    ) -> NudgeTiming:
        """Determina o timing atual baseado em hora do dia e contexto."""
        hour = datetime.now().hour

        # Timing baseado em contexto emocional
        if metrics.emotional_state in [EmotionalState.OVERWHELMED, EmotionalState.STRESSED]:
            return NudgeTiming.WHEN_STRUGGLING

        if context.get("just_completed_task"):
            return NudgeTiming.AFTER_WIN

        if metrics.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            return NudgeTiming.ENERGY_DROP

        # Timing baseado em hora do dia
        if 8 <= hour < 9:
            return NudgeTiming.MORNING_START
        elif 10 <= hour < 11:
            return NudgeTiming.MID_MORNING
        elif 12 <= hour < 13:
            return NudgeTiming.LUNCH_TIME
        elif 14 <= hour < 16:
            return NudgeTiming.AFTERNOON_SLUMP
        elif 17 <= hour < 19:
            return NudgeTiming.END_OF_DAY
        elif 19 <= hour < 22:
            return NudgeTiming.EVENING
        else:
            return NudgeTiming.MORNING_START  # Default

    def _calculate_match_score(
        self,
        nudge: Nudge,
        profile: PersonProfile,
        metrics: PsychologicalMetrics,
        current_timing: NudgeTiming
    ) -> float:
        """
        Calcula score de match entre nudge e pessoa (0-100).

        Fatores:
        - Personality match (30 pontos)
        - Emotional state match (30 pontos)
        - Energy level match (20 pontos)
        - Timing match (10 pontos)
        - Priority (10 pontos)
        """
        score = 0.0

        # Personality match (30 pontos)
        if nudge.personality_match:
            matching_traits = sum(
                1 for trait in nudge.personality_match
                if profile.has_trait(trait)
            )
            score += (matching_traits / len(nudge.personality_match)) * 30
        else:
            # Nudge universal (aplica a todos)
            score += 30

        # Emotional state match (30 pontos)
        if nudge.emotional_state_match:
            if metrics.emotional_state in nudge.emotional_state_match:
                score += 30
        else:
            score += 15  # Meio score se não especificado

        # Energy level match (20 pontos)
        if nudge.energy_level_match:
            if metrics.energy_level in nudge.energy_level_match:
                score += 20
        else:
            score += 10  # Meio score se não especificado

        # Timing match (10 pontos)
        if nudge.timing == current_timing:
            score += 10

        # Priority boost (10 pontos max)
        score += nudge.priority * 2

        return score

    def _is_in_cooldown(self, person_name: str, nudge: Nudge) -> bool:
        """Verifica se nudge está em cooldown."""
        if person_name not in self.nudge_history:
            return False

        history = self.nudge_history[person_name]
        cooldown_time = datetime.now() - timedelta(hours=nudge.cooldown_hours)

        # Verificar se mesmo tipo foi enviado recentemente
        for timestamp, nudge_type, _ in history:
            if timestamp > cooldown_time and nudge_type == nudge.nudge_type:
                return True

        return False

    def _record_nudge(self, person_name: str, nudge: Nudge) -> None:
        """Registra nudge no histórico."""
        if person_name not in self.nudge_history:
            self.nudge_history[person_name] = []

        self.nudge_history[person_name].append(
            (datetime.now(), nudge.nudge_type, nudge.message)
        )

        # Limitar histórico a últimos 50 nudges
        if len(self.nudge_history[person_name]) > 50:
            self.nudge_history[person_name] = self.nudge_history[person_name][-50:]

    def get_nudge_history(
        self,
        person_name: str,
        days: int = 7
    ) -> List[Tuple[datetime, NudgeType, str]]:
        """
        Retorna histórico de nudges enviados.

        Args:
            person_name: Nome da pessoa
            days: Número de dias para olhar para trás

        Returns:
            Lista de (timestamp, tipo, mensagem)
        """
        if person_name not in self.nudge_history:
            return []

        cutoff = datetime.now() - timedelta(days=days)

        return [
            (ts, nt, msg)
            for ts, nt, msg in self.nudge_history[person_name]
            if ts > cutoff
        ]

    def get_nudge_stats(self, person_name: str) -> Dict:
        """
        Retorna estatísticas de nudges para uma pessoa.

        Returns:
            Dict com estatísticas
        """
        history = self.get_nudge_history(person_name, days=30)

        if not history:
            return {"total": 0}

        type_counts = {}
        for _, nudge_type, _ in history:
            type_counts[nudge_type.value] = type_counts.get(nudge_type.value, 0) + 1

        return {
            "total": len(history),
            "last_30_days": len(history),
            "by_type": type_counts,
            "most_common": max(type_counts, key=type_counts.get) if type_counts else None
        }
