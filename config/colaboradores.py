"""
Configuração dos colaboradores da Pange.iA.

Este módulo contém o mapeamento de colaboradores para números de WhatsApp
e outras informações relevantes para o sistema.

Suporta busca em:
1. Dicionário hardcoded (COLABORADORES) - mais rápido
2. Google Sheets (fallback) - sincronizado dinamicamente
"""

import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


# Mapeamento de colaboradores: nome completo → informações
COLABORADORES: Dict[str, Dict[str, any]] = {
    "Estevao Antunes": {
        "telefone": "+554191851256",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None  # Será preenchido automaticamente
    },
    "Julio Inoue": {
        "telefone": "+5511999322027",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Arthur Leuzzi": {
        "telefone": "+554888428246",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Joaquim": {
        "telefone": "+5511980992410",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Kevin": {
        "telefone": "+554792054701",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Leo Confettura": {
        "telefone": "+552498117033",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Luna Machado": {
        "telefone": "+554484282600",
        "cargo": "Desenvolvedora",
        "ativo": True,
        "notion_id": None
    },
    "Sami Monteleone": {
        "telefone": "+551998100715",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Saraiva": {
        "telefone": "+551199143605",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
}


# Grupo do WhatsApp para postagem de tasks
GRUPO_TASKS = {
    "nome": "pange.ia Tasks",
    "numero": None,  # Será configurado posteriormente
    "ativo": False   # Ativar quando tiver o grupo configurado
}


def get_colaborador_by_phone(phone: str) -> Optional[str]:
    """
    Busca o nome do colaborador pelo número de telefone.

    Usa normalização flexível com suporte a:
    - Múltiplos formatos de telefone
    - Compatibilidade formato antigo (8 dígitos) e novo (9 dígitos)
    - Fallback para Google Sheets

    Args:
        phone: Número de telefone em qualquer formato

    Returns:
        Nome do colaborador ou None se não encontrado.
    """
    return find_colaborador_by_phone_flexible(phone)


def get_phone_by_name(name: str) -> Optional[str]:
    """
    Busca o telefone do colaborador pelo nome.

    Args:
        name: Nome do colaborador (busca exata ou por alias)

    Returns:
        Telefone no formato +XXXXXXXXXXX ou None.
    """
    # Busca exata
    if name in COLABORADORES:
        return COLABORADORES[name]["telefone"]

    # Busca por aliases
    for nome, info in COLABORADORES.items():
        aliases = info.get("aliases", [])
        if name.lower() in [a.lower() for a in aliases]:
            return info["telefone"]

    return None


def get_colaboradores_ativos() -> Dict[str, Dict[str, any]]:
    """
    Retorna apenas colaboradores ativos.

    Returns:
        Dicionário com colaboradores ativos.
    """
    return {
        nome: info
        for nome, info in COLABORADORES.items()
        if info.get("ativo", True)
    }


def get_all_phone_numbers() -> list[str]:
    """
    Retorna lista de todos os telefones dos colaboradores ativos.

    Returns:
        Lista de telefones no formato +XXXXXXXXXXX
    """
    return [
        info["telefone"]
        for info in get_colaboradores_ativos().values()
    ]


def normalize_phone_number(phone: str) -> Optional[str]:
    """
    Normaliza número de telefone para formato E.164 (+55XXXXXXXXXXX).

    Aceita múltiplos formatos:
    - +554191851256 (formato E.164)
    - 554191851256 (sem +)
    - +55 41 91851256 (com espaços)
    - 55 41 9185-1256 (com espaços e hífen)
    - 4191851256 (DDD + número)
    - 41 91851256 (DDD com espaço)

    Args:
        phone: Número de telefone em qualquer formato

    Returns:
        Número normalizado em formato E.164 ou None se inválido
    """
    if not phone:
        return None

    # Remove espaços, hífens, parênteses, pontos
    cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")

    # Remove + se estiver no início
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    # Se tem 12-13 dígitos e começa com 55 (código Brasil)
    if cleaned.startswith("55") and 12 <= len(cleaned) <= 13:
        return "+" + cleaned

    # Se tem 10 ou 11 dígitos (número local sem código país)
    if 10 <= len(cleaned) <= 11:
        # Adiciona código do Brasil (55)
        return "+" + "55" + cleaned

    # Se tem 8-9 dígitos (apenas número sem DDD)
    if 8 <= len(cleaned) <= 9:
        # Não temos DDD, retorna None
        logger.warning(f"Número de telefone incompleto (sem DDD): {phone}")
        return None

    logger.warning(f"Formato de telefone não reconhecido: {phone}")
    return None


def find_colaborador_by_phone_flexible(phone: str) -> Optional[str]:
    """
    Busca colaborador pelo telefone com normalização flexível.

    Tenta múltiplas variações do número para garantir reconhecimento,
    incluindo formatos antigo (8 dígitos) e novo (9 dígitos).

    Args:
        phone: Número de telefone em qualquer formato

    Returns:
        Nome do colaborador ou None se não encontrado
    """
    if not phone:
        return None

    normalized = normalize_phone_number(phone)
    if not normalized:
        return None

    # Tenta correspondência exata primeiro
    for nome, info in COLABORADORES.items():
        if info["telefone"] == normalized:
            return nome

    # Tenta com/sem 9º dígito (compatibilidade formato antigo/novo)
    # Se o número tem 14 caracteres (+55 DDD 9 XXXXXXXX), tenta remover o 9
    if len(normalized) == 14:  # +55DDD9XXXXXXXX (13 dígitos)
        # Tenta remover o 9 após o DDD (formato antigo tem 8 dígitos, novo tem 9)
        # Posições: 0-2 (+55), 3-4 (DDD), 5 (9?), 6-13 (números)
        if normalized[5] == "9":  # Se o 6º caractere é 9
            alt_number = normalized[:5] + normalized[6:]  # Remove o 9 na posição 5
            for nome, info in COLABORADORES.items():
                if info["telefone"] == alt_number:
                    logger.info(f"✅ Colaborador identificado (formato novo, BD antigo): {nome}")
                    return nome

    # Se o número tem 13 caracteres (+55 DDD XXXXXXXX), tenta adicionar 9
    elif len(normalized) == 13:  # +55DDDXXXXXXXX (12 dígitos)
        # Tenta adicionar 9 após o DDD (formato novo tem 9 dígitos, antigo tem 8)
        # Posições: 0-2 (+55), 3-4 (DDD), 5-12 (números)
        alt_number = normalized[:5] + "9" + normalized[5:]  # Adiciona 9 na posição 5
        for nome, info in COLABORADORES.items():
            if info["telefone"] == alt_number:
                logger.info(f"✅ Colaborador identificado (formato antigo, BD novo): {nome}")
                return nome

    # Fallback: Google Sheets
    try:
        sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        if sheets_url:
            from src.api.google_sheets import GoogleSheetsClient
            sheets_client = GoogleSheetsClient(sheets_url, cache_ttl_minutes=5)
            colaborador = sheets_client.get_colaborador_by_phone(phone)
            if colaborador:
                name = colaborador.get('Nome') or colaborador.get('nome') or 'Desconhecido'
                logger.info(f"✅ Colaborador identificado via Google Sheets: {name}")
                return name
    except Exception as e:
        logger.debug(f"Erro ao buscar em Google Sheets: {e}")

    return None


def get_colaborador_info(name: str) -> Optional[Dict[str, any]]:
    """
    Retorna informações completas de um colaborador.

    Args:
        name: Nome do colaborador

    Returns:
        Dicionário com informações ou None.
    """
    return COLABORADORES.get(name)
