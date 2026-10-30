/* Print Queue Reset — spooler service helpers.
 * Copyright (c) 2026 Tomasz Mucha
 * SPDX-License-Identifier: MIT
 */
#ifndef SPOOLER_H
#define SPOOLER_H

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>

#define MAX_PRINTERS 32
#define MAX_PRN_NAME 128

typedef struct {
    wchar_t name[MAX_PRN_NAME];
    DWORD status;
    DWORD jobs;
} PrinterInfo;

typedef struct {
    DWORD state;
    DWORD pid;
    int running;
    int can_pause;
    int can_resume;
    int buffer_ok;
    int buffer_files;
    unsigned long long buffer_bytes;
    int printer_count;
    int job_total;
    PrinterInfo printers[MAX_PRINTERS];
} SpoolerSnap;

int is_admin(void);
int relaunch_as_admin(void);
void spooler_snapshot(SpoolerSnap *s);
const wchar_t *state_text(DWORD state);
void printer_status_text(DWORD status, wchar_t *out, int outc);
int spooler_stop(wchar_t *msg, int msgc);
int spooler_start(wchar_t *msg, int msgc);
int spooler_clear(wchar_t *msg, int msgc);

#endif
