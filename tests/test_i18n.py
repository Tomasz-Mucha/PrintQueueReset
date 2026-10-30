"""Tests for Print Queue Reset i18n.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import i18n


class I18nTests(unittest.TestCase):
    def test_same_keys_in_all_languages(self) -> None:
        en = set(i18n.EN)
        self.assertEqual(en, set(i18n.PL))
        self.assertEqual(en, set(i18n.SV))
        self.assertTrue(en)

    def test_strings_do_not_name_the_old_vendor(self) -> None:
        for table in (i18n.EN, i18n.PL, i18n.SV):
            blob = "\n".join(table.values()).lower()
            self.assertNotIn("fly-tech", blob)
            self.assertNotIn("flytech", blob)
            self.assertNotIn("gpl", blob)
            self.assertIn("print queue reset", blob)

    def test_language_from_tag(self) -> None:
        self.assertEqual(i18n.language_from_tag("sv-SE"), "sv")
        self.assertEqual(i18n.language_from_tag("pl_PL"), "pl")
        self.assertEqual(i18n.language_from_tag("en-GB"), "en")
        self.assertIsNone(i18n.language_from_tag("de-DE"))
        self.assertIsNone(i18n.language_from_tag(""))

    def test_language_from_langid(self) -> None:
        self.assertEqual(i18n.language_from_langid(0x0415), "pl")
        self.assertEqual(i18n.language_from_langid(0x041D), "sv")
        self.assertEqual(i18n.language_from_langid(0x0409), "en")
        self.assertIsNone(i18n.language_from_langid(0x0407))  # German

    def test_swedish_and_english_strings(self) -> None:
        i18n.init("sv")
        self.assertEqual(i18n.t("pause"), "Pausa")
        self.assertEqual(i18n.t("reset_queue"), "Återställ utskriftskön")
        i18n.init("en")
        self.assertEqual(i18n.t("pause"), "Pause")
        self.assertEqual(i18n.t("reset_queue"), "Reset print queue")
        i18n.init("pl")
        self.assertEqual(i18n.t("pause"), "Wstrzymaj")

    def test_cli_lang(self) -> None:
        self.assertEqual(i18n.parse_cli_lang(["run.py", "--lang", "sv"]), "sv")
        self.assertEqual(i18n.parse_cli_lang(["run.py", "--lang=en"]), "en")
        self.assertIsNone(i18n.parse_cli_lang(["run.py"]))

    def test_files_word(self) -> None:
        i18n.init("pl")
        self.assertEqual(i18n.files_word(1), "plik")
        self.assertEqual(i18n.files_word(2), "pliki")
        self.assertEqual(i18n.files_word(5), "plików")
        self.assertEqual(i18n.files_word(22), "pliki")
        i18n.init("sv")
        self.assertEqual(i18n.files_word(1), "fil")
        self.assertEqual(i18n.files_word(3), "filer")
        i18n.init("en")
        self.assertEqual(i18n.files_word(1), "file")
        self.assertEqual(i18n.files_word(3), "files")


if __name__ == "__main__":
    unittest.main()
