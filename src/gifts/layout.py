from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GiftLayout:
    name_ratio: tuple[float, float, float, float] = (0.524, 0.166, 0.750, 0.240)
    gift_first_ratio: tuple[float, float, float, float] = (0.533, 0.497, 0.584, 0.534)
    gift_columns: int = 5
    gift_rows: int = 2
    gift_column_step: float = 0.0651
    gift_row_step: float = 0.1351
    unlimited_icon_x_offset_ratio: float = 0.10
    unlimited_icon_y_offset_ratio: float = 0.74
    unlimited_icon_width_reduction_ratio: float = 0.45
    character_slot_x: float = 0.946
    character_slot_ys: tuple[float, ...] = (0.177, 0.326, 0.472, 0.624, 0.772)
    sidebar_box: tuple[float, float, float, float] = (0.936, 0.146, 0.971, 0.205)
    sidebar_scroll_x: float = 0.947
    sidebar_scroll_y: float = 0.500
    sidebar_scroll_step: int = -5
    sidebar_reset_step: int = 40
    sidebar_scrolls_per_character: int = 5
    max_sidebar_pages: int = 30
    send_button: tuple[float, float] = (0.713, 0.806)
    counter_box: tuple[float, float, float, float] = (0.646, 0.780, 0.790, 0.840)


GIFT_LAYOUT = GiftLayout()
