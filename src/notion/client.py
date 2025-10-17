"""
Cliente Notion com rate limiting e tratamento de erros.

Este módulo fornece uma interface robusta para interagir com a API do Notion,
incluindo controle de taxa de requisições e retry logic.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from notion_client import Client
from notion_client.errors import APIResponseError

from config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Controla a taxa de requisições à API do Notion.

    Notion API tem limite de ~3 requisições por segundo.
    """

    def __init__(self, max_calls: int = 3, period: float = 1.0):
        """
        Inicializa o rate limiter.

        Args:
            max_calls: Número máximo de chamadas permitidas por período
            period: Período em segundos
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []

    def wait_if_needed(self) -> None:
        """Aguarda se necessário para respeitar o rate limit."""
        now = time.time()

        # Remove chamadas antigas (fora do período)
        self.calls = [call for call in self.calls if now - call < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit atingido. Aguardando {sleep_time:.2f}s")
                time.sleep(sleep_time)

        self.calls.append(time.time())


class NotionClient:
    """
    Cliente para interagir com a API do Notion.

    Inclui rate limiting, retry logic e tratamento de erros.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Inicializa o cliente Notion.

        Args:
            token: Token de autenticação (usa settings se não fornecido)
        """
        self.token = token or settings.NOTION_TOKEN
        self.client = Client(auth=self.token)
        self.rate_limiter = RateLimiter(max_calls=3, period=1.0)
        logger.info("Cliente Notion inicializado")

    def _make_request(
        self,
        method: callable,
        *args,
        retry_count: int = 0,
        **kwargs
    ) -> Any:
        """
        Executa uma requisição com rate limiting e retry.

        Args:
            method: Método da API do Notion a ser chamado
            *args: Argumentos posicionais para o método
            retry_count: Contador de tentativas (interno)
            **kwargs: Argumentos nomeados para o método

        Returns:
            Resposta da API do Notion

        Raises:
            APIResponseError: Se todas as tentativas falharem
        """
        self.rate_limiter.wait_if_needed()

        try:
            result = method(*args, **kwargs)
            return result

        except APIResponseError as e:
            # Se for erro 429 (rate limit) ou 5xx, tenta novamente
            if e.status in [429, 500, 502, 503, 504] and retry_count < settings.MAX_RETRIES:
                wait_time = (2 ** retry_count) * 1  # Backoff exponencial
                logger.warning(
                    f"Erro {e.status} na API Notion. "
                    f"Tentando novamente em {wait_time}s (tentativa {retry_count + 1}/{settings.MAX_RETRIES})"
                )
                time.sleep(wait_time)
                return self._make_request(method, *args, retry_count=retry_count + 1, **kwargs)

            logger.error(f"Erro na API Notion: {e}")
            raise

    def get_database(self, database_id: str) -> Dict:
        """
        Busca informações de uma database.

        Args:
            database_id: ID da database no Notion

        Returns:
            Dict com informações da database
        """
        logger.info(f"Buscando database: {database_id}")
        return self._make_request(
            self.client.databases.retrieve,
            database_id=database_id
        )

    def query_database(
        self,
        database_id: str,
        filters: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None,
        page_size: int = 100
    ) -> List[Dict]:
        """
        Consulta uma database com filtros e ordenação.

        Args:
            database_id: ID da database
            filters: Filtros no formato da API do Notion
            sorts: Ordenação no formato da API do Notion
            page_size: Número de resultados por página

        Returns:
            Lista de páginas que correspondem aos critérios
        """
        logger.info(f"Consultando database: {database_id}")

        query_params = {"database_id": database_id, "page_size": page_size}

        if filters:
            query_params["filter"] = filters

        if sorts:
            query_params["sorts"] = sorts

        results = []
        has_more = True
        start_cursor = None

        while has_more:
            if start_cursor:
                query_params["start_cursor"] = start_cursor

            response = self._make_request(
                self.client.databases.query,
                **query_params
            )

            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        logger.info(f"Encontradas {len(results)} páginas")
        return results

    def get_page(self, page_id: str) -> Dict:
        """
        Busca uma página específica.

        Args:
            page_id: ID da página

        Returns:
            Dict com informações da página
        """
        logger.info(f"Buscando página: {page_id}")
        return self._make_request(
            self.client.pages.retrieve,
            page_id=page_id
        )

    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """
        Atualiza propriedades de uma página.

        Args:
            page_id: ID da página
            properties: Propriedades a serem atualizadas

        Returns:
            Dict com a página atualizada
        """
        logger.info(f"Atualizando página: {page_id}")
        return self._make_request(
            self.client.pages.update,
            page_id=page_id,
            properties=properties
        )

    def create_page(
        self,
        parent_database_id: str,
        properties: Dict,
        children: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Cria uma nova página em uma database.

        Args:
            parent_database_id: ID da database pai
            properties: Propriedades da página
            children: Blocos de conteúdo (opcional)

        Returns:
            Dict com a página criada
        """
        logger.info(f"Criando página na database: {parent_database_id}")

        page_data = {
            "parent": {"database_id": parent_database_id},
            "properties": properties
        }

        if children:
            page_data["children"] = children

        return self._make_request(
            self.client.pages.create,
            **page_data
        )

    def append_block_children(self, block_id: str, children: List[Dict]) -> Dict:
        """
        Adiciona blocos de conteúdo a uma página.

        Args:
            block_id: ID do bloco pai (página)
            children: Lista de blocos a adicionar

        Returns:
            Dict com os blocos adicionados
        """
        logger.info(f"Adicionando blocos à página: {block_id}")
        return self._make_request(
            self.client.blocks.children.append,
            block_id=block_id,
            children=children
        )

    def get_block_children(self, block_id: str) -> List[Dict]:
        """
        Busca blocos filhos de uma página ou bloco.

        Args:
            block_id: ID do bloco pai

        Returns:
            Lista de blocos filhos
        """
        logger.info(f"Buscando blocos da página: {block_id}")
        response = self._make_request(
            self.client.blocks.children.list,
            block_id=block_id
        )
        return response.get("results", [])

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """
        Busca detalhes completos de uma tarefa específica.

        Args:
            task_id: ID da página no Notion

        Returns:
            Dict com todos os campos da tarefa ou None se erro
        """
        try:
            # Buscar página completa
            page = self.get_page(task_id)
            props = page.get('properties', {})

            # Extrair todos os campos
            task_details = {
                'id': task_id,
                'title': self._extract_title(props.get('Name') or props.get('Tarefa') or props.get('Task')),
                'description': self._extract_description(task_id),
                'status': self._extract_select(props.get('Status')),
                'priority': self._extract_priority(props.get('Priority') or props.get('Prioridade')),
                'deadline': self._extract_date(props.get('Deadline') or props.get('Prazo') or props.get('Due Date')),
                'tags': self._extract_multi_select(props.get('Tags') or props.get('Categorias')),
                'assignee': self._extract_people(props.get('Assignee') or props.get('Responsável') or props.get('Person')),
                'url': page.get('url'),
                'created_time': page.get('created_time'),
                'last_edited_time': page.get('last_edited_time')
            }

            return task_details

        except Exception as e:
            logger.error(f"Erro ao buscar detalhes da tarefa {task_id}: {e}")
            return None

    def _extract_title(self, title_prop: Optional[Dict]) -> str:
        """Extrai título de uma propriedade title."""
        if not title_prop:
            return "Sem título"

        title_array = title_prop.get('title', [])
        if not title_array:
            return "Sem título"

        return ''.join([t.get('plain_text', '') for t in title_array])

    def _extract_select(self, select_prop: Optional[Dict]) -> Optional[str]:
        """Extrai valor de uma propriedade select."""
        if not select_prop:
            return None

        select_obj = select_prop.get('select')
        if not select_obj:
            return None

        return select_obj.get('name')

    def _extract_priority(self, priority_prop: Optional[Dict]) -> Optional[str]:
        """Extrai prioridade com emoji."""
        priority = self._extract_select(priority_prop)
        if not priority:
            return None

        # Mapear para emojis
        priority_map = {
            'Alta': '🔴 Alta',
            'High': '🔴 Alta',
            'Média': '🟡 Média',
            'Medium': '🟡 Média',
            'Baixa': '🟢 Baixa',
            'Low': '🟢 Baixa'
        }

        return priority_map.get(priority, priority)

    def _extract_date(self, date_prop: Optional[Dict]) -> Optional[Dict]:
        """Extrai data de uma propriedade date."""
        if not date_prop:
            return None

        date_obj = date_prop.get('date')
        if not date_obj:
            return None

        return {
            'start': date_obj.get('start'),
            'end': date_obj.get('end')
        }

    def _extract_multi_select(self, multi_select_prop: Optional[Dict]) -> List[str]:
        """Extrai tags/categorias."""
        if not multi_select_prop:
            return []

        multi_select = multi_select_prop.get('multi_select', [])
        return [tag.get('name') for tag in multi_select]

    def _extract_people(self, people_prop: Optional[Dict]) -> List[str]:
        """Extrai pessoas."""
        if not people_prop:
            return []

        people = people_prop.get('people', [])
        return [person.get('name', 'Sem nome') for person in people]

    def _extract_description(self, page_id: str) -> str:
        """
        Extrai conteúdo/descrição da página (blocks).

        Args:
            page_id: ID da página

        Returns:
            Descrição formatada ou "Sem descrição"
        """
        try:
            blocks = self.get_block_children(page_id)

            description_parts = []
            for block in blocks:
                block_type = block.get('type')

                if block_type == 'paragraph':
                    text = self._extract_rich_text(block.get('paragraph', {}).get('rich_text', []))
                    if text:
                        description_parts.append(text)

                elif block_type == 'bulleted_list_item':
                    text = self._extract_rich_text(block.get('bulleted_list_item', {}).get('rich_text', []))
                    if text:
                        description_parts.append(f"• {text}")

                elif block_type == 'numbered_list_item':
                    text = self._extract_rich_text(block.get('numbered_list_item', {}).get('rich_text', []))
                    if text:
                        description_parts.append(f"- {text}")

            return '\n'.join(description_parts) if description_parts else "Sem descrição"

        except Exception as e:
            logger.error(f"Erro ao extrair descrição: {e}")
            return "Sem descrição"

    def _extract_rich_text(self, rich_text_array: List[Dict]) -> str:
        """Extrai texto de array de rich_text."""
        return ''.join([rt.get('plain_text', '') for rt in rich_text_array])

    def test_connection(self) -> tuple[bool, str]:
        """
        Testa a conexão com a API do Notion.

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Tenta buscar a database de tasks
            database = self.get_database(settings.NOTION_TASKS_DB_ID)
            database_name = database.get("title", [{}])[0].get("plain_text", "Sem nome")

            logger.info(f"✅ Conexão com Notion OK! Database: {database_name}")
            return True, f"Conectado à database: {database_name}"

        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Notion: {e}")
            return False, f"Erro: {str(e)}"
