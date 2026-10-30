/* Print Queue Reset — UI strings.
 * Copyright (c) 2026 Tomasz Mucha
 * SPDX-License-Identifier: MIT
 */
#include <windows.h>
#include "i18n.h"
#include <stdio.h>

static int g_lang; /* 0 en, 1 pl, 2 sv */

static const wchar_t *const EN[S_COUNT] = {
    L"Pauses printing, clears the buffer and resumes",
    L"Administrator rights are required to reset the print queue.",
    L"Run as administrator",
    L"SYSTEM STATUS",
    L"Refresh  F5",
    L"Spooler service",
    L"Print buffer",
    L"Jobs in queue",
    L"Printers",
    L"Pause",
    L"Clear buffer",
    L"Resume",
    L"Reset print queue",
    L"pause  ·  clear buffer  ·  resume",
    L"Pause",
    L"Clear buffer",
    L"Resume",
    L"LOG",
    L"Reset print queue",
    L"This will pause the print process (Spooler service), delete every job from the buffer and start printing again.\n\nDocuments that have not been printed will disappear from the queue.",
    L"no access",
    L"empty",
    L"none",
    L"UAC prompt was cancelled.",
    L"Administrator rights are required.",
    L"Started without administrator rights. Click Run as administrator.",
    L"Print Queue Reset is ready.",
    L"Stopped",
    L"Starting…",
    L"Stopping…",
    L"Running",
    L"Resuming…",
    L"Pausing…",
    L"Paused",
    L"Unknown",
    L"Ready",
    L"Paused",
    L"Error",
    L"Paper jam",
    L"Out of paper",
    L"Offline",
    L"Cover open",
    L"Printing",
    L"Busy",
    L"Unavailable",
    L"Cannot open the service manager",
    L"Cannot open the Spooler service",
    L"Cannot read Spooler service status",
    L"Cannot stop the Spooler service",
    L"Cannot start the Spooler service",
    L"Cannot open the spoolsv.exe process",
    L"Cannot terminate the spoolsv.exe process",
    L"Timed out waiting for the Spooler service.",
    L"The buffer can only be cleared after the print process has been paused.",
    L"Could not delete all files from the buffer.",
    L"The Spooler service was already stopped.",
    L"Spooler service stopped (printing paused).",
    L"Forced stop of the spoolsv.exe process.",
    L"The Spooler service is already running.",
    L"Spooler service started (printing resumed).",
    L"Buffer folder does not exist.",
    L"The print buffer was empty.",
    L"Print buffer cleared.",
    L"Pausing the print process…",
    L"Clearing the print buffer…",
    L"Resuming printing…",
    L"Done. The print queue has been reset.",
    L"License — MIT",
    L"Copyright (c) 2026 Tomasz Mucha\n\nThis program is free software under the MIT License.\nYou may use, copy, modify, and distribute it.\nThere is NO WARRANTY.\n\nhttps://opensource.org/licenses/MIT"
};

static const wchar_t *const PL[S_COUNT] = {
    L"Wstrzymuje drukowanie, czyści bufor i wznawia",
    L"Brak uprawnień administratora. Reset kolejki wymaga podniesienia uprawnień.",
    L"Uruchom jako administrator",
    L"STATUS SYSTEMU",
    L"Odśwież  F5",
    L"Usługa Spooler",
    L"Bufor druku",
    L"Zadania w kolejce",
    L"Drukarki",
    L"Wstrzymaj",
    L"Wyczyść bufor",
    L"Wznów",
    L"Resetuj kolejkę druku",
    L"wstrzymaj  ·  wyczyść bufor  ·  wznów",
    L"Wstrzymaj",
    L"Wyczyść bufor",
    L"Wznów",
    L"DZIENNIK",
    L"Reset kolejki druku",
    L"To wstrzyma proces drukowania (usługa Spooler), usunie wszystkie zadania z bufora i ponownie uruchomi drukowanie.\n\nNiewydrukowane dokumenty znikną z kolejki.",
    L"brak dostępu",
    L"pusty",
    L"brak",
    L"Anulowano monit UAC.",
    L"Wymagane uprawnienia administratora.",
    L"Uruchomiono bez uprawnień administratora. Kliknij Uruchom jako administrator.",
    L"Print Queue Reset gotowy.",
    L"Zatrzymana",
    L"Uruchamianie…",
    L"Zatrzymywanie…",
    L"Działa",
    L"Wznawianie…",
    L"Wstrzymywanie…",
    L"Wstrzymana",
    L"Nieznany",
    L"Gotowa",
    L"Wstrzymana",
    L"Błąd",
    L"Zacięcie papieru",
    L"Brak papieru",
    L"Offline",
    L"Otwarta pokrywa",
    L"Drukuje",
    L"Zajęta",
    L"Niedostępna",
    L"Nie można otworzyć menedżera usług",
    L"Nie można otworzyć usługi Spooler",
    L"Nie można odczytać statusu usługi Spooler",
    L"Nie można zatrzymać usługi Spooler",
    L"Nie można uruchomić usługi Spooler",
    L"Nie można otworzyć procesu spoolsv.exe",
    L"Nie można zakończyć procesu spoolsv.exe",
    L"Przekroczono czas oczekiwania na usługę Spooler.",
    L"Bufor można wyczyścić dopiero po wstrzymaniu procesu drukowania.",
    L"Nie udało się usunąć wszystkich plików z bufora.",
    L"Usługa Spooler była już zatrzymana.",
    L"Zatrzymano usługę Spooler (proces drukowania wstrzymany).",
    L"Wymuszono zatrzymanie procesu spoolsv.exe.",
    L"Usługa Spooler już działa.",
    L"Uruchomiono usługę Spooler (drukowanie wznowione).",
    L"Folder bufora nie istnieje.",
    L"Bufor druku był pusty.",
    L"Wyczyszczono bufor druku.",
    L"Wstrzymywanie procesu drukowania…",
    L"Czyszczenie bufora druku…",
    L"Wznawianie drukowania…",
    L"Gotowe. Kolejka druku została zresetowana.",
    L"Licencja — MIT",
    L"Copyright (c) 2026 Tomasz Mucha\n\nTo oprogramowanie jest wolnym oprogramowaniem na licencji MIT.\nMożesz je używać, kopiować, modyfikować i rozpowszechniać.\nBrak JAKIEJKOLWIEK GWARANCJI.\n\nhttps://opensource.org/licenses/MIT"
};

static const wchar_t *const SV[S_COUNT] = {
    L"Pausar utskrift, tömmer bufferten och återupptar",
    L"Administratörsbehörighet saknas. Återställning av kön kräver utökade rättigheter.",
    L"Kör som administratör",
    L"SYSTEMSTATUS",
    L"Uppdatera  F5",
    L"Spooler-tjänst",
    L"Utskriftsbuffert",
    L"Jobb i kön",
    L"Skrivare",
    L"Pausa",
    L"Töm buffert",
    L"Återuppta",
    L"Återställ utskriftskön",
    L"pausa  ·  töm buffert  ·  återuppta",
    L"Pausa",
    L"Töm buffert",
    L"Återuppta",
    L"LOGG",
    L"Återställ utskriftskön",
    L"Detta pausar utskriftsprocessen (Spooler-tjänsten), tar bort alla jobb från bufferten och startar utskriften igen.\n\nDokument som inte har skrivits ut försvinner från kön.",
    L"ingen åtkomst",
    L"tom",
    L"inga",
    L"UAC-prompten avbröts.",
    L"Administratörsbehörighet krävs.",
    L"Startades utan administratörsbehörighet. Klicka på Kör som administratör.",
    L"Print Queue Reset är redo.",
    L"Stoppad",
    L"Startar…",
    L"Stoppar…",
    L"Igång",
    L"Återupptar…",
    L"Pausar…",
    L"Pausad",
    L"Okänd",
    L"Redo",
    L"Pausad",
    L"Fel",
    L"Papperstrassel",
    L"Slut på papper",
    L"Offline",
    L"Luckan öppen",
    L"Skriver ut",
    L"Upptagen",
    L"Otillgänglig",
    L"Kan inte öppna tjänsthanteraren",
    L"Kan inte öppna Spooler-tjänsten",
    L"Kan inte läsa Spooler-tjänstens status",
    L"Kan inte stoppa Spooler-tjänsten",
    L"Kan inte starta Spooler-tjänsten",
    L"Kan inte öppna processen spoolsv.exe",
    L"Kan inte avsluta processen spoolsv.exe",
    L"Timeout vid väntan på Spooler-tjänsten.",
    L"Bufferten kan tömmas först efter att utskriftsprocessen har pausats.",
    L"Kunde inte ta bort alla filer från bufferten.",
    L"Spooler-tjänsten var redan stoppad.",
    L"Spooler-tjänsten stoppades (utskrift pausad).",
    L"Tvingade stopp av processen spoolsv.exe.",
    L"Spooler-tjänsten är redan igång.",
    L"Spooler-tjänsten startades (utskrift återupptagen).",
    L"Buffertmappen finns inte.",
    L"Utskriftsbufferten var tom.",
    L"Utskriftsbufferten tömdes.",
    L"Pausar utskriftsprocessen…",
    L"Tömmer utskriftsbufferten…",
    L"Återupptar utskrift…",
    L"Klart. Utskriftskön har återställts.",
    L"Licens — MIT",
    L"Copyright (c) 2026 Tomasz Mucha\n\nDetta program är fri programvara under MIT-licensen.\nDu får använda, kopiera, ändra och sprida det.\nDet finns INGEN GARANTI.\n\nhttps://opensource.org/licenses/MIT"
};

void i18n_init(void)
{
    typedef unsigned short (WINAPI *UiFn)(void);
    HMODULE k32 = GetModuleHandleW(L"kernel32.dll");
    UiFn fn = k32 ? (UiFn)GetProcAddress(k32, "GetUserDefaultUILanguage") : NULL;
    unsigned short ui = fn ? fn() : 0;
    int primary = ui & 0x3FF;
    if (primary == 0x15) g_lang = 1;
    else if (primary == 0x1D) g_lang = 2;
    else g_lang = 0;
}

int i18n_lang(void) { return g_lang; }

const wchar_t *I18N(int id)
{
    if (id < 0 || id >= S_COUNT) return L"";
    if (g_lang == 1) return PL[id];
    if (g_lang == 2) return SV[id];
    return EN[id];
}

void files_word(int n, wchar_t *out, int outc)
{
    if (g_lang == 1) {
        int m10 = n % 10, m100 = n % 100;
        if (m10 == 1 && m100 != 11) lstrcpynW(out, L"plik", outc);
        else if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) lstrcpynW(out, L"pliki", outc);
        else lstrcpynW(out, L"plików", outc);
    } else if (g_lang == 2) {
        lstrcpynW(out, n == 1 ? L"fil" : L"filer", outc);
    } else {
        lstrcpynW(out, n == 1 ? L"file" : L"files", outc);
    }
}

void format_bytes(unsigned long long n, wchar_t *out, int outc)
{
    wchar_t sep = (g_lang == 0) ? L'.' : L',';
    if (n < 1024) {
        _snwprintf(out, outc, L"%u B", (unsigned)n);
    } else if (n < 1024ull * 1024ull) {
        unsigned v = (unsigned)((n * 10) / 1024);
        _snwprintf(out, outc, L"%u%c%u KB", v / 10, sep, v % 10);
    } else {
        unsigned v = (unsigned)((n * 10) / (1024ull * 1024ull));
        _snwprintf(out, outc, L"%u%c%u MB", v / 10, sep, v % 10);
    }
    out[outc - 1] = 0;
}
