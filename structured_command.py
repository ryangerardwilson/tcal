
"""Parsing and formatting helpers for deterministic x/y/z commands."""


import re
from dataclasses import dataclass
from typing import Iterable, List

from models import Event, ValidationError, parse_datetime


class StructuredCommandError(ValueError):
    """Raised when a deterministic command is malformed."""


STRUCTURED_TEMPLATE = (
    "When x(YYYY-MM-DD HH:MM:SS) happens, I want y(<outcome>) outcome, "
    "to have z(<impact>) impact"
)


@dataclass
class ParsedCommand:
    """Small helper to expose raw fields when needed."""

    x: str
    y: str
    z: str


_COMPONENT_RE = re.compile(r"(?i){label}\((.*?)\)")


def _extract_component(text: str, label: str) -> str:
    pattern = re.compile(rf"(?i){label}\\((.*?)\\)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise StructuredCommandError(f"Missing {label}(...) block")
    return match.group(1).strip()


def parse_structured_command(text: str) -> Event:
    """Parse a single-line deterministic command into an Event."""

    if not text or not text.strip():
        raise StructuredCommandError("Command text is empty")

    x_raw = _extract_component(text, "x")
    y_raw = _extract_component(text, "y")
    z_raw = _extract_component(text, "z")

    if not y_raw:
        raise StructuredCommandError("y(...) must include an outcome description")

    try:
        dt = parse_datetime(x_raw)
    except ValidationError as exc:
        raise StructuredCommandError(str(exc)) from exc

    return Event(x=dt, y=y_raw, z=z_raw)


def parse_structured_block(text: str) -> List[Event]:
    """Parse one or more deterministic commands from editor text."""

    entries = _split_entries(text)
    if not entries:
        return []

    events: List[Event] = []
    for idx, chunk in enumerate(entries, start=1):
        try:
            events.append(parse_structured_command(chunk))
        except StructuredCommandError as exc:
            raise StructuredCommandError(f"Entry {idx}: {exc}") from exc
    return events


def format_event_as_command(event: Event) -> str:
    """Render an Event using the deterministic template."""

    return (
        f"When x({event.x:%Y-%m-%d %H:%M:%S}) happens, "
        f"I want y({event.y}) outcome, to have z({event.z}) impact"
    )


def format_events_block(events: Iterable[Event]) -> str:
    """Render multiple events separated by blank lines."""

    lines = [format_event_as_command(ev) for ev in events]
    return "\n\n".join(lines)


def _split_entries(text: str) -> List[str]:
    entries: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                entries.append(" ".join(current))
                current = []
            continue
        current.append(stripped)
    if current:
        entries.append(" ".join(current))
    return entries


__all__ = [
    "StructuredCommandError",
    "STRUCTURED_TEMPLATE",
    "ParsedCommand",
    "parse_structured_command",
    "parse_structured_block",
    "format_event_as_command",
    "format_events_block",
]
