"""Small locale helpers shared by UI surfaces."""

from ok import og


def is_chinese() -> bool:
    """Return whether the active application locale is any Chinese locale."""
    try:
        return bool(og.app and "zh" in og.app.locale.name())
    except Exception:
        return False
