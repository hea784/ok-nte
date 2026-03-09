import cv2
import numpy as np
from typing import List

from ok import BaseTask, Box
from src.scene.NTEScene import NTEScene
from src.Labels import Labels


class BaseNTETask(BaseTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene: NTEScene | None = None
        self.key_config = self.get_global_config('Game Hotkey Config')
        self._logged_in = False

    def in_team(self):
        c1 = self.find_one(Labels.char_1_text, threshold=0.7, frame_processor=binarize_bgr_by_brightness)
        c2 = self.find_one(Labels.char_2_text, threshold=0.7, frame_processor=binarize_bgr_by_brightness)
        c3 = self.find_one(Labels.char_3_text, threshold=0.7, frame_processor=binarize_bgr_by_brightness)
        c4 = self.find_one(Labels.char_4_text, threshold=0.7, frame_processor=binarize_bgr_by_brightness)
        arr: List[Box | None] = [c1, c2, c3, c4]
        current = -1
        exist_count = 0
        for i in range(len(arr)):
            if arr[i] is None:
                if current == -1:
                    current = i
            else:
                exist_count += 1
        if exist_count > 0:
            self._logged_in = True
            return True, current, exist_count + 1
        else:
            return False, -1, exist_count + 1

    def in_team_and_world(self):
        in_team, _, _ = self.in_team()
        in_world = True
        return in_team and in_world


lower_white = np.array([244, 244, 244], dtype=np.uint8)
upper_white = np.array([255, 255, 255], dtype=np.uint8)
black = np.array([0, 0, 0], dtype=np.uint8)
lower_white_none_inclusive = np.array([190, 190, 190], dtype=np.uint8)

def isolate_white_text_to_black(cv_image):
    """
    Converts pixels in the near-white range (244-255) to black,
    and all others to white.
    Args:
        cv_image: Input image (NumPy array, BGR).
    Returns:
        Black and white image (NumPy array), where matches are black.
    """
    match_mask = cv2.inRange(cv_image, black, lower_white_none_inclusive)
    output_image = cv2.cvtColor(match_mask, cv2.COLOR_GRAY2BGR)

    return output_image

def binarize_bgr_by_brightness(image):
    """
    根据亮度阈值对 BGR 图像进行二值化，并返回 BGR 格式的结果。
    
    参数:
    - image: 输入的 BGR 图像 (MatLike)
    
    返回:
    - 经过二值化处理的 BGR 图像 (MatLike)
    """
    # from hashlib import sha256
    # h = sha256(image.tobytes()).hexdigest()
    threshold = 200
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_gray = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    binary_bgr = cv2.cvtColor(binary_gray, cv2.COLOR_GRAY2BGR)
    # cv2.imwrite(f'{h}.png', binary_bgr)
    
    return binary_bgr