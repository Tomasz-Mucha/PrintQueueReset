"""Windows Print Spooler: status, stop, clear buffer, start.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import wintypes
from dataclasses import dataclass, field
from pathlib import Path

import i18n
from i18n import t

if sys.platform == "win32":
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    winspool = ctypes.WinDLL("winspool.drv", use_last_error=True)
else:
    # Pure helpers (formatting, license path) stay importable off Windows.
    advapi32 = None
    kernel32 = None
    winspool = None

SERVICE_NAME = "Spooler"
PROCESS_NAME = "spoolsv.exe"

SC_MANAGER_CONNECT = 0x0001
SERVICE_QUERY_STATUS = 0x0004
SERVICE_START = 0x0010
SERVICE_STOP = 0x0020
SERVICE_PAUSE_CONTINUE = 0x0040
SC_STATUS_PROCESS_INFO = 0
SERVICE_CONTROL_STOP = 0x0001

SERVICE_STOPPED = 0x00000001
SERVICE_START_PENDING = 0x00000002
SERVICE_STOP_PENDING = 0x00000003
SERVICE_RUNNING = 0x00000004
SERVICE_CONTINUE_PENDING = 0x00000005
SERVICE_PAUSE_PENDING = 0x00000006
SERVICE_PAUSED = 0x00000007

STATE_KEYS = {
    SERVICE_STOPPED: "state_stopped",
    SERVICE_START_PENDING: "state_start_pending",
    SERVICE_STOP_PENDING: "state_stop_pending",
    SERVICE_RUNNING: "state_running",
    SERVICE_CONTINUE_PENDING: "state_continue_pending",
    SERVICE_PAUSE_PENDING: "state_pause_pending",
    SERVICE_PAUSED: "state_paused",
}

PRINTER_ENUM_LOCAL = 0x00000002
PRINTER_ENUM_CONNECTIONS = 0x00000004

PRINTER_STATUS_PAUSED = 0x00000001
PRINTER_STATUS_ERROR = 0x00000002
PRINTER_STATUS_PAPER_JAM = 0x00000008
PRINTER_STATUS_PAPER_OUT = 0x00000010
PRINTER_STATUS_OFFLINE = 0x00000080
PRINTER_STATUS_BUSY = 0x00000200
PRINTER_STATUS_PRINTING = 0x00000400
PRINTER_STATUS_NOT_AVAILABLE = 0x00001000
PRINTER_STATUS_DOOR_OPEN = 0x00400000

PROCESS_TERMINATE = 0x0001


class SERVICE_STATUS(ctypes.Structure):
    _fields_ = [
        ("dwServiceType", wintypes.DWORD),
        ("dwCurrentState", wintypes.DWORD),
        ("dwControlsAccepted", wintypes.DWORD),
        ("dwWin32ExitCode", wintypes.DWORD),
        ("dwServiceSpecificExitCode", wintypes.DWORD),
        ("dwCheckPoint", wintypes.DWORD),
        ("dwWaitHint", wintypes.DWORD),
    ]


class SERVICE_STATUS_PROCESS(ctypes.Structure):
    _fields_ = [
        ("dwServiceType", wintypes.DWORD),
        ("dwCurrentState", wintypes.DWORD),
        ("dwControlsAccepted", wintypes.DWORD),
        ("dwWin32ExitCode", wintypes.DWORD),
        ("dwServiceSpecificExitCode", wintypes.DWORD),
        ("dwCheckPoint", wintypes.DWORD),
        ("dwWaitHint", wintypes.DWORD),
        ("dwProcessId", wintypes.DWORD),
        ("dwServiceFlags", wintypes.DWORD),
    ]


class PRINTER_INFO_2(ctypes.Structure):
    _fields_ = [
        ("pServerName", wintypes.LPWSTR),
        ("pPrinterName", wintypes.LPWSTR),
        ("pShareName", wintypes.LPWSTR),
        ("pPortName", wintypes.LPWSTR),
        ("pDriverName", wintypes.LPWSTR),
        ("pComment", wintypes.LPWSTR),
        ("pLocation", wintypes.LPWSTR),
        ("pDevMode", ctypes.c_void_p),
        ("pSepFile", wintypes.LPWSTR),
        ("pPrintProcessor", wintypes.LPWSTR),
        ("pDatatype", wintypes.LPWSTR),
        ("pParameters", wintypes.LPWSTR),
        ("pSecurityDescriptor", ctypes.c_void_p),
        ("Attributes", wintypes.DWORD),
        ("Priority", wintypes.DWORD),
        ("DefaultPriority", wintypes.DWORD),
        ("StartTime", wintypes.DWORD),
        ("UntilTime", wintypes.DWORD),
        ("Status", wintypes.DWORD),
        ("cJobs", wintypes.DWORD),
        ("AveragePPM", wintypes.DWORD),
    ]


if sys.platform == "win32":
    advapi32.OpenSCManagerW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    advapi32.OpenSCManagerW.restype = wintypes.HANDLE
    advapi32.OpenServiceW.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR, wintypes.DWORD]
    advapi32.OpenServiceW.restype = wintypes.HANDLE
    advapi32.CloseServiceHandle.argtypes = [wintypes.HANDLE]
    advapi32.CloseServiceHandle.restype = wintypes.BOOL
    advapi32.QueryServiceStatusEx.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    advapi32.QueryServiceStatusEx.restype = wintypes.BOOL
    advapi32.ControlService.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        ctypes.POINTER(SERVICE_STATUS),
    ]
    advapi32.ControlService.restype = wintypes.BOOL
    advapi32.StartServiceW.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p]
    advapi32.StartServiceW.restype = wintypes.BOOL

    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    winspool.EnumPrintersW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    winspool.EnumPrintersW.restype = wintypes.BOOL


class SpoolerError(RuntimeError):
    pass


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def bundle_dir() -> Path:
    """PyInstaller onefile unpacks data into sys._MEIPASS."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return project_root()


def assets_dir() -> Path:
    return bundle_dir() / "assets"


def license_path() -> Path:
    bundled = bundle_dir() / "LICENSE"
    if bundled.is_file():
        return bundled
    return project_root() / "LICENSE"


def relaunch_as_admin() -> bool:
    """Ask for elevation. Returns True if the elevated process was launched."""
    import subprocess

    root = project_root()
    extra = [a for a in sys.argv[1:] if a]
    if getattr(sys, "frozen", False):
        exe = sys.executable
        params = subprocess.list2cmdline(extra)
    else:
        exe = sys.executable
        script = Path(__file__).resolve().parent / "run.py"
        if not script.exists():
            script = Path(sys.argv[0]).resolve()
        params = subprocess.list2cmdline([str(script), *extra])
    rc = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe, params, str(root), 1
    )
    return rc > 32


def spool_directory() -> Path:
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    # 32-bit Python on 64-bit Windows sees a redirected System32.
    if sys.maxsize <= 2**32 and os.environ.get("PROCESSOR_ARCHITEW6432"):
        return system_root / "SysNative" / "spool" / "PRINTERS"
    return system_root / "System32" / "spool" / "PRINTERS"


def format_bytes(n: int) -> str:
    sep = "." if i18n.language() == "en" else ","
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB".replace(".", sep)
    return f"{n / (1024 * 1024):.1f} MB".replace(".", sep)


def printer_status_label(status: int) -> str:
    if status == 0:
        return t("printer_ready")
    parts: list[str] = []
    mapping = (
        (PRINTER_STATUS_PAUSED, "printer_paused"),
        (PRINTER_STATUS_ERROR, "printer_error"),
        (PRINTER_STATUS_PAPER_JAM, "printer_paper_jam"),
        (PRINTER_STATUS_PAPER_OUT, "printer_paper_out"),
        (PRINTER_STATUS_OFFLINE, "printer_offline"),
        (PRINTER_STATUS_DOOR_OPEN, "printer_door_open"),
        (PRINTER_STATUS_PRINTING, "printer_printing"),
        (PRINTER_STATUS_BUSY, "printer_busy"),
        (PRINTER_STATUS_NOT_AVAILABLE, "printer_not_available"),
    )
    for flag, key in mapping:
        if status & flag:
            parts.append(t(key))
    return ", ".join(parts) if parts else t("printer_status_hex", status=status)


def state_label(state: int) -> str:
    return t(STATE_KEYS.get(state, "state_unknown"))


@dataclass
class PrinterInfo:
    name: str
    port: str
    jobs: int
    status: int

    @property
    def status_label(self) -> str:
        return printer_status_label(self.status)


@dataclass
class BufferInfo:
    path: Path
    files: int
    bytes: int
    names: list[str] = field(default_factory=list)
    accessible: bool = True


@dataclass
class SpoolerSnapshot:
    state: int
    state_label: str
    pid: int
    running: bool
    buffer: BufferInfo
    printers: list[PrinterInfo]
    jobs: int

    @property
    def can_pause(self) -> bool:
        return self.state in (SERVICE_RUNNING, SERVICE_PAUSED, SERVICE_START_PENDING)

    @property
    def can_resume(self) -> bool:
        return self.state in (SERVICE_STOPPED, SERVICE_PAUSED)


class _ServiceHandle:
    def __init__(self, access: int) -> None:
        self._scm = advapi32.OpenSCManagerW(None, None, SC_MANAGER_CONNECT)
        if not self._scm:
            raise SpoolerError(_win_error(t("err_open_scm")))
        self._svc = advapi32.OpenServiceW(self._scm, SERVICE_NAME, access)
        if not self._svc:
            advapi32.CloseServiceHandle(self._scm)
            raise SpoolerError(_win_error(t("err_open_spooler")))

    def __enter__(self) -> "_ServiceHandle":
        return self

    def __exit__(self, *exc: object) -> None:
        if self._svc:
            advapi32.CloseServiceHandle(self._svc)
        if self._scm:
            advapi32.CloseServiceHandle(self._scm)

    def query(self) -> SERVICE_STATUS_PROCESS:
        status = SERVICE_STATUS_PROCESS()
        needed = wintypes.DWORD()
        ok = advapi32.QueryServiceStatusEx(
            self._svc,
            SC_STATUS_PROCESS_INFO,
            ctypes.byref(status),
            ctypes.sizeof(status),
            ctypes.byref(needed),
        )
        if not ok:
            raise SpoolerError(_win_error(t("err_query_status")))
        return status


def _win_error(prefix: str) -> str:
    code = ctypes.get_last_error()
    if code == 5:
        return t("err_access_denied", prefix=prefix)
    if code == 1062:
        return t("err_already_stopped", prefix=prefix)
    if code == 1056:
        return t("err_already_running", prefix=prefix)
    try:
        msg = ctypes.FormatError(code)
    except Exception:
        msg = ""
    extra = f" {msg}" if msg else ""
    return t("err_with_code", prefix=prefix, code=code, extra=extra)


def query_service() -> SERVICE_STATUS_PROCESS:
    with _ServiceHandle(SERVICE_QUERY_STATUS) as svc:
        return svc.query()


def read_buffer() -> BufferInfo:
    path = spool_directory()
    names: list[str] = []
    total = 0
    try:
        exists = path.is_dir()
    except OSError:
        return BufferInfo(path=path, files=0, bytes=0, accessible=False)
    if exists:
        try:
            items = list(path.iterdir())
        except OSError:
            return BufferInfo(path=path, files=0, bytes=0, accessible=False)
        for item in items:
            if item.is_file():
                names.append(item.name)
                try:
                    total += item.stat().st_size
                except OSError:
                    pass
    names.sort()
    return BufferInfo(path=path, files=len(names), bytes=total, names=names, accessible=True)


def enum_printers() -> list[PrinterInfo]:
    flags = PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS
    needed = wintypes.DWORD()
    returned = wintypes.DWORD()
    winspool.EnumPrintersW(
        flags, None, 2, None, 0, ctypes.byref(needed), ctypes.byref(returned)
    )
    if needed.value == 0:
        return []
    buf = (ctypes.c_byte * needed.value)()
    ok = winspool.EnumPrintersW(
        flags,
        None,
        2,
        ctypes.byref(buf),
        needed.value,
        ctypes.byref(needed),
        ctypes.byref(returned),
    )
    if not ok:
        return []
    array = ctypes.cast(buf, ctypes.POINTER(PRINTER_INFO_2))
    printers: list[PrinterInfo] = []
    for i in range(returned.value):
        info = array[i]
        name = info.pPrinterName or ""
        if not name:
            continue
        printers.append(
            PrinterInfo(
                name=name,
                port=info.pPortName or "",
                jobs=int(info.cJobs),
                status=int(info.Status),
            )
        )
    printers.sort(key=lambda p: p.name.lower())
    return printers


def snapshot() -> SpoolerSnapshot:
    try:
        status = query_service()
        state = int(status.dwCurrentState)
        pid = int(status.dwProcessId)
    except SpoolerError:
        state = 0
        pid = 0
    try:
        buffer = read_buffer()
    except OSError:
        buffer = BufferInfo(path=spool_directory(), files=0, bytes=0, accessible=False)
    try:
        printers = enum_printers()
    except OSError:
        printers = []
    jobs = sum(p.jobs for p in printers)
    return SpoolerSnapshot(
        state=state,
        state_label=state_label(state),
        pid=pid,
        running=state == SERVICE_RUNNING,
        buffer=buffer,
        printers=printers,
        jobs=jobs,
    )


def _wait_for_state(wanted: int, timeout: float) -> SERVICE_STATUS_PROCESS:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = query_service()
        if last.dwCurrentState == wanted:
            return last
        hint = max(last.dwWaitHint, 200)
        time.sleep(min(hint / 1000.0, 0.4))
    raise SpoolerError(t("err_wait_state", state=state_label(wanted)))


def _terminate_pid(pid: int) -> None:
    if pid <= 0:
        return
    handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not handle:
        raise SpoolerError(_win_error(t("err_open_process")))
    try:
        if not kernel32.TerminateProcess(handle, 1):
            raise SpoolerError(_win_error(t("err_kill_process")))
    finally:
        kernel32.CloseHandle(handle)


def stop_spooler(timeout: float = 12.0, force: bool = True) -> str:
    """Stop the Print Spooler. Returns a localized status message."""
    status = query_service()
    if status.dwCurrentState == SERVICE_STOPPED:
        return t("log_spooler_already_stopped")
    pid = int(status.dwProcessId)
    access = SERVICE_QUERY_STATUS | SERVICE_STOP
    try:
        with _ServiceHandle(access) as svc:
            st = SERVICE_STATUS()
            if not advapi32.ControlService(svc._svc, SERVICE_CONTROL_STOP, ctypes.byref(st)):
                code = ctypes.get_last_error()
                if code != 1062:
                    if not force:
                        raise SpoolerError(_win_error(t("err_stop_spooler")))
    except SpoolerError:
        if not force:
            raise
    try:
        _wait_for_state(SERVICE_STOPPED, timeout)
        return t("log_spooler_stopped")
    except SpoolerError:
        if not force:
            raise
        _terminate_pid(pid)
        _wait_for_state(SERVICE_STOPPED, 8.0)
        return t("log_spooler_killed")


def start_spooler(timeout: float = 12.0) -> str:
    status = query_service()
    if status.dwCurrentState == SERVICE_RUNNING:
        return t("log_spooler_already_running")
    with _ServiceHandle(SERVICE_QUERY_STATUS | SERVICE_START) as svc:
        if not advapi32.StartServiceW(svc._svc, 0, None):
            code = ctypes.get_last_error()
            if code != 1056:
                raise SpoolerError(_win_error(t("err_start_spooler")))
    _wait_for_state(SERVICE_RUNNING, timeout)
    return t("log_spooler_started")


def clear_buffer() -> str:
    """Delete SPL/SHD and other files in the printer spool folder."""
    status = query_service()
    if status.dwCurrentState not in (SERVICE_STOPPED, SERVICE_STOP_PENDING):
        raise SpoolerError(t("err_clear_while_running"))
    path = spool_directory()
    if not path.is_dir():
        return t("log_buffer_missing", path=path)
    removed = 0
    failed: list[str] = []
    for item in list(path.iterdir()):
        try:
            if item.is_file():
                item.unlink()
                removed += 1
            elif item.is_dir():
                for child in item.rglob("*"):
                    if child.is_file():
                        child.unlink()
                        removed += 1
                item.rmdir()
        except OSError as exc:
            failed.append(f"{item.name}: {exc}")
    leftover = read_buffer()
    if leftover.files:
        detail = "; ".join(failed[:4]) if failed else ", ".join(leftover.names[:4])
        raise SpoolerError(t("err_clear_failed", n=leftover.files, detail=detail))
    if removed == 0:
        return t("log_buffer_was_empty")
    return t("log_buffer_cleared", n=removed)


def reset_queue(progress=None) -> list[str]:
    """Pause spooler, clear buffer, resume.

    `progress` is callable(step_index, message, kind) where kind is 'info' or 'ok'.
    """
    log: list[str] = []

    def report(step: int, message: str, kind: str = "ok") -> None:
        log.append(message)
        if progress:
            progress(step, message, kind)

    report(0, t("log_pausing"), "info")
    report(0, stop_spooler())
    report(1, t("log_clearing"), "info")
    report(1, clear_buffer())
    report(2, t("log_resuming"), "info")
    report(2, start_spooler())
    report(2, t("log_done"))
    return log
