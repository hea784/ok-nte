"""Helpers for formatting rich text used by UI widgets."""

import re
from html import escape

_BRACKETED_TEXT_PATTERN = re.compile(r"\[([^\[\]]+)\]")


def highlight_bracketed_text(text: str, color_code: str) -> str:
    """Render square-bracketed labels in rich text using the supplied color."""
    color = escape(color_code, quote=True)
    return _BRACKETED_TEXT_PATTERN.sub(
        lambda match: f'<b style="color: {color};">{escape(match.group(1))}</b>', text
    )
