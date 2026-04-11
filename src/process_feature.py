import cv2
from src.tasks.BaseNTETask import binarize_bgr_by_brightness, binarize_bgr_by_adaptive_brightness
from src.Labels import Labels

from ok.feature.Feature import Feature

def process_feature(feature_name, feature: Feature):
    if feature_name in char_labels:
        feature.mat = binarize_bgr_by_brightness(feature.mat, threshold=180)
    if feature_name in element_labels:
        feature.mat = process_element(feature.mat, 0.47)
    match(feature_name):
        case Labels.boss_lv_text:
            feature.mat = binarize_bgr_by_brightness(feature.mat, threshold=180)
        case Labels.mini_map_arrow:
            feature.mat = binarize_bgr_by_brightness(feature.mat, threshold=200)

char_labels = {
    Labels.char_1_text, 
    Labels.char_2_text, 
    Labels.char_3_text, 
    Labels.char_4_text
}

element_labels = {
    Labels.blue_element,
    Labels.green_element,
    Labels.red_element,
    Labels.purple_element,
    Labels.yellow_element,
    Labels.white_element
}

def process_element(image, scale):
    resized = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    resized = binarize_bgr_by_brightness(resized, threshold=60)
    return resized
