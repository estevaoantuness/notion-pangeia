"""
Comunicador Empático - Empathetic Communicator.

Este módulo gera mensagens calibradas psicologicamente usando:
- Entrevista Motivacional (OARS): Open questions, Affirming, Reflections, Summaries
- Comunicação Não-Violenta (OFNR): Observation, Feeling, Need, Request
- Reforço Positivo

"""

import logging
import random
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from .engine import PsychologicalMetrics, EmotionalState, EnergyLevel

logger = logging.getLogger(__name__)


class EmpatheticCommunicator:
    """
    Gera mensagens empáticas baseadas no estado psicológico da pessoa.
    """

    def __init__(self, responses_file: Optional[str] = None):
        """
        Inicializa o comunicador empático.

        Args:
            responses_file: Caminho para arquivo YAML de respostas
        """
        if responses_file is None:
            responses_file = Path(__file__).parent.parent.parent / "config" / "psychology" / "psychological_responses.yaml"

        self.responses = self._load_responses(responses_file)
        logger.info("Empathetic Communicator inicializado")

    def _load_responses(self, file_path: Path) -> Dict:
        """Carrega respostas do arquivo YAML."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar respostas: {e}")
            return {}

    def generate_task_completion_message(
        self,
        name: str,
        task_name: str,
        metrics: PsychologicalMetrics,
        is_first_today: bool = False,
        is_last_today: bool = False
    ) -> str:
        """
        Gera mensagem de celebração de tarefa concluída.

        Args:
            name: Nome da pessoa
            task_name: Nome da tarefa
            metrics: Métricas psicológicas
            is_first_today: Se é a primeira do dia
            is_last_today: Se é a última do dia

        Returns:
            Mensagem personalizada
        """
        messages = []

        # Mensagem principal de conclusão
        template = random.choice(
            self.responses.get("encouragement", {}).get("task_completed", [])
        )
        messages.append(template.format(name=name, task_name=task_name))

        # Se for primeira do dia
        if is_first_today:
            first_msg = random.choice(
                self.responses.get("encouragement", {}).get("first_task_of_day", [])
            )
            messages.append(first_msg.format(name=name))

        # Se for última do dia (todas concluídas)
        if is_last_today:
            last_msg = random.choice(
                self.responses.get("encouragement", {}).get("last_task_completed", [])
            )
            messages.append(last_msg.format(name=name))

        # Se tiver sequência (streak)
        if metrics.streak_days > 3:
            streak_msg = random.choice(
                self.responses.get("encouragement", {}).get("streak_recognition", [])
            )
            messages.append(streak_msg.format(name=name, days=metrics.streak_days))

        return "\n\n".join(messages)

    def generate_task_blocked_message(
        self,
        name: str,
        task_name: str,
        metrics: PsychologicalMetrics
    ) -> str:
        """
        Gera mensagem empática quando tarefa é bloqueada.

        Args:
            name: Nome da pessoa
            task_name: Nome da tarefa bloqueada
            metrics: Métricas psicológicas

        Returns:
            Mensagem empática
        """
        # Escolher tom baseado no estado emocional
        if metrics.emotional_state in [EmotionalState.STRESSED, EmotionalState.OVERWHELMED]:
            # Tom mais suave e suportivo
            template = random.choice(
                self.responses.get("empathy", {}).get("task_blocked", [])[-2:]  # Últimas 2 (mais suaves)
            )
        else:
            template = random.choice(
                self.responses.get("empathy", {}).get("task_blocked", [])
            )

        return template.format(name=name, task=task_name)

    def generate_check_in_message(
        self,
        name: str,
        period: str,  # "morning", "afternoon", "evening"
        metrics: PsychologicalMetrics,
        tasks: Optional[List[str]] = None
    ) -> str:
        """
        Gera mensagem de check-in personalizada.

        Args:
            name: Nome da pessoa
            period: Período do dia
            metrics: Métricas psicológicas
            tasks: Lista de tarefas (opcional)

        Returns:
            Mensagem de check-in
        """
        messages = []

        # Saudação apropriada ao período
        greeting = random.choice(
            self.responses.get("check_in", {}).get(period, {}).get("greeting", [])
        )
        messages.append(greeting.format(name=name))

        # Verificação de energia (manhã)
        if period == "morning":
            energy_check = random.choice(
                self.responses.get("check_in", {}).get("morning", {}).get("energy_check", [])
            )
            messages.append(energy_check)

            # Introduzir tarefas
            if tasks:
                task_intro = random.choice(
                    self.responses.get("check_in", {}).get("morning", {}).get("task_intro", [])
                )
                messages.append(task_intro)

                # Listar tarefas
                messages.append(self._format_task_list(tasks))

                # Dar autonomia na escolha
                autonomy_msg = random.choice(
                    self.responses.get("autonomy", {}).get("task_order", [])
                )
                messages.append(autonomy_msg.format(name=name, n=len(tasks)))

        # Check de progresso (tarde)
        elif period == "afternoon":
            progress_msg = random.choice(
                self.responses.get("check_in", {}).get("afternoon", {}).get("progress_check", [])
            )
            messages.append(progress_msg)

            # Reconhecer progresso se houver
            if metrics.tasks_completed_today > 0:
                messages.append(
                    f"\n📊 Progresso: {metrics.tasks_completed_today} tarefas concluídas!"
                )

            # Oferecer suporte
            support = random.choice(
                self.responses.get("check_in", {}).get("afternoon", {}).get("support_offer", [])
            )
            messages.append(support)

        # Reflexão (noite)
        elif period == "evening":
            reflection_intro = random.choice(
                self.responses.get("check_in", {}).get("evening", {}).get("reflection_intro", [])
            )
            messages.append(reflection_intro)

            # Perguntas de reflexão
            messages.append("")
            victory_q = random.choice(
                self.responses.get("reflection", {}).get("victory_question", [])
            )
            messages.append(f"1. {victory_q.format(name=name)}")

            learning_q = random.choice(
                self.responses.get("reflection", {}).get("learning_question", [])
            )
            messages.append(f"2. {learning_q}")

            tomorrow_q = random.choice(
                self.responses.get("reflection", {}).get("tomorrow_question", [])
            )
            messages.append(f"3. {tomorrow_q}")

            messages.append("")
            messages.append("Não precisa ser perfeito, só honesto 💙")

        return "\n\n".join(messages)

    def generate_intervention_message(
        self,
        name: str,
        metrics: PsychologicalMetrics,
        intervention_type: str = "burnout"
    ) -> str:
        """
        Gera mensagem de intervenção quando detecta problemas.

        Args:
            name: Nome da pessoa
            metrics: Métricas psicológicas
            intervention_type: Tipo de intervenção (burnout, overload, etc)

        Returns:
            Mensagem de intervenção
        """
        messages = []

        if intervention_type == "burnout":
            warning = random.choice(
                self.responses.get("intervention", {}).get("burnout_warning", [])
            )
            messages.append(warning.format(name=name))

        elif intervention_type == "overload":
            overload_msg = random.choice(
                self.responses.get("empathy", {}).get("overload_detected", [])
            )
            messages.append(overload_msg.format(name=name))

        # Oferecer ajuda específica
        messages.append("\nPosso ajudar você a:")

        if metrics.tasks_pending > 8:
            messages.append("1. Priorizar só as 3 tarefas mais importantes")

        if metrics.tasks_blocked > 2:
            messages.append("2. Desbloquear algumas tarefas")

        messages.append("3. Reorganizar sua semana")
        messages.append("4. Redistribuir algumas tarefas")

        # Mensagem de suporte
        help_msg = random.choice(
            self.responses.get("intervention", {}).get("help_offer", [])
        )
        messages.append(f"\n{help_msg.format(name=name)}")

        return "\n".join(messages)

    def generate_positive_reinforcement(
        self,
        name: str,
        metrics: PsychologicalMetrics,
        achievement_type: str = "consistency"
    ) -> str:
        """
        Gera reforço positivo baseado em conquistas.

        Args:
            name: Nome da pessoa
            metrics: Métricas psicológicas
            achievement_type: Tipo de conquista (consistency, quality, etc)

        Returns:
            Mensagem de reforço positivo
        """
        template = random.choice(
            self.responses.get("positive_reinforcement", {}).get(achievement_type, [])
        )

        message = template.format(name=name)

        # Adicionar dados específicos
        if achievement_type == "consistency" and metrics.streak_days > 0:
            message += f"\n\nVocê está em uma sequência de {metrics.streak_days} dias!"

        if metrics.completion_rate > 0.8:
            message += f"\n\nSua taxa de conclusão é de {metrics.completion_rate * 100:.0f}%!"

        return message

    def generate_autonomy_message(
        self,
        name: str,
        context: str = "task_order"
    ) -> str:
        """
        Gera mensagem que promove autonomia.

        Args:
            name: Nome da pessoa
            context: Contexto (task_order, timing, approach, etc)

        Returns:
            Mensagem que dá escolha
        """
        template = random.choice(
            self.responses.get("autonomy", {}).get(context, [])
        )

        return template.format(name=name)

    def generate_competence_recognition(
        self,
        name: str,
        skill: str,
        metrics: PsychologicalMetrics
    ) -> str:
        """
        Gera reconhecimento de competência.

        Args:
            name: Nome da pessoa
            skill: Habilidade a reconhecer
            metrics: Métricas psicológicas

        Returns:
            Mensagem de reconhecimento
        """
        template = random.choice(
            self.responses.get("competence", {}).get("skill_recognition", [])
        )

        return template.format(name=name, skill=skill)

    def generate_team_impact_message(
        self,
        name: str,
        task_name: str
    ) -> str:
        """
        Gera mensagem destacando impacto no time (relacionamento).

        Args:
            name: Nome da pessoa
            task_name: Nome da tarefa

        Returns:
            Mensagem de impacto no time
        """
        template = random.choice(
            self.responses.get("relatedness", {}).get("team_impact", [])
        )

        return template.format(name=name, task=task_name)

    def adapt_tone_to_energy(
        self,
        message: str,
        energy_level: EnergyLevel
    ) -> str:
        """
        Adapta o tom da mensagem ao nível de energia.

        Args:
            message: Mensagem original
            energy_level: Nível de energia detectado

        Returns:
            Mensagem com tom adaptado
        """
        # Se energia está baixa, remover emojis muito animados
        if energy_level in [EnergyLevel.LOW, EnergyLevel.VERY_LOW]:
            message = message.replace("🎉", "✅")
            message = message.replace("🚀", "💪")
            message = message.replace("⚡", "👍")

        # Se energia está alta, pode adicionar mais entusiasmo
        elif energy_level == EnergyLevel.VERY_HIGH:
            # Adicionar um emoji extra de vez em quando
            if random.random() < 0.3:
                message += " 🌟"

        return message

    def _format_task_list(self, tasks: List[str]) -> str:
        """
        Formata lista de tarefas de forma legível.

        Args:
            tasks: Lista de tarefas

        Returns:
            String formatada
        """
        formatted_tasks = []
        for i, task in enumerate(tasks, 1):
            formatted_tasks.append(f"{i}. {task}")

        return "\n".join(formatted_tasks)

    def generate_oars_question(
        self,
        name: str,
        context: str,
        metrics: PsychologicalMetrics
    ) -> str:
        """
        Gera pergunta aberta (Open-ended) seguindo OARS.

        Args:
            name: Nome da pessoa
            context: Contexto da pergunta
            metrics: Métricas psicológicas

        Returns:
            Pergunta aberta
        """
        questions = {
            "feeling": [
                f"{name}, como você está se sentindo com suas tarefas hoje?",
                f"Como você se sente em relação ao seu dia, {name}?",
                f"{name}, o que está passando pela sua cabeça agora?"
            ],
            "challenge": [
                f"{name}, qual é o maior desafio que você está enfrentando?",
                f"O que está sendo mais difícil pra você agora, {name}?",
                f"{name}, que obstáculo você gostaria de superar?"
            ],
            "goal": [
                f"{name}, o que você gostaria de alcançar hoje?",
                f"Qual é sua prioridade número 1 agora, {name}?",
                f"{name}, como você quer que seu dia termine?"
            ],
            "support": [
                f"{name}, como eu posso te ajudar hoje?",
                f"Do que você precisa de mim agora, {name}?",
                f"{name}, o que faria sua vida mais fácil hoje?"
            ]
        }

        return random.choice(questions.get(context, questions["feeling"]))

    def generate_reflection_message(
        self,
        name: str,
        observation: str,
        metrics: PsychologicalMetrics
    ) -> str:
        """
        Gera reflexão (Reflection) seguindo OARS.

        Args:
            name: Nome da pessoa
            observation: O que foi observado
            metrics: Métricas psicológicas

        Returns:
            Mensagem de reflexão
        """
        reflections = [
            f"{name}, parece que {observation}.",
            f"Percebi que {observation}, {name}.",
            f"{name}, notei que {observation}."
        ]

        base = random.choice(reflections)

        # Adicionar validação/empatia
        validations = [
            " É normal se sentir assim.",
            " Isso acontece com todo mundo.",
            " Você não está sozinho(a) nisso.",
            ""
        ]

        return base + random.choice(validations)

    def generate_summary_message(
        self,
        name: str,
        achievements: List[str],
        metrics: PsychologicalMetrics
    ) -> str:
        """
        Gera resumo (Summary) seguindo OARS.

        Args:
            name: Nome da pessoa
            achievements: Lista de conquistas
            metrics: Métricas psicológicas

        Returns:
            Mensagem de resumo
        """
        intro = f"Então, {name}, deixa eu recapitular:\n\n"

        summary_items = []
        for achievement in achievements:
            summary_items.append(f"✅ {achievement}")

        summary = "\n".join(summary_items)

        # Afirmação final
        affirmations = [
            "\n\nIsso é muito bom! Continue assim!",
            "\n\nVocê está indo muito bem!",
            "\n\nEstou impressionado(a) com seu progresso!",
            "\n\nEsse é o caminho! Parabéns!"
        ]

        return intro + summary + random.choice(affirmations)
