"""UI language: Polish, Swedish, English — follows Windows display language.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ctypes
import locale
import os
import sys

SUPPORTED = ("pl", "sv", "en")
DEFAULT_LANG = "en"

# PRIMARYLANGID values (LANGID & 0x3FF)
_PRIMARY = {
    0x09: "en",  # LANG_ENGLISH
    0x15: "pl",  # LANG_POLISH
    0x1D: "sv",  # LANG_SWEDISH
}

_lang = DEFAULT_LANG

EN = {
    "tagline": "Pauses printing, clears the buffer and resumes",
    "admin_banner": "Administrator rights are required to reset the print queue.",
    "run_as_admin": "Run as administrator",
    "status_heading": "SYSTEM STATUS",
    "refresh": "Refresh  F5",
    "status_spooler": "Spooler service",
    "status_buffer": "Print buffer",
    "status_jobs": "Jobs in queue",
    "status_printers": "Printers",
    "step_pause": "Pause",
    "step_clear": "Clear buffer",
    "step_resume": "Resume",
    "reset_queue": "Reset print queue",
    "reset_subtitle": "pause  ·  clear buffer  ·  resume",
    "pause": "Pause",
    "clear_buffer": "Clear buffer",
    "resume": "Resume",
    "log_heading": "LOG",
    "confirm_title": "Reset print queue",
    "confirm_body": (
        "This will pause the print process (Spooler service), delete every job "
        "from the buffer and start printing again.\n\n"
        "Documents that have not been printed will disappear from the queue."
    ),
    "confirm_reset": "Reset queue",
    "cancel": "Cancel",
    "close": "Close",
    "license_title": "License — MIT",
    "license_summary": (
        "{copyright}\n\n"
        "This program is free software: you may use, copy, modify, and "
        "distribute it under the MIT License.\n\n"
        "The program is provided WITHOUT ANY WARRANTY."
    ),
    "license_missing": (
        "LICENSE file not found.\n"
        "Full text: https://opensource.org/licenses/MIT"
    ),
    "buffer_no_access": "no access",
    "buffer_empty": "empty",
    "buffer_files": "{n} {files}  ·  {size}",
    "printers_none": "none",
    "jobs_short": "{n} jobs",
    "jobs_short_one": "{n} job",
    "word_file": "file",
    "word_files": "files",
    "log_uac_cancelled": "UAC prompt was cancelled.",
    "log_refresh_failed": "Could not refresh status: {error}",
    "log_need_admin": "Administrator rights are required.",
    "log_started_no_admin": (
        "Started without administrator rights. Click “Run as administrator”."
    ),
    "log_ready": "Print Queue Reset is ready.",
    "log_summary": "Spooler: {state}  ·  buffer: {files} {word}  ·  printers: {n}",
    "state_stopped": "Stopped",
    "state_start_pending": "Starting…",
    "state_stop_pending": "Stopping…",
    "state_running": "Running",
    "state_continue_pending": "Resuming…",
    "state_pause_pending": "Pausing…",
    "state_paused": "Paused",
    "state_unknown": "Unknown",
    "printer_ready": "Ready",
    "printer_paused": "Paused",
    "printer_error": "Error",
    "printer_paper_jam": "Paper jam",
    "printer_paper_out": "Out of paper",
    "printer_offline": "Offline",
    "printer_door_open": "Cover open",
    "printer_printing": "Printing",
    "printer_busy": "Busy",
    "printer_not_available": "Unavailable",
    "printer_status_hex": "Status 0x{status:X}",
    "err_open_scm": "Cannot open the service manager",
    "err_open_spooler": "Cannot open the Spooler service",
    "err_query_status": "Cannot read Spooler service status",
    "err_access_denied": "{prefix}: administrator rights required (code 5).",
    "err_already_stopped": "{prefix}: the service is already stopped.",
    "err_already_running": "{prefix}: the service is already running.",
    "err_with_code": "{prefix} (code {code}).{extra}",
    "err_wait_state": "Timed out waiting for service state ({state}).",
    "err_open_process": "Cannot open the spoolsv.exe process",
    "err_kill_process": "Cannot terminate the spoolsv.exe process",
    "err_stop_spooler": "Cannot stop the Spooler service",
    "err_start_spooler": "Cannot start the Spooler service",
    "err_clear_while_running": (
        "The buffer can only be cleared after the print process has been paused."
    ),
    "err_clear_failed": "Could not delete {n} files from the buffer. {detail}",
    "log_spooler_already_stopped": "The Spooler service was already stopped.",
    "log_spooler_stopped": "Spooler service stopped (printing paused).",
    "log_spooler_killed": "Forced stop of the spoolsv.exe process.",
    "log_spooler_already_running": "The Spooler service is already running.",
    "log_spooler_started": "Spooler service started (printing resumed).",
    "log_buffer_missing": "Buffer folder does not exist: {path}",
    "log_buffer_was_empty": "The print buffer was empty.",
    "log_buffer_cleared": "Print buffer cleared ({n} files).",
    "log_pausing": "Pausing the print process…",
    "log_clearing": "Clearing the print buffer…",
    "log_resuming": "Resuming printing…",
    "log_done": "Done. The print queue has been reset.",
}

PL = {
    "tagline": "Wstrzymuje drukowanie, czyści bufor i wznawia",
    "admin_banner": (
        "Brak uprawnień administratora. Reset kolejki wymaga podniesienia uprawnień."
    ),
    "run_as_admin": "Uruchom jako administrator",
    "status_heading": "STATUS SYSTEMU",
    "refresh": "Odśwież  F5",
    "status_spooler": "Usługa Spooler",
    "status_buffer": "Bufor druku",
    "status_jobs": "Zadania w kolejce",
    "status_printers": "Drukarki",
    "step_pause": "Wstrzymaj",
    "step_clear": "Wyczyść bufor",
    "step_resume": "Wznów",
    "reset_queue": "Resetuj kolejkę druku",
    "reset_subtitle": "wstrzymaj  ·  wyczyść bufor  ·  wznów",
    "pause": "Wstrzymaj",
    "clear_buffer": "Wyczyść bufor",
    "resume": "Wznów",
    "log_heading": "DZIENNIK",
    "confirm_title": "Reset kolejki druku",
    "confirm_body": (
        "To wstrzyma proces drukowania (usługa Spooler), usunie wszystkie "
        "zadania z bufora i ponownie uruchomi drukowanie.\n\n"
        "Niewydrukowane dokumenty znikną z kolejki."
    ),
    "confirm_reset": "Resetuj kolejkę",
    "cancel": "Anuluj",
    "close": "Zamknij",
    "license_title": "Licencja — MIT",
    "license_summary": (
        "{copyright}\n\n"
        "To oprogramowanie jest wolnym oprogramowaniem: możesz je "
        "używać, kopiować, modyfikować i rozpowszechniać na warunkach "
        "licencji MIT.\n\n"
        "Program jest dostarczany BEZ JAKIEJKOLWIEK GWARANCJI."
    ),
    "license_missing": (
        "Nie znaleziono pliku LICENSE.\n"
        "Pełny tekst: https://opensource.org/licenses/MIT"
    ),
    "buffer_no_access": "brak dostępu",
    "buffer_empty": "pusty",
    "buffer_files": "{n} {files}  ·  {size}",
    "printers_none": "brak",
    "jobs_short": "{n} zad.",
    "jobs_short_one": "{n} zad.",
    "word_file": "plik",
    "word_files": "plików",
    "log_uac_cancelled": "Anulowano monit UAC.",
    "log_refresh_failed": "Nie można odświeżyć statusu: {error}",
    "log_need_admin": "Wymagane uprawnienia administratora.",
    "log_started_no_admin": (
        "Uruchomiono bez uprawnień administratora. Kliknij „Uruchom jako administrator”."
    ),
    "log_ready": "Print Queue Reset gotowy.",
    "log_summary": "Spooler: {state}  ·  bufor: {files} {word}  ·  drukarki: {n}",
    "state_stopped": "Zatrzymana",
    "state_start_pending": "Uruchamianie…",
    "state_stop_pending": "Zatrzymywanie…",
    "state_running": "Działa",
    "state_continue_pending": "Wznawianie…",
    "state_pause_pending": "Wstrzymywanie…",
    "state_paused": "Wstrzymana",
    "state_unknown": "Nieznany",
    "printer_ready": "Gotowa",
    "printer_paused": "Wstrzymana",
    "printer_error": "Błąd",
    "printer_paper_jam": "Zacięcie papieru",
    "printer_paper_out": "Brak papieru",
    "printer_offline": "Offline",
    "printer_door_open": "Otwarta pokrywa",
    "printer_printing": "Drukuje",
    "printer_busy": "Zajęta",
    "printer_not_available": "Niedostępna",
    "printer_status_hex": "Status 0x{status:X}",
    "err_open_scm": "Nie można otworzyć menedżera usług",
    "err_open_spooler": "Nie można otworzyć usługi Spooler",
    "err_query_status": "Nie można odczytać statusu usługi Spooler",
    "err_access_denied": "{prefix}: brak uprawnień administratora (kod 5).",
    "err_already_stopped": "{prefix}: usługa jest już zatrzymana.",
    "err_already_running": "{prefix}: usługa jest już uruchomiona.",
    "err_with_code": "{prefix} (kod {code}).{extra}",
    "err_wait_state": "Przekroczono czas oczekiwania na stan usługi ({state}).",
    "err_open_process": "Nie można otworzyć procesu spoolsv.exe",
    "err_kill_process": "Nie można zakończyć procesu spoolsv.exe",
    "err_stop_spooler": "Nie można zatrzymać usługi Spooler",
    "err_start_spooler": "Nie można uruchomić usługi Spooler",
    "err_clear_while_running": (
        "Bufor można wyczyścić dopiero po wstrzymaniu procesu drukowania."
    ),
    "err_clear_failed": "Nie udało się usunąć {n} plików z bufora. {detail}",
    "log_spooler_already_stopped": "Usługa Spooler była już zatrzymana.",
    "log_spooler_stopped": "Zatrzymano usługę Spooler (proces drukowania wstrzymany).",
    "log_spooler_killed": "Wymuszono zatrzymanie procesu spoolsv.exe.",
    "log_spooler_already_running": "Usługa Spooler już działa.",
    "log_spooler_started": "Uruchomiono usługę Spooler (drukowanie wznowione).",
    "log_buffer_missing": "Folder bufora nie istnieje: {path}",
    "log_buffer_was_empty": "Bufor druku był pusty.",
    "log_buffer_cleared": "Wyczyszczono bufor druku ({n} plików).",
    "log_pausing": "Wstrzymywanie procesu drukowania…",
    "log_clearing": "Czyszczenie bufora druku…",
    "log_resuming": "Wznawianie drukowania…",
    "log_done": "Gotowe. Kolejka druku została zresetowana.",
}

SV = {
    "tagline": "Pausar utskrift, tömmer bufferten och återupptar",
    "admin_banner": (
        "Administratörsbehörighet saknas. Återställning av kön kräver utökade rättigheter."
    ),
    "run_as_admin": "Kör som administratör",
    "status_heading": "SYSTEMSTATUS",
    "refresh": "Uppdatera  F5",
    "status_spooler": "Spooler-tjänst",
    "status_buffer": "Utskriftsbuffert",
    "status_jobs": "Jobb i kön",
    "status_printers": "Skrivare",
    "step_pause": "Pausa",
    "step_clear": "Töm buffert",
    "step_resume": "Återuppta",
    "reset_queue": "Återställ utskriftskön",
    "reset_subtitle": "pausa  ·  töm buffert  ·  återuppta",
    "pause": "Pausa",
    "clear_buffer": "Töm buffert",
    "resume": "Återuppta",
    "log_heading": "LOGG",
    "confirm_title": "Återställ utskriftskön",
    "confirm_body": (
        "Detta pausar utskriftsprocessen (Spooler-tjänsten), tar bort alla "
        "jobb från bufferten och startar utskriften igen.\n\n"
        "Dokument som inte har skrivits ut försvinner från kön."
    ),
    "confirm_reset": "Återställ kön",
    "cancel": "Avbryt",
    "close": "Stäng",
    "license_title": "Licens — MIT",
    "license_summary": (
        "{copyright}\n\n"
        "Detta program är fri programvara: du får använda, kopiera, "
        "ändra och sprida det enligt MIT-licensen.\n\n"
        "Programmet tillhandahålls UTAN NÅGON GARANTI."
    ),
    "license_missing": (
        "LICENSE-filen hittades inte.\n"
        "Fullständig text: https://opensource.org/licenses/MIT"
    ),
    "buffer_no_access": "ingen åtkomst",
    "buffer_empty": "tom",
    "buffer_files": "{n} {files}  ·  {size}",
    "printers_none": "inga",
    "jobs_short": "{n} jobb",
    "jobs_short_one": "{n} jobb",
    "word_file": "fil",
    "word_files": "filer",
    "log_uac_cancelled": "UAC-prompten avbröts.",
    "log_refresh_failed": "Kunde inte uppdatera status: {error}",
    "log_need_admin": "Administratörsbehörighet krävs.",
    "log_started_no_admin": (
        "Startades utan administratörsbehörighet. Klicka på “Kör som administratör”."
    ),
    "log_ready": "Print Queue Reset är redo.",
    "log_summary": "Spooler: {state}  ·  buffert: {files} {word}  ·  skrivare: {n}",
    "state_stopped": "Stoppad",
    "state_start_pending": "Startar…",
    "state_stop_pending": "Stoppar…",
    "state_running": "Igång",
    "state_continue_pending": "Återupptar…",
    "state_pause_pending": "Pausar…",
    "state_paused": "Pausad",
    "state_unknown": "Okänd",
    "printer_ready": "Redo",
    "printer_paused": "Pausad",
    "printer_error": "Fel",
    "printer_paper_jam": "Papperstrassel",
    "printer_paper_out": "Slut på papper",
    "printer_offline": "Offline",
    "printer_door_open": "Luckan öppen",
    "printer_printing": "Skriver ut",
    "printer_busy": "Upptagen",
    "printer_not_available": "Otillgänglig",
    "printer_status_hex": "Status 0x{status:X}",
    "err_open_scm": "Kan inte öppna tjänsthanteraren",
    "err_open_spooler": "Kan inte öppna Spooler-tjänsten",
    "err_query_status": "Kan inte läsa Spooler-tjänstens status",
    "err_access_denied": "{prefix}: administratörsbehörighet krävs (kod 5).",
    "err_already_stopped": "{prefix}: tjänsten är redan stoppad.",
    "err_already_running": "{prefix}: tjänsten är redan igång.",
    "err_with_code": "{prefix} (kod {code}).{extra}",
    "err_wait_state": "Timeout vid väntan på tjänststatus ({state}).",
    "err_open_process": "Kan inte öppna processen spoolsv.exe",
    "err_kill_process": "Kan inte avsluta processen spoolsv.exe",
    "err_stop_spooler": "Kan inte stoppa Spooler-tjänsten",
    "err_start_spooler": "Kan inte starta Spooler-tjänsten",
    "err_clear_while_running": (
        "Bufferten kan tömmas först efter att utskriftsprocessen har pausats."
    ),
    "err_clear_failed": "Kunde inte ta bort {n} filer från bufferten. {detail}",
    "log_spooler_already_stopped": "Spooler-tjänsten var redan stoppad.",
    "log_spooler_stopped": "Spooler-tjänsten stoppades (utskrift pausad).",
    "log_spooler_killed": "Tvingade stopp av processen spoolsv.exe.",
    "log_spooler_already_running": "Spooler-tjänsten är redan igång.",
    "log_spooler_started": "Spooler-tjänsten startades (utskrift återupptagen).",
    "log_buffer_missing": "Buffertmappen finns inte: {path}",
    "log_buffer_was_empty": "Utskriftsbufferten var tom.",
    "log_buffer_cleared": "Utskriftsbufferten tömdes ({n} filer).",
    "log_pausing": "Pausar utskriftsprocessen…",
    "log_clearing": "Tömmer utskriftsbufferten…",
    "log_resuming": "Återupptar utskrift…",
    "log_done": "Klart. Utskriftskön har återställts.",
}

STRINGS = {"en": EN, "pl": PL, "sv": SV}


def language_from_tag(tag: str | None) -> str | None:
    if not tag:
        return None
    primary = tag.replace("_", "-").strip().lower().split("-", 1)[0]
    if primary in SUPPORTED:
        return primary
    return None


def language_from_langid(langid: int) -> str | None:
    return _PRIMARY.get(langid & 0x3FF)


def detect_system_language() -> str:
    env = os.environ.get("PQR_LANG") or os.environ.get("LANG")
    from_env = language_from_tag(env)
    if from_env:
        return from_env

    try:
        ui = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        mapped = language_from_langid(int(ui))
        if mapped:
            return mapped
    except Exception:
        pass

    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.GetUserDefaultLocaleName.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_int,
        ]
        kernel32.GetUserDefaultLocaleName.restype = ctypes.c_int
        buf = ctypes.create_unicode_buffer(16)
        if kernel32.GetUserDefaultLocaleName(buf, 16):
            mapped = language_from_tag(buf.value)
            if mapped:
                return mapped
    except Exception:
        pass

    try:
        loc = locale.getlocale()[0] or locale.getdefaultlocale()[0]
        mapped = language_from_tag(loc)
        if mapped:
            return mapped
    except Exception:
        pass

    return DEFAULT_LANG


def init(explicit: str | None = None) -> str:
    global _lang
    chosen = language_from_tag(explicit) if explicit else None
    _lang = chosen or detect_system_language()
    return _lang


def language() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    table = STRINGS.get(_lang) or STRINGS[DEFAULT_LANG]
    text = table.get(key) or STRINGS[DEFAULT_LANG].get(key) or key
    if kwargs:
        return text.format(**kwargs)
    return text


def files_word(n: int) -> str:
    if _lang == "pl":
        mod10, mod100 = n % 10, n % 100
        if mod10 == 1 and mod100 != 11:
            return "plik"
        if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
            return "pliki"
        return "plików"
    if n == 1:
        return t("word_file")
    return t("word_files")


def jobs_label(n: int) -> str:
    if n == 1:
        return t("jobs_short_one", n=n)
    return t("jobs_short", n=n)


def parse_cli_lang(argv: list[str] | None = None) -> str | None:
    args = list(sys.argv if argv is None else argv)
    if "--lang" in args:
        i = args.index("--lang")
        if i + 1 < len(args):
            return args[i + 1]
    for arg in args:
        if arg.startswith("--lang="):
            return arg.split("=", 1)[1]
    return None
