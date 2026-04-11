import cv2
import numpy as np
from typing import List
import time

from ok import BaseTask, Box
from src.scene.NTEScene import NTEScene
from src.Labels import Labels


class BaseNTETask(BaseTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene: NTEScene | None = None
        self.key_config = self.get_global_config('Game Hotkey Config')
        self._logged_in = False
        self.arrow_contour = {"contours": None, "shape":None}

    def is_in_team(self):
        find_box = self.get_box_by_name(Labels.health_bar_slash).scale(1.5)
        box = self.find_one(Labels.health_bar_slash, box=find_box, mask_function=mask_corners)
        result = box is not None
        self.log_debug(f"is_in_team {box}")
        return result

    def in_team(self):
        if not self.is_in_team():
            return False, -1, 0

        def process_char_text(image):
            return binarize_bgr_by_brightness(image, threshold=180)
        
        c1 = self.find_one(Labels.char_1_text, threshold=0.7, frame_processor=process_char_text, mask_function=mask_outside_white_rect)
        c2 = self.find_one(Labels.char_2_text, threshold=0.7, frame_processor=process_char_text, mask_function=mask_outside_white_rect)
        c3 = self.find_one(Labels.char_3_text, threshold=0.7, frame_processor=process_char_text, mask_function=mask_outside_white_rect)
        c4 = self.find_one(Labels.char_4_text, threshold=0.7, frame_processor=process_char_text, mask_function=mask_outside_white_rect)
        arr: List[Box | None] = [c1, c2, c3, c4]
        self.log_debug(f"in_team {arr}")
        current = -1
        exist_count = 0
        for i in range(len(arr)):
            if arr[i] is None:
                if current == -1:
                    current = i
            else:
                exist_count += 1

        self._logged_in = True
        return True, current, exist_count + 1
        
    def in_world(self) -> bool:
        frame = self.frame
        if self.arrow_contour["shape"] != frame.shape[:2]:
            template_bgr = self.get_feature_by_name(Labels.mini_map_arrow).mat
            t_bin = template_bgr[:, :, 0]
            contours, _ = cv2.findContours(t_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                raise ValueError("contours is None")
            self.arrow_contour["contours"] = max(contours, key=cv2.contourArea)
            self.arrow_contour["shape"] = frame.shape[:2]

        mat = self.box_of_screen(0.0691, 0.1083, 0.0949, 0.1493, name="in_world").crop_frame(frame)
        mat = binarize_bgr_by_brightness(mat, threshold=200)
        res, cost = self._find_rotated_shape(mat)
        self.log_debug(f"in_world {res}, cost {cost} ms")
        return len(res) == 1

    def _find_rotated_shape(self, scene_bgr, score_threshold=0.1):
        """
        score_threshold: 越小越严格。通常 0.05-0.2 之间。
        """
        start_time = time.time()
        s_bin = scene_bgr[:, :, 0]
        scene_contours, _ = cv2.findContours(s_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        for cnt in scene_contours:
            if cv2.contourArea(cnt) < 50:
                continue
            
            # 核心算法：比较两个形状的胡氏矩 (I1 模式最常用)
            # 返回值越小，匹配度越高（0 为完美匹配）
            score = cv2.matchShapes(self.arrow_contour["contours"], cnt, cv2.CONTOURS_MATCH_I1, 0.0)
            
            if score < score_threshold:
                # 计算重心和角度
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # 使用最小外接矩形获取角度
                    rect = cv2.minAreaRect(cnt)
                    angle = rect[2] # 得到角度
                    
                    results.append({
                        'center': (cx, cy),
                        'angle': angle,
                        'score': score
                    })
        
        # 按分数升序排列（得分越低越好）
        results = sorted(results, key=lambda x: x['score'])
        return results, (time.time() - start_time) * 1000

    def in_team_and_world(self):
        in_team = self.in_team()[0]
        in_world = self.in_world()
        return in_team and in_world
    
    def wait_in_team_and_world(self, time_out=10, raise_if_not_found=True, esc=False):
        success = self.wait_until(self.in_team_and_world, time_out=time_out, raise_if_not_found=raise_if_not_found,
                                  post_action=lambda: self.back(after_sleep=2) if esc else None)
        if success:
            self.sleep(0.1)
        return success

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

def binarize_bgr_by_brightness(image, threshold=180):
    """
    根据亮度阈值对 BGR 图像进行二值化，并返回 BGR 格式的结果。
    
    参数:
    - image: 输入的 BGR 图像 (MatLike)
    
    返回:
    - 经过二值化处理的 BGR 图像 (MatLike)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_gray = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    binary_bgr = cv2.cvtColor(binary_gray, cv2.COLOR_GRAY2BGR)
    
    return binary_bgr

def binarize_bgr_by_adaptive_center(image):
    """
    根据图像中心 50% 范围的亮度自适应计算阈值，并对全图进行二值化。
    
    参数:
    - image: 输入的 BGR 图像 (MatLike)
    
    返回:
    - 经过二值化处理的 BGR 图像 (MatLike)
    """
    # 1. 获取图像尺寸
    h, w = image.shape[:2]
    
    # 2. 确定中心 50% 的范围 (即长宽各取中间的 1/2 区域)
    y1, y2 = h // 4, 3 * h // 4
    x1, x2 = w // 4, 3 * w // 4
    
    # 3. 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 4. 提取中心区域 (ROI)
    roi = gray[y1:y2, x1:x2]
    
    # 5. 使用 Otsu 算法在 ROI 区域自动计算阈值
    # cv2.THRESH_OTSU 会忽略传入的 0，自动返回最佳阈值 ret
    ret, _ = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 6. 使用计算出的阈值对整张灰度图进行二值化
    _, binary_gray = cv2.threshold(gray, ret, 255, cv2.THRESH_BINARY)
    
    # 7. 转回 BGR 格式
    binary_bgr = cv2.cvtColor(binary_gray, cv2.COLOR_GRAY2BGR)
    
    return binary_bgr

def blackout_corners_by_circle(image):
    """
    以方形图像中心为圆心，到边长的距离为半径，将半径以外的四个角区域涂黑。
    
    参数:
    - image: 输入的 BGR 图像 (MatLike)，通常应为正方形
    
    返回:
    - 处理后的 BGR 图像
    """
    # 1. 获取图像的尺寸
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # 2. 计算半径（中心到边长的距离）
    # 如果是非方形图像，取宽和高中较小的那个的一半作为半径
    radius = min(w, h) // 2
    
    # 3. 创建一个全黑的遮罩 (与原图大小相同，单通道)
    # 也可以直接创建三通道遮罩，这里用单通道更节省内存
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # 4. 在遮罩上画一个白色的实心圆 (颜色为 255)
    # 参数：(图像, 圆心坐标, 半径, 颜色, 粗细=-1表示填充)
    cv2.circle(mask, center, radius, 255, thickness=-1)
    
    # 5. 将遮罩应用到原图上
    # 使用 bitwise_and，只有遮罩中为白色（255）的部分会被保留，黑色部分变为 0
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    return masked_image

def binarize_bgr_by_adaptive_brightness(image, ratio_threshold=0.05, offset=20, min_threshold=100):
    """
    根据图像平均亮度动态计算“高亮度”阈值进行二值化。
    
    参数:
    - image: 输入 BGR 图像
    - ratio_threshold: 高亮度像素占总像素的比例 (0.01 表示 1%)
    - offset: 定义“高亮度”比平均亮度高出多少 (0-255)
    - min_threshold: 允许的最小高亮度阈值，防止在纯黑图像中误触发
    
    返回:
    - 经过二值化处理的 BGR 图像
    """
    # 1. 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. 计算当前图像的平均亮度
    avg_brightness = np.mean(gray)
    
    # 3. 计算“候选”高亮度阈值
    # 逻辑：高亮度 = 平均亮度 + 偏移量
    # 使用 np.clip 确保阈值在 0-255 之间，且不低于 min_threshold
    candidate_threshold = np.clip(avg_brightness + offset, min_threshold, 255)
    
    # 4. 统计超过该候选阈值的像素比例
    high_brightness_pixels = np.sum(gray > candidate_threshold)
    total_pixels = gray.shape[0] * gray.shape[1]
    current_ratio = high_brightness_pixels / total_pixels

    # 5. 判定并设定最终二值化阈值
    if current_ratio >= ratio_threshold:
        final_threshold = candidate_threshold
    else:
        final_threshold = 255

    _, binary_gray = cv2.threshold(gray, int(final_threshold), 255, cv2.THRESH_BINARY)
    binary_bgr = cv2.cvtColor(binary_gray, cv2.COLOR_GRAY2BGR)
    
    return binary_bgr

def mask_corners(image, ratio_w=0.5555, ratio_h=0.8571):
    h, w = image.shape[:2]
    
    # 1. 计算左上角三角区域顶点
    pt1_tl = [0, 0]
    pt2_tl = [int(w * ratio_w), 0]
    pt3_tl = [0, int(h * ratio_h)]
    
    # 2. 计算右下角三角区域顶点
    pt1_br = [w, h]
    pt2_br = [int(w * (1 - ratio_w)), h]
    pt3_br = [w, int(h * (1 - ratio_h))]
    
    # 定义多边形点集
    contours = [
        np.array([pt1_tl, pt2_tl, pt3_tl], dtype=np.int32),
        np.array([pt1_br, pt2_br, pt3_br], dtype=np.int32)
    ]
    
    # 在掩码图上填充白色
    white = np.ones_like(image) * 255
    result = cv2.fillPoly(white, contours, (0, 0, 0)) # 黑色填充
    
    return result

def mask_outside_white_rect(image):
    # 转为灰度图以便寻找白色像素边界
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 获得图像内白色部份的矩形范围边界
    x, y, w, h = cv2.boundingRect(gray)
    
    # 创建与原图等大且全黑的 mask
    mask = np.zeros_like(image)
    
    # 将矩形范围内设为全白 (保留作为mask)
    if w > 0 and h > 0:
        mask[y:y+h, x:x+w] = 255
        
    return mask

def display_image(image, name="image"):
    cv2.imshow(name, image)
    cv2.waitKey(0)