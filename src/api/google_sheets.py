"""
Google Sheets API integration for fetching colaborador data.

Este módulo permite ler dados de uma planilha Google compartilhada
para identificar usuários pelo número de telefone.
"""

import logging
import os
import re
import csv
from io import StringIO
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """
    Client para acessar dados de uma Google Sheet via URL público.

    Usa o endpoint de exportação CSV do Google Sheets para ler dados
    sem necessidade de OAuth ou chaves de API.
    """

    def __init__(self, sheet_url: str, cache_ttl_minutes: int = 5):
        """
        Inicializa o cliente Google Sheets.

        Args:
            sheet_url: URL da planilha (incluindo /edit?usp=sharing)
            cache_ttl_minutes: Tempo de cache em minutos (padrão 5)
        """
        self.sheet_url = sheet_url
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache_data = None
        self.cache_timestamp = None

        # Extrai o sheet ID da URL
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            raise ValueError(f"URL de Google Sheet inválida: {sheet_url}")

        self.sheet_id = match.group(1)
        self.csv_export_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv"
        logger.info(f"✅ GoogleSheetsClient inicializado para sheet: {self.sheet_id[:20]}...")

    def _fetch_data(self) -> Optional[str]:
        """
        Faz download dos dados da planilha em formato CSV.

        Returns:
            String CSV ou None em caso de erro
        """
        try:
            logger.debug(f"Fetching data from: {self.csv_export_url}")
            response = requests.get(self.csv_export_url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados do Google Sheets: {e}")
            return None

    def _get_cached_data(self) -> Optional[str]:
        """
        Retorna dados em cache se ainda forem válidos.

        Returns:
            String CSV em cache ou None se expirado
        """
        if self.cache_data is None or self.cache_timestamp is None:
            return None

        # Verifica se cache ainda é válido
        if datetime.now() - self.cache_timestamp > self.cache_ttl:
            logger.debug("Cache expirado, recarregando...")
            self.cache_data = None
            self.cache_timestamp = None
            return None

        logger.debug("Usando dados em cache")
        return self.cache_data

    def _load_sheet_data(self) -> Optional[list[Dict[str, str]]]:
        """
        Carrega dados da planilha (com cache).

        Returns:
            Lista de dicionários com dados da planilha ou None
        """
        # Tenta usar cache
        csv_data = self._get_cached_data()

        # Se não tiver cache, faz download
        if csv_data is None:
            csv_data = self._fetch_data()
            if csv_data is None:
                return None

            # Salva no cache
            self.cache_data = csv_data
            self.cache_timestamp = datetime.now()

        # Parseia CSV
        try:
            rows = []
            reader = csv.DictReader(StringIO(csv_data))
            for row in reader:
                rows.append(row)

            logger.debug(f"Loaded {len(rows)} rows from Google Sheets")
            return rows
        except Exception as e:
            logger.error(f"❌ Erro ao parsear CSV: {e}")
            return None

    def get_colaborador_by_phone(self, phone: str) -> Optional[Dict[str, str]]:
        """
        Busca colaborador pelo número de telefone.

        Args:
            phone: Telefone no formato +XXXXXXXXXXX ou sem +

        Returns:
            Dicionário com dados do colaborador ou None
        """
        # Normaliza phone para comparação
        phone_normalized = phone.replace("+", "").strip()

        # Carrega dados
        rows = self._load_sheet_data()
        if not rows:
            logger.warning(f"❌ Não foi possível carregar dados do Google Sheets")
            return None

        # Busca por telefone em diferentes colunas possíveis
        for row in rows:
            # Tenta diferentes nomes de coluna que podem conter o telefone
            for phone_col in ['telefone', 'phone', 'whatsapp', 'numero', 'number']:
                if phone_col not in row:
                    continue

                row_phone = row[phone_col].replace("+", "").strip()

                if row_phone == phone_normalized:
                    logger.info(f"✅ Colaborador encontrado no Google Sheets: {row.get('nome', 'Desconhecido')} ({phone})")
                    return row

        logger.debug(f"❌ Telefone não encontrado no Google Sheets: {phone}")
        return None

    def get_all_colaboradores(self) -> Optional[list[Dict[str, str]]]:
        """
        Retorna todos os colaboradores da planilha.

        Returns:
            Lista de dicionários com dados dos colaboradores ou None
        """
        rows = self._load_sheet_data()
        if not rows:
            return None

        logger.info(f"📋 Carregados {len(rows)} colaboradores do Google Sheets")
        return rows

    def clear_cache(self):
        """Limpa o cache de dados."""
        self.cache_data = None
        self.cache_timestamp = None
        logger.debug("Cache limpo")
