"""Event bus for scanner package.

Lightweight publish/subscribe event system. Subscribers register callbacks
by event name and receive keyword arguments. Thread-safe and dependency-free
so UI/notification layers can subscribe without modifying scanner core.
"""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable, Dict, List


class EventBus:
    """Simple thread-safe event bus.

    Usage:
        bus = EventBus()
        bus.subscribe("opportunity_discovered", callback)
        bus.emit("opportunity_discovered", entry=entry)
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        with self._lock:
            if callback not in self._subscribers[event_name]:
                self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        with self._lock:
            if callback in self._subscribers[event_name]:
                self._subscribers[event_name].remove(callback)

    def emit(self, event_name: str, **kwargs) -> None:
        """Emit an event to all subscribers. Exceptions in handlers are
        caught and ignored so a failing consumer cannot stop the scanner.
        """
        with self._lock:
            subscribers = list(self._subscribers.get(event_name, []))
        for cb in subscribers:
            try:
                cb(**kwargs)
            except Exception:
                # Keep bus resilient: do not allow subscriber errors to bubble
                # up to the scanner core. Consumers should log/handle errors.
                continue
