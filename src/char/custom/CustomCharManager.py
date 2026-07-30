import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, RLock, Thread
from typing import TYPE_CHECKING

import cv2
import numpy as np
from ok import Logger, og

from src.char.custom.CustomCharDb import CustomCharDb
from src.char.custom.CustomCharDbMigrator import MigrationContext
from src.Labels import Labels

if TYPE_CHECKING:
    from src.combat.BaseCombatTask import BaseCombatTask

logger = Logger.get_logger(__name__)

CUSTOM_CHARS_DIR = "custom_chars"
FEATURES_DIR = os.path.join(CUSTOM_CHARS_DIR, "features")
DB_PATH = os.path.join(CUSTOM_CHARS_DIR, "db.json")


class CustomCharManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CustomCharManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized") and self.initialized:
            return
        self._data_lock = RLock()
        os.makedirs(FEATURES_DIR, exist_ok=True)
        context = MigrationContext(
            is_builtin_combo=self.is_builtin_combo,
            get_builtin_prefix=self.get_builtin_prefix,
            iter_builtin_combo_items=self.iter_builtin_combo_items,
            generate_combo_id=lambda _existing: f"combo_{uuid.uuid4().hex}",
        )
        self._db = CustomCharDb(DB_PATH, FEATURES_DIR, context, logger)
        self._feature_cache = {}
        self._raw_feature_cache = {}
        self._cache_mask = None
        self._cache_scr_w = -1
        self._cache_scr_h = -1
        self._cache_fids = set()
        self._preheat_started = False
        self._db.reload()
        self.initialized = True
        self.preheat_feature_cache_async()

    @staticmethod
    def _builtin_entries() -> dict:
        from src.char.CharFactory import char_dict

        return {key: value for key, value in char_dict.items() if key != "char_default"}

    @staticmethod
    def _locale_name() -> str:
        app = getattr(og, "app", None)
        if app and hasattr(app, "locale"):
            try:
                return app.locale.name()
            except Exception:
                return ""
        return ""

    @staticmethod
    def get_builtin_prefix() -> str:
        app = getattr(og, "app", None)
        if app and hasattr(app, "tr"):
            return f"{app.tr('[内置代码]')} "
        return "[内置代码] "

    @classmethod
    def is_builtin_combo(cls, combo_id: str) -> bool:
        return ("" if combo_id is None else str(combo_id)) in cls._builtin_entries()

    @classmethod
    def get_builtin_combo_name(cls, combo_id: str) -> str:
        entries = cls._builtin_entries()
        combo_id = "" if combo_id is None else str(combo_id)
        meta = entries.get(combo_id)
        if not isinstance(meta, dict):
            return combo_id
        if cls._locale_name() == "zh_CN" and meta.get("cn_name"):
            return str(meta["cn_name"])
        char_cls = meta.get("cls")
        return getattr(char_cls, "__name__", combo_id)

    @classmethod
    def iter_builtin_combo_items(cls):
        for combo_id in cls._builtin_entries().keys():
            yield cls.get_builtin_combo_name(combo_id), combo_id

    def load_db(self):
        self._db.reload()

    def validate_db(self):
        self._db.reload()
        self._invalidate_feature_cache()

    def save_db(self):
        self._db.save()

    def _invalidate_feature_cache(self):
        self._feature_cache.clear()
        self._cache_scr_w = -1
        self._cache_scr_h = -1
        self._cache_fids = set()

    def _invalidate_raw_feature_cache(self, feature_id=None):
        if feature_id is None:
            self._raw_feature_cache.clear()
        else:
            self._raw_feature_cache.pop(feature_id, None)

    def _get_feature_ids_snapshot(self):
        return self._db.get_feature_ids()

    def preheat_feature_cache(self):
        feature_ids = self._get_feature_ids_snapshot()
        if not feature_ids:
            return

        worker_count = min(8, len(feature_ids))
        if worker_count == 1:
            for fid in feature_ids:
                self._load_feature_image_cached(fid)
        else:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                list(executor.map(self._load_feature_image_cached, feature_ids))
        logger.debug(f"preheated {len(feature_ids)} custom feature images")

    def _preheat_feature_cache_worker(self):
        try:
            self.preheat_feature_cache()
        except Exception as e:
            logger.error("Failed to preheat custom feature images", e)

    def preheat_feature_cache_async(self):
        with self._data_lock:
            if self._preheat_started:
                return
            self._preheat_started = True
        Thread(
            target=self._preheat_feature_cache_worker,
            name="custom-feature-cache-preheat",
            daemon=True,
        ).start()

    def migrate_db_schema(self):
        self._db.reload()

    def _find_character_id_by_name(self, char_name: str) -> str | None:
        """Compatibility helper for existing callers; lookup ownership is in CustomCharDb."""
        return self._db.find_character_id_by_name(char_name)

    def find_custom_combo_id_by_name(self, combo_name: str) -> str:
        return self._db.find_combo_id_by_name(combo_name)

    def add_combo(self, combo_name: str, content: str, combo_id: str | None = None) -> str:
        """Add or update a custom combo and return its stable combo id."""
        return self._db.add_combo(combo_name, content, combo_id)

    def update_combo(self, combo_id: str, content: str, combo_name: str | None = None) -> bool:
        return self._db.update_combo(combo_id, content, combo_name)

    def delete_combo(self, combo_id: str):
        """删除出招表"""
        self._db.delete_combo(combo_id)

    def is_custom_combo_exist(self, combo_id: str):
        """判断出招表是否存在"""
        return self._db.has_custom_combo(combo_id)

    def get_combo(self, combo_id: str):
        """获取出招表"""
        return self._db.get_combo(combo_id)

    def get_combo_name(self, combo_id: str, with_builtin_prefix=False) -> str:
        combo_id = "" if combo_id is None else str(combo_id)
        if not combo_id:
            return ""
        if self.is_builtin_combo(combo_id):
            name = self.get_builtin_combo_name(combo_id)
            if with_builtin_prefix:
                return f"{self.get_builtin_prefix()}{name}"
            return name
        return self._db.get_custom_combo_name(combo_id) or combo_id

    def get_all_combos(self):
        combos = [name for name, _ in self._db.get_custom_combo_items()]
        combos.extend(name for name, _ in self.iter_builtin_combo_items())
        return combos

    def get_all_combo_items(self, with_builtin_prefix=False):
        """
        Return combo options as (name, id) tuples for UI binding.
        """
        items = self._db.get_custom_combo_items()
        for combo_name, combo_id in self.iter_builtin_combo_items():
            if with_builtin_prefix:
                combo_name = f"{self.get_builtin_prefix()}{combo_name}"
            items.append((combo_name, combo_id))
        return items

    def create_character(self, char_name, combo_id) -> str:
        """创建角色并返回 char_id"""
        char_id = self._db.create_character(char_name, combo_id)
        if char_id:
            self._invalidate_feature_cache()
        return char_id

    def update_character(self, char_id, char_name=None, combo_id=None) -> bool:
        """更新角色名称或出招表"""
        updated = self._db.update_character(char_id, char_name, combo_id)
        if updated:
            self._invalidate_feature_cache()
        return updated

    def delete_character(self, char_id: str):
        """删除角色及其所有特征图，不影响出招表"""
        feature_ids = self._db.delete_character(char_id)
        for feature_id in feature_ids:
            self.delete_feature_image(feature_id)
        self._invalidate_feature_cache()

    def add_feature_to_character(self, char_id: str, image_mat, width=0, height=0):
        """为角色保存一张截图并关联特征 UUID"""
        if self._db.get_character_record(char_id) is None:
            return ""
        feature_id = f"feat_{uuid.uuid4().hex}"
        self.save_feature_image(feature_id, image_mat)
        if not self._db.add_feature(char_id, feature_id, width, height):
            self.delete_feature_image(feature_id)
            return ""
        self._invalidate_feature_cache()
        return feature_id

    def remove_feature_from_character(self, char_id: str, feature_id: str):
        """从角色中移除某个特征"""
        if self._db.remove_feature(char_id, feature_id):
            self.delete_feature_image(feature_id)
            self._invalidate_feature_cache()

    def save_feature_image(self, feature_id, image_mat):
        """保存特征图"""
        path = os.path.join(FEATURES_DIR, f"{feature_id}.png")
        ok = cv2.imwrite(path, image_mat)
        if not ok:
            raise IOError(f"Failed to write feature image: {path}")
        with self._data_lock:
            self._invalidate_raw_feature_cache(feature_id)

    def delete_feature_image(self, feature_id):
        """删除特征图文件；对应的 DB 元数据由 CustomCharDb 统一维护。"""
        with self._data_lock:
            path = os.path.join(FEATURES_DIR, f"{feature_id}.png")
            if os.path.exists(path):
                os.remove(path)
            self._invalidate_raw_feature_cache(feature_id)

    def _load_feature_image_cached(self, feature_id):
        """读取特征图以及其原始分辨率"""
        path = os.path.join(FEATURES_DIR, f"{feature_id}.png")
        try:
            stat = os.stat(path)
        except FileNotFoundError:
            with self._data_lock:
                self._invalidate_raw_feature_cache(feature_id)
            return None, 0, 0

        cache_key = (stat.st_mtime_ns, stat.st_size)
        with self._data_lock:
            cached = self._raw_feature_cache.get(feature_id)
            if cached and cached[0] == cache_key:
                return cached[1], cached[2], cached[3]
            feat_info = self._db.get_feature_info(feature_id)
            w = feat_info.get("width", 0)
            h = feat_info.get("height", 0)

        mat = cv2.imread(path)
        if mat is None:
            return None, 0, 0

        with self._data_lock:
            self._raw_feature_cache[feature_id] = (cache_key, mat, w, h)
        return mat, w, h

    def load_feature_image(self, feature_id):
        """读取特征图以及其原始分辨率"""
        mat, w, h = self._load_feature_image_cached(feature_id)
        return (mat.copy() if mat is not None else None), w, h

    def _load_resized_feature(self, char_id, feature_id, current_scr_w, current_scr_h):
        saved_img, w, h = self._load_feature_image_cached(feature_id)
        if saved_img is None:
            return char_id, feature_id, None

        if w and h and (w != current_scr_w or h != current_scr_h):
            scale_x = current_scr_w / w
            scale_y = current_scr_h / h
            scale = min(scale_x, scale_y)
            save_h, save_w = saved_img.shape[:2]
            new_w = max(1, round(save_w * scale))
            new_h = max(1, round(save_h * scale))
            resized_saved = cv2.resize(saved_img, (new_w, new_h))
        else:
            scale = 1
            resized_saved = saved_img

        logger.debug(
            f"loaded {char_id} resized width {current_scr_w} / original_width:{w}, scale_x:{scale}"
        )
        return char_id, feature_id, resized_saved

    def match_feature(self, task: "BaseCombatTask", new_image_mat, threshold=0.6, target_char=None):
        """比对新截图与所有数据库内特征图，返回(是/否匹配, 匹配到的角色名, 相似度)"""
        current_scr_h, current_scr_w = task.height, task.width

        with self._data_lock:
            character_snapshot = self._db.get_character_feature_snapshot()
            current_fids = set()
            for feature_ids in character_snapshot.values():
                current_fids.update(feature_ids)

            need_rebuild = (
                self._cache_scr_w != current_scr_w
                or self._cache_scr_h != current_scr_h
                or self._cache_fids != current_fids
            )
            if need_rebuild:
                self._feature_cache.clear()
                self._cache_scr_w = current_scr_w
                self._cache_scr_h = current_scr_h
                self._cache_fids = current_fids

        if need_rebuild:
            rebuilt_cache = {}
            load_jobs = []
            for char_id, feature_ids in character_snapshot.items():
                rebuilt_cache[char_id] = {}
                for fid in feature_ids:
                    load_jobs.append((char_id, fid))

            worker_count = min(8, max(1, len(load_jobs)))
            if worker_count == 1:
                results = [
                    self._load_resized_feature(char_id, fid, current_scr_w, current_scr_h)
                    for char_id, fid in load_jobs
                ]
            else:
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    results = executor.map(
                        lambda job: self._load_resized_feature(
                            job[0], job[1], current_scr_w, current_scr_h
                        ),
                        load_jobs,
                    )

            for char_id, fid, resized_saved in results:
                if resized_saved is not None:
                    rebuilt_cache[char_id][fid] = resized_saved

            with self._data_lock:
                self._feature_cache = rebuilt_cache
                box = task.get_box_by_name(Labels.box_char_1)
                self._cache_mask = (
                    create_ellipse_mask(box.width, box.height, box.width * 0.4, box.height * 0.4)
                    if box
                    else None
                )

        with self._data_lock:
            cache_snapshot = {
                char_id: dict(features) for char_id, features in self._feature_cache.items()
            }

        best_match_char_id = None
        best_similarity = 0.0

        for char_id, cached_features in cache_snapshot.items():
            if target_char and char_id != target_char:
                continue
            for fid, cached_mat in cached_features.items():
                mask = None
                if self._cache_mask is not None:
                    if cached_mat.shape[0:2] == self._cache_mask.shape[0:2]:
                        mask = self._cache_mask
                    else:
                        mask = cv2.resize(
                            self._cache_mask,
                            (cached_mat.shape[1], cached_mat.shape[0]),
                            interpolation=cv2.INTER_NEAREST,
                        )

                if (
                    cached_mat.shape[0] > new_image_mat.shape[0]
                    or cached_mat.shape[1] > new_image_mat.shape[1]
                ):
                    ch = min(cached_mat.shape[0], new_image_mat.shape[0])
                    cw = min(cached_mat.shape[1], new_image_mat.shape[1])
                    cached_mat = cached_mat[:ch, :cw]
                    if mask is not None:
                        mask = mask[:ch, :cw]

                margin = 2
                if cached_mat.shape[0] > margin * 2 and cached_mat.shape[1] > margin * 2:
                    cached_mat = cached_mat[margin:-margin, margin:-margin]
                    if mask is not None:
                        mask = mask[margin:-margin, margin:-margin]

                res = cv2.matchTemplate(new_image_mat, cached_mat, cv2.TM_CCOEFF_NORMED, mask=mask)
                res[np.isinf(res)] = 0
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > best_similarity:
                    best_similarity = max_val
                    best_match_char_id = char_id

        if best_similarity >= threshold:
            return True, best_match_char_id, best_similarity
        return False, None, best_similarity

    def get_all_characters(self):
        """获取所有角色数据"""
        characters = {}
        for char_id, char_data in self._db.get_character_records().items():
            out = dict(char_data)
            char_name = str(out.pop("name", char_id)).strip() or char_id
            combo_id = "" if out.get("combo_id") is None else str(out.get("combo_id", ""))
            out["char_id"] = char_id
            out["char_name"] = char_name
            out["combo_id"] = combo_id
            out["combo_name"] = self.get_combo_name(combo_id)
            characters[char_id] = out
        return characters

    def get_character_combo_id_by_id(self, char_id: str) -> str:
        info = self.get_character_info_by_id(char_id)
        return info["combo_id"] if info else ""

    def get_character_combo_name_by_id(self, char_id: str) -> str:
        return self.get_combo_name(self.get_character_combo_id_by_id(char_id))

    def get_character_info_by_id(self, char_id: str) -> dict | None:
        char_info = self._db.get_character_record(char_id)
        if char_info is None:
            return None
        combo_id = "" if char_info.get("combo_id") is None else str(char_info.get("combo_id", ""))
        out = dict(char_info)
        char_name = str(out.pop("name", char_id)).strip() or char_id
        out["char_id"] = char_id
        out["char_name"] = char_name
        out["combo_id"] = combo_id
        out["combo_name"] = self.get_combo_name(combo_id)
        return out

    def get_fixed_team(self):
        return self._db.get_fixed_team()

    def set_fixed_team(self, enabled: bool, slots):
        self._db.set_fixed_team(enabled, slots)

    def clear_fixed_team(self):
        self._db.clear_fixed_team()


def create_ellipse_mask(w, h, rx, ry):
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (int(w // 2), int(h // 2))
    axes = (int(rx), int(ry))
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

    return mask


def show_masked_template(cached_mat, _cache_mask):
    h, w = cached_mat.shape[:2]

    if len(_cache_mask.shape) == 3:
        mask = _cache_mask[:, :, 0]
    else:
        mask = _cache_mask.copy()

    if mask.shape != (h, w):
        print(f"警告：尺寸不匹配！Mat: {h}x{w}, Mask: {mask.shape}。正在强制 resize...")
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

    mask = mask.astype(np.uint8)

    result = cv2.bitwise_and(cached_mat, cached_mat, mask=mask)
    result = cv2.resize(result, (w * 5, h * 5), interpolation=cv2.INTER_NEAREST)
    unmasked = cv2.resize(cached_mat, (w * 5, h * 5), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("Masked Result", result)
    cv2.imshow("unMasked Result", unmasked)
    cv2.waitKey(0)
