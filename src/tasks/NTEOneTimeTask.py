from ok import PostMessageInteraction
from ok.device.intercation import PynputInteraction


class NTEOneTimeTask:

    def run(self, *args, **kwargs):
        if isinstance(self.executor.interaction, PostMessageInteraction):
            self.executor.interaction.activate()
        elif isinstance(self.executor.interaction, PynputInteraction):
            self.bring_to_front()
        self.sleep(0.5)
        self.set_check_monthly_card()
        return super().run(*args, **kwargs)