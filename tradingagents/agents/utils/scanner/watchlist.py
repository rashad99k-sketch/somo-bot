"""Watchlist store adapter using TradingMemoryLog.

This class implements the WatchlistStoreInterface and persists entries
into the existing TradingMemoryLog file using a safe, additive marker so
we reuse the same persistence layer as the rest of TradingAgents.
"""
from __future__ import annotations

import json
from typing import Iterable, List, Dict, Any

from tradingagents.agents.utils.memory import TradingMemoryLog
from .interfaces import WatchlistStoreInterface
from .models import WatchEntry


class WatchlistStore(WatchlistStoreInterface):
    """Simple watchlist store backed by TradingMemoryLog.

    Persistence format: each watchlist entry is appended as a block starting
    with the marker "<!-- WATCHLIST_ENTRY -->" followed by a single-line
    JSON object and the standard TradingMemoryLog separator. This is
    intentionally additive and does not interfere with existing decision
    entries.
    """

    _MARKER = "<!-- WATCHLIST_ENTRY -->"

    def __init__(self, memory_log: TradingMemoryLog):
        self._mem = memory_log

    def add(self, entry: WatchEntry) -> None:
        payload = json.dumps(entry.to_dict(), ensure_ascii=False)
        block = f"{self._MARKER}\n{payload}{self._mem._SEPARATOR}"
        # Append raw block to memory file using the same path as TradingMemoryLog
        if not self._mem._log_path:
            return
        with open(self._mem._log_path, "a", encoding="utf-8") as f:
            f.write(block)

    def list(self) -> Iterable[WatchEntry]:
        if not self._mem._log_path or not self._mem._log_path.exists():
            return []
        raw = self._mem._log_path.read_text(encoding="utf-8")
        blocks = [b for b in raw.split(self._mem._SEPARATOR) if b.strip()]
        result: List[WatchEntry] = []
        for b in blocks:
            if not b.strip().startswith(self._MARKER):
                continue
            try:
                payload = b.strip()[len(self._MARKER):].strip()
                data = json.loads(payload)
                result.append(WatchEntry(**data))
            except Exception:
                continue
        return result

    def update(self, entry_id: str, **fields) -> bool:
        if not self._mem._log_path or not self._mem._log_path.exists():
            return False
        text = self._mem._log_path.read_text(encoding="utf-8")
        blocks = text.split(self._mem._SEPARATOR)
        updated = False
        new_blocks = []
        for block in blocks:
            stripped = block.strip()
            if not stripped or not stripped.startswith(self._MARKER):
                new_blocks.append(block)
                continue
            payload = stripped[len(self._MARKER):].strip()
            try:
                data = json.loads(payload)
            except Exception:
                new_blocks.append(block)
                continue
            if data.get("id") == entry_id:
                data.update(fields)
                new_payload = json.dumps(data, ensure_ascii=False)
                new_blocks.append(f"{self._MARKER}\n{new_payload}")
                updated = True
            else:
                new_blocks.append(block)
        if not updated:
            return False
        new_text = self._mem._SEPARATOR.join(new_blocks)
        tmp = self._mem._log_path.with_suffix(".tmp")
        tmp.write_text(new_text, encoding="utf-8")
        tmp.replace(self._mem._log_path)
        return True
