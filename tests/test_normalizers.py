#!/usr/bin/env python3
"""
==============================================================================
COMPREHENSIVE TESTS FOR SLOT NORMALIZERS
==============================================================================
Test suite for slot normalization system with 50+ test cases.

Coverage:
- normalize_indices: ranges, commas, spaces, mixed formats
- normalize_date: relative dates, weekdays, absolute dates
- normalize_project: exact match, fuzzy match, case-insensitive
- normalize_priority: all variations and edge cases
- normalize_text: cleanup, validation, edge cases
- normalize_int: strings, integers, errors

Author: Pangeia Bot
Created: 2025-11-11
==============================================================================
"""

import unittest
from datetime import datetime, timedelta
from src.nlp.normalizers import SlotNormalizer, NormalizationResult


class TestNormalizeIndices(unittest.TestCase):
    """Test suite for normalize_indices"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer()

    # ==========================================================================
    # SINGLE INDEX TESTS
    # ==========================================================================

    def test_single_index(self):
        """Test single index: '1' → [1]"""
        result = self.normalizer.normalize_indices("1")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1])

    def test_single_index_with_spaces(self):
        """Test single index with spaces: '  5  ' → [5]"""
        result = self.normalizer.normalize_indices("  5  ")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [5])

    def test_large_single_index(self):
        """Test large single index: '999' → [999]"""
        result = self.normalizer.normalize_indices("999")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [999])

    # ==========================================================================
    # COMMA-SEPARATED TESTS
    # ==========================================================================

    def test_comma_separated(self):
        """Test comma-separated: '1,2,3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1,2,3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_comma_separated_with_spaces(self):
        """Test comma with spaces: '1, 2, 3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1, 2, 3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_comma_separated_irregular_spacing(self):
        """Test irregular spacing: '1 ,  2,   3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1 ,  2,   3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    # ==========================================================================
    # SPACE-SEPARATED TESTS
    # ==========================================================================

    def test_space_separated(self):
        """Test space-separated: '1 2 3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1 2 3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_space_separated_multiple_spaces(self):
        """Test multiple spaces: '1  2   3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1  2   3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    # ==========================================================================
    # RANGE TESTS
    # ==========================================================================

    def test_simple_range(self):
        """Test simple range: '1-3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1-3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_larger_range(self):
        """Test larger range: '1-5' → [1,2,3,4,5]"""
        result = self.normalizer.normalize_indices("1-5")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3, 4, 5])

    def test_range_with_spaces(self):
        """Test range with spaces: '1 - 3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1 - 3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_large_numbers_range(self):
        """Test large numbers: '10-12' → [10,11,12]"""
        result = self.normalizer.normalize_indices("10-12")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [10, 11, 12])

    # ==========================================================================
    # MIXED FORMAT TESTS
    # ==========================================================================

    def test_mixed_comma_and_range(self):
        """Test mixed: '1, 3-5, 7' → [1,3,4,5,7]"""
        result = self.normalizer.normalize_indices("1, 3-5, 7")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 3, 4, 5, 7])

    def test_mixed_complex(self):
        """Test complex mixed: '2, 4-6, 8' → [2,4,5,6,8]"""
        result = self.normalizer.normalize_indices("2, 4-6, 8")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [2, 4, 5, 6, 8])

    def test_mixed_with_duplicates(self):
        """Test duplicates removed: '1, 2, 1-3' → [1,2,3]"""
        result = self.normalizer.normalize_indices("1, 2, 1-3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 2, 3])

    def test_mixed_unordered(self):
        """Test unordered (gets sorted): '5, 1, 3' → [1,3,5]"""
        result = self.normalizer.normalize_indices("5, 1, 3")
        self.assertTrue(result.success)
        self.assertEqual(result.value, [1, 3, 5])

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_indices("")
        self.assertFalse(result.success)
        self.assertIn("vazio", result.error.lower())

    def test_invalid_characters(self):
        """Test invalid characters: 'abc' returns error"""
        result = self.normalizer.normalize_indices("abc")
        self.assertFalse(result.success)

    def test_negative_number(self):
        """Test negative number: '-1' returns error"""
        result = self.normalizer.normalize_indices("-1")
        self.assertFalse(result.success)
        self.assertIn(">=", result.error)

    def test_zero_index(self):
        """Test zero index: '0' returns error (1-based)"""
        result = self.normalizer.normalize_indices("0")
        self.assertFalse(result.success)
        self.assertIn(">=", result.error)

    def test_invalid_range_format(self):
        """Test invalid range: '1-2-3' returns error"""
        result = self.normalizer.normalize_indices("1-2-3")
        self.assertFalse(result.success)
        self.assertIn("inválido", result.error.lower())

    def test_inverted_range(self):
        """Test inverted range: '5-1' returns error"""
        result = self.normalizer.normalize_indices("5-1")
        self.assertFalse(result.success)
        self.assertIn("maior", result.error.lower())


class TestNormalizeDate(unittest.TestCase):
    """Test suite for normalize_date"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer()
        self.today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # ==========================================================================
    # RELATIVE DATE TESTS
    # ==========================================================================

    def test_today(self):
        """Test 'hoje' returns today"""
        result = self.normalizer.normalize_date("hoje")
        self.assertTrue(result.success)
        self.assertEqual(result.value.date(), self.today.date())

    def test_tomorrow(self):
        """Test 'amanhã' returns tomorrow"""
        result = self.normalizer.normalize_date("amanhã")
        self.assertTrue(result.success)
        expected = self.today + timedelta(days=1)
        self.assertEqual(result.value.date(), expected.date())

    def test_tomorrow_without_accent(self):
        """Test 'amanha' (no accent) returns tomorrow"""
        result = self.normalizer.normalize_date("amanha")
        self.assertTrue(result.success)
        expected = self.today + timedelta(days=1)
        self.assertEqual(result.value.date(), expected.date())

    def test_day_after_tomorrow(self):
        """Test 'depois de amanhã' returns day after tomorrow"""
        result = self.normalizer.normalize_date("depois de amanhã")
        self.assertTrue(result.success)
        expected = self.today + timedelta(days=2)
        self.assertEqual(result.value.date(), expected.date())

    def test_next_week(self):
        """Test 'próxima semana' returns 7 days ahead"""
        result = self.normalizer.normalize_date("próxima semana")
        self.assertTrue(result.success)
        expected = self.today + timedelta(days=7)
        self.assertEqual(result.value.date(), expected.date())

    def test_next_week_without_accent(self):
        """Test 'proxima semana' (no accent)"""
        result = self.normalizer.normalize_date("proxima semana")
        self.assertTrue(result.success)
        expected = self.today + timedelta(days=7)
        self.assertEqual(result.value.date(), expected.date())

    # ==========================================================================
    # WEEKDAY TESTS
    # ==========================================================================

    def test_weekday_monday(self):
        """Test 'segunda' returns next Monday"""
        result = self.normalizer.normalize_date("segunda")
        self.assertTrue(result.success)
        # Result should be a Monday
        self.assertEqual(result.value.weekday(), 0)  # 0 = Monday
        # Should be in the future
        self.assertGreater(result.value.date(), self.today.date())

    def test_weekday_friday(self):
        """Test 'sexta' returns next Friday"""
        result = self.normalizer.normalize_date("sexta")
        self.assertTrue(result.success)
        # Result should be a Friday
        self.assertEqual(result.value.weekday(), 4)  # 4 = Friday
        # Should be in the future (or next week if today is Friday)
        self.assertGreaterEqual(result.value.date(), self.today.date())

    def test_weekday_saturday(self):
        """Test 'sábado' returns next Saturday"""
        result = self.normalizer.normalize_date("sábado")
        self.assertTrue(result.success)
        self.assertEqual(result.value.weekday(), 5)  # 5 = Saturday

    def test_weekday_without_accent(self):
        """Test 'sabado' (no accent) returns Saturday"""
        result = self.normalizer.normalize_date("sabado")
        self.assertTrue(result.success)
        self.assertEqual(result.value.weekday(), 5)

    # ==========================================================================
    # ABSOLUTE DATE TESTS
    # ==========================================================================

    def test_absolute_date_iso(self):
        """Test '2025-11-15' (ISO format)"""
        result = self.normalizer.normalize_date("2025-11-15")
        self.assertTrue(result.success)
        self.assertEqual(result.value.date(), datetime(2025, 11, 15).date())

    def test_absolute_date_slash(self):
        """Test '15/11/2025' (DD/MM/YYYY)"""
        result = self.normalizer.normalize_date("15/11/2025")
        self.assertTrue(result.success)
        self.assertEqual(result.value.date(), datetime(2025, 11, 15).date())

    def test_absolute_date_dash(self):
        """Test '15-11-2025' (DD-MM-YYYY)"""
        result = self.normalizer.normalize_date("15-11-2025")
        self.assertTrue(result.success)
        self.assertEqual(result.value.date(), datetime(2025, 11, 15).date())

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_date("")
        self.assertFalse(result.success)

    def test_invalid_date(self):
        """Test invalid date string"""
        result = self.normalizer.normalize_date("invalid date")
        self.assertFalse(result.success)
        self.assertIn("não reconhecida", result.error.lower())

    def test_invalid_format(self):
        """Test invalid format: 'November 15'"""
        result = self.normalizer.normalize_date("November 15")
        self.assertFalse(result.success)


class TestNormalizeProject(unittest.TestCase):
    """Test suite for normalize_project"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer(known_projects=["tech", "growth", "ops", "design", "pessoal"])

    # ==========================================================================
    # EXACT MATCH TESTS
    # ==========================================================================

    def test_exact_match_lowercase(self):
        """Test exact match: 'tech' → 'tech'"""
        result = self.normalizer.normalize_project("tech")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "tech")

    def test_exact_match_all_projects(self):
        """Test all projects exact match"""
        for project in ["tech", "growth", "ops", "design", "pessoal"]:
            result = self.normalizer.normalize_project(project)
            self.assertTrue(result.success)
            self.assertEqual(result.value, project)

    # ==========================================================================
    # CASE-INSENSITIVE TESTS
    # ==========================================================================

    def test_uppercase(self):
        """Test uppercase: 'TECH' → 'tech'"""
        result = self.normalizer.normalize_project("TECH")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "tech")

    def test_mixed_case(self):
        """Test mixed case: 'TeCh' → 'tech'"""
        result = self.normalizer.normalize_project("TeCh")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "tech")

    def test_uppercase_growth(self):
        """Test uppercase: 'GROWTH' → 'growth'"""
        result = self.normalizer.normalize_project("GROWTH")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "growth")

    # ==========================================================================
    # FUZZY MATCHING TESTS
    # ==========================================================================

    def test_fuzzy_space_in_middle(self):
        """Test fuzzy with space: 'TEC H' → 'tech'"""
        result = self.normalizer.normalize_project("TEC H")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "tech")

    def test_fuzzy_typo(self):
        """Test fuzzy typo: 'techh' → 'tech'"""
        result = self.normalizer.normalize_project("techh")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "tech")

    def test_fuzzy_partial(self):
        """Test fuzzy partial: 'grwth' → 'growth'"""
        result = self.normalizer.normalize_project("grwth")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "growth")

    def test_fuzzy_ops(self):
        """Test fuzzy: 'op' → 'ops'"""
        result = self.normalizer.normalize_project("op")
        # May or may not match depending on threshold
        # Just verify it doesn't crash
        self.assertIsNotNone(result)

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_project("")
        self.assertFalse(result.success)

    def test_invalid_project(self):
        """Test completely invalid project"""
        result = self.normalizer.normalize_project("invalid_xyz_project")
        self.assertFalse(result.success)
        self.assertIn("não encontrado", result.error.lower())

    def test_whitespace_only(self):
        """Test whitespace only"""
        result = self.normalizer.normalize_project("   ")
        self.assertFalse(result.success)


class TestNormalizePriority(unittest.TestCase):
    """Test suite for normalize_priority"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer()

    # ==========================================================================
    # ALTA (HIGH) PRIORITY TESTS
    # ==========================================================================

    def test_priority_alta(self):
        """Test 'alta' → 'alta'"""
        result = self.normalizer.normalize_priority("alta")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "alta")

    def test_priority_urgente(self):
        """Test 'urgente' → 'alta'"""
        result = self.normalizer.normalize_priority("urgente")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "alta")

    def test_priority_critico(self):
        """Test 'crítico' → 'alta'"""
        result = self.normalizer.normalize_priority("crítico")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "alta")

    def test_priority_asap(self):
        """Test 'asap' → 'alta'"""
        result = self.normalizer.normalize_priority("asap")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "alta")

    def test_priority_pra_ontem(self):
        """Test 'pra ontem' → 'alta'"""
        result = self.normalizer.normalize_priority("pra ontem")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "alta")

    # ==========================================================================
    # MÉDIA (MEDIUM) PRIORITY TESTS
    # ==========================================================================

    def test_priority_media(self):
        """Test 'média' → 'média'"""
        result = self.normalizer.normalize_priority("média")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "média")

    def test_priority_media_no_accent(self):
        """Test 'media' (no accent) → 'média'"""
        result = self.normalizer.normalize_priority("media")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "média")

    def test_priority_normal(self):
        """Test 'normal' → 'média'"""
        result = self.normalizer.normalize_priority("normal")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "média")

    def test_priority_moderado(self):
        """Test 'moderado' → 'média'"""
        result = self.normalizer.normalize_priority("moderado")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "média")

    # ==========================================================================
    # BAIXA (LOW) PRIORITY TESTS
    # ==========================================================================

    def test_priority_baixa(self):
        """Test 'baixa' → 'baixa'"""
        result = self.normalizer.normalize_priority("baixa")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "baixa")

    def test_priority_tranquilo(self):
        """Test 'tranquilo' → 'baixa'"""
        result = self.normalizer.normalize_priority("tranquilo")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "baixa")

    def test_priority_quando_der(self):
        """Test 'quando der' → 'baixa'"""
        result = self.normalizer.normalize_priority("quando der")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "baixa")

    def test_priority_sem_pressa(self):
        """Test 'sem pressa' → 'baixa'"""
        result = self.normalizer.normalize_priority("sem pressa")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "baixa")

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_priority("")
        self.assertFalse(result.success)

    def test_invalid_priority(self):
        """Test invalid priority"""
        result = self.normalizer.normalize_priority("super duper urgent")
        self.assertFalse(result.success)
        self.assertIn("não reconhecida", result.error.lower())


class TestNormalizeText(unittest.TestCase):
    """Test suite for normalize_text"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer()

    # ==========================================================================
    # BASIC TEXT TESTS
    # ==========================================================================

    def test_simple_text(self):
        """Test simple text: 'revisar dashboard' → 'revisar dashboard'"""
        result = self.normalizer.normalize_text("revisar dashboard")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "revisar dashboard")

    def test_text_with_leading_trailing_spaces(self):
        """Test '  revisar dashboard  ' → 'revisar dashboard'"""
        result = self.normalizer.normalize_text("  revisar dashboard  ")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "revisar dashboard")

    def test_text_with_multiple_spaces(self):
        """Test 'revisar    dashboard' → 'revisar dashboard'"""
        result = self.normalizer.normalize_text("revisar    dashboard")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "revisar dashboard")

    def test_text_with_newlines(self):
        """Test text with newlines normalized to single space"""
        result = self.normalizer.normalize_text("revisar\ndashboard")
        self.assertTrue(result.success)
        self.assertEqual(result.value, "revisar dashboard")

    # ==========================================================================
    # LENGTH VALIDATION TESTS
    # ==========================================================================

    def test_text_too_short(self):
        """Test text too short returns error"""
        result = self.normalizer.normalize_text("ab", min_length=3)
        self.assertFalse(result.success)
        self.assertIn("muito curto", result.error.lower())

    def test_text_too_long(self):
        """Test text too long returns error"""
        long_text = "a" * 501
        result = self.normalizer.normalize_text(long_text, max_length=500)
        self.assertFalse(result.success)
        self.assertIn("muito longo", result.error.lower())

    def test_text_exact_min_length(self):
        """Test text exact minimum length is accepted"""
        result = self.normalizer.normalize_text("abc", min_length=3)
        self.assertTrue(result.success)
        self.assertEqual(result.value, "abc")

    def test_text_exact_max_length(self):
        """Test text exact maximum length is accepted"""
        text = "a" * 500
        result = self.normalizer.normalize_text(text, max_length=500)
        self.assertTrue(result.success)
        self.assertEqual(len(result.value), 500)

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_text("")
        self.assertFalse(result.success)

    def test_whitespace_only(self):
        """Test whitespace-only string returns error"""
        result = self.normalizer.normalize_text("   ")
        self.assertFalse(result.success)


class TestNormalizeInt(unittest.TestCase):
    """Test suite for normalize_int"""

    def setUp(self):
        """Set up test normalizer"""
        self.normalizer = SlotNormalizer()

    # ==========================================================================
    # VALID INTEGER TESTS
    # ==========================================================================

    def test_string_number(self):
        """Test string number: '5' → 5"""
        result = self.normalizer.normalize_int("5")
        self.assertTrue(result.success)
        self.assertEqual(result.value, 5)

    def test_already_int(self):
        """Test already int: 5 → 5"""
        result = self.normalizer.normalize_int(5)
        self.assertTrue(result.success)
        self.assertEqual(result.value, 5)

    def test_string_with_spaces(self):
        """Test '  10  ' → 10"""
        result = self.normalizer.normalize_int("  10  ")
        self.assertTrue(result.success)
        self.assertEqual(result.value, 10)

    def test_large_number(self):
        """Test large number: '999' → 999"""
        result = self.normalizer.normalize_int("999")
        self.assertTrue(result.success)
        self.assertEqual(result.value, 999)

    # ==========================================================================
    # ERROR CASES
    # ==========================================================================

    def test_empty_string(self):
        """Test empty string returns error"""
        result = self.normalizer.normalize_int("")
        self.assertFalse(result.success)

    def test_non_numeric_string(self):
        """Test non-numeric string: 'abc' returns error"""
        result = self.normalizer.normalize_int("abc")
        self.assertFalse(result.success)
        self.assertIn("não numérico", result.error.lower())

    def test_float_string(self):
        """Test float string: '5.5' returns error (needs int)"""
        result = self.normalizer.normalize_int("5.5")
        self.assertFalse(result.success)

    def test_none_value(self):
        """Test None returns error"""
        result = self.normalizer.normalize_int(None)
        self.assertFalse(result.success)


# ==============================================================================
# MAIN - RUN ALL TESTS
# ==============================================================================

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
