/* Print Queue Reset — spooler service helpers.
 * Copyright (c) 2026 Tomasz Mucha
 * SPDX-License-Identifier: MIT
 */
#include "spooler.h"
#include "i18n.h"
#include <stdio.h>

#ifdef __TINYC__
#ifndef SC_MANAGER_CONNECT
#define SC_MANAGER_CONNECT 0x0001
#define SERVICE_QUERY_STATUS 0x0004
#define SERVICE_START 0x0010
#define SERVICE_STOP 0x0020
#define SERVICE_CONTROL_STOP 1
#define SC_STATUS_PROCESS_INFO 0
#define SERVICE_STOPPED 1
#define SERVICE_START_PENDING 2
#define SERVICE_STOP_PENDING 3
#define SERVICE_RUNNING 4
#define SERVICE_CONTINUE_PENDING 5
#define SERVICE_PAUSE_PENDING 6
#define SERVICE_PAUSED 7
#endif
#ifndef PRINTER_ENUM_LOCAL
#define PRINTER_ENUM_LOCAL 2
#define PRINTER_ENUM_CONNECTIONS 4
#endif
#endif

#define PRN_PAUSED 0x00000001
#define PRN_ERROR 0x00000002
#define PRN_JAM 0x00000008
#define PRN_PAPER 0x00000010
#define PRN_OFFLINE 0x00000080
#define PRN_BUSY 0x00000200
#define PRN_PRINTING 0x00000400
#define PRN_NA 0x00001000
#define PRN_DOOR 0x00400000

#ifdef __TINYC__
typedef HANDLE SC_HANDLE;
typedef struct {
    DWORD dwServiceType, dwCurrentState, dwControlsAccepted, dwWin32ExitCode;
    DWORD dwServiceSpecificExitCode, dwCheckPoint, dwWaitHint;
} SERVICE_STATUS;
typedef struct {
    DWORD dwServiceType, dwCurrentState, dwControlsAccepted, dwWin32ExitCode;
    DWORD dwServiceSpecificExitCode, dwCheckPoint, dwWaitHint, dwProcessId, dwServiceFlags;
} SERVICE_STATUS_PROCESS;
typedef struct {
    LPWSTR pServerName, pPrinterName, pShareName, pPortName, pDriverName, pComment, pLocation;
    LPVOID pDevMode;
    LPWSTR pSepFile, pPrintProcessor, pDatatype, pParameters;
    LPVOID pSecurityDescriptor;
    DWORD Attributes, Priority, DefaultPriority, StartTime, UntilTime, Status, cJobs, AveragePPM;
} PRINTER_INFO_2W;
SC_HANDLE WINAPI OpenSCManagerW(LPCWSTR, LPCWSTR, DWORD);
SC_HANDLE WINAPI OpenServiceW(SC_HANDLE, LPCWSTR, DWORD);
BOOL WINAPI CloseServiceHandle(SC_HANDLE);
BOOL WINAPI QueryServiceStatusEx(SC_HANDLE, DWORD, LPBYTE, DWORD, LPDWORD);
BOOL WINAPI ControlService(SC_HANDLE, DWORD, SERVICE_STATUS *);
BOOL WINAPI StartServiceW(SC_HANDLE, DWORD, LPCWSTR *);
BOOL WINAPI AllocateAndInitializeSid(PSID_IDENTIFIER_AUTHORITY, BYTE, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, PSID *);
BOOL WINAPI CheckTokenMembership(HANDLE, PSID, PBOOL);
PVOID WINAPI FreeSid(PSID);
BOOL WINAPI EnumPrintersW(DWORD, LPWSTR, DWORD, LPBYTE, DWORD, LPDWORD, LPDWORD);
HINSTANCE WINAPI ShellExecuteW(HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT);
#else
#include <winsvc.h>
#include <winspool.h>
#include <shellapi.h>
#endif

int is_admin(void)
{
    BOOL ok = FALSE;
    PSID sid = NULL;
    SID_IDENTIFIER_AUTHORITY nt = {0, 0, 0, 0, 0, 5};
    if (AllocateAndInitializeSid(&nt, 2, 32, 544, 0, 0, 0, 0, 0, 0, &sid)) {
        CheckTokenMembership(NULL, sid, &ok);
        FreeSid(sid);
    }
    return ok ? 1 : 0;
}

int relaunch_as_admin(void)
{
    wchar_t exe[MAX_PATH];
    GetModuleFileNameW(NULL, exe, MAX_PATH);
    HINSTANCE r = ShellExecuteW(NULL, L"runas", exe, NULL, NULL, SW_SHOWNORMAL);
    return ((INT_PTR)r > 32) ? 1 : 0;
}

static int query_status(SERVICE_STATUS_PROCESS *st)
{
    SC_HANDLE scm, svc;
    DWORD need = 0;
    int ok = 0;
    scm = OpenSCManagerW(NULL, NULL, SC_MANAGER_CONNECT);
    if (!scm) return 0;
    svc = OpenServiceW(scm, L"Spooler", SERVICE_QUERY_STATUS);
    if (svc) {
        if (QueryServiceStatusEx(svc, SC_STATUS_PROCESS_INFO, (LPBYTE)st, sizeof(*st), &need))
            ok = 1;
        CloseServiceHandle(svc);
    }
    CloseServiceHandle(scm);
    return ok;
}

const wchar_t *state_text(DWORD state)
{
    switch (state) {
    case SERVICE_STOPPED: return I18N(S_STATE_STOPPED);
    case SERVICE_START_PENDING: return I18N(S_STATE_START_PENDING);
    case SERVICE_STOP_PENDING: return I18N(S_STATE_STOP_PENDING);
    case SERVICE_RUNNING: return I18N(S_STATE_RUNNING);
    case SERVICE_CONTINUE_PENDING: return I18N(S_STATE_CONTINUE_PENDING);
    case SERVICE_PAUSE_PENDING: return I18N(S_STATE_PAUSE_PENDING);
    case SERVICE_PAUSED: return I18N(S_STATE_PAUSED);
    default: return I18N(S_STATE_UNKNOWN);
    }
}

void printer_status_text(DWORD status, wchar_t *out, int outc)
{
    if (status == 0) {
        lstrcpynW(out, I18N(S_PRN_READY), outc);
        return;
    }
    out[0] = 0;
    if (status & PRN_PAUSED) lstrcpynW(out, I18N(S_PRN_PAUSED), outc);
    else if (status & PRN_ERROR) lstrcpynW(out, I18N(S_PRN_ERROR), outc);
    else if (status & PRN_JAM) lstrcpynW(out, I18N(S_PRN_JAM), outc);
    else if (status & PRN_PAPER) lstrcpynW(out, I18N(S_PRN_PAPER), outc);
    else if (status & PRN_OFFLINE) lstrcpynW(out, I18N(S_PRN_OFFLINE), outc);
    else if (status & PRN_DOOR) lstrcpynW(out, I18N(S_PRN_DOOR), outc);
    else if (status & PRN_PRINTING) lstrcpynW(out, I18N(S_PRN_PRINTING), outc);
    else if (status & PRN_BUSY) lstrcpynW(out, I18N(S_PRN_BUSY), outc);
    else if (status & PRN_NA) lstrcpynW(out, I18N(S_PRN_NA), outc);
    else lstrcpynW(out, I18N(S_PRN_READY), outc);
}

static void spool_dir(wchar_t *path, int pathc)
{
    wchar_t win[MAX_PATH];
    GetWindowsDirectoryW(win, MAX_PATH);
    _snwprintf(path, pathc, L"%s\\System32\\spool\\PRINTERS", win);
    path[pathc - 1] = 0;
}

static void read_buffer(SpoolerSnap *s)
{
    WIN32_FIND_DATAW fd;
    HANDLE h;
    wchar_t path[MAX_PATH], glob[MAX_PATH];
    s->buffer_ok = 0;
    s->buffer_files = 0;
    s->buffer_bytes = 0;
    spool_dir(path, MAX_PATH);
    _snwprintf(glob, MAX_PATH, L"%s\\*", path);
    glob[MAX_PATH - 1] = 0;
    h = FindFirstFileW(glob, &fd);
    if (h == INVALID_HANDLE_VALUE) {
        if (GetLastError() == ERROR_FILE_NOT_FOUND) s->buffer_ok = 1;
        return;
    }
    s->buffer_ok = 1;
    do {
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) continue;
        s->buffer_files++;
        s->buffer_bytes += ((unsigned long long)fd.nFileSizeHigh << 32) | fd.nFileSizeLow;
    } while (FindNextFileW(h, &fd));
    FindClose(h);
}

static void read_printers(SpoolerSnap *s)
{
    DWORD need = 0, got = 0, flags = PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS;
    s->printer_count = 0;
    s->job_total = 0;
    EnumPrintersW(flags, NULL, 2, NULL, 0, &need, &got);
    if (!need) return;
    {
        BYTE *buf = (BYTE *)LocalAlloc(LMEM_FIXED, need);
        PRINTER_INFO_2W *info;
        DWORD i;
        if (!buf) return;
        if (EnumPrintersW(flags, NULL, 2, buf, need, &need, &got)) {
            info = (PRINTER_INFO_2W *)buf;
            for (i = 0; i < got && s->printer_count < MAX_PRINTERS; i++) {
                if (!info[i].pPrinterName) continue;
                lstrcpynW(s->printers[s->printer_count].name, info[i].pPrinterName, MAX_PRN_NAME);
                s->printers[s->printer_count].status = info[i].Status;
                s->printers[s->printer_count].jobs = info[i].cJobs;
                s->job_total += (int)info[i].cJobs;
                s->printer_count++;
            }
        }
        LocalFree(buf);
    }
}

void spooler_snapshot(SpoolerSnap *s)
{
    SERVICE_STATUS_PROCESS st;
    ZeroMemory(s, sizeof(*s));
    if (query_status(&st)) {
        s->state = st.dwCurrentState;
        s->pid = st.dwProcessId;
        s->running = (st.dwCurrentState == SERVICE_RUNNING);
        s->can_pause = (st.dwCurrentState == SERVICE_RUNNING || st.dwCurrentState == SERVICE_PAUSED);
        s->can_resume = (st.dwCurrentState == SERVICE_STOPPED || st.dwCurrentState == SERVICE_PAUSED);
    }
    read_buffer(s);
    read_printers(s);
}

static int wait_state(DWORD wanted, DWORD timeout_ms)
{
    DWORD start = GetTickCount();
    SERVICE_STATUS_PROCESS st;
    while (GetTickCount() - start < timeout_ms) {
        if (!query_status(&st)) return 0;
        if (st.dwCurrentState == wanted) return 1;
        Sleep(200);
    }
    return 0;
}

static int kill_pid(DWORD pid)
{
    HANDLE h;
    int ok = 0;
    if (!pid) return 0;
    h = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
    if (!h) return 0;
    ok = TerminateProcess(h, 1) ? 1 : 0;
    CloseHandle(h);
    return ok;
}

int spooler_stop(wchar_t *msg, int msgc)
{
    SERVICE_STATUS_PROCESS st;
    SC_HANDLE scm, svc;
    DWORD pid;
    if (!query_status(&st)) {
        lstrcpynW(msg, I18N(S_ERR_QUERY), msgc);
        return 0;
    }
    if (st.dwCurrentState == SERVICE_STOPPED) {
        lstrcpynW(msg, I18N(S_LOG_ALREADY_STOPPED), msgc);
        return 1;
    }
    pid = st.dwProcessId;
    scm = OpenSCManagerW(NULL, NULL, SC_MANAGER_CONNECT);
    if (!scm) {
        lstrcpynW(msg, I18N(S_ERR_OPEN_SCM), msgc);
        return 0;
    }
    svc = OpenServiceW(scm, L"Spooler", SERVICE_QUERY_STATUS | SERVICE_STOP);
    if (svc) {
        SERVICE_STATUS ss;
        ControlService(svc, SERVICE_CONTROL_STOP, &ss);
        CloseServiceHandle(svc);
    }
    CloseServiceHandle(scm);
    if (wait_state(SERVICE_STOPPED, 12000)) {
        lstrcpynW(msg, I18N(S_LOG_STOPPED), msgc);
        return 1;
    }
    kill_pid(pid);
    if (wait_state(SERVICE_STOPPED, 8000)) {
        lstrcpynW(msg, I18N(S_LOG_KILLED), msgc);
        return 1;
    }
    lstrcpynW(msg, I18N(S_ERR_STOP), msgc);
    return 0;
}

int spooler_start(wchar_t *msg, int msgc)
{
    SERVICE_STATUS_PROCESS st;
    SC_HANDLE scm, svc;
    if (!query_status(&st)) {
        lstrcpynW(msg, I18N(S_ERR_QUERY), msgc);
        return 0;
    }
    if (st.dwCurrentState == SERVICE_RUNNING) {
        lstrcpynW(msg, I18N(S_LOG_ALREADY_RUNNING), msgc);
        return 1;
    }
    scm = OpenSCManagerW(NULL, NULL, SC_MANAGER_CONNECT);
    if (!scm) {
        lstrcpynW(msg, I18N(S_ERR_OPEN_SCM), msgc);
        return 0;
    }
    svc = OpenServiceW(scm, L"Spooler", SERVICE_QUERY_STATUS | SERVICE_START);
    if (!svc) {
        CloseServiceHandle(scm);
        lstrcpynW(msg, I18N(S_ERR_OPEN_SPOOLER), msgc);
        return 0;
    }
    StartServiceW(svc, 0, NULL);
    CloseServiceHandle(svc);
    CloseServiceHandle(scm);
    if (wait_state(SERVICE_RUNNING, 12000)) {
        lstrcpynW(msg, I18N(S_LOG_STARTED), msgc);
        return 1;
    }
    lstrcpynW(msg, I18N(S_ERR_START), msgc);
    return 0;
}

int spooler_clear(wchar_t *msg, int msgc)
{
    SERVICE_STATUS_PROCESS st;
    wchar_t path[MAX_PATH], glob[MAX_PATH];
    WIN32_FIND_DATAW fd;
    HANDLE h;
    int removed = 0, failed = 0;
    if (!query_status(&st)) {
        lstrcpynW(msg, I18N(S_ERR_QUERY), msgc);
        return 0;
    }
    if (st.dwCurrentState != SERVICE_STOPPED && st.dwCurrentState != SERVICE_STOP_PENDING) {
        lstrcpynW(msg, I18N(S_ERR_CLEAR_RUNNING), msgc);
        return 0;
    }
    spool_dir(path, MAX_PATH);
    _snwprintf(glob, MAX_PATH, L"%s\\*", path);
    glob[MAX_PATH - 1] = 0;
    h = FindFirstFileW(glob, &fd);
    if (h == INVALID_HANDLE_VALUE) {
        lstrcpynW(msg, I18N(S_LOG_BUF_EMPTY), msgc);
        return 1;
    }
    do {
        wchar_t full[MAX_PATH];
        if (fd.cFileName[0] == L'.' && (fd.cFileName[1] == 0 || (fd.cFileName[1] == L'.' && fd.cFileName[2] == 0)))
            continue;
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) continue;
        _snwprintf(full, MAX_PATH, L"%s\\%s", path, fd.cFileName);
        full[MAX_PATH - 1] = 0;
        if (DeleteFileW(full)) removed++;
        else failed++;
    } while (FindNextFileW(h, &fd));
    FindClose(h);
    if (failed) {
        lstrcpynW(msg, I18N(S_ERR_CLEAR_FAIL), msgc);
        return 0;
    }
    if (!removed) lstrcpynW(msg, I18N(S_LOG_BUF_EMPTY), msgc);
    else {
        wchar_t word[32], extra[80];
        files_word(removed, word, 32);
        _snwprintf(extra, 80, L"%s (%d %s)", I18N(S_LOG_BUF_CLEARED), removed, word);
        extra[79] = 0;
        lstrcpynW(msg, extra, msgc);
    }
    return 1;
}
