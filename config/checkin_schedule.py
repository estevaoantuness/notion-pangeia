"""
Configuração dos horários e conteúdo dos check-ins estratégicos.

Este módulo define os 4 check-ins diários e suas respectivas perguntas.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class CheckinConfig:
    """Configuração de um check-in."""
    nome: str
    horario: str
    tipo: str
    descricao: str
    perguntas: List[str]


# Check-in 1: Planejamento Profundo (13:30)
CHECKIN_PLANEJAMENTO = CheckinConfig(
    nome="Planejamento Profundo",
    horario="13:30",
    tipo="planning",
    descricao="Entender intenção e estratégia do dia",
    perguntas=[
        "O que você precisa fazer hoje?",
        "Em quais projetos você está trabalhando?",
        "Quais são as tasks específicas?",
        "Por quê essas tasks são importantes?",
        "Qual é o objetivo final dessa task?",
        "Como você pensa em fazer isso?"
    ]
)

# Check-in 2: Status e Adaptação (15:30)
CHECKIN_STATUS = CheckinConfig(
    nome="Status e Adaptação",
    horario="15:30",
    tipo="status",
    descricao="Monitorar progresso e identificar bloqueios",
    perguntas=[
        "Como está a task que você estava fazendo?",
        "O que você está fazendo agora?",
        "Algo mudou desde o planejamento da manhã?",
        "Surgiu alguma demanda nova?",
        "Quais dúvidas você tem?",
        "O que evoluímos até agora?"
    ]
)

# Check-in 3: Fechamento e Insights (18:00)
CHECKIN_FECHAMENTO = CheckinConfig(
    nome="Fechamento e Insights",
    horario="18:00",
    tipo="closing",
    descricao="Capturar aprendizados do dia",
    perguntas=[
        "O que você está fazendo agora?",
        "Quais foram os insights do dia?",
        "O que você fez hoje? (resumo)",
        "Qual foi o maior desafio de hoje?",
        "Como você resolveu esse desafio?"
    ]
)

# Check-in 4: Reflexão Noturna (22:00)
CHECKIN_REFLEXAO = CheckinConfig(
    nome="Reflexão Noturna",
    horario="22:00",
    tipo="reflection",
    descricao="Auto-avaliação profunda de alta performance",
    perguntas=[
        """HOJE EU MOVI O CONTINENTE — OU SÓ CUMPRI TAREFAS?

"O que fiz hoje criou avanço real, impacto mensurável ou insight novo para o time?"

A diferença entre estar ocupado e estar em movimento é brutal.
Quem constrói um continente digital não marca ponto — cria marcos.""",

        """EU AGI COMO DONO OU COMO PASSAGEIRO?

"Esperei alguém dizer o que fazer ou fui eu quem puxou a próxima ação?"

Ser dono não tem a ver com o contrato social — é mentalidade.
Os donos de verdade antecipam, resolvem e comunicam com clareza.""",

        """EU DEIXEI O AMBIENTE MAIS LEVE, RÁPIDO E INTELIGENTE?

"Minha presença hoje facilitou o trabalho dos outros ou criou ruído?"

Na Pange.iA, velocidade é cultura.
Cada pessoa é um nó da rede: se você simplifica, a rede flui; se complica, a rede trava.""",

        """BÔNUS (versão brutalista):

"Se todos tivessem trabalhado como eu hoje, a companhia teria acelerado ou travado?"
""",

        "O que você espera para amanhã?",
        "Principais aprendizados de hoje?",
        "Insights finais?"
    ]
)


# Mapeamento de todos os check-ins
CHECKINS: Dict[str, CheckinConfig] = {
    "planning": CHECKIN_PLANEJAMENTO,
    "status": CHECKIN_STATUS,
    "closing": CHECKIN_FECHAMENTO,
    "reflection": CHECKIN_REFLEXAO
}


def get_checkin_by_type(checkin_type: str) -> CheckinConfig:
    """
    Retorna configuração de um check-in pelo tipo.

    Args:
        checkin_type: Tipo do check-in (planning, status, closing, reflection)

    Returns:
        CheckinConfig: Configuração do check-in.

    Raises:
        ValueError: Se o tipo não existir.
    """
    if checkin_type not in CHECKINS:
        raise ValueError(f"Tipo de check-in inválido: {checkin_type}")
    return CHECKINS[checkin_type]


def get_checkin_by_time(time: str) -> CheckinConfig:
    """
    Retorna configuração de um check-in pelo horário.

    Args:
        time: Horário no formato HH:MM

    Returns:
        CheckinConfig: Configuração do check-in.

    Raises:
        ValueError: Se não houver check-in nesse horário.
    """
    for checkin in CHECKINS.values():
        if checkin.horario == time:
            return checkin
    raise ValueError(f"Nenhum check-in configurado para o horário: {time}")


def get_all_checkin_times() -> List[str]:
    """
    Retorna lista de todos os horários de check-in.

    Returns:
        List[str]: Lista de horários no formato HH:MM
    """
    return [checkin.horario for checkin in CHECKINS.values()]
