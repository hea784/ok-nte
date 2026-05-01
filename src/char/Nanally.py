import time

from src.char.BaseChar import BaseChar


class Nanally(BaseChar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_perform(self):
        if self.has_intro:
            self.continues_normal_attack(2)
        self.click_skill()
        if self.click_ultimate():
            self.perform_in_ult()

    def perform_in_ult(self):
        start = time.time()
        while (elapsed := time.time() - start) < 6:
            if elapsed > 1 and self.ultimate_available():
                start = time.time()
            self.normal_attack()
            self.sleep(0.2)
