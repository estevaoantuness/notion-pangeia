"""
Gerenciador de Tasks do Notion.

Este módulo gerencia operações de leitura e consulta de tasks,
incluindo busca por colaborador, filtragem e agrupamento.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, date
import pytz

from src.notion.client import NotionClient
from config.settings import settings
from config.colaboradores import get_colaborador_info

logger = logging.getLogger(__name__)


class TasksManager:
    """
    Gerencia operações com tasks no Notion.

    Responsável por buscar, filtrar e organizar tasks de colaboradores.
    """

    def __init__(self, notion_client: Optional[NotionClient] = None):
        """
        Inicializa o gerenciador de tasks.

        Args:
            notion_client: Cliente Notion (cria um novo se não fornecido)
        """
        self.notion_client = notion_client or NotionClient()
        self.database_id = settings.NOTION_TASKS_DB_ID
        logger.info("TasksManager inicializado")

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normaliza nome removendo acentos e convertendo para minúsculas.

        Args:
            name: Nome para normalizar

        Returns:
            Nome normalizado
        """
        import unicodedata
        # Remove acentos
        normalized = unicodedata.normalize('NFKD', name)
        normalized = ''.join([c for c in normalized if not unicodedata.combining(c)])
        return normalized.lower().strip()

    def get_person_tasks(
        self,
        person_name: str,
        include_completed: bool = True,
        date_filter: Optional[date] = None
    ) -> Dict[str, List[Dict]]:
        """
        Busca tasks de uma pessoa específica.

        Args:
            person_name: Nome completo do colaborador
            include_completed: Se True, inclui tasks concluídas
            date_filter: Data específica para filtrar (default: todas)

        Returns:
            Dict com tasks agrupadas por status:
            {
                "concluidas": [task1, task2, ...],
                "em_andamento": [task3, task4, ...],
                "a_fazer": [task5, ...]
            }
        """
        logger.info(f"Buscando tasks de: {person_name}")

        # Busca todas as tasks (sem filtro por enquanto)
        # Vamos filtrar manualmente depois
        try:
            results = self.notion_client.query_database(
                database_id=self.database_id
            )

            # Filtra manualmente por responsável
            filtered_results = []
            for task in results:
                # Propriedade "Assignees" é multi_select, não people
                assignees_prop = task.get("properties", {}).get("Assignees", {})
                assignees = assignees_prop.get("multi_select", [])

                # Verifica se a pessoa é responsável
                is_responsible = False
                for assignee in assignees:
                    assignee_name = assignee.get("name", "")
                    # Remove acentos para comparação
                    assignee_normalized = self._normalize_name(assignee_name)
                    person_normalized = self._normalize_name(person_name)

                    # Verifica se qualquer parte do nome coincide
                    if (assignee_normalized in person_normalized or
                        person_normalized in assignee_normalized or
                        any(part in assignee_normalized for part in person_normalized.split() if len(part) > 2)):
                        is_responsible = True
                        break

                if not is_responsible:
                    continue

                filtered_results.append(task)

            logger.info(f"Encontradas {len(filtered_results)} tasks para {person_name}")

            # Agrupa por status
            grouped_tasks = self._group_by_status(filtered_results)

            return grouped_tasks

        except Exception as e:
            logger.error(f"Erro ao buscar tasks de {person_name}: {e}")
            raise

    def _group_by_status(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa tasks por status PARA EXIBIÇÃO NA LISTA.

        IMPORTANTE: Tasks concluídas NÃO são incluídas na lista!
        Usuário deve ver apenas o que ainda precisa fazer.

        Status:
        - concluidas: [] (SEMPRE VAZIO - não mostra na lista)
        - em_andamento: Status = "Em Andamento"
        - a_fazer: Status = "A Fazer", "Bloqueada", ou outros

        Args:
            tasks: Lista de tasks do Notion

        Returns:
            Dict com tasks agrupadas (concluidas sempre vazio)
        """
        grouped = {
            "concluidas": [],  # Sempre vazio - não mostramos na lista
            "em_andamento": [],
            "a_fazer": []
        }

        for task in tasks:
            parsed_task = self._parse_task(task)
            status = parsed_task.get("status", "")

            if status in ["Concluído", "Concluída", "Done", "Completed"]:
                # NÃO adiciona à lista - usuário não precisa ver
                # Tasks concluídas só aparecem no contador de progresso
                continue
            elif status == "Em Andamento":
                grouped["em_andamento"].append(parsed_task)
            else:
                # A Fazer, Bloqueada, ou qualquer outro status
                grouped["a_fazer"].append(parsed_task)

        logger.info(
            f"Tasks para lista: 0 concluídas (filtradas), "
            f"{len(grouped['em_andamento'])} em andamento, "
            f"{len(grouped['a_fazer'])} a fazer"
        )

        return grouped

    def _group_by_priority(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa tasks por prioridade baseado no prazo.

        Prioridades:
        - urgente: prazo hoje ou atrasadas
        - importante: prazo nos próximos 7 dias
        - normal: prazo > 7 dias ou sem prazo

        Args:
            tasks: Lista de tasks do Notion

        Returns:
            Dict com tasks agrupadas por prioridade
        """
        today = datetime.now(pytz.timezone(settings.TIMEZONE)).date()

        grouped = {
            "urgente": [],
            "importante": [],
            "normal": []
        }

        for task in tasks:
            parsed_task = self._parse_task(task)

            prazo = parsed_task.get("prazo_date")

            if prazo:
                dias_ate_prazo = (prazo - today).days

                if dias_ate_prazo <= 0:
                    # Prazo hoje ou atrasado
                    grouped["urgente"].append(parsed_task)
                elif dias_ate_prazo <= 7:
                    # Prazo esta semana
                    grouped["importante"].append(parsed_task)
                else:
                    # Prazo futuro
                    grouped["normal"].append(parsed_task)
            else:
                # Sem prazo
                grouped["normal"].append(parsed_task)

        logger.info(
            f"Tasks agrupadas: {len(grouped['urgente'])} urgentes, "
            f"{len(grouped['importante'])} importantes, "
            f"{len(grouped['normal'])} normais"
        )

        return grouped

    def _parse_task(self, task: Dict) -> Dict:
        """
        Extrai informações relevantes de uma task do Notion.

        Args:
            task: Task raw do Notion

        Returns:
            Dict com informações formatadas
        """
        properties = task.get("properties", {})

        # Nome da task (propriedade "Task")
        nome_prop = properties.get("Task", {})
        nome = ""
        if nome_prop.get("title"):
            nome = nome_prop["title"][0].get("plain_text", "")

        # Status (tipo 'status', não 'select')
        status_prop = properties.get("Status", {})
        status = ""
        if status_prop.get("status"):
            status = status_prop["status"].get("name", "")
        elif status_prop.get("select"):  # Fallback para databases antigas
            status = status_prop["select"].get("name", "")

        # Prazo
        prazo_prop = properties.get("Prazo", {})
        prazo_str = None
        prazo_date = None
        if prazo_prop.get("date"):
            prazo_str = prazo_prop["date"].get("start", "")
            if prazo_str:
                try:
                    prazo_date = datetime.strptime(prazo_str, "%Y-%m-%d").date()
                except:
                    pass

        # Data de Conclusão
        data_conclusao = None
        if status in ["Concluído", "Concluída", "Done", "Completed"]:
            # Primeiro tenta campo "Data de Conclusão" se existir
            conclusao_prop = properties.get("Data de Conclusão", {})
            if conclusao_prop.get("date"):
                conclusao_str = conclusao_prop["date"].get("start", "")
                if conclusao_str:
                    try:
                        data_conclusao = datetime.strptime(conclusao_str, "%Y-%m-%d").date()
                    except:
                        pass

            # Se não tiver campo específico, usa last_edited_time
            if not data_conclusao:
                last_edited = task.get("last_edited_time", "")
                if last_edited:
                    try:
                        # Formato ISO: "2025-10-17T19:42:00.000Z"
                        dt = datetime.fromisoformat(last_edited.replace('Z', '+00:00'))
                        # Converte para timezone local
                        tz = pytz.timezone(settings.TIMEZONE)
                        dt_local = dt.astimezone(tz)
                        data_conclusao = dt_local.date()
                    except:
                        pass

        # Prioridade
        prioridade_prop = properties.get("Prioridade", {})
        prioridade = ""
        if prioridade_prop.get("select"):
            prioridade = prioridade_prop["select"].get("name", "")

        # Link do Notion
        notion_link = task.get("url", "")

        # ID da task
        task_id = task.get("id", "")

        return {
            "id": task_id,
            "nome": nome,
            "status": status,
            "prazo_str": prazo_str,
            "prazo_date": prazo_date,
            "prioridade": prioridade,
            "link": notion_link,
            "data_conclusao": data_conclusao
        }

    def get_all_active_tasks(self) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Busca tasks ativas de todos os colaboradores.

        Returns:
            Dict com tasks por pessoa:
            {
                "Estevao Antunes": {
                    "urgente": [...],
                    "importante": [...],
                    "normal": [...]
                },
                ...
            }
        """
        logger.info("Buscando tasks de todos os colaboradores")

        from config.colaboradores import get_colaboradores_ativos

        colaboradores = get_colaboradores_ativos()
        all_tasks = {}

        for nome in colaboradores.keys():
            try:
                tasks = self.get_person_tasks(nome)
                all_tasks[nome] = tasks
            except Exception as e:
                logger.error(f"Erro ao buscar tasks de {nome}: {e}")
                all_tasks[nome] = {"urgente": [], "importante": [], "normal": []}

        return all_tasks

    def get_active_tasks(self, person_name: str) -> List[Dict]:
        """
        Compatibilidade: retorna lista simples de tasks ativas.

        Alguns fluxos legados (e deploys antigos) ainda chamam este método,
        então mantemos o helper para evitar AttributeError.
        """
        grouped = self.get_person_tasks(person_name, include_completed=False)
        active_tasks: List[Dict] = []
        active_tasks.extend(grouped.get("em_andamento", []))
        active_tasks.extend(grouped.get("a_fazer", []))
        return active_tasks

    def calculate_progress(self, person_name: str) -> Dict:
        """
        Calcula progresso do colaborador INCLUINDO tasks concluídas.

        IMPORTANTE: Diferente de _group_by_status(), este método
        CONTA tasks concluídas para mostrar estatísticas completas.

        Usado para:
        - Contador de progresso ("3 concluídas | 2 em andamento")
        - Percentual de conclusão (3/11 = 27%)
        - Mensagens contextuais de progresso

        Args:
            person_name: Nome do colaborador

        Returns:
            Dict com estatísticas:
            {
                "total": 10,           # Total do dia (incluindo concluídas)
                "concluidas": 5,       # Quantas foram concluídas
                "em_andamento": 3,     # Quantas estão em progresso
                "pendentes": 2,        # Quantas faltam fazer
                "percentual": 50       # % de conclusão
            }
        """
        logger.info(f"Calculando progresso de {person_name}")

        try:
            # Busca todas as tasks (incluindo concluídas) e filtra manualmente
            results = self.notion_client.query_database(
                database_id=self.database_id
            )

            # Filtra manualmente por pessoa
            filtered_results = []
            for task in results:
                assignees_prop = task.get("properties", {}).get("Assignees", {})
                assignees = assignees_prop.get("multi_select", [])

                is_responsible = False
                for assignee in assignees:
                    assignee_name = assignee.get("name", "")
                    assignee_normalized = self._normalize_name(assignee_name)
                    person_normalized = self._normalize_name(person_name)

                    if (assignee_normalized in person_normalized or
                        person_normalized in assignee_normalized or
                        any(part in assignee_normalized for part in person_normalized.split() if len(part) > 2)):
                        is_responsible = True
                        break

                if is_responsible:
                    filtered_results.append(task)

            results = filtered_results

            total = len(results)
            concluidas = 0
            em_andamento = 0
            pendentes = 0

            for task in results:
                status_prop = task.get("properties", {}).get("Status", {})

                # Tipo 'status' (novo) ou 'select' (antigo)
                status = ""
                if status_prop.get("status"):
                    status = status_prop["status"].get("name", "")
                elif status_prop.get("select"):
                    status = status_prop["select"].get("name", "")

                if status:
                    if status in ["Concluído", "Concluída", "Done", "Completed"]:
                        concluidas += 1
                    elif status == "Em Andamento":
                        em_andamento += 1
                    else:
                        pendentes += 1
                else:
                    pendentes += 1

            percentual = int((concluidas / total * 100)) if total > 0 else 0

            progress = {
                "total": total,
                "concluidas": concluidas,
                "em_andamento": em_andamento,
                "pendentes": pendentes,
                "percentual": percentual
            }

            logger.info(f"Progresso de {person_name}: {percentual}% ({concluidas}/{total})")

            return progress

        except Exception as e:
            logger.error(f"Erro ao calcular progresso: {e}")
            return {
                "total": 0,
                "concluidas": 0,
                "em_andamento": 0,
                "pendentes": 0,
                "percentual": 0
            }
