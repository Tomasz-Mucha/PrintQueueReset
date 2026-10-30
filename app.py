"""Print Queue Reset — pause printing, clear the spooler buffer, resume.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import ctypes
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import font as tkfont

import i18n
import spooler
from i18n import t

APP_NAME = "Print Queue Reset"
APP_VERSION = "1.0.0"
LICENSE_ID = "MIT"
COPYRIGHT = "Copyright (c) 2026 Tomasz Mucha"

# Dark theme
BG = "#10151F"
BG_CARD = "#1A2030"
BG_CARD_ALT = "#151B28"
BG_HOVER = "#243044"
ACCENT = "#0D6EFD"
ACCENT_HOVER = "#3D8BFF"
ACCENT_DIM = "#0A58CA"
TEXT = "#E8EEF7"
TEXT_DIM = "#9AA8BC"
TEXT_MUTED = "#6E7B8F"
LINE = "#2A3348"
SUCCESS = "#3DDC97"
WARN = "#FFB020"
DANGER = "#FF5C7A"
GREEN_DIM = "#1B3D32"
RED_DIM = "#3A1E28"


def enable_dpi_awareness() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def apply_dark_titlebar(root: tk.Tk) -> None:
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        if not hwnd:
            hwnd = root.winfo_id()
        value = ctypes.c_int(1)
        dwm = ctypes.windll.dwmapi
        # 20 = DWMWA_USE_IMMERSIVE_DARK_MODE (Win 10 1809+ / Win 11)
        dwm.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), 4)
        dwm.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), 4)
    except Exception:
        pass


def set_app_id() -> None:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "PrintQueueReset"
        )
    except Exception:
        pass


def _window_rect(hwnd: int) -> tuple[int, int, int, int] | None:
    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    rect = RECT()
    if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def activate_existing() -> bool:
    """Restore a living instance. Ignore hung/elevated windows we cannot un-minimize."""
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, APP_NAME)
    if not hwnd:
        return False
    SW_RESTORE = 9
    try:
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
    except Exception:
        return False
    pos = _window_rect(hwnd)
    if pos is None or pos[0] <= -10000 or pos[1] <= -10000:
        return False
    return True


def show_crash(message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, message[:2000], APP_NAME, 0x10)
    except Exception:
        pass


class FlatButton(tk.Frame):
    def __init__(
        self,
        master,
        text: str,
        command,
        *,
        variant: str = "secondary",
        width: int = 0,
        subtitle: str | None = None,
    ) -> None:
        super().__init__(master, bg=master.cget("bg"), highlightthickness=0)
        self._command = command
        self._variant = variant
        self._enabled = True
        self._subtitle = subtitle

        if variant == "primary":
            self._bg, self._fg, self._hover, self._disabled_bg, self._disabled_fg = (
                ACCENT,
                "#FFFFFF",
                ACCENT_HOVER,
                "#1E3A6E",
                "#8AA4D4",
            )
        elif variant == "danger":
            self._bg, self._fg, self._hover, self._disabled_bg, self._disabled_fg = (
                "#2A1C24",
                DANGER,
                "#3A2430",
                "#241820",
                "#7A4A58",
            )
        else:
            self._bg, self._fg, self._hover, self._disabled_bg, self._disabled_fg = (
                BG_HOVER,
                TEXT,
                "#2C3A52",
                "#182030",
                TEXT_MUTED,
            )

        pad_y = 14 if subtitle else 10
        self._btn = tk.Label(
            self,
            text=text,
            bg=self._bg,
            fg=self._fg,
            font=("Segoe UI Semibold", 11 if not subtitle else 12),
            padx=16,
            pady=pad_y,
            cursor="hand2",
            justify="center",
        )
        if width:
            self._btn.configure(width=width)
        self._btn.pack(fill="both", expand=True)
        if subtitle:
            self._btn.configure(text=f"{text}\n{subtitle}", font=("Segoe UI Semibold", 11))

        for w in (self, self._btn):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def configure_text(self, text: str) -> None:
        if self._subtitle:
            self._btn.configure(text=f"{text}\n{self._subtitle}")
        else:
            self._btn.configure(text=text)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if enabled:
            self._btn.configure(bg=self._bg, fg=self._fg, cursor="hand2")
        else:
            self._btn.configure(
                bg=self._disabled_bg, fg=self._disabled_fg, cursor="arrow"
            )

    def _on_enter(self, _e=None) -> None:
        if self._enabled:
            self._btn.configure(bg=self._hover)

    def _on_leave(self, _e=None) -> None:
        if self._enabled:
            self._btn.configure(bg=self._bg)

    def _on_click(self, _e=None) -> None:
        if self._enabled and self._command:
            self._command()


class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, title: str, body: str) -> None:
        super().__init__(parent)
        self.result = False
        self.configure(bg=BG)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        wrap = tk.Frame(self, bg=BG, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)
        tk.Label(
            wrap,
            text=title,
            bg=BG,
            fg=TEXT,
            font=("Segoe UI Semibold", 13),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            wrap,
            text=body,
            bg=BG,
            fg=TEXT_DIM,
            font=("Segoe UI", 10),
            wraplength=360,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(8, 18))

        row = tk.Frame(wrap, bg=BG)
        row.pack(fill="x")
        FlatButton(row, t("cancel"), self._no, variant="secondary").pack(
            side="right", padx=(8, 0)
        )
        FlatButton(row, t("confirm_reset"), self._yes, variant="primary").pack(
            side="right"
        )

        self.bind("<Escape>", lambda e: self._no())
        self.bind("<Return>", lambda e: self._yes())
        self.protocol("WM_DELETE_WINDOW", self._no)
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")
        apply_dark_titlebar(self)
        self.wait_window()

    def _yes(self) -> None:
        self.result = True
        self.destroy()

    def _no(self) -> None:
        self.result = False
        self.destroy()


class LicenseDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title(t("license_title"))
        self.configure(bg=BG)
        self.resizable(True, True)
        self.transient(parent)
        self.minsize(520, 420)
        self.geometry("640x520")

        wrap = tk.Frame(self, bg=BG, padx=18, pady=14)
        wrap.pack(fill="both", expand=True)
        tk.Label(
            wrap,
            text=f"{APP_NAME}  ·  {LICENSE_ID}",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI Semibold", 12),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            wrap,
            text=t("license_summary", copyright=COPYRIGHT),
            bg=BG,
            fg=TEXT_DIM,
            font=("Segoe UI", 9),
            wraplength=580,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(8, 12))

        text = tk.Text(
            wrap,
            bg=BG_CARD_ALT,
            fg=TEXT_DIM,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 8),
            wrap="word",
            padx=10,
            pady=8,
            highlightthickness=0,
        )
        scroll = tk.Scrollbar(wrap, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        body = tk.Frame(wrap, bg=BG)
        body.pack(fill="both", expand=True)
        text.pack(in_=body, side="left", fill="both", expand=True)
        scroll.pack(in_=body, side="right", fill="y")
        try:
            license_text = spooler.license_path().read_text(encoding="utf-8")
        except OSError:
            license_text = t("license_missing")
        text.insert("1.0", license_text)
        text.configure(state="disabled")

        FlatButton(wrap, t("close"), self.destroy, variant="secondary").pack(
            anchor="e", pady=(12, 0)
        )
        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        apply_dark_titlebar(self)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.configure(bg=BG)
        self.resizable(False, False)
        self._busy = False
        self._refresh_job: str | None = None
        self._step_dots: list[tk.Label] = []
        self._step_labels: list[tk.Label] = []
        self._step_lines: list[tk.Frame] = []

        self._load_fonts()
        self._load_icon()
        self._build()
        apply_dark_titlebar(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<F5>", lambda e: self.refresh())
        self.refresh()
        self._schedule_refresh()

        self.update_idletasks()
        w = 500
        max_h = max(480, self.winfo_screenheight() - 80)
        h = min(self.winfo_reqheight(), max_h)
        x = max(0, (self.winfo_screenwidth() - w) // 2)
        y = max(0, (self.winfo_screenheight() - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()
        self.lift()
        try:
            self.attributes("-topmost", True)
            self.after(500, lambda: self.attributes("-topmost", False))
        except Exception:
            pass
        self.focus_force()

    def _load_fonts(self) -> None:
        available = set(tkfont.families())
        self.font_ui = "Segoe UI" if "Segoe UI" in available else "Calibri"
        self.font_bold = (
            "Segoe UI Semibold" if "Segoe UI Semibold" in available else self.font_ui
        )

    def _assets(self) -> Path:
        return spooler.assets_dir()

    def _load_icon(self) -> None:
        ico = self._assets() / "icon.ico"
        png = self._assets() / "icon.png"
        try:
            if ico.exists():
                self.iconbitmap(default=str(ico))
        except Exception:
            pass
        try:
            if png.exists():
                self._icon_img = tk.PhotoImage(file=str(png))
                self.iconphoto(True, self._icon_img)
                self._header_icon = self._icon_img.subsample(4, 4)
            else:
                self._header_icon = None
        except Exception:
            self._header_icon = None

    def _build(self) -> None:
        root = tk.Frame(self, bg=BG, padx=22, pady=18)
        root.pack(fill="both", expand=True)

        self._header = self._build_header(root)
        self._build_admin_banner(root)
        self._status_card = self._build_status_card(root)
        self._build_steps(root)
        self._build_actions(root)
        self._build_log(root)
        self._build_footer(root)

    def _build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", pady=(0, 14))

        if self._header_icon is not None:
            tk.Label(header, image=self._header_icon, bg=BG).pack(
                side="left", padx=(0, 12)
            )

        titles = tk.Frame(header, bg=BG)
        titles.pack(side="left", fill="x", expand=True)
        tk.Label(
            titles,
            text=APP_NAME,
            bg=BG,
            fg=TEXT,
            font=(self.font_bold, 18),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            titles,
            text=t("tagline"),
            bg=BG,
            fg=TEXT_DIM,
            font=(self.font_ui, 9),
            anchor="w",
        ).pack(fill="x")

        self.admin_chip = tk.Label(
            header,
            text="ADMIN",
            bg=GREEN_DIM,
            fg=SUCCESS,
            font=(self.font_bold, 8),
            padx=10,
            pady=5,
        )
        self.admin_chip.pack(side="right", anchor="n")
        return header

    def _build_admin_banner(self, parent: tk.Frame) -> None:
        self.admin_banner = tk.Frame(parent, bg=RED_DIM)
        inner = tk.Frame(self.admin_banner, bg=RED_DIM, padx=12, pady=10)
        inner.pack(fill="x")
        tk.Label(
            inner,
            text=t("admin_banner"),
            bg=RED_DIM,
            fg=DANGER,
            font=(self.font_ui, 9),
            wraplength=440,
            justify="left",
            anchor="w",
        ).pack(fill="x")
        self._elevate_btn = FlatButton(
            inner, t("run_as_admin"), self._elevate, variant="primary"
        )
        self._elevate_btn.pack(fill="x", pady=(8, 0))

    def _build_status_card(self, parent: tk.Frame) -> None:
        card = tk.Frame(parent, bg=BG_CARD, padx=16, pady=14)
        card.pack(fill="x", pady=(0, 14))

        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill="x")
        tk.Label(
            top,
            text=t("status_heading"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=(self.font_bold, 8),
            anchor="w",
        ).pack(side="left")
        self.refresh_link = tk.Label(
            top,
            text=t("refresh"),
            bg=BG_CARD,
            fg=ACCENT_HOVER,
            font=(self.font_ui, 8),
            cursor="hand2",
        )
        self.refresh_link.pack(side="right")
        self.refresh_link.bind("<Button-1>", lambda e: self.refresh())

        self.status_rows: dict[str, tuple[tk.Label, tk.Label]] = {}
        for key, label in (
            ("spooler", t("status_spooler")),
            ("buffer", t("status_buffer")),
            ("jobs", t("status_jobs")),
            ("printers", t("status_printers")),
        ):
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", pady=(8, 0))
            left = tk.Label(
                row,
                text=label,
                bg=BG_CARD,
                fg=TEXT_DIM,
                font=(self.font_ui, 10),
                anchor="w",
            )
            left.pack(side="left")
            right = tk.Label(
                row,
                text="—",
                bg=BG_CARD,
                fg=TEXT,
                font=(self.font_bold, 10),
                anchor="e",
            )
            right.pack(side="right")
            self.status_rows[key] = (left, right)

        self.printer_box = tk.Frame(card, bg=BG_CARD)
        self.printer_box.pack(fill="x", pady=(6, 0))
        return card

    def _build_steps(self, parent: tk.Frame) -> None:
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x", pady=(0, 14))

        names = (t("step_pause"), t("step_clear"), t("step_resume"))
        for i, name in enumerate(names):
            col = tk.Frame(wrap, bg=BG)
            col.pack(side="left")
            dot = tk.Label(
                col,
                text=str(i + 1),
                bg=BG_CARD,
                fg=TEXT_DIM,
                font=(self.font_bold, 9),
                width=3,
                pady=4,
            )
            dot.pack()
            lbl = tk.Label(
                col,
                text=name,
                bg=BG,
                fg=TEXT_MUTED,
                font=(self.font_ui, 8),
            )
            lbl.pack(pady=(4, 0))
            self._step_dots.append(dot)
            self._step_labels.append(lbl)
            if i < len(names) - 1:
                line_holder = tk.Frame(wrap, bg=BG)
                line_holder.pack(side="left", fill="x", expand=True, padx=6, pady=(10, 18))
                line = tk.Frame(line_holder, bg=LINE, height=2)
                line.pack(fill="x")
                self._step_lines.append(line)

        self._set_steps(-1)

    def _set_steps(self, active: int, done_through: int = -1) -> None:
        for i, (dot, lbl) in enumerate(zip(self._step_dots, self._step_labels)):
            if i <= done_through:
                dot.configure(bg=SUCCESS, fg=BG, text="✓")
                lbl.configure(fg=SUCCESS)
            elif i == active:
                dot.configure(bg=ACCENT, fg="#FFFFFF", text=str(i + 1))
                lbl.configure(fg=TEXT)
            else:
                dot.configure(bg=BG_CARD, fg=TEXT_DIM, text=str(i + 1))
                lbl.configure(fg=TEXT_MUTED)
        for i, line in enumerate(self._step_lines):
            line.configure(bg=SUCCESS if i <= done_through - 1 else LINE)

    def _build_actions(self, parent: tk.Frame) -> None:
        self.primary = FlatButton(
            parent,
            t("reset_queue"),
            self._on_reset,
            variant="primary",
            subtitle=t("reset_subtitle"),
        )
        self.primary.pack(fill="x", pady=(0, 8))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=(0, 14))
        row.columnconfigure((0, 1, 2), weight=1)

        self.btn_pause = FlatButton(row, t("pause"), self._on_pause, variant="danger")
        self.btn_clear = FlatButton(row, t("clear_buffer"), self._on_clear)
        self.btn_resume = FlatButton(row, t("resume"), self._on_resume)
        self.btn_pause.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.btn_clear.grid(row=0, column=1, sticky="ew", padx=3)
        self.btn_resume.grid(row=0, column=2, sticky="ew", padx=(6, 0))

    def _build_log(self, parent: tk.Frame) -> None:
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=10)
        card.pack(fill="both", expand=True, pady=(0, 10))
        tk.Label(
            card,
            text=t("log_heading"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=(self.font_bold, 8),
            anchor="w",
        ).pack(fill="x")
        self.log = tk.Text(
            card,
            height=5,
            bg=BG_CARD_ALT,
            fg=TEXT_DIM,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 9),
            wrap="word",
            state="disabled",
            padx=10,
            pady=8,
            highlightthickness=0,
        )
        self.log.pack(fill="both", expand=True, pady=(8, 0))
        self.log.tag_configure("ok", foreground=SUCCESS)
        self.log.tag_configure("err", foreground=DANGER)
        self.log.tag_configure("info", foreground=ACCENT_HOVER)
        self.log.tag_configure("dim", foreground=TEXT_MUTED)

    def _build_footer(self, parent: tk.Frame) -> None:
        foot = tk.Frame(parent, bg=BG)
        foot.pack(fill="x")
        tk.Label(
            foot,
            text=f"{APP_NAME}  ·  v{APP_VERSION}",
            bg=BG,
            fg=TEXT_MUTED,
            font=(self.font_ui, 8),
            anchor="w",
        ).pack(side="left")
        license_link = tk.Label(
            foot,
            text=LICENSE_ID,
            bg=BG,
            fg=ACCENT_HOVER,
            font=(self.font_ui, 8),
            anchor="e",
            cursor="hand2",
        )
        license_link.pack(side="right")
        license_link.bind("<Button-1>", lambda e: LicenseDialog(self))

    def _append_log(self, message: str, tag: str = "dim") -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"{stamp}  ", "dim")
        self.log.insert("end", f"{message}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _elevate(self) -> None:
        if spooler.relaunch_as_admin():
            self.destroy()
        else:
            self._append_log(t("log_uac_cancelled"), "err")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        enabled = (not busy) and spooler.is_admin()
        self.primary.set_enabled(enabled and not busy)
        if busy:
            self.btn_pause.set_enabled(False)
            self.btn_clear.set_enabled(False)
            self.btn_resume.set_enabled(False)
        else:
            self.refresh()

    def refresh(self) -> None:
        try:
            self._refresh_status()
        except Exception as exc:
            self._append_log(t("log_refresh_failed", error=exc), "err")

    def _refresh_status(self) -> None:
        admin = spooler.is_admin()
        if admin:
            if not self.admin_chip.winfo_ismapped():
                self.admin_chip.pack(side="right", anchor="n")
            self.admin_chip.configure(text="ADMIN", bg=GREEN_DIM, fg=SUCCESS)
            self.admin_banner.pack_forget()
        else:
            self.admin_chip.pack_forget()
            if not self.admin_banner.winfo_ismapped():
                self.admin_banner.pack(
                    fill="x", pady=(0, 14), before=self._status_card
                )

        snap = spooler.snapshot()
        color = SUCCESS if snap.running else (WARN if snap.state else DANGER)
        extra = f"  PID {snap.pid}" if snap.pid else ""
        self.status_rows["spooler"][1].configure(
            text=f"●  {snap.state_label}{extra}", fg=color
        )

        if not snap.buffer.accessible:
            buf = t("buffer_no_access")
            buf_fg = WARN
        elif snap.buffer.files == 0:
            buf = t("buffer_empty")
            buf_fg = TEXT_DIM
        else:
            buf = t(
                "buffer_files",
                n=snap.buffer.files,
                files=i18n.files_word(snap.buffer.files),
                size=spooler.format_bytes(snap.buffer.bytes),
            )
            buf_fg = WARN
        self.status_rows["buffer"][1].configure(text=buf, fg=buf_fg)
        self.status_rows["jobs"][1].configure(
            text=str(snap.jobs), fg=WARN if snap.jobs else TEXT_DIM
        )

        if snap.printers:
            self.status_rows["printers"][1].configure(
                text=str(len(snap.printers)), fg=TEXT
            )
        else:
            self.status_rows["printers"][1].configure(
                text=t("printers_none"), fg=TEXT_DIM
            )

        for child in self.printer_box.winfo_children():
            child.destroy()
        for printer in snap.printers[:6]:
            line = tk.Frame(self.printer_box, bg=BG_CARD)
            line.pack(fill="x", pady=(2, 0))
            tk.Label(
                line,
                text=printer.name,
                bg=BG_CARD,
                fg=TEXT_DIM,
                font=(self.font_ui, 8),
                anchor="w",
            ).pack(side="left")
            jobs = (
                i18n.jobs_label(printer.jobs) if printer.jobs else printer.status_label
            )
            tk.Label(
                line,
                text=jobs,
                bg=BG_CARD,
                fg=WARN if printer.jobs else TEXT_MUTED,
                font=(self.font_ui, 8),
                anchor="e",
            ).pack(side="right")

        if not self._busy:
            self.primary.set_enabled(admin)
            self.btn_pause.set_enabled(admin and snap.can_pause)
            self.btn_clear.set_enabled(admin)
            self.btn_resume.set_enabled(admin and snap.can_resume)

    def _schedule_refresh(self) -> None:
        if not self._busy:
            try:
                self.refresh()
            except Exception:
                pass
        self._refresh_job = self.after(2500, self._schedule_refresh)

    def _on_close(self) -> None:
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self.destroy()

    def _run_bg(self, fn, *, reset_steps: bool = False) -> None:
        if self._busy:
            return
        if not spooler.is_admin():
            self._append_log(t("log_need_admin"), "err")
            return
        self._set_busy(True)
        if reset_steps:
            self._set_steps(0)

        def worker() -> None:
            try:
                fn()
            except spooler.SpoolerError as exc:
                msg = str(exc)
                self.after(0, lambda m=msg: self._fail(m))
            except Exception as exc:  # surface unexpected Windows errors in the log
                msg = str(exc)
                self.after(0, lambda m=msg: self._fail(m))
            else:
                self.after(0, self._done)

        threading.Thread(target=worker, daemon=True).start()

    def _fail(self, message: str) -> None:
        self._append_log(message, "err")
        self._set_busy(False)

    def _done(self) -> None:
        self._set_busy(False)

    def _on_pause(self) -> None:
        def work() -> None:
            self.after(0, lambda: self._set_steps(0))
            msg = spooler.stop_spooler()
            self.after(0, lambda: self._append_log(msg, "ok"))
            self.after(0, lambda: self._set_steps(-1, done_through=0))

        self._run_bg(work)

    def _on_clear(self) -> None:
        def work() -> None:
            snap = spooler.snapshot()
            if snap.running:
                self.after(0, lambda: self._set_steps(0))
                msg = spooler.stop_spooler()
                self.after(0, lambda: self._append_log(msg, "ok"))
            self.after(0, lambda: self._set_steps(1, done_through=0))
            msg = spooler.clear_buffer()
            self.after(0, lambda: self._append_log(msg, "ok"))
            self.after(0, lambda: self._set_steps(-1, done_through=1))

        self._run_bg(work)

    def _on_resume(self) -> None:
        def work() -> None:
            self.after(0, lambda: self._set_steps(2, done_through=1))
            msg = spooler.start_spooler()
            self.after(0, lambda: self._append_log(msg, "ok"))
            self.after(0, lambda: self._set_steps(-1, done_through=2))

        self._run_bg(work)

    def _on_reset(self) -> None:
        if self._busy:
            return
        dlg = ConfirmDialog(
            self,
            t("confirm_title"),
            t("confirm_body"),
        )
        if not dlg.result:
            return

        def progress(step: int, message: str, kind: str = "ok") -> None:
            def ui() -> None:
                self._set_steps(step, done_through=step - 1)
                self._append_log(message, "info" if kind == "info" else "ok")

            self.after(0, ui)

        def work() -> None:
            spooler.reset_queue(progress=progress)
            self.after(0, lambda: self._set_steps(-1, done_through=2))

        self._run_bg(work, reset_steps=True)


def main() -> int:
    enable_dpi_awareness()
    set_app_id()
    i18n.init(i18n.parse_cli_lang())
    if activate_existing():
        return 0
    if not spooler.is_admin():
        # Relaunch elevated; if the user cancels UAC, still show the window.
        if "--no-elevate" not in sys.argv:
            if spooler.relaunch_as_admin():
                return 0
    os_chdir()
    app = App()
    if "--no-elevate" in sys.argv or not spooler.is_admin():
        app._append_log(t("log_started_no_admin"), "err")
    else:
        app._append_log(t("log_ready"), "info")
        snap = spooler.snapshot()
        app._append_log(
            t(
                "log_summary",
                state=snap.state_label,
                files=snap.buffer.files,
                word=i18n.files_word(snap.buffer.files),
                n=len(snap.printers),
            ),
            "dim",
        )
    app.mainloop()
    return 0


def os_chdir() -> None:
    try:
        import os

        os.chdir(spooler.project_root())
    except Exception:
        pass
