import cv2

from src import text_white_color
from src.utils import image_utils as iu

dialog_white_color = {
    "r": (220, 240),  # Red range
    "g": (220, 240),  # Green range
    "b": (220, 240),  # Blue range
}

lv_white_color = {
    "r": (235, 255),  # Red range
    "g": (235, 255),  # Green range
    "b": (235, 255),  # Blue range
}

lv_red_color = {
    "r": (235, 255),
    "g": (0, 1),
    "b": (0, 1),
}


def isolate_cd_to_black(cv_image):
    return iu.create_color_mask(cv_image, text_white_color, invert=True)


def isolate_lv_to_white(cv_image):
    cv_image = iu.restore_world_brightness(cv_image)
    mask_white = iu.create_color_mask(cv_image, lv_white_color, to_bgr=False)
    mask_red = iu.create_color_mask(cv_image, lv_red_color, to_bgr=False)
    mask = cv2.bitwise_or(mask_white, mask_red)
    mask = iu.dilate_mask(mask, to_bgr=False)
    return mask


def isolate_dialog_to_white(cv_image):
    return iu.create_color_mask(cv_image, dialog_white_color, invert=False)


def current_char_filter(cv_image, blur=False):
    if blur:
        hsv = iu.HSVRange((150, 140, 125), (179, 255, 255))
    else:
        hsv = iu.HSVRange((150, 170, 165), (179, 255, 255))
    return iu.filter_by_hsv(cv_image, hsv, return_mask=True)
