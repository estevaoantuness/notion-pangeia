"""
Message Fragmenter - Fragmentador de Mensagens Humanas.

Transforma recomendações técnicas em conversas naturais de WhatsApp.
Envia 2-5 mensagens fracionadas, como se fosse uma pessoa real falando.
"""

import logging
from typing import List, Dict
from enum import Enum
import random

from .collaboration_recommender import Recommendation, RecommendationPriority

logger = logging.getLogger(__name__)


class MessageFragmenter:
    """
    Fragmentador de mensagens.

    Transforma recomendações em conversas naturais
    divididas em 2-5 mensagens.
    """

    def __init__(self):
        """Inicializa fragmentador."""
        logger.info("MessageFragmenter inicializado")

    def fragment_recommendation(self, recommendation: Recommendation) -> List[str]:
        """
        Fragmenta recomendação em 2-5 mensagens naturais.

        Args:
            recommendation: Recomendação a fragmentar

        Returns:
            Lista de 2-5 mensagens prontas para envio
        """
        action_type = recommendation.action_type
        priority = recommendation.priority

        # Delega para método específico
        if action_type == "unblock":
            return self._fragment_unblock(recommendation)
        elif action_type == "wait_or_help":
            return self._fragment_wait(recommendation)
        elif action_type == "unblocked":
            return self._fragment_unblocked(recommendation)
        elif action_type == "pair":
            return self._fragment_pair(recommendation)
        elif action_type == "coordinate":
            return self._fragment_coordinate(recommendation)
        else:
            # Fallback genérico
            return self._fragment_generic(recommendation)

    def _fragment_unblock(self, rec: Recommendation) -> List[str]:
        """Fragmenta mensagem de bloqueio crítico."""
        bloqueado = rec.involves[0] if rec.involves else "alguém"

        # Variações de abertura
        openers = [
            f"Oi {rec.target_person}! Descobri uma coisa importante...",
            f"Ei {rec.target_person}, preciso te avisar de algo",
            f"{rec.target_person}, achei um bloqueio aqui",
            f"Opa {rec.target_person}! Olha só isso",
        ]

        messages = []

        # Msg 1: Abertura casual
        messages.append(random.choice(openers))

        # Msg 2: O problema
        messages.append(f"A {bloqueado} tá parada esperando você terminar uma task")

        # Msg 3: Detalhe específico (extrai do reason)
        # Parse do reason para pegar a task
        connection = rec.connection
        # Pega título da task bloqueadora do evidence
        task_blocker = "a task"  # default
        if "'" in connection.reason:
            # Extrai entre aspas
            parts = connection.reason.split("'")
            if len(parts) >= 2:
                task_blocker = parts[1][:60]  # Limita tamanho

        if "agente" in task_blocker.lower():
            messages.append(f"É o Agente OXY... ela precisa disso pra fazer a parte dela")
        elif "ux" in task_blocker.lower() or "interface" in task_blocker.lower():
            messages.append(f"É a interface/UX... precisa disso pra continuar")
        else:
            messages.append(f"É sobre: {task_blocker}")

        # Msg 4: Urgência + empatia
        urgency_msgs = [
            "Dá pra priorizar? Ela tá bloqueada 😬",
            "Consegue dar uma olhada nisso? Tá travando o trampo dela",
            "Será que rola focar nisso? O time tá esperando",
            "Bora resolver isso? Tá segurando outras coisas",
        ]
        messages.append(random.choice(urgency_msgs))

        # Msg 5 (opcional): Oferecer ajuda
        if len(messages) < 5 and random.random() > 0.5:
            help_msgs = [
                "Se precisar de ajuda, me avisa que eu conecto vocês 🤝",
                "Precisa de alguém pra ajudar? Posso sugerir alguém",
                "Quer fazer pair com alguém nisso? Acelera!",
            ]
            messages.append(random.choice(help_msgs))

        return messages

    def _fragment_wait(self, rec: Recommendation) -> List[str]:
        """Fragmenta mensagem para quem tá bloqueado."""
        bloqueador = rec.involves[0] if rec.involves else "alguém"

        messages = []

        # Msg 1: Aviso empático
        messages.append(f"Oi {rec.target_person}, vi aqui que você tá bloqueado numa task")

        # Msg 2: Explicação
        messages.append(f"Tá esperando o {bloqueador} terminar algo, né?")

        # Msg 3: Tranquiliza
        messages.append("Já avisei ele que é importante! 🚨")

        # Msg 4: Sugestão
        suggestions = [
            "Enquanto isso, tem outras tasks que você pode adiantar?",
            "Ou, se quiser, pode ajudar ele a terminar mais rápido",
            "Dá uma olhada nas suas outras tasks, ou descansa um pouco 😊",
        ]
        messages.append(random.choice(suggestions))

        return messages

    def _fragment_unblocked(self, rec: Recommendation) -> List[str]:
        """Fragmenta mensagem de desbloqueio."""
        messages = []

        # Msg 1: Boa notícia!
        messages.append(f"Opa {rec.target_person}! Boas notícias 🎉")

        # Msg 2: O que mudou
        liberador = rec.involves[0] if rec.involves else "alguém"
        messages.append(f"O {liberador} terminou a task que tava te bloqueando")

        # Msg 3: Motivação
        messages.append("Agora você pode continuar! Bora lá 🚀")

        return messages

    def _fragment_pair(self, rec: Recommendation) -> List[str]:
        """Fragmenta sugestão de pair programming."""
        parceiro = rec.involves[0] if rec.involves else "alguém"

        messages = []

        # Msg 1: Abertura casual
        openers = [
            f"Ei {rec.target_person}, tive uma ideia aqui",
            f"{rec.target_person}, olha isso que eu percebi",
            f"Opa! Achei uma parada interessante, {rec.target_person}",
        ]
        messages.append(random.choice(openers))

        # Msg 2: A descoberta
        messages.append(f"Você e o {parceiro} estão trabalhando em tasks super relacionadas")

        # Msg 3: Sugestão
        pair_suggestions = [
            "Que tal fazer um pair? Acelera pra caramba",
            "Já pensou em fazer junto? Sai mais rápido e melhor",
            "Bora juntar forças nisso? Fica muito mais fácil",
        ]
        messages.append(random.choice(pair_suggestions))

        # Msg 4: Benefícios (casual)
        messages.append("Além de ser mais rápido, evita retrabalho depois 😉")

        # Msg 5 (opcional): Oferece conectar
        if random.random() > 0.3:
            messages.append("Quer que eu mande mensagem pra ele também?")

        return messages

    def _fragment_coordinate(self, rec: Recommendation) -> List[str]:
        """Fragmenta sugestão de coordenação."""
        parceiro = rec.involves[0] if rec.involves else "alguém"

        # Extrai projeto do reason
        projeto = "esse projeto"
        if "projeto '" in rec.connection.reason.lower():
            parts = rec.connection.reason.split("'")
            if len(parts) >= 2:
                projeto = parts[1]

        messages = []

        # Msg 1: Observação
        messages.append(f"Oi {rec.target_person}, vi que você e o {parceiro} tão no {projeto}")

        # Msg 2: Sugestão leve
        coord_suggestions = [
            "Vale alinhar pra ver se não tem trabalho duplicado, né?",
            "Bora dar uma alinhada pra dividir melhor as tasks?",
            "Seria legal coordenar pra não pisar no pé um do outro",
        ]
        messages.append(random.choice(coord_suggestions))

        # Msg 3 (opcional): Benefício
        if random.random() > 0.5:
            benefits = [
                "Ajuda a manter todo mundo na mesma página 📄",
                "Fica mais organizado e ninguém faz coisa repetida",
                "E ainda dá pra combinar os deadlines certinho",
            ]
            messages.append(random.choice(benefits))

        return messages

    def _fragment_generic(self, rec: Recommendation) -> List[str]:
        """Fragmenta mensagem genérica."""
        messages = []

        # Msg 1: Abertura
        messages.append(f"Oi {rec.target_person}!")

        # Msg 2: A mensagem principal (simplificada)
        # Pega primeiras 100 chars da mensagem original
        main_msg = rec.message.split('\n\n')[0][:100]
        messages.append(main_msg)

        # Msg 3: Ação sugerida
        if rec.involves:
            messages.append(f"Envolve: {', '.join(rec.involves)}")

        return messages

    def add_delays_between_messages(self, messages: List[str]) -> List[Dict]:
        """
        Adiciona delays naturais entre mensagens.

        Args:
            messages: Lista de mensagens

        Returns:
            Lista de dict com {text, delay_seconds}
        """
        result = []

        for i, msg in enumerate(messages):
            # Delay baseado no tamanho da mensagem
            # Simula "tempo de digitação"
            chars = len(msg)
            delay = 0 if i == 0 else min(3, max(1, chars / 30))  # 1-3 segundos

            result.append({
                "text": msg,
                "delay_seconds": delay
            })

        return result

    def batch_recommendations_by_person(
        self,
        recommendations: List[Recommendation]
    ) -> Dict[str, List[Recommendation]]:
        """
        Agrupa recomendações por pessoa.

        Args:
            recommendations: Lista de recomendações

        Returns:
            Dict {person_name: [recommendations]}
        """
        batches = {}

        for rec in recommendations:
            person = rec.target_person
            if person not in batches:
                batches[person] = []
            batches[person].append(rec)

        return batches

    def should_send_now(
        self,
        recommendation: Recommendation,
        current_hour: int
    ) -> bool:
        """
        Decide se deve enviar recomendação agora.

        Args:
            recommendation: Recomendação
            current_hour: Hora atual (0-23)

        Returns:
            True se deve enviar agora
        """
        # Críticas: envia sempre (exceto madrugada)
        if recommendation.priority == RecommendationPriority.CRITICAL:
            return 7 <= current_hour <= 22  # 7h-22h

        # High: envia em horário comercial
        if recommendation.priority == RecommendationPriority.HIGH:
            return 9 <= current_hour <= 19  # 9h-19h

        # Medium/Low: envia só em horários específicos
        return current_hour in [9, 14, 17]  # 9h, 14h, 17h
