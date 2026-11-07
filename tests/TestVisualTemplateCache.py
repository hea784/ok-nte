import threading
import time
import unittest

from src.utils.visual_template_cache import VisualTemplateCache


class TestVisualTemplateCache(unittest.TestCase):
    _LV_KEY = "Labels.lv"

    def setUp(self):
        self.cache = VisualTemplateCache()

    def test_same_key_builds_once_for_concurrent_callers(self):
        call_count = 0
        count_lock = threading.Lock()
        results = []
        result_lock = threading.Lock()

        def builder():
            nonlocal call_count
            with count_lock:
                call_count += 1
            time.sleep(0.03)
            return object()

        def worker():
            value = self.cache.get_or_build((self._LV_KEY, 2560, 1440), builder)
            with result_lock:
                results.append(value)

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(call_count, 1)
        self.assertTrue(all(value is results[0] for value in results))

    def test_lv_cache_is_partitioned_by_resolution(self):
        call_count = 0

        def builder():
            nonlocal call_count
            call_count += 1
            return object()

        first = self.cache.get_or_build((self._LV_KEY, 1920, 1080), builder)
        second = self.cache.get_or_build((self._LV_KEY, 2560, 1440), builder)

        self.assertEqual(call_count, 2)
        self.assertIsNot(first, second)

    def test_generic_values_are_shared(self):
        call_count = 0
        value = object()

        def builder():
            nonlocal call_count
            call_count += 1
            return value

        first = self.cache.get_or_build("element_templates", builder)
        second = self.cache.get_or_build("element_templates", builder)

        self.assertEqual(call_count, 1)
        self.assertIs(first, second)

    def test_failed_build_is_not_cached(self):
        call_count = 0

        def builder():
            nonlocal call_count
            call_count += 1
            return None

        key = (self._LV_KEY, 2560, 1440)
        self.assertIsNone(self.cache.get_or_build(key, builder))
        self.assertIsNone(self.cache.get_or_build(key, builder))
        self.assertEqual(call_count, 2)
