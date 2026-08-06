from __future__ import annotations

from collections.abc import Callable, Hashable
from concurrent.futures import Future
from threading import Lock, Thread
from typing import TypeVar

T = TypeVar("T")


class VisualTemplateCache:
    """Process-wide, concurrent-safe cache for immutable values."""

    def __init__(self):
        self._ready: dict[Hashable, object] = {}
        self._in_flight: dict[Hashable, Future] = {}
        self._preheating: set[Hashable] = set()
        self._lock = Lock()
        self._generation = 0

    def get_or_build(self, key: Hashable, builder: Callable[[], T | None]) -> T | None:
        """Return a cached value, or have exactly one caller build it.

        ``None`` is treated as a transient build failure and is intentionally not cached.
        """
        with self._lock:
            cached = self._ready.get(key)
            if cached is not None:
                return cached  # type: ignore[return-value]

            future = self._in_flight.get(key)
            if future is None:
                future = Future()
                self._in_flight[key] = future
                generation = self._generation
                should_build = True
            else:
                generation = None
                should_build = False

        if not should_build:
            return future.result()

        try:
            value = builder()
        except BaseException as error:
            with self._lock:
                if self._in_flight.get(key) is future:
                    self._in_flight.pop(key)
                future.set_exception(error)
            raise

        with self._lock:
            if self._in_flight.get(key) is future:
                self._in_flight.pop(key)
            if value is not None and generation == self._generation:
                self._ready[key] = value
            future.set_result(value)
        return value

    def preheat_async(
        self,
        key: Hashable,
        builder: Callable[[], T | None],
        thread_name: str = "visual-template-preheat",
    ) -> None:
        with self._lock:
            if key in self._ready or key in self._in_flight or key in self._preheating:
                return
            self._preheating.add(key)

        def worker():
            try:
                self.get_or_build(key, builder)
            finally:
                with self._lock:
                    self._preheating.discard(key)

        Thread(target=worker, name=thread_name, daemon=True).start()

    def clear(self) -> None:
        """Reset completed cache entries for controlled test isolation."""
        with self._lock:
            self._generation += 1
            self._ready.clear()
            self._in_flight.clear()
            self._preheating.clear()


_visual_template_cache = VisualTemplateCache()


def get_visual_template_cache() -> VisualTemplateCache:
    return _visual_template_cache


def reset_visual_template_cache_for_tests() -> None:
    get_visual_template_cache().clear()
