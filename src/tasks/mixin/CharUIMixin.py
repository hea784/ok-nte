import time
from dataclasses import dataclass

import cv2
import numpy as np
from ok import BaseTask, Box

from src.Labels import Labels
from src.utils import game_filters as gf
from src.utils import image_utils as iu


@dataclass
class _CurrentCharDetection:
    index: int
    score: float
    scores: list[float]
    accepted: bool
    strong: bool
    reason: str
    raw_scores: list[float]
    core_scores: list[float] | None


@dataclass(frozen=True)
class _CurrentCharConfig:
    reject_score: float = 0.75
    accept_score: float = 0.45
    raw_candidate_score: float = 0.85
    raw_candidate_margin: float = 0.06
    raw_strong_score: float = 0.45
    raw_strong_margin: float = 0.15
    core_strong_score: float = 0.70
    core_strong_margin: float = 0.08
    sticky_seconds: float = 0.8


class CharUIMixin(BaseTask):
    _CURRENT_CHAR = _CurrentCharConfig()

    def _init_char_ui_state(self):
        self._char_ui_offset = False
        self._current_char_tracker = {
            "index": -1,
            "score": 1.0,
            "time": 0,
            "reason": "",
        }

    def _get_char_text_box(self, index: int):
        box = self.get_box_by_name(f"char_{index + 1}_text")
        return box

    def get_base_char_element_box(self):
        box = self.box_of_screen_scaled(
            2560, 1440, 2438, 335, width_original=29, height_original=29
        )
        box = self._shift_char_ui_box(box, expend=True)
        return box

    def _shift_char_ui_box(self, box: Box, expend=False):
        offset = -9 * self.width / 2560
        width_offset = 0
        if expend:
            width_offset = -offset
        box = box.copy(x_offset=offset, width_offset=width_offset)
        return box

    @property
    def _char_vertical_spacing(self):
        return int(self.height * 176 / 1440)

    def get_box_by_char_spacing(self, box: Box, index: int):
        return box.copy(y_offset=index * self._char_vertical_spacing, name=f"{box.name}_{index}")

    def _get_char_template_data(self):
        if (
            not hasattr(self, "_char_template_cache")
            or self._char_template_cache.get("width") != self.width
            or self._char_template_cache.get("height") != self.height
        ):
            feature = self.get_feature_by_name(Labels.is_current_char)
            mat: np.ndarray = feature.mat
            if len(mat.shape) == 3 and mat.shape[2] != 2:
                mat = gf.current_char_filter(mat)
            self._char_template_cache = {
                "width": self.width,
                "height": self.height,
                "mat": mat,
            }

        return self._char_template_cache["mat"]

    def _match_current_char_feature(self, current_mat: np.ndarray, template_mat: np.ndarray):
        th, tw = template_mat.shape[:2]
        ch, cw = current_mat.shape[:2]
        if ch < th or cw < tw:
            return 1.0

        result = cv2.matchTemplate(current_mat, template_mat, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if np.isnan(max_val):
            return 1.0
        return 1.0 - max_val

    def _get_current_char_core_scores(self, frame, template_mat, base_box):
        """Match the stable inner part of the current-character marker."""
        tpl_x, tpl_y, width, height = 6, 3, 20, 21
        frame_x, frame_y = 15, 3

        template_slice = template_mat[tpl_y : tpl_y + height, tpl_x : tpl_x + width]
        if template_slice.shape[0] < 8 or template_slice.shape[1] < 12:
            return None

        scores = []
        for i in range(4):
            box = self.get_box_by_char_spacing(base_box, i)
            current_mat = gf.current_char_filter(box.crop_frame(frame))
            marker_slice = current_mat[
                frame_y : frame_y + height,
                frame_x : frame_x + width,
            ]
            scores.append(self._match_current_char_feature(marker_slice, template_slice))
        return scores

    def _build_current_char_scores(self, index, score, accepted):
        scores = [self._CURRENT_CHAR.reject_score] * 4
        if accepted and 0 <= index < len(scores):
            scores[index] = min(score, self._CURRENT_CHAR.accept_score)
        return scores

    def _rank_current_char_scores(self, scores):
        if not scores:
            return -1, 1.0, 0.0
        best_idx = int(np.argmin(scores))
        ordered_scores = sorted(scores)
        best_score = ordered_scores[0]
        second_score = ordered_scores[1] if len(ordered_scores) > 1 else 1.0
        return best_idx, best_score, second_score - best_score

    def _get_current_char_boxes(self):
        base_box = self.get_box_by_name(Labels.is_current_char)
        base_box = self._shift_char_ui_box(base_box, expend=True)
        return base_box, [self.get_box_by_char_spacing(base_box, i) for i in range(4)]

    def _detect_current_char_once(self, frame=None):
        if frame is None:
            frame = self.frame
        if frame is None:
            return _CurrentCharDetection(
                index=-1,
                score=1.0,
                scores=[self._CURRENT_CHAR.reject_score] * 4,
                accepted=False,
                strong=False,
                reason="empty_frame",
                raw_scores=[1.0] * 4,
                core_scores=None,
            )

        template_mat = self._get_char_template_data()
        base_box, boxes = self._get_current_char_boxes()
        raw_scores = []
        for box in boxes:
            current_mat = gf.current_char_filter(box.crop_frame(frame))
            raw_scores.append(self._match_current_char_feature(current_mat, template_mat))

        raw_idx, raw_score, raw_margin = self._rank_current_char_scores(raw_scores)
        core_scores = self._get_current_char_core_scores(frame, template_mat, base_box)
        core_idx, core_score, core_margin = self._rank_current_char_scores(core_scores or [])

        index = raw_idx
        score = 1.0
        accepted = False
        strong = False
        reason = "rejected"

        raw_candidate = (
            raw_score <= self._CURRENT_CHAR.raw_candidate_score
            and raw_margin >= self._CURRENT_CHAR.raw_candidate_margin
        )
        raw_strong = (
            raw_score <= self._CURRENT_CHAR.raw_strong_score
            and raw_margin >= self._CURRENT_CHAR.raw_strong_margin
        )
        core_strong = (
            core_scores is not None
            and core_score <= self._CURRENT_CHAR.core_strong_score
            and core_margin >= self._CURRENT_CHAR.core_strong_margin
        )

        if core_scores is not None and raw_idx == core_idx and raw_candidate:
            index = raw_idx
            score = max(0.0, min(raw_score, core_score) - min(raw_margin, core_margin))
            accepted = True
            strong = True
            reason = "raw_core_agree"
        elif core_strong:
            raw_support = (
                raw_scores[core_idx] <= self._CURRENT_CHAR.raw_candidate_score
                or raw_scores[core_idx] <= raw_score + 0.20
            )
            if raw_support:
                index = core_idx
                score = max(0.0, core_score - core_margin)
                accepted = True
                strong = core_margin >= self._CURRENT_CHAR.raw_candidate_margin
                reason = "core_strong"
        elif raw_strong:
            index = raw_idx
            score = max(0.0, raw_score - min(raw_margin, self._CURRENT_CHAR.raw_strong_margin))
            accepted = True
            strong = True
            reason = "raw_strong"

        scores = self._build_current_char_scores(index, score, accepted)
        if 0 <= index < len(boxes):
            self.draw_boxes(boxes=boxes[index], color="red")

        return _CurrentCharDetection(
            index=index if accepted else -1,
            score=score if accepted else 1.0,
            scores=scores,
            accepted=accepted,
            strong=strong,
            reason=reason,
            raw_scores=raw_scores,
            core_scores=core_scores,
        )

    def _apply_current_char_tracker(self, detection: _CurrentCharDetection):
        now = time.time()
        tracker = self._current_char_tracker
        if detection.accepted:
            tracker["index"] = detection.index
            tracker["score"] = detection.score
            tracker["time"] = now
            tracker["reason"] = detection.reason
            return detection

        if tracker["index"] != -1 and now - tracker["time"] <= self._CURRENT_CHAR.sticky_seconds:
            index = tracker["index"]
            score = max(tracker["score"], self._CURRENT_CHAR.accept_score)
            scores = self._build_current_char_scores(index, score, accepted=True)
            return _CurrentCharDetection(
                index=index,
                score=scores[index],
                scores=scores,
                accepted=True,
                strong=False,
                reason=f"sticky:{tracker['reason']}",
                raw_scores=detection.raw_scores,
                core_scores=detection.core_scores,
            )

        return detection

    def _get_current_char_detection(self, frame=None):
        detection = self._detect_current_char_once(frame=frame)
        if frame is None:
            return self._apply_current_char_tracker(detection)
        return detection

    def _get_char_match_scores(self, frame=None):
        """Return four slot scores; lower means the slot is the current char."""
        return self._get_current_char_detection(frame=frame).scores

    def get_current_char_index(self):
        # frame = self.frame
        detection = self._get_current_char_detection()
        if detection.accepted:
            self.log_debug(
                f"current_char found at {detection.index} "
                f"with score {detection.score:.4f} ({detection.reason})"
            )
            # if detection.score > 0.5:
            #     self.screenshot("low_conf", frame)
            return detection.index

        self.log_debug(
            f"current_char rejected ({detection.reason}) raw={detection.raw_scores} "
            f"core={detection.core_scores}"
        )
        return -1

    def _multi_stage_char_match(self):
        results = [None, None, None, None]
        contrast_steps = [0, 30, 60, 90]

        for c_val in contrast_steps:
            if all(res is not None for res in results):
                break

            for i in range(4):
                if results[i] is not None:
                    continue

                def process(image, current_c=c_val):
                    return iu.adjust_lightness_contrast_lab(image, brightness=0, contrast=current_c)

                res = self.find_one(
                    f"char_{i + 1}_text",
                    threshold=0.7,
                    frame_processor=process,
                    mask_function=iu.mask_outside_white_rect,
                    horizontal_variance=0.005,
                )
                if res:
                    results[i] = res

        return results

    def _update_char_ui_offset(self):
        # now = time.time()
        arr = self._multi_stage_char_match()
        results = [
            c.x < self._get_char_text_box(idx).x for idx, c in enumerate(arr) if c is not None
        ]

        if results:
            self._char_ui_offset = sum(results) > (len(results) / 2)
        else:
            self._char_ui_offset = False
        # logger.debug(f"update_char_ui_offset cost {time.time() - now:.3f}")
        return arr
