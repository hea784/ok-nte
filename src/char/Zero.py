import time

from src.char.BaseChar import BaseChar


class Zero(BaseChar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_perform(self):
        if self.has_intro:
            self.continues_normal_attack(2)
        self.click_ultimate()
        self.click_skill()
