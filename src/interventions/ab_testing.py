"""
A/B Testing Engine - Sistema de Testes A/B para Nudges.

Sistema que testa diferentes variações de nudges para descobrir
quais mensagens são mais efetivas para cada perfil de pessoa.
"""

import logging
import random
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

from .nudge_engine import Nudge, NudgeType

logger = logging.getLogger(__name__)


@dataclass
class NudgeVariant:
    """Variante de um nudge para A/B testing."""
    variant_id: str
    message: str
    nudge_type: NudgeType
    impressions: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0


@dataclass
class ABTest:
    """Representa um teste A/B."""
    test_id: str
    test_name: str
    nudge_type: NudgeType
    variants: List[NudgeVariant]
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    winner: Optional[str] = None  # variant_id vencedor
    confidence_level: float = 0.0  # 0-100


class ABTestingEngine:
    """
    Motor de A/B testing para nudges.

    Permite:
    - Criar testes com múltiplas variantes
    - Distribuir variantes aleatoriamente
    - Rastrear impressões e conversões
    - Calcular significância estatística
    - Determinar vencedor
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Inicializa motor de A/B testing.

        Args:
            storage_path: Caminho para armazenar dados de testes
        """
        if storage_path is None:
            storage_path = Path.home() / ".pangeia" / "ab_tests.json"
        else:
            storage_path = Path(storage_path)

        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.active_tests: Dict[str, ABTest] = {}
        self.test_assignments: Dict[str, Dict[str, str]] = {}  # {person_name: {test_id: variant_id}}

        self._load_tests()
        logger.info("ABTestingEngine inicializado")

    def create_test(
        self,
        test_name: str,
        nudge_type: NudgeType,
        variant_messages: List[str],
        duration_days: int = 14
    ) -> str:
        """
        Cria novo teste A/B.

        Args:
            test_name: Nome descritivo do teste
            nudge_type: Tipo de nudge sendo testado
            variant_messages: Lista de mensagens variantes (2-4)
            duration_days: Duração do teste em dias

        Returns:
            test_id do teste criado
        """
        if len(variant_messages) < 2:
            raise ValueError("Teste A/B precisa de pelo menos 2 variantes")

        if len(variant_messages) > 4:
            raise ValueError("Máximo de 4 variantes por teste")

        # Gerar test_id
        test_id = f"{nudge_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Criar variantes
        variants = []
        for idx, message in enumerate(variant_messages):
            variant = NudgeVariant(
                variant_id=f"{test_id}_v{idx + 1}",
                message=message,
                nudge_type=nudge_type
            )
            variants.append(variant)

        # Criar teste
        test = ABTest(
            test_id=test_id,
            test_name=test_name,
            nudge_type=nudge_type,
            variants=variants,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days)
        )

        self.active_tests[test_id] = test
        self._save_tests()

        logger.info(
            f"Teste A/B criado: {test_name} ({len(variants)} variantes, "
            f"{duration_days} dias)"
        )

        return test_id

    def get_variant_for_person(
        self,
        person_name: str,
        nudge_type: NudgeType
    ) -> Optional[Tuple[str, str]]:
        """
        Retorna variante de nudge para pessoa (assignment consistente).

        Args:
            person_name: Nome da pessoa
            nudge_type: Tipo de nudge

        Returns:
            Tuple (test_id, message) ou None se não houver teste ativo
        """
        # Buscar teste ativo para este tipo de nudge
        active_test = self._get_active_test_for_type(nudge_type)

        if not active_test:
            return None

        # Verificar se pessoa já tem assignment
        if person_name in self.test_assignments:
            if active_test.test_id in self.test_assignments[person_name]:
                variant_id = self.test_assignments[person_name][active_test.test_id]
                variant = self._get_variant(active_test, variant_id)
                if variant:
                    return (active_test.test_id, variant.message)

        # Atribuir variante aleatória (mas consistente)
        variant = self._assign_variant(person_name, active_test)

        if person_name not in self.test_assignments:
            self.test_assignments[person_name] = {}

        self.test_assignments[person_name][active_test.test_id] = variant.variant_id

        return (active_test.test_id, variant.message)

    def record_impression(self, test_id: str, variant_id: str) -> None:
        """
        Registra impressão de uma variante.

        Args:
            test_id: ID do teste
            variant_id: ID da variante mostrada
        """
        if test_id not in self.active_tests:
            logger.warning(f"Teste {test_id} não encontrado")
            return

        test = self.active_tests[test_id]
        variant = self._get_variant(test, variant_id)

        if variant:
            variant.impressions += 1
            self._save_tests()
            logger.debug(f"Impressão registrada: {test_id} / {variant_id}")

    def record_conversion(self, test_id: str, variant_id: str) -> None:
        """
        Registra conversão de uma variante.

        Args:
            test_id: ID do teste
            variant_id: ID da variante que converteu
        """
        if test_id not in self.active_tests:
            logger.warning(f"Teste {test_id} não encontrado")
            return

        test = self.active_tests[test_id]
        variant = self._get_variant(test, variant_id)

        if variant:
            variant.conversions += 1

            # Atualizar conversion rate
            if variant.impressions > 0:
                variant.conversion_rate = variant.conversions / variant.impressions

            self._save_tests()
            logger.info(
                f"Conversão registrada: {test_id} / {variant_id} "
                f"({variant.conversion_rate * 100:.1f}%)"
            )

            # Verificar se teste pode ser encerrado
            self._check_test_completion(test)

    def _assign_variant(self, person_name: str, test: ABTest) -> NudgeVariant:
        """Atribui variante aleatória mas determinística para pessoa."""
        # Usar hash do nome para determinismo
        person_hash = hash(person_name + test.test_id)
        variant_idx = person_hash % len(test.variants)

        return test.variants[variant_idx]

    def _get_variant(self, test: ABTest, variant_id: str) -> Optional[NudgeVariant]:
        """Busca variante por ID."""
        for variant in test.variants:
            if variant.variant_id == variant_id:
                return variant
        return None

    def _get_active_test_for_type(self, nudge_type: NudgeType) -> Optional[ABTest]:
        """Retorna teste ativo para tipo de nudge."""
        for test in self.active_tests.values():
            if test.nudge_type == nudge_type and test.is_active:
                # Verificar se não expirou
                if test.end_date and datetime.now() > test.end_date:
                    test.is_active = False
                    self._save_tests()
                    continue

                return test

        return None

    def _check_test_completion(self, test: ABTest) -> None:
        """
        Verifica se teste tem dados suficientes para conclusão.

        Critérios:
        - Mínimo 30 impressões por variante
        - Diferença estatisticamente significante (p < 0.05)
        """
        # Verificar mínimo de impressões
        min_impressions = 30
        all_variants_have_data = all(
            v.impressions >= min_impressions
            for v in test.variants
        )

        if not all_variants_have_data:
            return

        # Calcular significância estatística
        confidence, winner_id = self._calculate_statistical_significance(test)

        if confidence >= 95.0:  # 95% de confiança
            test.winner = winner_id
            test.confidence_level = confidence
            test.is_active = False

            winner = self._get_variant(test, winner_id)

            logger.info(
                f"🎯 Teste A/B concluído: {test.test_name}\n"
                f"   Vencedor: {winner_id}\n"
                f"   Confiança: {confidence:.1f}%\n"
                f"   Conversion rate: {winner.conversion_rate * 100:.1f}%"
            )

            self._save_tests()

    def _calculate_statistical_significance(
        self,
        test: ABTest
    ) -> Tuple[float, Optional[str]]:
        """
        Calcula significância estatística entre variantes.

        Returns:
            Tuple (confidence_level, winner_variant_id)
        """
        if len(test.variants) != 2:
            # Para simplificar, apenas A/B (não A/B/C/D)
            # Retornar melhor variante sem cálculo estatístico
            best = max(test.variants, key=lambda v: v.conversion_rate)
            return (0.0, best.variant_id)

        # A/B test simples
        variant_a, variant_b = test.variants

        # Verificar se ambas têm dados
        if variant_a.impressions == 0 or variant_b.impressions == 0:
            return (0.0, None)

        # Calcular Z-score (simplified)
        p_a = variant_a.conversion_rate
        p_b = variant_b.conversion_rate
        n_a = variant_a.impressions
        n_b = variant_b.impressions

        # Pooled probability
        p_pool = (variant_a.conversions + variant_b.conversions) / (n_a + n_b)

        # Standard error
        se = (p_pool * (1 - p_pool) * (1/n_a + 1/n_b)) ** 0.5

        if se == 0:
            return (0.0, None)

        # Z-score
        z = abs(p_a - p_b) / se

        # Converter Z para confiança (aproximado)
        # z = 1.96 → 95% confiança
        # z = 2.58 → 99% confiança
        if z >= 2.58:
            confidence = 99.0
        elif z >= 1.96:
            confidence = 95.0
        elif z >= 1.64:
            confidence = 90.0
        else:
            confidence = 50.0 + (z / 1.96) * 45  # Aproximação linear

        # Determinar vencedor
        winner = variant_a if p_a > p_b else variant_b

        return (confidence, winner.variant_id)

    def get_test_results(self, test_id: str) -> Optional[Dict]:
        """
        Retorna resultados de um teste.

        Args:
            test_id: ID do teste

        Returns:
            Dict com resultados ou None se não encontrado
        """
        if test_id not in self.active_tests:
            return None

        test = self.active_tests[test_id]

        return {
            "test_id": test.test_id,
            "test_name": test.test_name,
            "nudge_type": test.nudge_type.value,
            "is_active": test.is_active,
            "start_date": test.start_date.isoformat(),
            "end_date": test.end_date.isoformat() if test.end_date else None,
            "winner": test.winner,
            "confidence": test.confidence_level,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "message": v.message,
                    "impressions": v.impressions,
                    "conversions": v.conversions,
                    "conversion_rate": f"{v.conversion_rate * 100:.1f}%"
                }
                for v in test.variants
            ]
        }

    def list_active_tests(self) -> List[Dict]:
        """Lista todos os testes ativos."""
        return [
            self.get_test_results(test_id)
            for test_id, test in self.active_tests.items()
            if test.is_active
        ]

    def _load_tests(self) -> None:
        """Carrega testes do disco."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reconstruir testes
            for test_data in data.get("tests", []):
                variants = [
                    NudgeVariant(
                        variant_id=v["variant_id"],
                        message=v["message"],
                        nudge_type=NudgeType(v["nudge_type"]),
                        impressions=v["impressions"],
                        conversions=v["conversions"],
                        conversion_rate=v["conversion_rate"]
                    )
                    for v in test_data["variants"]
                ]

                test = ABTest(
                    test_id=test_data["test_id"],
                    test_name=test_data["test_name"],
                    nudge_type=NudgeType(test_data["nudge_type"]),
                    variants=variants,
                    start_date=datetime.fromisoformat(test_data["start_date"]),
                    end_date=datetime.fromisoformat(test_data["end_date"]) if test_data.get("end_date") else None,
                    is_active=test_data["is_active"],
                    winner=test_data.get("winner"),
                    confidence_level=test_data.get("confidence_level", 0.0)
                )

                self.active_tests[test.test_id] = test

            # Carregar assignments
            self.test_assignments = data.get("assignments", {})

            logger.info(f"Carregados {len(self.active_tests)} testes A/B")

        except Exception as e:
            logger.error(f"Erro ao carregar testes A/B: {e}")

    def _save_tests(self) -> None:
        """Salva testes no disco."""
        try:
            data = {
                "tests": [
                    {
                        "test_id": test.test_id,
                        "test_name": test.test_name,
                        "nudge_type": test.nudge_type.value,
                        "start_date": test.start_date.isoformat(),
                        "end_date": test.end_date.isoformat() if test.end_date else None,
                        "is_active": test.is_active,
                        "winner": test.winner,
                        "confidence_level": test.confidence_level,
                        "variants": [
                            {
                                "variant_id": v.variant_id,
                                "message": v.message,
                                "nudge_type": v.nudge_type.value,
                                "impressions": v.impressions,
                                "conversions": v.conversions,
                                "conversion_rate": v.conversion_rate
                            }
                            for v in test.variants
                        ]
                    }
                    for test in self.active_tests.values()
                ],
                "assignments": self.test_assignments
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Testes A/B salvos: {len(self.active_tests)} testes")

        except Exception as e:
            logger.error(f"Erro ao salvar testes A/B: {e}")
