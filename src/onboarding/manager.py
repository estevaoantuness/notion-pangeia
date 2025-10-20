"""
Gerenciador de onboarding para novos usuários.

Este módulo controla o fluxo de onboarding, perguntando se o usuário
quer tutorial completo ou explicação rápida.

PERSISTÊNCIA: Agora usa Notion para armazenar estado, garantindo que:
- Bot lembra conversas anteriores
- Não repete onboarding após restart
- Rastreia última interação de cada usuário
"""

import logging
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Estado de onboarding em memória (apenas para sessão atual)
# IMPORTANTE: _onboarding_complete não é mais usado! Agora usa Notion
_onboarding_state = {}
_onboarding_complete = set()  # Deprecated - mantido por compatibilidade


class OnboardingManager:
    """
    Gerencia o processo de onboarding de novos usuários.

    Controla o fluxo de tutorial inicial para novos usuários.
    """

    # Sinônimos de SIM (EXPANDIDO - aceita 's', números, emojis)
    YES_SYNONYMS = [
        # Variações de "sim"
        'sim', 's', 'si', 'ss', 'sim!', 'sim.', 'sim,',
        # Confirmações casuais
        'quero', 'ok', 'okay', 'pode', 'pode ser',
        'claro', 'com certeza', 'certeza', 'certo',
        'dale', 'bora', 'vamos', 'manda', 'vai',
        'aceito', 'beleza', 'blz', 'show', 'top',
        # Inglês
        'yes', 'y', 'yep', 'yeah', 'sure',
        # Números (1 = sim)
        '1',
        # Emojis
        '👍', '✅', '✓', '☑️'
    ]

    # Sinônimos de NÃO (EXPANDIDO - aceita 'n', números, emojis)
    NO_SYNONYMS = [
        # Variações de "não"
        'nao', 'não', 'n', 'nn', 'nope',
        'não quero', 'nao quero',
        # Recusas casuais
        'depois', 'agora não', 'agora nao',
        'pular', 'skip', 'talvez depois', 'mais tarde',
        'deixa', 'deixa pra la', 'deixa pra lá',
        # Negações
        'neg', 'negativo', 'nada',
        # Números (2 = não)
        '2',
        # Emojis
        '👎', '❌', '✗', '☒'
    ]

    # Sinônimos para tutorial completo
    FULL_SYNONYMS = [
        'completo', 'detalhado', 'tudo', 'full',
        'tutorial completo', 'explicacao completa'
    ]

    # Sinônimos para tutorial básico
    BASIC_SYNONYMS = [
        'basico', 'básico', 'resumo', 'rapido', 'rápido',
        'quick', 'simples', 'só o básico', 'so o basico'
    ]

    def __init__(self):
        """Inicializa o gerenciador de onboarding com persistência."""
        # Importação lazy para evitar ciclo
        from src.onboarding.persistence import get_persistence
        self.persistence = get_persistence()
        logger.info(f"OnboardingManager inicializado (persistência: {self.persistence.is_enabled()})")

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza texto para comparação (aceita emojis, números, pontuação).

        IMPORTANTE: Preserva emojis e números para matching!
        Remove apenas pontuação comum (. ! ? ,) mas mantém símbolos especiais.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado (lowercase, sem acentos, sem pontuação comum)
        """
        import unicodedata

        # Lowercase
        text = text.lower().strip()

        # Remove acentos (mas preserva outros caracteres unicode como emojis)
        normalized = []
        for c in unicodedata.normalize('NFD', text):
            # Remove apenas combining marks (acentos)
            if unicodedata.category(c) != 'Mn':
                normalized.append(c)
        text = ''.join(normalized)

        # Remove pontuação comum (mas preserva emojis e símbolos especiais)
        # Remove: . ! ? , ; : - " ' ( )
        # Preserva: números, letras, espaços, emojis (✅ ✓ etc)
        import re
        text = re.sub(r'[.!?,;:\-"\'()]', '', text)

        # Remove espaços extras
        text = ' '.join(text.split())

        return text

    def is_first_time_user(self, person_name: str) -> bool:
        """
        Verifica se é primeira interação do usuário.

        IMPORTANTE: Agora usa persistência do Notion!
        - Verifica se usuário já completou onboarding
        - Funciona mesmo após reinicialização do bot
        - Atualiza última interação automaticamente

        Args:
            person_name: Nome do colaborador

        Returns:
            True se for primeira vez, False caso contrário
        """
        # Usa persistência do Notion (se habilitada)
        if self.persistence.is_enabled():
            has_completed = self.persistence.has_completed_onboarding(person_name)
            logger.info(f"[PERSISTÊNCIA] {person_name}: has_completed={has_completed}")
            return not has_completed
        else:
            # Fallback: usa cache em memória (deprecated)
            logger.warning("Persistência desabilitada - usando cache em memória")
            return person_name not in _onboarding_complete

    def is_waiting_onboarding_answer(self, person_name: str) -> bool:
        """
        Verifica se está aguardando resposta sobre tutorial.

        Args:
            person_name: Nome do colaborador

        Returns:
            True se estiver aguardando resposta
        """
        is_waiting = _onboarding_state.get(person_name) == 'waiting_initial_answer'
        logger.info(f"[DEBUG] is_waiting_onboarding_answer({person_name}): {is_waiting}, estado: {_onboarding_state.get(person_name)}")
        return is_waiting

    def is_waiting_help_answer(self, person_name: str) -> bool:
        """
        Verifica se está aguardando resposta do comando ajuda.

        Args:
            person_name: Nome do colaborador

        Returns:
            True se estiver aguardando resposta
        """
        return _onboarding_state.get(person_name) == 'waiting_help_answer'

    def start_onboarding(self, person_name: str) -> str:
        """
        Inicia processo de onboarding com pergunta inicial.

        Args:
            person_name: Nome do colaborador

        Returns:
            Mensagem de boas-vindas com pergunta
        """
        logger.info(f"Iniciando onboarding para {person_name}")

        # Marcar que está aguardando resposta
        _onboarding_state[person_name] = 'waiting_initial_answer'

        logger.info(f"[DEBUG] Estado setado para {person_name}: {_onboarding_state.get(person_name)}")
        logger.info(f"[DEBUG] Estado global: {_onboarding_state}")

        message = f"👋 Olá, {person_name}! Sou o Pangeia Bot.\n\n"
        message += "Gerencio suas tarefas do Notion pelo WhatsApp.\n\n"
        message += "Quer um tutorial rápido? (sim / não)"

        return message

    def handle_onboarding_response(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa resposta do usuário sobre tutorial.

        Args:
            person_name: Nome do colaborador
            message: Mensagem recebida

        Returns:
            Tuple (resposta_processada, mensagem_resposta)
        """
        logger.info(f"Processando resposta de onboarding de {person_name}: '{message}'")

        # Normalizar resposta
        response = self.normalize_text(message)

        # Verificar se é afirmativa
        if any(syn in response for syn in self.YES_SYNONYMS):
            logger.info(f"{person_name} optou pelo tutorial completo")
            self._mark_onboarding_complete(person_name, 'full')
            return True, self._get_full_tutorial()

        # Verificar se é negativa
        elif any(syn in response for syn in self.NO_SYNONYMS):
            logger.info(f"{person_name} optou pela explicação rápida")
            self._mark_onboarding_complete(person_name, 'quick')
            return True, self._get_quick_explanation()

        # Não entendeu - perguntar novamente
        else:
            logger.info(f"Resposta não reconhecida de {person_name}: '{message}'")
            return False, (
                "Não entendi. 🤔\n\n"
                "Você quer um tutorial rápido?\n\n"
                "Responda: *sim* ou *não*"
            )

    def handle_help_response(
        self,
        person_name: str,
        message: str
    ) -> Tuple[bool, str]:
        """
        Processa resposta do comando ajuda (completo/básico).

        Args:
            person_name: Nome do colaborador
            message: Mensagem recebida

        Returns:
            Tuple (resposta_processada, mensagem_resposta)
        """
        logger.info(f"Processando resposta de ajuda de {person_name}: '{message}'")

        # Normalizar resposta
        response = self.normalize_text(message)

        # Verificar se é completo
        if any(syn in response for syn in self.FULL_SYNONYMS):
            logger.info(f"{person_name} solicitou tutorial completo via ajuda")
            self._clear_state(person_name)
            return True, self._get_full_tutorial()

        # Verificar se é básico
        elif any(syn in response for syn in self.BASIC_SYNONYMS):
            logger.info(f"{person_name} solicitou explicação básica via ajuda")
            self._clear_state(person_name)
            return True, self._get_quick_explanation()

        # Não entendeu - perguntar novamente
        else:
            logger.info(f"Resposta de ajuda não reconhecida de {person_name}: '{message}'")
            return False, (
                "Não entendi. 🤔\n\n"
                "Você quer tutorial *completo* ou *básico*?\n\n"
                "Responda: completo ou básico"
            )

    def start_help_flow(self, person_name: str) -> str:
        """
        Inicia fluxo de ajuda com pergunta.

        Args:
            person_name: Nome do colaborador

        Returns:
            Mensagem de ajuda com pergunta
        """
        logger.info(f"Iniciando fluxo de ajuda para {person_name}")

        # Marcar que está aguardando resposta
        _onboarding_state[person_name] = 'waiting_help_answer'

        message = "📖 Posso te ajudar!\n\n"
        message += "Quer um tutorial completo ou só o básico?\n\n"
        message += "Responda:\n"
        message += "• *completo* → tutorial detalhado\n"
        message += "• *básico* → comandos principais"

        return message

    def _mark_onboarding_complete(self, person_name: str, onboarding_type: str):
        """
        Marca onboarding como completo.

        IMPORTANTE: Agora salva no Notion para persistir entre reinicializações!

        Args:
            person_name: Nome do colaborador
            onboarding_type: 'full' ou 'quick'
        """
        # Mapeia tipo interno para nome amigável
        type_map = {
            'full': 'completo',
            'quick': 'básico'
        }
        notion_type = type_map.get(onboarding_type, onboarding_type)

        # Salvar no Notion (se habilitado)
        if self.persistence.is_enabled():
            success = self.persistence.mark_onboarding_complete(
                person_name=person_name,
                onboarding_type=notion_type
            )
            if success:
                logger.info(f"✅ Onboarding salvo no Notion: {person_name} (tipo: {notion_type})")
            else:
                logger.error(f"❌ Erro ao salvar onboarding no Notion para {person_name}")
        else:
            logger.warning(f"Persistência desabilitada - onboarding de {person_name} não será salvo")

        # Atualizar cache em memória (fallback)
        _onboarding_complete.add(person_name)
        _onboarding_state.pop(person_name, None)

        logger.info(f"Onboarding completo para {person_name} (tipo: {onboarding_type})")

    def _clear_state(self, person_name: str):
        """
        Limpa estado de onboarding.

        Args:
            person_name: Nome do colaborador
        """
        _onboarding_state.pop(person_name, None)

    def _get_full_tutorial(self) -> str:
        """
        Retorna tutorial completo.

        Returns:
            Mensagem com tutorial detalhado
        """
        message = "👋 *Pangeia Bot - Tutorial Completo*\n\n"
        message += "Eu gerencio suas tarefas do Notion pelo WhatsApp.\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*🎯 COMO FUNCIONA*\n\n"
        message += "*1️⃣ Digite:* tarefas\n"
        message += "   Você verá sua lista numerada:\n"
        message += "   1️⃣ Reunião com cliente\n"
        message += "   2️⃣ Revisar documento\n"
        message += "   3️⃣ Ligar fornecedor\n\n"
        message += "*2️⃣ Para marcar como feita:*\n"
        message += "   Digite: feito 2\n"
        message += "   (marca a tarefa número 2)\n\n"
        message += "*3️⃣ Para marcar várias:*\n"
        message += "   Digite: feito 1 3 5\n"
        message += "   (marca tarefas 1, 3 e 5 de uma vez)\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*📋 COMANDOS DISPONÍVEIS*\n\n"
        message += "*📌 VER TAREFAS*\n"
        message += "• tarefas → lista resumida\n"
        message += "• ver mais → lista completa\n"
        message += "• progresso → relatório detalhado\n\n"
        message += "*✅ MARCAR COMO CONCLUÍDA*\n"
        message += "• feito 2 → marca tarefa 2\n"
        message += "• feito 1 3 5 → marca múltiplas\n"
        message += "• pronto 2 / concluí 2 → sinônimos\n\n"
        message += "*🔵 MARCAR EM ANDAMENTO*\n"
        message += "• andamento 3 → marca tarefa 3\n"
        message += "• fazendo 2 / comecei 2 → sinônimos\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*⏰ NOTIFICAÇÕES AUTOMÁTICAS*\n\n"
        message += "Você receberá mensagens:\n"
        message += "• 08:00 → Lista de tarefas do dia\n"
        message += "• 13:30, 15:30, 17:00, 21:00 → Check-ins\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*💡 DICAS*\n\n"
        message += "• Os números mudam conforme você conclui tarefas\n"
        message += "• Sempre veja 'tarefas' antes de marcar\n"
        message += "• Tarefas concluídas somem da lista\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "*🚀 Pronto!*\n\n"
        message += "Digite: *tarefas*"

        return message

    def _get_quick_explanation(self) -> str:
        """
        Retorna explicação rápida.

        Returns:
            Mensagem com comandos básicos
        """
        message = "✅ *Sem problemas!*\n\n"
        message += "*Comandos básicos:*\n"
        message += "• tarefas → ver lista\n"
        message += "• feito 2 → marcar tarefa 2\n"
        message += "• progresso → resumo do dia\n\n"
        message += "Quando precisar: *ajuda*\n\n"
        message += "Vamos começar? Digite: *tarefas*"

        return message


# Instância global
_onboarding_manager = None


def get_onboarding_manager() -> OnboardingManager:
    """
    Retorna instância global do OnboardingManager.

    Returns:
        OnboardingManager singleton
    """
    global _onboarding_manager
    if _onboarding_manager is None:
        _onboarding_manager = OnboardingManager()
    return _onboarding_manager
