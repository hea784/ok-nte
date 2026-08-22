"""Audio output and routing integrations."""

from .routing import (
    DEFAULT_RENDER_DEVICE,
    audio_route_command,
    connect_background_audio_router,
    create_background_audio_routing_config_option,
    discover_output_devices,
    restore_background_audio_router,
    route_background_audio_for_current_window,
)

__all__ = [
    "DEFAULT_RENDER_DEVICE",
    "audio_route_command",
    "connect_background_audio_router",
    "create_background_audio_routing_config_option",
    "discover_output_devices",
    "restore_background_audio_router",
    "route_background_audio_for_current_window",
]
