#!/usr/bin/env python3
"""Basic UI helpers for curses rendering."""

from __future__ import annotations

import curses
from typing import Iterable


_BOX_COLOR_PAIR: int | None = None


def _box_color_attr() -> int:
    global _BOX_COLOR_PAIR
    if _BOX_COLOR_PAIR is not None:
        return _BOX_COLOR_PAIR
    if not curses.has_colors():
        _BOX_COLOR_PAIR = 0
        return _BOX_COLOR_PAIR
    try:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    except curses.error:
        _BOX_COLOR_PAIR = 0
        return _BOX_COLOR_PAIR
    _BOX_COLOR_PAIR = curses.color_pair(1)
    return _BOX_COLOR_PAIR


def draw_header(stdscr: "curses.window", text: str) -> None:  # type: ignore[name-defined]
    h, w = stdscr.getmaxyx()
    if w <= 0 or h <= 0:
        return
    stdscr.addnstr(0, 0, text.ljust(max(1, w - 1)), max(0, w - 1))


def draw_footer(stdscr: "curses.window", text: str) -> None:  # type: ignore[name-defined]
    h, w = stdscr.getmaxyx()
    if w <= 0 or h <= 0:
        return
    stdscr.addnstr(h - 1, 0, text.ljust(max(1, w - 1)), max(0, w - 1))


def draw_centered_box(stdscr: "curses._CursesWindow", lines: Iterable[str]) -> None:  # type: ignore[name-defined]
    h, w = stdscr.getmaxyx()
    lines_list = list(lines)
    win_h = min(len(lines_list) + 2, h - 2)
    win_w = min(max(len(line) for line in lines_list) + 4, w - 2)
    win_y = (h - win_h) // 2
    win_x = (w - win_w) // 2
    win = stdscr.derwin(win_h, win_w, win_y, win_x)
    attr = _box_color_attr()
    if attr:
        win.bkgd(" ", attr)
        win.attrset(attr)
    win.erase()
    win.border()
    for idx, line in enumerate(lines_list, start=1):
        if attr:
            win.addnstr(idx, 2, line[: win_w - 4], win_w - 4, attr)
        else:
            win.addnstr(idx, 2, line[: win_w - 4], win_w - 4)
    win.refresh()


def draw_help_overlay(
    stdscr: "curses.window",  # type: ignore[name-defined]
    lines: Iterable[str],
    *,
    scroll: int = 0,
    footer: str = "",
) -> int:
    """Render a full-screen overlay for the help/cheatsheet view.

    Returns the clamped scroll offset used for rendering.
    """

    h, w = stdscr.getmaxyx()
    if h <= 0 or w <= 0:
        return 0

    lines_list = list(lines)
    total = len(lines_list)
    max_visible = max(1, h - 1)
    max_scroll = max(0, total - max_visible)
    scroll = clamp(scroll, 0, max_scroll)

    dim_attr = curses.A_DIM if hasattr(curses, "A_DIM") else 0

    blank_line = " " * max(0, w - 1)
    for y in range(h - 1):
        stdscr.addnstr(y, 0, blank_line, max(0, w - 1), dim_attr)

    visible = lines_list[scroll : scroll + max_visible]
    for row, line in enumerate(visible):
        stdscr.addnstr(row, 0, line.ljust(max(1, w - 1)), max(0, w - 1))

    draw_footer(stdscr, footer)

    return scroll


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


__all__ = [
    "draw_header",
    "draw_footer",
    "draw_centered_box",
    "draw_help_overlay",
    "clamp",
]
