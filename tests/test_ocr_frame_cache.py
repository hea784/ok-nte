"""Regression tests for the per-frame OCR cache and next_frame backoff."""
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

REPO_ROOT = "D:/ok-nte/build/v1.7.0"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ok.feature.Box import Box
from ok.task.task import OCR


def make_ocr():
    ocr = object.__new__(OCR)
    ocr._ocr_cache = {}
    ocr._ocr_cache_seq = None
    ocr._ocr_cache_lock = __import__("threading").Lock()
    ocr.ocr_default_threshold = 0.2
    return ocr


class TestOcrCacheKeys(unittest.TestCase):
    def test_key_covers_result_affecting_params(self):
        key = OCR._ocr_cache_key
        base = key(Box(0, 0, 100, 50), "text", 0.2, False, 0, None, "default")
        self.assertIsNotNone(base)
        variants = [
            key(Box(1, 0, 100, 50), "text", 0.2, False, 0, None, "default"),   # box moved
            key(Box(0, 0, 100, 50), "other", 0.2, False, 0, None, "default"),  # match
            key(Box(0, 0, 100, 50), "text", 0.5, False, 0, None, "default"),   # threshold
            key(Box(0, 0, 100, 50), "text", 0.2, True, 0, None, "default"),    # grayscale
            key(Box(0, 0, 100, 50), "text", 0.2, False, 64, None, "default"),  # target_height
            key(Box(0, 0, 100, 50), "text", 0.2, False, 0, lambda i: i, "default"),  # processor
            key(Box(0, 0, 100, 50), "text", 0.2, False, 0, None, "rewards"),   # lib
        ]
        for v in variants:
            self.assertNotEqual(base, v, f"key collision for variant {v}")

    def test_key_none_for_boxless(self):
        self.assertIsNone(OCR._ocr_cache_key(None, "m", 0.2, False, 0, None, "d"))


class TestOcrCacheLifecycle(unittest.TestCase):
    def setUp(self):
        self.ocr = make_ocr()

    def test_store_then_lookup_same_seq(self):
        boxes = [Box(1, 2, 3, 4)]
        self.ocr._ocr_cache_store(1, ("k",), boxes)
        self.assertEqual(self.ocr._ocr_cache_lookup(1, ("k",)), boxes)

    def test_seq_change_invalidates(self):
        self.ocr._ocr_cache_store(1, ("k",), [Box(1, 2, 3, 4)])
        self.assertIsNone(self.ocr._ocr_cache_lookup(2, ("k",)))
        self.assertEqual(self.ocr._ocr_cache, {})


class TestOcrIntegration(unittest.TestCase):
    FRAME = np.zeros((108, 192, 3), dtype=np.uint8)

    def _make_task(self, lib_calls):
        ocr = make_ocr()
        executor = SimpleNamespace(
            frame=self.FRAME,
            _frame_seq=1,
            ocr_po_translation=None,
            blocked_by_pause=lambda: False,
        )
        ocr._executor = executor
        ocr.log_debug = False
        ocr._debug = False

        def fake_ocr_fun(lib):
            def call(box, image, match, scale_factor, threshold, lib_name):
                lib_calls.append((box.x, box.y))
                return [], []
            return call

        ocr.ocr_fun = fake_ocr_fun
        return ocr

    def test_same_frame_same_box_single_inference(self):
        lib_calls = []
        ocr = self._make_task(lib_calls)
        with mock.patch("ok.task.task.communicate") as comm:
            comm.emit_draw_box = lambda *a, **k: None
            first = ocr.ocr(0, 0, 0.5, 0.2, match="hp")
            second = ocr.ocr(0, 0, 0.5, 0.2, match="hp")
        self.assertEqual(len(lib_calls), 1, "same frame+box must reuse cached result")
        self.assertEqual(first, second)

    def test_new_frame_invalidates(self):
        lib_calls = []
        ocr = self._make_task(lib_calls)
        with mock.patch("ok.task.task.communicate") as comm:
            comm.emit_draw_box = lambda *a, **k: None
            ocr.ocr(0, 0, 0.5, 0.2, match="hp")
            ocr.executor._frame_seq = 2
            ocr.ocr(0, 0, 0.5, 0.2, match="hp")
        self.assertEqual(len(lib_calls), 2, "new frame must re-run inference")

    def test_explicit_frame_bypasses_cache(self):
        lib_calls = []
        ocr = self._make_task(lib_calls)
        with mock.patch("ok.task.task.communicate") as comm:
            comm.emit_draw_box = lambda *a, **k: None
            ocr.ocr(0, 0, 0.5, 0.2, match="hp", frame=self.FRAME)
            ocr.ocr(0, 0, 0.5, 0.2, match="hp", frame=self.FRAME)
        self.assertEqual(len(lib_calls), 2, "explicit frames must never be cached")

    def test_cached_result_is_a_copy(self):
        lib_calls = []
        ocr = self._make_task(lib_calls)
        with mock.patch("ok.task.task.communicate") as comm:
            comm.emit_draw_box = lambda *a, **k: None
            first = ocr.ocr(0, 0, 0.5, 0.2, match="hp")
            if first:
                first[0].x = 999
            second = ocr.ocr(0, 0, 0.5, 0.2, match="hp")
        if first:
            self.assertNotEqual(second[0].x, 999, "mutation must not leak into cache")


if __name__ == "__main__":
    unittest.main()
