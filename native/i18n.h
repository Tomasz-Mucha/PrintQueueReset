/* Print Queue Reset — UI strings.
 * Copyright (c) 2026 Tomasz Mucha
 * SPDX-License-Identifier: MIT
 */
#ifndef I18N_H
#define I18N_H

#include <wchar.h>

enum {
    S_TAGLINE,
    S_ADMIN_BANNER,
    S_RUN_AS_ADMIN,
    S_STATUS_HEADING,
    S_REFRESH,
    S_STATUS_SPOOLER,
    S_STATUS_BUFFER,
    S_STATUS_JOBS,
    S_STATUS_PRINTERS,
    S_STEP_PAUSE,
    S_STEP_CLEAR,
    S_STEP_RESUME,
    S_RESET_QUEUE,
    S_RESET_SUB,
    S_PAUSE,
    S_CLEAR,
    S_RESUME,
    S_LOG_HEADING,
    S_CONFIRM_TITLE,
    S_CONFIRM_BODY,
    S_BUFFER_NO_ACCESS,
    S_BUFFER_EMPTY,
    S_PRINTERS_NONE,
    S_LOG_UAC_CANCEL,
    S_LOG_NEED_ADMIN,
    S_LOG_NO_ADMIN,
    S_LOG_READY,
    S_STATE_STOPPED,
    S_STATE_START_PENDING,
    S_STATE_STOP_PENDING,
    S_STATE_RUNNING,
    S_STATE_CONTINUE_PENDING,
    S_STATE_PAUSE_PENDING,
    S_STATE_PAUSED,
    S_STATE_UNKNOWN,
    S_PRN_READY,
    S_PRN_PAUSED,
    S_PRN_ERROR,
    S_PRN_JAM,
    S_PRN_PAPER,
    S_PRN_OFFLINE,
    S_PRN_DOOR,
    S_PRN_PRINTING,
    S_PRN_BUSY,
    S_PRN_NA,
    S_ERR_OPEN_SCM,
    S_ERR_OPEN_SPOOLER,
    S_ERR_QUERY,
    S_ERR_STOP,
    S_ERR_START,
    S_ERR_OPEN_PROC,
    S_ERR_KILL_PROC,
    S_ERR_WAIT,
    S_ERR_CLEAR_RUNNING,
    S_ERR_CLEAR_FAIL,
    S_LOG_ALREADY_STOPPED,
    S_LOG_STOPPED,
    S_LOG_KILLED,
    S_LOG_ALREADY_RUNNING,
    S_LOG_STARTED,
    S_LOG_BUF_MISSING,
    S_LOG_BUF_EMPTY,
    S_LOG_BUF_CLEARED,
    S_LOG_PAUSING,
    S_LOG_CLEARING,
    S_LOG_RESUMING,
    S_LOG_DONE,
    S_LICENSE_TITLE,
    S_LICENSE_BODY,
    S_COUNT
};

void i18n_init(void);
const wchar_t *I18N(int id);
int i18n_lang(void); /* 0=en 1=pl 2=sv */
void files_word(int n, wchar_t *out, int outc);
void format_bytes(unsigned long long n, wchar_t *out, int outc);

#endif
