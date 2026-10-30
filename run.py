"""Print Queue Reset — launcher.

Copyright (c) 2026 Tomasz Mucha
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

import app


if __name__ == "__main__":
    try:
        sys.exit(app.main())
    except Exception as exc:
        import traceback

        app.show_crash(traceback.format_exc() or str(exc))
        raise
