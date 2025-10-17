"""
Mapeador de Tasks para números.

Este módulo gerencia o mapeamento temporário entre números (1, 2, 3...)
e IDs de tasks do Notion, permitindo que usuários referenciem tasks por número.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz

from config.settings import settings

logger = logging.getLogger(__name__)


class TaskMapper:
    """
    Gerencia mapeamento temporário: número → task.

    O cache expira após o período configurado (padrão: 24h).
    """

    def __init__(self):
        """Inicializa o mapeador de tasks."""
        self.cache: Dict[str, Dict] = {}
        # Estrutura: {
        #     "person_name": {
        #         "mapping": {1: {"id": "...", "nome": "...", "status": "..."}, 2: {...}},
        #         "expires_at": datetime,
        #         "tasks_grouped": {"a_fazer": [], "em_andamento": [], "concluidas": []}
        #     }
        # }
        logger.info("TaskMapper inicializado")

    def create_mapping(
        self,
        person_name: str,
        tasks_grouped: Dict[str, List[Dict]]
    ) -> Dict[int, Dict]:
        """
        Cria mapeamento de números para tasks.

        Args:
            person_name: Nome do colaborador
            tasks_grouped: Tasks agrupadas por status (a_fazer, em_andamento, concluidas)

        Returns:
            Dict com mapeamento {número: task_info}
        """
        logger.info(f"Criando mapeamento de tasks para {person_name}")

        mapping = {}
        numero = 1

        # Mapeia tasks A FAZER
        for task in tasks_grouped.get("a_fazer", []):
            mapping[numero] = {
                "id": task["id"],
                "nome": task["nome"],
                "prioridade": task.get("prioridade", "Normal"),
                "status": "A Fazer"
            }
            numero += 1

        # Mapeia tasks EM ANDAMENTO
        for task in tasks_grouped.get("em_andamento", []):
            mapping[numero] = {
                "id": task["id"],
                "nome": task["nome"],
                "prioridade": task.get("prioridade", "Normal"),
                "status": "Em Andamento"
            }
            numero += 1

        # Mapeia tasks CONCLUÍDAS
        for task in tasks_grouped.get("concluidas", []):
            mapping[numero] = {
                "id": task["id"],
                "nome": task["nome"],
                "prioridade": task.get("prioridade", "Normal"),
                "status": "Concluída"
            }
            numero += 1

        # Calcula expiração
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)
        expires_at = now + timedelta(hours=settings.CACHE_EXPIRY_HOURS)

        # Armazena no cache
        self.cache[person_name] = {
            "mapping": mapping,
            "expires_at": expires_at,
            "tasks_grouped": tasks_grouped
        }

        logger.info(
            f"Mapeamento criado: {len(mapping)} tasks para {person_name}. "
            f"Expira em: {expires_at.strftime('%d/%m/%Y %H:%M')}"
        )

        return mapping

    def get_task(self, person_name: str, task_number: int) -> Optional[Dict]:
        """
        Retorna task pelo número, se ainda válido.

        Args:
            person_name: Nome do colaborador
            task_number: Número da task (1, 2, 3...)

        Returns:
            Dict com informações da task ou None se não encontrado/expirado
        """
        # Verifica se existe cache para essa pessoa
        if person_name not in self.cache:
            logger.warning(f"Nenhum mapeamento encontrado para {person_name}")
            return None

        cache_entry = self.cache[person_name]

        # Verifica se expirou
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)
        if now > cache_entry["expires_at"]:
            logger.warning(f"Mapeamento expirado para {person_name}")
            del self.cache[person_name]
            return None

        # Busca task
        mapping = cache_entry["mapping"]
        task = mapping.get(task_number)

        if task:
            logger.info(f"Task {task_number} encontrada para {person_name}: {task['nome']}")
        else:
            logger.warning(f"Task {task_number} não encontrada para {person_name}")

        return task

    def get_all_tasks(self, person_name: str) -> Optional[Dict[int, Dict]]:
        """
        Retorna todos os mapeamentos de uma pessoa.

        Args:
            person_name: Nome do colaborador

        Returns:
            Dict com todos os mapeamentos ou None
        """
        if person_name not in self.cache:
            return None

        cache_entry = self.cache[person_name]

        # Verifica expiração
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)
        if now > cache_entry["expires_at"]:
            del self.cache[person_name]
            return None

        return cache_entry["mapping"]

    def cleanup_expired(self) -> int:
        """
        Remove mapeamentos expirados.

        Returns:
            Número de mapeamentos removidos
        """
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)

        expired = []
        for person_name, cache_entry in self.cache.items():
            if now > cache_entry["expires_at"]:
                expired.append(person_name)

        for person_name in expired:
            del self.cache[person_name]

        if expired:
            logger.info(f"Removidos {len(expired)} mapeamentos expirados")

        return len(expired)

    def has_mapping(self, person_name: str) -> bool:
        """
        Verifica se existe mapeamento válido para uma pessoa.

        Args:
            person_name: Nome do colaborador

        Returns:
            True se existe mapeamento válido
        """
        if person_name not in self.cache:
            return False

        # Verifica expiração
        cache_entry = self.cache[person_name]
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)

        if now > cache_entry["expires_at"]:
            del self.cache[person_name]
            return False

        return True

    def invalidate(self, person_name: str) -> bool:
        """
        Invalida (remove) mapeamento de uma pessoa.

        Args:
            person_name: Nome do colaborador

        Returns:
            True se havia mapeamento para remover
        """
        if person_name in self.cache:
            del self.cache[person_name]
            logger.info(f"Mapeamento invalidado para {person_name}")
            return True

        return False

    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do cache.

        Returns:
            Dict com estatísticas
        """
        total_people = len(self.cache)
        total_tasks = sum(
            len(entry["mapping"])
            for entry in self.cache.values()
        )

        return {
            "total_people": total_people,
            "total_tasks": total_tasks,
            "cache_entries": list(self.cache.keys())
        }


# Instância global do mapper
_task_mapper_instance = None


def get_task_mapper() -> TaskMapper:
    """
    Retorna instância singleton do TaskMapper.

    Returns:
        TaskMapper: Instância global
    """
    global _task_mapper_instance

    if _task_mapper_instance is None:
        _task_mapper_instance = TaskMapper()

    return _task_mapper_instance
