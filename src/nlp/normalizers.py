#!/usr/bin/env python3
"""
==============================================================================
SLOT NORMALIZERS - NLP Variables and Slots System
==============================================================================
Comprehensive slot normalization system for extracting and normalizing
variables from user messages.

Normalizers:
- normalize_indices: Handles ranges, commas, spaces (1,2,3 → [1,2,3]; 1-3 → [1,2,3])
- normalize_date: Converts relative dates (amanhã → tomorrow's date, sexta → next friday)
- normalize_project: Case-insensitive fuzzy matching against known projects
- normalize_priority: Maps variations to alta/media/baixa

Author: Pangeia Bot
Created: 2025-11-11
Version: 1.0
==============================================================================
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

# Attempt to import fuzzy matching library
try:
    from rapidfuzz import fuzz, process
    HAVE_RAPIDFUZZ = True
except ImportError:
    from difflib import SequenceMatcher
    HAVE_RAPIDFUZZ = False

logger = logging.getLogger(__name__)

# ==============================================================================
# CONSTANTS AND MAPPINGS
# ==============================================================================

# Known projects (lowercase for matching)
KNOWN_PROJECTS = ["tech", "growth", "ops", "design", "pessoal"]

# Priority mappings (variations → canonical)
PRIORITY_MAP = {
    # Alta
    "alta": "alta",
    "urgente": "alta",
    "urgentíssimo": "alta",
    "crítico": "alta",
    "critico": "alta",
    "importante": "alta",
    "prioridade": "alta",
    "asap": "alta",
    "pra ontem": "alta",
    "para ontem": "alta",
    "high": "alta",
    "1": "alta",

    # Média
    "média": "média",
    "media": "média",
    "normal": "média",
    "médio": "média",
    "medio": "média",
    "moderado": "média",
    "moderada": "média",
    "medium": "média",
    "2": "média",

    # Baixa
    "baixa": "baixa",
    "tranquilo": "baixa",
    "tranquila": "baixa",
    "quando der": "baixa",
    "quando possível": "baixa",
    "quando possivel": "baixa",
    "sem pressa": "baixa",
    "low": "baixa",
    "3": "baixa",
}

# Day names (Portuguese)
WEEKDAYS_PT = {
    "segunda": 0,
    "segunda-feira": 0,
    "terca": 1,
    "terça": 1,
    "terça-feira": 1,
    "terca-feira": 1,
    "quarta": 2,
    "quarta-feira": 2,
    "quinta": 3,
    "quinta-feira": 3,
    "sexta": 4,
    "sexta-feira": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}

# Relative date keywords
RELATIVE_DATES = {
    "hoje": 0,
    "amanhã": 1,
    "amanha": 1,
    "depois de amanhã": 2,
    "depois de amanha": 2,
    "daqui a 2 dias": 2,
    "daqui a 3 dias": 3,
    "daqui a uma semana": 7,
    "semana que vem": 7,
    "próxima semana": 7,
    "proxima semana": 7,
    "próximo mês": 30,
    "proximo mês": 30,
    "proximo mes": 30,
    "próximo mes": 30,
}


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class NormalizationResult:
    """Result of slot normalization"""
    success: bool
    value: Any
    error: Optional[str] = None
    original: Optional[str] = None

    def __repr__(self) -> str:
        if self.success:
            return f"NormalizationResult(success=True, value={self.value})"
        else:
            return f"NormalizationResult(success=False, error='{self.error}')"


# ==============================================================================
# SLOT NORMALIZER CLASS
# ==============================================================================

class SlotNormalizer:
    """
    Comprehensive slot normalization system.

    Handles all slot types defined in intents_schema.yaml:
    - indices (list[int]): ranges, commas, spaces
    - dates: relative and absolute
    - projects: fuzzy matching
    - priorities: variation mapping
    - text: basic cleanup
    """

    def __init__(self, known_projects: Optional[List[str]] = None):
        """
        Initialize slot normalizer.

        Args:
            known_projects: List of known project names (defaults to KNOWN_PROJECTS)
        """
        self.known_projects = known_projects or KNOWN_PROJECTS
        logger.info(f"SlotNormalizer initialized with {len(self.known_projects)} known projects")

    # ==========================================================================
    # INDICES NORMALIZATION
    # ==========================================================================

    def normalize_indices(self, value: str) -> NormalizationResult:
        """
        Normalize task indices from various formats to list of integers.

        Supports:
        - Single: "1" → [1]
        - Comma-separated: "1, 2, 3" → [1, 2, 3]
        - Space-separated: "1 2 3" → [1, 2, 3]
        - Ranges: "1-3" → [1, 2, 3]
        - Mixed: "1, 3-5, 7" → [1, 3, 4, 5, 7]

        Args:
            value: String containing indices

        Returns:
            NormalizationResult with list of integers or error

        Examples:
            >>> normalizer.normalize_indices("1")
            NormalizationResult(success=True, value=[1])

            >>> normalizer.normalize_indices("1, 2, 3")
            NormalizationResult(success=True, value=[1, 2, 3])

            >>> normalizer.normalize_indices("1-3")
            NormalizationResult(success=True, value=[1, 2, 3])

            >>> normalizer.normalize_indices("1, 3-5, 7")
            NormalizationResult(success=True, value=[1, 3, 4, 5, 7])
        """
        if not value:
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=value
            )

        try:
            # Clean up input: remove extra spaces, normalize separators
            cleaned = value.strip()

            # Replace multiple separators with single comma
            cleaned = re.sub(r'[,\s]+', ',', cleaned)

            indices = []
            parts = cleaned.split(',')

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                # Check if it's a range (e.g., "1-3")
                if '-' in part:
                    range_parts = part.split('-')
                    if len(range_parts) != 2:
                        return NormalizationResult(
                            success=False,
                            error=f"Range inválido: '{part}'",
                            original=value
                        )

                    try:
                        start = int(range_parts[0].strip())
                        end = int(range_parts[1].strip())

                        if start > end:
                            return NormalizationResult(
                                success=False,
                                error=f"Range inválido: início ({start}) maior que fim ({end})",
                                original=value
                            )

                        # Add all numbers in range (inclusive)
                        indices.extend(range(start, end + 1))
                    except ValueError:
                        return NormalizationResult(
                            success=False,
                            error=f"Range contém valores não numéricos: '{part}'",
                            original=value
                        )
                else:
                    # Single number
                    try:
                        num = int(part)
                        indices.append(num)
                    except ValueError:
                        return NormalizationResult(
                            success=False,
                            error=f"Valor não numérico: '{part}'",
                            original=value
                        )

            # Remove duplicates and sort
            indices = sorted(list(set(indices)))

            # Validate minimum value (tasks are 1-based)
            if any(idx < 1 for idx in indices):
                return NormalizationResult(
                    success=False,
                    error="Índices devem ser >= 1",
                    original=value
                )

            logger.debug(f"Normalized indices: '{value}' → {indices}")

            return NormalizationResult(
                success=True,
                value=indices,
                original=value
            )

        except Exception as e:
            logger.error(f"Error normalizing indices '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar índices: {str(e)}",
                original=value
            )

    # ==========================================================================
    # DATE NORMALIZATION
    # ==========================================================================

    def normalize_date(self, value: str) -> NormalizationResult:
        """
        Normalize date from relative or absolute format to datetime.

        Supports:
        - Relative: "amanhã", "sexta", "próxima semana"
        - Absolute: "2025-11-15", "15/11/2025"
        - Context: "hoje", "esta semana"

        Args:
            value: String containing date

        Returns:
            NormalizationResult with datetime object or error

        Examples:
            >>> normalizer.normalize_date("amanhã")
            NormalizationResult(success=True, value=datetime(2025, 11, 12))

            >>> normalizer.normalize_date("sexta")
            NormalizationResult(success=True, value=datetime(2025, 11, 15))

            >>> normalizer.normalize_date("2025-11-15")
            NormalizationResult(success=True, value=datetime(2025, 11, 15))
        """
        if not value:
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=value
            )

        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            value_lower = value.lower().strip()

            # 1. Check relative date keywords
            if value_lower in RELATIVE_DATES:
                days_offset = RELATIVE_DATES[value_lower]
                result_date = today + timedelta(days=days_offset)
                logger.debug(f"Normalized relative date: '{value}' → {result_date.date()}")
                return NormalizationResult(
                    success=True,
                    value=result_date,
                    original=value
                )

            # 2. Check weekday names (next occurrence)
            if value_lower in WEEKDAYS_PT:
                target_weekday = WEEKDAYS_PT[value_lower]
                current_weekday = today.weekday()

                # Calculate days until next occurrence
                days_ahead = target_weekday - current_weekday
                if days_ahead <= 0:  # Target day already passed this week
                    days_ahead += 7

                result_date = today + timedelta(days=days_ahead)
                logger.debug(f"Normalized weekday: '{value}' → {result_date.date()}")
                return NormalizationResult(
                    success=True,
                    value=result_date,
                    original=value
                )

            # 3. Try parsing absolute dates
            # Format: YYYY-MM-DD
            try:
                result_date = datetime.strptime(value, "%Y-%m-%d")
                logger.debug(f"Normalized absolute date (YYYY-MM-DD): '{value}' → {result_date.date()}")
                return NormalizationResult(
                    success=True,
                    value=result_date,
                    original=value
                )
            except ValueError:
                pass

            # Format: DD/MM/YYYY
            try:
                result_date = datetime.strptime(value, "%d/%m/%Y")
                logger.debug(f"Normalized absolute date (DD/MM/YYYY): '{value}' → {result_date.date()}")
                return NormalizationResult(
                    success=True,
                    value=result_date,
                    original=value
                )
            except ValueError:
                pass

            # Format: DD-MM-YYYY
            try:
                result_date = datetime.strptime(value, "%d-%m-%Y")
                logger.debug(f"Normalized absolute date (DD-MM-YYYY): '{value}' → {result_date.date()}")
                return NormalizationResult(
                    success=True,
                    value=result_date,
                    original=value
                )
            except ValueError:
                pass

            # 4. If nothing matched, return error
            return NormalizationResult(
                success=False,
                error=f"Data não reconhecida: '{value}'. Use: amanhã, sexta, 2025-11-15, etc.",
                original=value
            )

        except Exception as e:
            logger.error(f"Error normalizing date '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar data: {str(e)}",
                original=value
            )

    # ==========================================================================
    # PROJECT NORMALIZATION
    # ==========================================================================

    def normalize_project(self, value: str) -> NormalizationResult:
        """
        Normalize project name using fuzzy matching.

        Supports:
        - Case-insensitive: "TECH" → "tech"
        - Fuzzy matching: "TEC H" → "tech"
        - Typos: "techh" → "tech"

        Args:
            value: String containing project name

        Returns:
            NormalizationResult with normalized project name or error

        Examples:
            >>> normalizer.normalize_project("TECH")
            NormalizationResult(success=True, value="tech")

            >>> normalizer.normalize_project("TEC H")
            NormalizationResult(success=True, value="tech")

            >>> normalizer.normalize_project("grwth")
            NormalizationResult(success=True, value="growth")
        """
        if not value:
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=value
            )

        try:
            value_clean = value.strip().lower()

            # 1. Exact match (after lowercase)
            if value_clean in self.known_projects:
                logger.debug(f"Exact match for project: '{value}' → '{value_clean}'")
                return NormalizationResult(
                    success=True,
                    value=value_clean,
                    original=value
                )

            # 2. Fuzzy matching
            if HAVE_RAPIDFUZZ:
                result = process.extractOne(
                    value_clean,
                    self.known_projects,
                    scorer=fuzz.ratio
                )
                if result and result[1] >= 70:  # 70% similarity threshold
                    matched_project = result[0]
                    logger.debug(f"Fuzzy match for project: '{value}' → '{matched_project}' (score: {result[1]})")
                    return NormalizationResult(
                        success=True,
                        value=matched_project,
                        original=value
                    )
            else:
                # Fallback: difflib
                best_match = None
                best_score = 0.0
                for project in self.known_projects:
                    score = SequenceMatcher(None, value_clean, project).ratio() * 100
                    if score > best_score:
                        best_score = score
                        best_match = project

                if best_score >= 70:
                    logger.debug(f"Fuzzy match for project: '{value}' → '{best_match}' (score: {best_score:.0f})")
                    return NormalizationResult(
                        success=True,
                        value=best_match,
                        original=value
                    )

            # 3. No match found
            projects_str = ", ".join(self.known_projects)
            return NormalizationResult(
                success=False,
                error=f"Projeto '{value}' não encontrado. Projetos disponíveis: {projects_str}",
                original=value
            )

        except Exception as e:
            logger.error(f"Error normalizing project '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar projeto: {str(e)}",
                original=value
            )

    # ==========================================================================
    # PRIORITY NORMALIZATION
    # ==========================================================================

    def normalize_priority(self, value: str) -> NormalizationResult:
        """
        Normalize priority level using variation mapping.

        Maps variations to canonical values: alta, média, baixa

        Args:
            value: String containing priority

        Returns:
            NormalizationResult with normalized priority or error

        Examples:
            >>> normalizer.normalize_priority("urgente")
            NormalizationResult(success=True, value="alta")

            >>> normalizer.normalize_priority("tranquilo")
            NormalizationResult(success=True, value="baixa")

            >>> normalizer.normalize_priority("normal")
            NormalizationResult(success=True, value="média")
        """
        if not value:
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=value
            )

        try:
            value_clean = value.strip().lower()

            # Check direct mapping
            if value_clean in PRIORITY_MAP:
                canonical = PRIORITY_MAP[value_clean]
                logger.debug(f"Normalized priority: '{value}' → '{canonical}'")
                return NormalizationResult(
                    success=True,
                    value=canonical,
                    original=value
                )

            # If not found, return error with valid options
            return NormalizationResult(
                success=False,
                error=f"Prioridade '{value}' não reconhecida. Use: alta, média ou baixa",
                original=value
            )

        except Exception as e:
            logger.error(f"Error normalizing priority '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar prioridade: {str(e)}",
                original=value
            )

    # ==========================================================================
    # TEXT NORMALIZATION
    # ==========================================================================

    def normalize_text(self, value: str, min_length: int = 1, max_length: int = 500) -> NormalizationResult:
        """
        Normalize text field with basic cleanup and validation.

        Args:
            value: String to normalize
            min_length: Minimum allowed length
            max_length: Maximum allowed length

        Returns:
            NormalizationResult with cleaned text or error

        Examples:
            >>> normalizer.normalize_text("  Revisar dashboard  ")
            NormalizationResult(success=True, value="Revisar dashboard")
        """
        if not value:
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=value
            )

        try:
            # Basic cleanup: strip whitespace, normalize multiple spaces
            cleaned = re.sub(r'\s+', ' ', value.strip())

            # Validate length
            if len(cleaned) < min_length:
                return NormalizationResult(
                    success=False,
                    error=f"Texto muito curto (mínimo {min_length} caracteres)",
                    original=value
                )

            if len(cleaned) > max_length:
                return NormalizationResult(
                    success=False,
                    error=f"Texto muito longo (máximo {max_length} caracteres)",
                    original=value
                )

            logger.debug(f"Normalized text: '{value}' → '{cleaned}'")

            return NormalizationResult(
                success=True,
                value=cleaned,
                original=value
            )

        except Exception as e:
            logger.error(f"Error normalizing text '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar texto: {str(e)}",
                original=value
            )

    # ==========================================================================
    # INTEGER NORMALIZATION
    # ==========================================================================

    def normalize_int(self, value: Union[str, int]) -> NormalizationResult:
        """
        Normalize integer value.

        Args:
            value: String or int to normalize

        Returns:
            NormalizationResult with integer or error

        Examples:
            >>> normalizer.normalize_int("5")
            NormalizationResult(success=True, value=5)

            >>> normalizer.normalize_int(5)
            NormalizationResult(success=True, value=5)
        """
        if value is None or value == "":
            return NormalizationResult(
                success=False,
                error="Valor vazio",
                original=str(value)
            )

        try:
            # If already int, return it
            if isinstance(value, int):
                return NormalizationResult(
                    success=True,
                    value=value,
                    original=str(value)
                )

            # Try to parse string
            cleaned = str(value).strip()
            num = int(cleaned)

            logger.debug(f"Normalized int: '{value}' → {num}")

            return NormalizationResult(
                success=True,
                value=num,
                original=str(value)
            )

        except ValueError:
            return NormalizationResult(
                success=False,
                error=f"Valor não numérico: '{value}'",
                original=str(value)
            )
        except Exception as e:
            logger.error(f"Error normalizing int '{value}': {e}")
            return NormalizationResult(
                success=False,
                error=f"Erro ao processar número: {str(e)}",
                original=str(value)
            )


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

# Global normalizer instance
_normalizer = None


def get_normalizer() -> SlotNormalizer:
    """Get or create global normalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = SlotNormalizer()
    return _normalizer


# ==============================================================================
# MAIN - FOR TESTING
# ==============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    print("=" * 80)
    print("TESTING SLOT NORMALIZERS")
    print("=" * 80)
    print()

    normalizer = SlotNormalizer()

    # Test indices
    print("--- INDICES ---")
    test_indices = ["1", "1,2,3", "1-3", "1 2 3", "1, 3-5, 7", "2,4-6,8"]
    for test in test_indices:
        result = normalizer.normalize_indices(test)
        print(f"'{test}' → {result}")
    print()

    # Test dates
    print("--- DATES ---")
    test_dates = ["amanhã", "sexta", "próxima semana", "2025-11-15", "15/11/2025"]
    for test in test_dates:
        result = normalizer.normalize_date(test)
        if result.success:
            print(f"'{test}' → {result.value.date()}")
        else:
            print(f"'{test}' → ERROR: {result.error}")
    print()

    # Test projects
    print("--- PROJECTS ---")
    test_projects = ["tech", "TECH", "TEC H", "techh", "growth", "grwth", "ops", "invalid"]
    for test in test_projects:
        result = normalizer.normalize_project(test)
        print(f"'{test}' → {result}")
    print()

    # Test priorities
    print("--- PRIORITIES ---")
    test_priorities = ["alta", "urgente", "média", "normal", "baixa", "tranquilo", "asap"]
    for test in test_priorities:
        result = normalizer.normalize_priority(test)
        print(f"'{test}' → {result}")
    print()

    print("=" * 80)
