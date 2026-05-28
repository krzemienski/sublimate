"""Parse Claude Code session JSONL files into ToolEvent streams."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional, Tuple


@dataclass
class ToolEvent:
    role: str
    turn_index: int
    tool_name: Optional[str]
    tool_input_hash: str
    ts: str
    is_user_prompt: bool


def _hash_input(obj) -> str:
    try:
        payload = json.dumps(obj, sort_keys=True, default=str)
    except (TypeError, ValueError):
        payload = repr(obj)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:8]


def _extract_content_list(message) -> list:
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, list):
        return content
    return []


def _is_tool_result_user(message) -> bool:
    content = _extract_content_list(message)
    if not content:
        return False
    first = content[0]
    if not isinstance(first, dict):
        return False
    return first.get("type") == "tool_result"


def _parse_file(path: Path) -> List[ToolEvent]:
    events: List[ToolEvent] = []
    try:
        fh = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return events

    with fh:
        for turn_index, raw in enumerate(fh):
            raw = raw.strip()
            if not raw:
                continue
            try:
                line = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(line, dict):
                continue

            line_type = line.get("type")
            if line_type not in ("user", "assistant"):
                continue

            ts = line.get("timestamp", "") or ""
            message = line.get("message", {})

            if line_type == "user":
                if _is_tool_result_user(message):
                    continue
                events.append(
                    ToolEvent(
                        role="user",
                        turn_index=turn_index,
                        tool_name=None,
                        tool_input_hash="",
                        ts=ts,
                        is_user_prompt=True,
                    )
                )
                continue

            # assistant
            for item in _extract_content_list(message):
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "tool_use":
                    continue
                name = item.get("name", "") or ""
                tool_input = item.get("input", {})
                events.append(
                    ToolEvent(
                        role="assistant",
                        turn_index=turn_index,
                        tool_name=name,
                        tool_input_hash=_hash_input(tool_input),
                        ts=ts,
                        is_user_prompt=False,
                    )
                )

    return events


def iter_sessions(
    projects_dir, max_sessions: Optional[int] = None
) -> Iterator[Tuple[str, List[ToolEvent]]]:
    root = Path(projects_dir)
    if not root.exists():
        return

    yielded = 0
    for path in sorted(root.rglob("*.jsonl")):
        if not path.is_file():
            continue
        events = _parse_file(path)
        if not events:
            continue
        yield (path.stem, events)
        yielded += 1
        if max_sessions is not None and yielded >= max_sessions:
            return
