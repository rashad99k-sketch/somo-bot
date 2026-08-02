"""Scanner interfaces (abstract base classes).

Defines the public interfaces that any scanner implementation must
implement so the scanner package stays pluggable.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import WatchEntry, WaitingEntry, ScanSignal


class ScannerInterface(ABC):
    """Public scanner interface.

    Implementations must be pure data producers: discovery, scoring,
    and persistence via the provided stores. No trading logic.
    """

    @abstractmethod
    def start(self) -> None:
        """Start continuous scanning (non-blocking)."""

    @abstractmethod
    def stop(self) -> None:
        """Stop background scanning and clean up resources."""

    @abstractmethod
    def scan_once(self) -> Iterable[ScanSignal]:
        """Perform a single scan and return any discovered signals.

        Must not persist signals by itself; return them so the manager or
        stores can persist or enqueue them as desired.
        """


class WatchlistStoreInterface(ABC):
    @abstractmethod
    def add(self, entry: WatchEntry) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[WatchEntry]:
        raise NotImplementedError

    @abstractmethod
    def update(self, entry_id: str, **fields) -> bool:
        raise NotImplementedError


class WaitingListStoreInterface(ABC):
    @abstractmethod
    def add(self, entry: WaitingEntry) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[WaitingEntry]:
        raise NotImplementedError

