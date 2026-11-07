"""Regression tests for the WGC static-screen fallback in windows_graphics.

Windows Graphics Capture only raises FrameArrived when the captured content
changes. A static screen (loading screen, throttled background window) used to
block every frame request for WGC_FRAME_WAIT_TIMEOUT and then return None,
freezing the executor. These tests stub the WinRT surface and verify the
direct-pool-pull / static-content-fallback logic.
"""
import sys
import threading
import time
import unittest
from types import SimpleNamespace

import numpy as np


class WindowsGraphicsStubMixin:
    """Build a WindowsGraphicsCaptureMethod without running __init__ (no WinRT)."""

    def make_method(self, pool_frames, last_content_frame=None, last_frame_time_age=0.0):
        import ok.device.capture_methods.windows_graphics as wgm

        m = object.__new__(wgm.WindowsGraphicsCaptureMethod)
        m.lock = threading.RLock()
        m.get_frame_lock = threading.RLock()
        m.frame_event = threading.Event()
        m.frame_requested = threading.Event()
        m._frame_cancel_generation = 0
        m.exit_event = threading.Event()
        m.last_frame = None
        m.last_content_frame = last_content_frame
        m.last_frame_time = time.time() - last_frame_time_age
        m.contexts = {}
        m.cputex = None

        class Pool:
            def __init__(self, frames):
                self.frames = list(frames)

            def TryGetNextFrame(self):
                if self.frames:
                    return self.frames.pop(0)
                return None

            def Close(self):
                pass

        m.frame_pool = Pool(pool_frames)
        # instance-level stubs must be in place before hwnd_window, whose
        # setter calls start_or_stop()
        m.start_or_stop = lambda capture_cursor=False: True
        m.close = lambda: None
        m.convert_dx_frame = lambda frame: self.FRAME.copy()
        wgm.composite_hwnds = lambda frame, *a, **k: frame
        m.hwnd_window = SimpleNamespace(width=1920, height=1080, exists=True)
        return m


class TestWgcStaticScreen(unittest.TestCase, WindowsGraphicsStubMixin):
    FRAME = np.zeros((1080, 1920, 4), dtype=np.uint8)

    def test_pull_grabs_pooled_frame_immediately(self):
        """A frame delivered between requests is served without the 4s wait."""
        m = self.make_method(pool_frames=[object()])
        start = time.monotonic()
        frame = m._do_get_frame()
        elapsed = time.monotonic() - start
        self.assertIsNotNone(frame)
        self.assertLess(elapsed, 1.0, f"should not wait the 4s timeout, took {elapsed:.2f}s")
        self.assertFalse(m.frame_requested.is_set(), "request must be consumed")

    def test_static_fallback_serves_last_content(self):
        """Static screen with an empty pool returns the last content frame."""
        m = self.make_method(pool_frames=[], last_content_frame=self.FRAME, last_frame_time_age=3.0)
        start = time.monotonic()
        frame = m._do_get_frame(frame_deadline=time.monotonic() + 0.3)
        elapsed = time.monotonic() - start
        self.assertIsNotNone(frame, "static screen must serve the last content frame")
        self.assertLess(elapsed, 2.0, f"fallback must not block 4s, took {elapsed:.2f}s")

    def test_no_cache_returns_none(self):
        """Nothing ever delivered (fresh session, dead window) stays None."""
        m = self.make_method(pool_frames=[], last_content_frame=None, last_frame_time_age=0.0)
        self.assertIsNone(m._do_get_frame(frame_deadline=time.monotonic() + 0.3))

    def test_stale_cache_triggers_restart(self):
        """Cache older than WGC_STATIC_FRAME_MAX_AGE runs the restart heuristic."""
        import ok.device.capture_methods.windows_graphics as wgm

        m = self.make_method(
            pool_frames=[],
            last_content_frame=self.FRAME,
            last_frame_time_age=wgm.WGC_STATIC_FRAME_MAX_AGE + 1,
        )
        closes = []
        m.close = lambda: closes.append(1)
        frame = m._do_get_frame(frame_deadline=time.monotonic() + 0.3)
        self.assertEqual(len(closes), 1, "stale age must trigger the restart heuristic")
        self.assertIsNotNone(frame, "after revalidation a static screen serves its content")

    def test_reset_framepool_clears_cache(self):
        """A size change invalidates stored content."""
        import ok.device.capture_methods.windows_graphics as wgm

        m = self.make_method(pool_frames=[], last_content_frame=self.FRAME)
        m.rtdevice = SimpleNamespace()
        original_property = wgm.WindowsGraphicsCaptureMethod.pixel_format
        wgm.WindowsGraphicsCaptureMethod.pixel_format = property(lambda self: object())
        try:
            m.frame_pool.Recreate = lambda *a, **k: None
            m.reset_framepool((1920, 1080))
        finally:
            wgm.WindowsGraphicsCaptureMethod.pixel_format = original_property
        self.assertIsNone(m.last_content_frame, "reset_framepool must clear the cache")


if __name__ == "__main__":
    unittest.main()
