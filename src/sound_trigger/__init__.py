__all__ = ["SoundListener", "DodgeCounterTrigger", "SoundCombatContext"]


def __getattr__(name):
    if name == "SoundListener":
        from .SoundListener import SoundListener

        return SoundListener
    if name == "DodgeCounterTrigger":
        from .DodgeCounterTrigger import DodgeCounterTrigger

        return DodgeCounterTrigger
    if name == "SoundCombatContext":
        from .SoundCombatContext import SoundCombatContext

        return SoundCombatContext
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
