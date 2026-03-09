from src.tasks.BaseNTETask import binarize_bgr_by_brightness
from src.Labels import Labels

def process_feature(feature_name, feature):
    if feature_name == Labels.char_1_text:
        feature.mat = binarize_bgr_by_brightness(feature.mat)
    elif feature_name == Labels.char_2_text:
        feature.mat = binarize_bgr_by_brightness(feature.mat)
    elif feature_name == Labels.char_3_text:
        feature.mat = binarize_bgr_by_brightness(feature.mat)
    elif feature_name == Labels.char_4_text:
        feature.mat = binarize_bgr_by_brightness(feature.mat)
