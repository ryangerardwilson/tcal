#!/usr/bin/env python3
"""Thin entrypoint for tcal."""
from __future__ import annotations

import os
import sys

from orchestrator import Orchestrator


def main() -> int:
    print('a')
    # Make ESC detection snappy inside curses.
    os.environ.setdefault("ESCDELAY", "25")

    try:
        orchestrator = Orchestrator()
        orchestrator.run()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
