"""Core scanner implementation (scaffolding only).

This Scanner implementation is a plugin-style, asset-agnostic skeleton.
It performs no market analysis. It emits structured events via the
EventBus so downstream systems can subscribe. Replace scanner_impl.Scanner
with your MIN.py implementation later without touching the rest of the
project.
"""
from __future__ import annotations

from typing import Iterable, List
import threading
import logging

from .interfaces import ScannerInterface
from .models import ScanSignal
from .events import EventBus
from .watchlist import WatchlistStore
from .waitinglist import WaitingListStore
from .config import get_scanner_config

logger = logging.getLogger(__name__)


class Scanner(ScannerInterface):
    """Production-ready scanner skeleton.

    Responsibilities:
    - discover opportunities (scan_once)
    - score opportunities (scoring is a TODO)
    - return ScanSignal objects (no persistence)

    The Scanner itself does not persist results; it returns ScanSignal
    objects so the ScannerManager can decide what to persist / emit.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        watchlist_store: WatchlistStore | None = None,
        waitinglist_store: WaitingListStore | None = None,
        config: dict | None = None,
    ) -> None:
        self._config = config or get_scanner_config()
        self._event_bus = event_bus or EventBus()
        self._watchlist = watchlist_store
        self._waiting = waitinglist_store
        self._running = threading.Event()
        # Lock protects scanner internal state when running in background
        self._lock = threading.RLock()

    def configure(self, **kwargs) -> None:
        with self._lock:
            self._config.update(kwargs)

    def start(self) -> None:
        """Start background scanning. Non-blocking.

        Scanning logic is NOT implemented here — replace with MIN.py.
        This method currently sets an internal running flag and emits
        the "scanner_started" event.
        """
        with self._lock:
            if self._running.is_set():
                return
            self._running.set()
        self._event_bus.emit("scanner_started", started_at=None)
        logger.info("Scanner started (skeleton only)")

    def stop(self) -> None:
        with self._lock:
            if not self._running.is_set():
                return
            self._running.clear()
        self._event_bus.emit("scanner_stopped", stopped_at=None)
        logger.info("Scanner stopped (skeleton only)")

    def scan_once(self) -> Iterable[ScanSignal]:
        """Perform a single scan pass and return any discovered signals.

        NOTE: No scanning logic is implemented here. Return an empty list.
        Replace this method in your MIN.py implementation to return real
        ScanSignal objects.
        """
        # TODO: implement real scanning logic in MIN.py replacement.
        logger.debug("scan_once called on Scanner skeleton; returning empty list")
        return []

