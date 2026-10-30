/* Print Queue Reset — native Win32
 * Copyright (c) 2026 Tomasz Mucha
 * SPDX-License-Identifier: MIT
 */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "i18n.h"
#include "spooler.h"
#include "icon_data.h"

#define APP_CLASS L"PrintQueueReset"
#define APP_TITLE L"Print Queue Reset"
#define APP_VERSION L"1.0.0"

#define ID_RESET 101
#define ID_PAUSE 102
#define ID_CLEAR 103
#define ID_RESUME 104
#define ID_ADMIN 105
#define ID_LOG 106
#define ID_TIMER 1
#define WM_JOB_LOG (WM_APP + 1)
#define WM_JOB_DONE (WM_APP + 2)

#define COL_BG RGB(16, 21, 31)
#define COL_CARD RGB(26, 32, 48)
#define COL_TEXT RGB(232, 238, 247)
#define COL_DIM RGB(154, 168, 188)
#define COL_MUTED RGB(110, 123, 143)
#define COL_ACCENT RGB(13, 110, 253)
#define COL_ACCENT2 RGB(61, 139, 255)
#define COL_OK RGB(61, 220, 151)
#define COL_WARN RGB(255, 176, 32)
#define COL_ERR RGB(255, 92, 122)
#define COL_BTN RGB(36, 48, 68)
#define COL_DANGER_BG RGB(42, 28, 36)

#define ACT_RESET 1
#define ACT_PAUSE 2
#define ACT_CLEAR 3
#define ACT_RESUME 4

static HWND g_hwnd, g_log, g_btnReset, g_btnPause, g_btnClear, g_btnResume, g_btnAdmin;
static HBRUSH g_brBg, g_brCard, g_brEdit, g_brAccent, g_brBtn, g_brDanger;
static HFONT g_font, g_fontBold, g_fontSmall, g_fontTitle, g_fontMono;
static HICON g_icon;
static SpoolerSnap g_snap;
static int g_busy;
static int g_step = -1;
static int g_stepDone = -1;

static HICON load_icon(int size)
{
    return CreateIconFromResourceEx((PBYTE)ICON_PNG, ICON_PNG_SIZE, TRUE, 0x00030000, size, size, 0);
}

static void dark_titlebar(HWND hwnd)
{
    HMODULE dwm = LoadLibraryW(L"dwmapi.dll");
    if (!dwm) return;
    {
        typedef HRESULT(WINAPI *FN)(HWND, DWORD, LPCVOID, DWORD);
        FN fn = (FN)GetProcAddress(dwm, "DwmSetWindowAttribute");
        if (fn) {
            BOOL on = TRUE;
            fn(hwnd, 20, &on, sizeof(on));
            fn(hwnd, 19, &on, sizeof(on));
        }
    }
    FreeLibrary(dwm);
}

static int activate_existing(void)
{
    HWND hwnd = FindWindowW(APP_CLASS, NULL);
    RECT r;
    if (!hwnd) return 0;
    ShowWindow(hwnd, SW_RESTORE);
    SetForegroundWindow(hwnd);
    BringWindowToTop(hwnd);
    if (!GetWindowRect(hwnd, &r) || r.left <= -10000) return 0;
    return 1;
}

static wchar_t *wdup(const wchar_t *s)
{
    int n = lstrlenW(s) + 1;
    wchar_t *p = (wchar_t *)HeapAlloc(GetProcessHeap(), 0, n * sizeof(wchar_t));
    if (p) lstrcpynW(p, s, n);
    return p;
}

static void append_log(const wchar_t *msg)
{
    SYSTEMTIME st;
    wchar_t line[700];
    int len;
    GetLocalTime(&st);
    _snwprintf(line, 700, L"%02d:%02d:%02d  %s\r\n", st.wHour, st.wMinute, st.wSecond, msg);
    line[699] = 0;
    len = GetWindowTextLengthW(g_log);
    SendMessageW(g_log, EM_SETSEL, len, len);
    SendMessageW(g_log, EM_REPLACESEL, FALSE, (LPARAM)line);
    SendMessageW(g_log, EM_SCROLLCARET, 0, 0);
}

static void set_busy(int busy)
{
    g_busy = busy;
    EnableWindow(g_btnReset, !busy && is_admin());
    EnableWindow(g_btnPause, !busy && is_admin() && g_snap.can_pause);
    EnableWindow(g_btnClear, !busy && is_admin());
    EnableWindow(g_btnResume, !busy && is_admin() && g_snap.can_resume);
    EnableWindow(g_btnAdmin, !is_admin());
}

static void refresh_status(void)
{
    spooler_snapshot(&g_snap);
    if (!g_busy) set_busy(0);
    InvalidateRect(g_hwnd, NULL, FALSE);
}

static DWORD WINAPI worker(LPVOID param)
{
    int act = (int)(INT_PTR)param;
    wchar_t msg[512];
    HWND hwnd = g_hwnd;
    if (act == ACT_RESET) {
        g_step = 0; g_stepDone = -1;
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(I18N(S_LOG_PAUSING)));
        if (!spooler_stop(msg, 512)) {
            PostMessageW(hwnd, WM_JOB_LOG, 1, (LPARAM)wdup(msg));
            PostMessageW(hwnd, WM_JOB_DONE, 0, 0);
            return 0;
        }
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        g_step = 1; g_stepDone = 0;
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(I18N(S_LOG_CLEARING)));
        if (!spooler_clear(msg, 512)) {
            PostMessageW(hwnd, WM_JOB_LOG, 1, (LPARAM)wdup(msg));
            PostMessageW(hwnd, WM_JOB_DONE, 0, 0);
            return 0;
        }
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        g_step = 2; g_stepDone = 1;
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(I18N(S_LOG_RESUMING)));
        if (!spooler_start(msg, 512)) {
            PostMessageW(hwnd, WM_JOB_LOG, 1, (LPARAM)wdup(msg));
            PostMessageW(hwnd, WM_JOB_DONE, 0, 0);
            return 0;
        }
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(I18N(S_LOG_DONE)));
        g_step = -1; g_stepDone = 2;
        PostMessageW(hwnd, WM_JOB_DONE, 1, 0);
        return 0;
    }
    if (act == ACT_PAUSE) {
        g_step = 0;
        spooler_stop(msg, 512);
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        g_stepDone = 0; g_step = -1;
    } else if (act == ACT_CLEAR) {
        if (g_snap.running) {
            g_step = 0;
            spooler_stop(msg, 512);
            PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        }
        g_step = 1; g_stepDone = 0;
        spooler_clear(msg, 512);
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        g_stepDone = 1; g_step = -1;
    } else if (act == ACT_RESUME) {
        g_step = 2; g_stepDone = 1;
        spooler_start(msg, 512);
        PostMessageW(hwnd, WM_JOB_LOG, 0, (LPARAM)wdup(msg));
        g_stepDone = 2; g_step = -1;
    }
    PostMessageW(hwnd, WM_JOB_DONE, 1, 0);
    return 0;
}

static void start_job(int act)
{
    HANDLE th;
    if (g_busy) return;
    if (!is_admin()) {
        append_log(I18N(S_LOG_NEED_ADMIN));
        return;
    }
    if (act == ACT_RESET) {
        if (MessageBoxW(g_hwnd, I18N(S_CONFIRM_BODY), I18N(S_CONFIRM_TITLE),
                        MB_YESNO | MB_ICONWARNING | MB_DEFBUTTON2) != IDYES)
            return;
    }
    set_busy(1);
    th = CreateThread(NULL, 0, worker, (LPVOID)(INT_PTR)act, 0, NULL);
    if (th) CloseHandle(th);
}

static void draw_round_rect(HDC hdc, RECT *r, HBRUSH br)
{
    FillRect(hdc, r, br);
}

static void text_out(HDC hdc, int x, int y, int w, int h, const wchar_t *s, COLORREF c, HFONT f, UINT fmt)
{
    RECT rc;
    HFONT old;
    rc.left = x; rc.top = y; rc.right = x + w; rc.bottom = y + h;
    old = (HFONT)SelectObject(hdc, f);
    SetTextColor(hdc, c);
    SetBkMode(hdc, TRANSPARENT);
    DrawTextW(hdc, s, -1, &rc, fmt);
    SelectObject(hdc, old);
}

static void paint_ui(HWND hwnd, HDC hdc)
{
    RECT rc, card;
    wchar_t buf[256], word[32], size[32], st[64];
    COLORREF col;
    int y, i, admin = is_admin();
    GetClientRect(hwnd, &rc);
    FillRect(hdc, &rc, g_brBg);

    if (g_icon) DrawIconEx(hdc, 22, 18, g_icon, 40, 40, 0, NULL, DI_NORMAL);
    text_out(hdc, 72, 20, 320, 28, APP_TITLE, COL_TEXT, g_fontTitle, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);
    text_out(hdc, 72, 50, 400, 18, I18N(S_TAGLINE), COL_DIM, g_fontSmall, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);

    if (admin) {
        RECT chip = {410, 20, 478, 40};
        HBRUSH b = CreateSolidBrush(RGB(27, 61, 50));
        FillRect(hdc, &chip, b);
        DeleteObject(b);
        text_out(hdc, 410, 22, 68, 16, L"ADMIN", COL_OK, g_fontSmall, DT_CENTER);
    }

    y = 88;
    if (!admin) {
        RECT ban = {22, y, 478, y + 70};
        HBRUSH b = CreateSolidBrush(RGB(58, 30, 40));
        FillRect(hdc, &ban, b);
        DeleteObject(b);
        text_out(hdc, 32, y + 8, 430, 36, I18N(S_ADMIN_BANNER), COL_ERR, g_fontSmall, DT_LEFT | DT_WORDBREAK);
        y += 78;
    }

    card.left = 22; card.top = y; card.right = 478; card.bottom = y + 128 + (g_snap.printer_count > 0 ? g_snap.printer_count * 16 : 0);
    if (card.bottom > y + 176) card.bottom = y + 176;
    FillRect(hdc, &card, g_brCard);
    text_out(hdc, 36, y + 8, 200, 14, I18N(S_STATUS_HEADING), COL_MUTED, g_fontSmall, DT_LEFT);
    text_out(hdc, 320, y + 8, 140, 14, I18N(S_REFRESH), COL_ACCENT2, g_fontSmall, DT_RIGHT);

    col = g_snap.running ? COL_OK : COL_WARN;
    _snwprintf(st, 64, L"•  %s", state_text(g_snap.state));
    st[63] = 0;
    text_out(hdc, 36, y + 30, 180, 16, I18N(S_STATUS_SPOOLER), COL_DIM, g_font, DT_LEFT);
    text_out(hdc, 230, y + 30, 230, 16, st, col, g_fontBold, DT_RIGHT);

    text_out(hdc, 36, y + 50, 180, 16, I18N(S_STATUS_BUFFER), COL_DIM, g_font, DT_LEFT);
    if (!g_snap.buffer_ok) lstrcpynW(buf, I18N(S_BUFFER_NO_ACCESS), 256);
    else if (g_snap.buffer_files == 0) lstrcpynW(buf, I18N(S_BUFFER_EMPTY), 256);
    else {
        files_word(g_snap.buffer_files, word, 32);
        format_bytes(g_snap.buffer_bytes, size, 32);
        _snwprintf(buf, 256, L"%d %s  ·  %s", g_snap.buffer_files, word, size);
        buf[255] = 0;
    }
    text_out(hdc, 230, y + 50, 230, 16, buf, g_snap.buffer_files ? COL_WARN : COL_DIM, g_fontBold, DT_RIGHT);

    _snwprintf(buf, 256, L"%d", g_snap.job_total);
    text_out(hdc, 36, y + 70, 180, 16, I18N(S_STATUS_JOBS), COL_DIM, g_font, DT_LEFT);
    text_out(hdc, 230, y + 70, 230, 16, buf, g_snap.job_total ? COL_WARN : COL_DIM, g_fontBold, DT_RIGHT);

    _snwprintf(buf, 256, L"%d", g_snap.printer_count);
    text_out(hdc, 36, y + 90, 180, 16, I18N(S_STATUS_PRINTERS), COL_DIM, g_font, DT_LEFT);
    text_out(hdc, 230, y + 90, 230, 16, g_snap.printer_count ? buf : I18N(S_PRINTERS_NONE), COL_TEXT, g_fontBold, DT_RIGHT);

    for (i = 0; i < g_snap.printer_count && i < 3; i++) {
        wchar_t right[80];
        printer_status_text(g_snap.printers[i].status, right, 80);
        text_out(hdc, 36, y + 110 + i * 16, 260, 14, g_snap.printers[i].name, COL_DIM, g_fontSmall, DT_LEFT | DT_END_ELLIPSIS);
        text_out(hdc, 300, y + 110 + i * 16, 160, 14, right, COL_MUTED, g_fontSmall, DT_RIGHT);
    }

    /* steps */
    {
        int sy = admin ? 300 : 378;
        const wchar_t *names[3];
        names[0] = I18N(S_STEP_PAUSE);
        names[1] = I18N(S_STEP_CLEAR);
        names[2] = I18N(S_STEP_RESUME);
        for (i = 0; i < 3; i++) {
            int x = 50 + i * 150;
            RECT d = {x, sy, x + 28, sy + 22};
            wchar_t n[4];
            HBRUSH br;
            COLORREF tc = COL_MUTED;
            _snwprintf(n, 4, L"%d", i + 1);
            if (i <= g_stepDone) {
                br = CreateSolidBrush(COL_OK);
                tc = COL_BG;
                lstrcpynW(n, L"✓", 4);
            } else if (i == g_step) {
                br = g_brAccent;
                tc = RGB(255, 255, 255);
            } else br = g_brCard;
            FillRect(hdc, &d, br);
            if (i <= g_stepDone) DeleteObject(br);
            text_out(hdc, x, sy + 2, 28, 18, n, tc, g_fontBold, DT_CENTER);
            text_out(hdc, x - 30, sy + 26, 90, 16, names[i], (i == g_step || i <= g_stepDone) ? COL_TEXT : COL_MUTED, g_fontSmall, DT_CENTER);
            if (i < 2) {
                RECT line = {x + 34, sy + 10, x + 150 - 8, sy + 12};
                if (i <= g_stepDone - 1) {
                    HBRUSH okb = CreateSolidBrush(COL_OK);
                    FillRect(hdc, &line, okb);
                    DeleteObject(okb);
                } else {
                    FillRect(hdc, &line, g_brCard);
                }
            }
        }
    }

    text_out(hdc, 22, admin ? 548 : 626, 200, 14, I18N(S_LOG_HEADING), COL_MUTED, g_fontSmall, DT_LEFT);
    text_out(hdc, 22, admin ? 678 : 756, 280, 14, L"Print Queue Reset  ·  v" APP_VERSION, COL_MUTED, g_fontSmall, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);
    text_out(hdc, 300, admin ? 678 : 756, 178, 14, L"MIT", COL_ACCENT2, g_fontSmall, DT_RIGHT);
}

static void layout_controls(int admin)
{
    int y = admin ? 348 : 426;
    MoveWindow(g_btnReset, 22, y, 456, 52, TRUE);
    MoveWindow(g_btnPause, 22, y + 58, 146, 36, TRUE);
    MoveWindow(g_btnClear, 176, y + 58, 146, 36, TRUE);
    MoveWindow(g_btnResume, 332, y + 58, 146, 36, TRUE);
    MoveWindow(g_log, 22, y + 118, 456, 90, TRUE);
    if (!admin) {
        ShowWindow(g_btnAdmin, SW_SHOW);
        MoveWindow(g_btnAdmin, 32, 130, 436, 28, TRUE);
    } else {
        ShowWindow(g_btnAdmin, SW_HIDE);
    }
}

static void draw_button(DRAWITEMSTRUCT *d, const wchar_t *label, const wchar_t *sub, int kind)
{
    RECT r = d->rcItem;
    HDC hdc = d->hDC;
    HBRUSH br;
    COLORREF fg = COL_TEXT;
    int disabled = d->itemState & ODS_DISABLED;
    int pressed = d->itemState & ODS_SELECTED;
    if (kind == 1) { /* primary */
        br = disabled ? CreateSolidBrush(RGB(30, 58, 110)) : g_brAccent;
        fg = disabled ? RGB(138, 164, 212) : RGB(255, 255, 255);
    } else if (kind == 2) { /* danger */
        br = g_brDanger;
        fg = disabled ? RGB(122, 74, 88) : COL_ERR;
    } else {
        br = g_brBtn;
        fg = disabled ? COL_MUTED : COL_TEXT;
    }
    FillRect(hdc, &r, br);
    if (kind == 1) {
        /* don't delete g_brAccent */
    } else if (kind != 1 && kind != 2 && kind != 0) {
        DeleteObject(br);
    }
    if (pressed) OffsetRect(&r, 1, 1);
    if (sub && sub[0]) {
        RECT a = r, b = r;
        a.bottom = (r.top + r.bottom) / 2 + 4;
        b.top = a.bottom - 4;
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, fg);
        SelectObject(hdc, g_fontBold);
        DrawTextW(hdc, label, -1, &a, DT_CENTER | DT_BOTTOM | DT_SINGLELINE);
        SelectObject(hdc, g_fontSmall);
        DrawTextW(hdc, sub, -1, &b, DT_CENTER | DT_TOP | DT_SINGLELINE);
    } else {
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, fg);
        SelectObject(hdc, g_fontBold);
        DrawTextW(hdc, label, -1, &r, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    }
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg) {
    case WM_CREATE:
        g_hwnd = hwnd;
        dark_titlebar(hwnd);
        g_font = CreateFontW(-15, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Segoe UI");
        g_fontBold = CreateFontW(-15, 0, 0, 0, FW_SEMIBOLD, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Segoe UI");
        g_fontSmall = CreateFontW(-12, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Segoe UI");
        g_fontTitle = CreateFontW(-24, 0, 0, 0, FW_SEMIBOLD, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Segoe UI");
        g_fontMono = CreateFontW(-13, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Consolas");
        g_brBg = CreateSolidBrush(COL_BG);
        g_brCard = CreateSolidBrush(COL_CARD);
        g_brEdit = CreateSolidBrush(RGB(21, 27, 40));
        g_brAccent = CreateSolidBrush(COL_ACCENT);
        g_brBtn = CreateSolidBrush(COL_BTN);
        g_brDanger = CreateSolidBrush(COL_DANGER_BG);
        g_btnReset = CreateWindowW(L"BUTTON", I18N(S_RESET_QUEUE), WS_CHILD | WS_VISIBLE | BS_OWNERDRAW, 0, 0, 0, 0, hwnd, (HMENU)ID_RESET, NULL, NULL);
        g_btnPause = CreateWindowW(L"BUTTON", I18N(S_PAUSE), WS_CHILD | WS_VISIBLE | BS_OWNERDRAW, 0, 0, 0, 0, hwnd, (HMENU)ID_PAUSE, NULL, NULL);
        g_btnClear = CreateWindowW(L"BUTTON", I18N(S_CLEAR), WS_CHILD | WS_VISIBLE | BS_OWNERDRAW, 0, 0, 0, 0, hwnd, (HMENU)ID_CLEAR, NULL, NULL);
        g_btnResume = CreateWindowW(L"BUTTON", I18N(S_RESUME), WS_CHILD | WS_VISIBLE | BS_OWNERDRAW, 0, 0, 0, 0, hwnd, (HMENU)ID_RESUME, NULL, NULL);
        g_btnAdmin = CreateWindowW(L"BUTTON", I18N(S_RUN_AS_ADMIN), WS_CHILD | BS_OWNERDRAW, 0, 0, 0, 0, hwnd, (HMENU)ID_ADMIN, NULL, NULL);
        g_log = CreateWindowExW(0, L"EDIT", L"", WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_READONLY | ES_AUTOVSCROLL,
                                0, 0, 0, 0, hwnd, (HMENU)ID_LOG, NULL, NULL);
        SendMessageW(g_log, WM_SETFONT, (WPARAM)g_fontMono, TRUE);
        layout_controls(is_admin());
        refresh_status();
        if (is_admin()) append_log(I18N(S_LOG_READY));
        else append_log(I18N(S_LOG_NO_ADMIN));
        SetTimer(hwnd, ID_TIMER, 2500, NULL);
        return 0;

    case WM_ERASEBKGND:
        return 1;

    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);
        paint_ui(hwnd, hdc);
        EndPaint(hwnd, &ps);
        return 0;
    }

    case WM_DRAWITEM: {
        DRAWITEMSTRUCT *d = (DRAWITEMSTRUCT *)lParam;
        if (d->CtlID == ID_RESET) draw_button(d, I18N(S_RESET_QUEUE), I18N(S_RESET_SUB), 1);
        else if (d->CtlID == ID_PAUSE) draw_button(d, I18N(S_PAUSE), NULL, 2);
        else if (d->CtlID == ID_CLEAR) draw_button(d, I18N(S_CLEAR), NULL, 0);
        else if (d->CtlID == ID_RESUME) draw_button(d, I18N(S_RESUME), NULL, 0);
        else if (d->CtlID == ID_ADMIN) draw_button(d, I18N(S_RUN_AS_ADMIN), NULL, 1);
        return TRUE;
    }

    case WM_CTLCOLOREDIT:
        SetTextColor((HDC)wParam, COL_DIM);
        SetBkColor((HDC)wParam, RGB(21, 27, 40));
        return (LRESULT)g_brEdit;

    case WM_COMMAND:
        switch (LOWORD(wParam)) {
        case ID_RESET: start_job(ACT_RESET); break;
        case ID_PAUSE: start_job(ACT_PAUSE); break;
        case ID_CLEAR: start_job(ACT_CLEAR); break;
        case ID_RESUME: start_job(ACT_RESUME); break;
        case ID_ADMIN:
            if (relaunch_as_admin()) DestroyWindow(hwnd);
            else append_log(I18N(S_LOG_UAC_CANCEL));
            break;
        }
        return 0;

    case WM_LBUTTONUP: {
        POINT p;
        RECT rc;
        p.x = LOWORD(lParam); p.y = HIWORD(lParam);
        GetClientRect(hwnd, &rc);
        if (p.y > rc.bottom - 24 && p.x > rc.right - 180)
            MessageBoxW(hwnd, I18N(S_LICENSE_BODY), I18N(S_LICENSE_TITLE), MB_OK | MB_ICONINFORMATION);
        return 0;
    }

    case WM_TIMER:
        if (!g_busy) refresh_status();
        return 0;

    case WM_KEYDOWN:
        if (wParam == VK_F5) refresh_status();
        return 0;

    case WM_JOB_LOG:
        if (lParam) {
            append_log((const wchar_t *)lParam);
            HeapFree(GetProcessHeap(), 0, (void *)lParam);
        }
        InvalidateRect(hwnd, NULL, FALSE);
        return 0;

    case WM_JOB_DONE:
        g_busy = 0;
        refresh_status();
        return 0;

    case WM_DESTROY:
        KillTimer(hwnd, ID_TIMER);
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, LPWSTR cmd, int show)
{
    WNDCLASSEXW wc;
    HWND hwnd;
    MSG msg;
    RECT wr;
    int w = 516, h = 740;
    (void)prev; (void)cmd;

    {
        typedef BOOL (WINAPI *DpiFn)(void);
        HMODULE u32 = GetModuleHandleW(L"user32.dll");
        DpiFn dpi = u32 ? (DpiFn)GetProcAddress(u32, "SetProcessDPIAware") : NULL;
        if (dpi) dpi();
    }
    i18n_init();
    if (activate_existing()) return 0;

    g_icon = load_icon(40);
    ZeroMemory(&wc, sizeof(wc));
    wc.cbSize = sizeof(wc);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = inst;
    wc.hIcon = load_icon(32);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = CreateSolidBrush(COL_BG);
    wc.lpszClassName = APP_CLASS;
    wc.hIconSm = load_icon(16);
    if (!RegisterClassExW(&wc)) {
        MessageBoxW(NULL, L"RegisterClassExW failed.", APP_TITLE, MB_ICONERROR);
        return 1;
    }

    wr.left = 0; wr.top = 0; wr.right = w; wr.bottom = is_admin() ? 720 : 798;
    AdjustWindowRectEx(&wr, WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX, FALSE, 0);
    hwnd = CreateWindowExW(0, APP_CLASS, APP_TITLE,
                           WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_VISIBLE,
                           (GetSystemMetrics(SM_CXSCREEN) - (wr.right - wr.left)) / 2,
                           40,
                           wr.right - wr.left, wr.bottom - wr.top,
                           NULL, NULL, inst, NULL);
    if (!hwnd) {
        wchar_t err[128];
        _snwprintf(err, 128, L"CreateWindowExW failed (%u).", GetLastError());
        MessageBoxW(NULL, err, APP_TITLE, MB_ICONERROR);
        return 1;
    }
    ShowWindow(hwnd, show <= 0 ? SW_SHOW : show);
    UpdateWindow(hwnd);
    SetForegroundWindow(hwnd);

    while (GetMessageW(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return (int)msg.wParam;
}

/* TCC / mingw ANSI entry */
int WINAPI WinMain(HINSTANCE inst, HINSTANCE prev, LPSTR cmd, int show)
{
    (void)cmd;
    return wWinMain(inst, prev, GetCommandLineW(), show);
}
