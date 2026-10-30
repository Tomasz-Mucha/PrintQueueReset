"""Tests for Print Queue Reset.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import i18n
import spooler


class FormatTests(unittest.TestCase):
    def setUp(self) -> None:
        i18n.init("pl")

    def test_bytes(self) -> None:
        self.assertEqual(spooler.format_bytes(0), "0 B")
        self.assertEqual(spooler.format_bytes(512), "512 B")
        self.assertEqual(spooler.format_bytes(2048), "2,0 KB")
        self.assertEqual(spooler.format_bytes(2 * 1024 * 1024), "2,0 MB")
        i18n.init("en")
        self.assertEqual(spooler.format_bytes(2048), "2.0 KB")
        i18n.init("sv")
        self.assertEqual(spooler.format_bytes(2048), "2,0 KB")

    def test_printer_ready(self) -> None:
        self.assertEqual(spooler.printer_status_label(0), "Gotowa")

    def test_printer_paused_offline(self) -> None:
        status = spooler.PRINTER_STATUS_PAUSED | spooler.PRINTER_STATUS_OFFLINE
        label = spooler.printer_status_label(status)
        self.assertIn("Wstrzymana", label)
        self.assertIn("Offline", label)

    def test_spool_directory_name(self) -> None:
        path = spooler.spool_directory()
        self.assertEqual(path.name, "PRINTERS")
        self.assertEqual(path.parent.name, "spool")

    def test_license_file_present(self) -> None:
        path = spooler.license_path()
        self.assertTrue(path.is_file(), path)
        text = path.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Copyright (c) 2026 Tomasz Mucha", text)
        self.assertIn("Permission is hereby granted", text)
        self.assertNotIn("GNU GENERAL PUBLIC LICENSE", text)


if __name__ == "__main__":
    unittest.main()
