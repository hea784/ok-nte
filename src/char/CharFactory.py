import math
from typing import TYPE_CHECKING

from typing_extensions import Any

from src.Labels import Labels
from src.char.BaseChar import BaseChar
from src.char.Zero import Zero
from src.char.Mint import Mint

if TYPE_CHECKING:
    from src.char.custom.CustomCharManager import CustomCharManager
    from src.combat.BaseCombatTask import BaseCombatTask
    from ok import Box
    import numpy as np

char_dict: dict[str, dict[str, Any]] = {
    "char_default": {'cls': BaseChar},
    "char_zero": {'cls': Zero, 'cn_name': '零'},
    "char_mint": {'cls': Mint, 'cn_name': '薄荷'},
}

char_names = char_dict.keys()


def _build_char_instance(task, index, match_name, sim, manager: 'CustomCharManager'):
    from src.char.custom.CustomChar import CustomChar

    char_info = manager.get_character_info(match_name)
    combo_ref = manager.to_combo_ref(char_info.get("combo_ref", "")) if char_info else ""
    
    if not combo_ref:
        return BaseChar(task, index, char_name=match_name, confidence=sim)

    builtin_key = manager.get_builtin_key(combo_ref)
    if builtin_key and builtin_key in char_dict:
        cls: 'BaseChar' = char_dict[builtin_key].get('cls', BaseChar)
        instance: 'BaseChar' = cls(task, index, char_name=match_name, confidence=sim)
        instance.builtin_key = builtin_key
        instance.combo_label = manager.to_combo_label(combo_ref)
        return instance
    
    # Otherwise return default parsed CustomChar
    return CustomChar(task, index, char_name=match_name, confidence=sim)


def get_char_by_pos(task: 'BaseCombatTask', box: 'Box', index: int, old_char: BaseChar | None):
    # Retrieve CustomCharManager and test match
    from src.char.custom.CustomCharManager import CustomCharManager
    
    manager = CustomCharManager()
    cropped = box.crop_frame(task.frame)
    # Fast path check: if we already have an old_char, specifically test its matching only
    if old_char and old_char.confidence > 0.8:
        is_match, match_name, sim = manager.match_feature(task,cropped, threshold=0.8, target_char=old_char.char_name)
        if is_match and match_name == old_char.char_name:
            return _build_char_instance(task, index, match_name, sim, manager)
            
    # Perform Full DB Scan using the memory-cached match_feature
    is_match, match_name, sim = manager.match_feature(task, cropped, threshold=0.8)

    if is_match and match_name:
        return _build_char_instance(task, index, match_name, sim, manager)
        
    task.log_info(f"No match found for char {index + 1} set as default char")
    return BaseChar(task, index, char_name="unknown")

def get_char_feature_by_pos(task: 'BaseCombatTask', index, frame=None, scale_box=1.0, single_char=False) -> tuple['np.ndarray', int, int]:
    """
    Get the feature image of the character at the given position.
    
    Args:
        task: The combat task.
        index: The index of the character.
    
    Returns:
        A tuple containing the feature image, width, and height.
    """
    if frame is None:
        frame = task.frame
    box = task.get_box_by_name(f'box_char_{index + 1}')
    if single_char:
        offset = int(task.width * -9 / 2560)
        box = box.copy(x_offset=offset)
    if not math.isclose(scale_box, 1.0):
        box = box.scale(scale_box, scale_box)
    return box.crop_frame(frame), task.width, task.height

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
