"""
Configuração dos colaboradores da Pange.iA.

Este módulo contém o mapeamento de colaboradores para números de WhatsApp
e outras informações relevantes para o sistema.
"""

from typing import Dict, Optional


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
    "Leticia": {
        "telefone": "+551191095230",
        "cargo": "Designer",
        "ativo": True,
        "notion_id": None,
        "aliases": ["leebuani", "Leebuani"]
    },
    "Joaquim": {
        "telefone": "+551198099410",
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
        "telefone": "+552498170330",
        "cargo": "Desenvolvedor",
        "ativo": True,
        "notion_id": None
    },
    "Rebeca Figueredo": {
        "telefone": "+559991244030",
        "cargo": "Product Manager",
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

    Args:
        phone: Número de telefone no formato +XXXXXXXXXXX ou whatsapp:+XXXXXXXXXXX (compatibilidade)

    Returns:
        Nome do colaborador ou None se não encontrado.
    """
    for nome, info in COLABORADORES.items():
        if info["telefone"] == phone:
            return nome
    return None


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


def get_colaborador_info(name: str) -> Optional[Dict[str, any]]:
    """
    Retorna informações completas de um colaborador.

    Args:
        name: Nome do colaborador

    Returns:
        Dicionário com informações ou None.
    """
    return COLABORADORES.get(name)
