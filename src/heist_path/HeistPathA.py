from src.heist_path.HeistPath import HeistPath


class HeistPathA(HeistPath):
    def run_path(self):
        self.arb_bank_goto_b1()
        self.arb_bank_b1_attack()
        self.arb_bank_goto_lg1()
        if not self.check_current_floor(1):
            # 这里之后加个薄荷狗哥死没死的检测，死了直接重开
            return False
        self.sleep(0.10)
        self.arb_bank_goto_colle()
        if not self.check_current_floor(2):
            # 这里之后加个薄荷死没死的检测，死了直接重开或者看谁还活着用新线路
            return False
        self.sleep(0.10)
        self.arb_bank_colle_f1_earn()
        self.arb_bank_goto_colle_f2()
        self.arb_bank_colle_f2_earn()
        self.arb_bank_goto_safeexit()

    def arb_bank_goto_b1(self):
        self.custom_log("寻路到大厅负一层")
        self.sleep(1.00)
        self.send_key(f"{self.config.get(self.CONF_MINT, 3)}", down_time=0.15)  # 再次确认使用薄荷
        self.sleep(0.10)
        self.send_key_down("w")
        self.sleep(4.50)
        self.send_key("d", down_time=3.404)
        self.sleep(1.00)
        self.send_key_up("w")
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.sleep(4.00)
        self.send_key_down("w")
        self.sleep(1.70)
        self.send_key("d", down_time=0.107)
        self.send_key("f", down_time=0.06)
        self.send_key("space", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.062)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.06)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.061)
        self.sleep(0.216)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.06)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.06)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.062)
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.send_key("space", down_time=0.061)
        self.sleep(0.20)
        self.send_key("f", down_time=0.061)
        self.send_key("space", down_time=0.06)
        self.sleep(0.215)
        self.send_key_up("w")
        self.sleep(0.10)
        self.send_key("f", down_time=0.062)
        self.sleep(0.15)
        self.send_key("f", down_time=0.062)
        self.sleep(0.15)
        self.send_key("f", down_time=0.062)
        self.sleep(5.0)
        self.send_key_down("w")
        self.sleep(1.00)
        self.send_key("a", down_time=1.00)
        self.sleep(1.00)
        self.send_key_up("w")
        self.sleep(0.10)
        self.send_key("a", down_time=4.60)
        self.sleep(0.10)
        self.send_key("s", down_time=1.52)
        self.sleep(0.10)
        self.send_key("d", down_time=2.50)
        self.sleep(0.10)
        self.send_key("s", down_time=0.06)
        self.sleep(0.10)
        self.send_key("s", down_time=0.06)
        self.sleep(0.10)
        self.click(0.50, 0.50, key="middle", down_time=0.15)
        self.sleep(0.10)

    # 早雾打怪，然后使用墙角重置定位
    def arb_bank_b1_attack(self):
        self.custom_log("大厅负一层，早雾打怪")
        self.sleep(0.10)
        self.send_key(f"{self.config.get(self.CONF_SAKIRI, 4)}", down_time=0.15)  # 切换到早雾
        self.sleep(0.10)
        self.send_key("w", down_time=2.20)  # press key 'w'
        self.sleep(0.10)
        self.send_key("s", down_time=2.00)  # press key 's'
        self.sleep(0.10)
        self.send_key("w", down_time=0.10)  # press key 'w'
        self.sleep(0.10)
        self.send_key("w", down_time=0.10)  # press key 'w'
        self.sleep(2.40)
        self.send_key("e", down_time=2.00)  # press key 'e'
        self.sleep(0.74)
        self.send_key("space", down_time=0.16)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(1.0)  # wait for 1.08s
        self.send_key("space", down_time=0.12)  # press key 'space'
        self.sleep(0.13)  # wait for 0.13s
        self.click(0.99, 0.01, down_time=0.15)  # left click at (0.99, 0.01)
        self.sleep(0.76)  # wait for 0.76s
        self.send_key("space", down_time=0.15)  # press key 'space'
        self.sleep(0.13)  # wait for 0.13s
        self.click(0.99, 0.01, down_time=0.15)  # left click at (0.99, 0.01)
        self.sleep(0.63)  # wait for 0.63s
        self.send_key("space", down_time=0.14)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.13)  # left click at (0.99, 0.01)
        self.sleep(0.35)  # wait for 0.35s
        self.send_key("space", down_time=0.16)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.17)  # left click at (0.99, 0.01)
        self.sleep(0.27)  # wait for 0.27s
        self.send_key("space", down_time=0.18)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.32)  # wait for 0.32s
        self.send_key("space", down_time=0.16)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.15)  # left click at (0.99, 0.01)
        self.sleep(0.29)  # wait for 0.29s
        self.send_key("space", down_time=0.19)  # press key 'space'
        self.sleep(0.17)  # wait for 0.17s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.30)  # wait for 0.30s
        self.send_key("space", down_time=0.18)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.15)  # left click at (0.99, 0.01)
        self.sleep(0.26)  # wait for 0.26s
        self.send_key("space", down_time=0.20)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.33)  # wait for 0.33s
        self.send_key("space", down_time=0.17)  # press key 'space'
        self.sleep(0.17)  # wait for 0.17s
        self.click(0.99, 0.01, down_time=0.15)  # left click at (0.99, 0.01)
        self.sleep(0.31)  # wait for 0.31s
        self.send_key("space", down_time=0.16)  # press key 'space'
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.98)  # wait for 0.98s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.send_key("space", down_time=0.15)  # press key 'space'
        self.sleep(0.92)  # wait for 0.92s
        self.send_key("space", down_time=0.12)  # press key 'space'
        self.sleep(0.18)  # wait for 0.18s
        self.send_key("space", down_time=0.16)  # press key 'space'
        self.sleep(0.15)  # wait for 0.15s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.40)  # wait for 0.40s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.18)  # wait for 0.18s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.17)  # wait for 0.17s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.38)  # wait for 0.38s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.33)  # wait for 0.33s
        self.click(0.99, 0.01, down_time=0.10)  # left click at (0.99, 0.01)
        self.sleep(0.45)  # wait for 0.45s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.send_key("space", down_time=0.15)  # press key 'space'
        self.sleep(0.16)  # wait for 0.16s
        self.click(0.99, 0.01, down_time=0.13)  # left click at (0.99, 0.01)
        self.sleep(0.42)  # wait for 0.42s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.10)  # wait for 0.10s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.42)  # wait for 0.42s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.10)  # wait for 0.10s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.42)  # wait for 0.42s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.10)  # wait for 0.10s
        self.click(0.99, 0.01, down_time=0.14)  # left click at (0.99, 0.01)
        self.sleep(0.43)  # wait for 0.43s
        self.send_key("space", down_time=0.13)  # press key 'space'
        self.sleep(0.60)
        self.custom_log("结束打怪，使用墙角重置定位")
        self.send_key("s", down_time=1.72)  # press key 's'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.13)  # press key 's'
        self.send_key("s", down_time=0.12)  # press key 's'
        self.send_key("s", down_time=0.12)  # press key 's'
        self.send_key("s", down_time=0.13)  # press key 's'
        self.send_key("s", down_time=0.12)  # press key 's'
        self.send_key("s", down_time=0.14)  # press key 's'
        self.send_key("s", down_time=0.08)  # press key 's'
        self.sleep(0.28)  # wait for 0.28s
        self.send_key("a", down_time=1.43)  # press key 'a'
        self.sleep(0.19)  # wait for 0.19s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.11)  # wait for 0.11s
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("a", down_time=0.07)  # press key 'a'
        self.sleep(0.10)  # wait for 0.10s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.sleep(0.11)  # wait for 0.11s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.10)  # wait for 0.10s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.11)  # wait for 0.11s
        self.send_key("a", down_time=0.07)  # press key 'a'
        self.sleep(0.10)  # wait for 0.10s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.10)  # wait for 0.10s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.07)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.25)  # wait for 0.25s
        self.send_key("s", down_time=0.09)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.09)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.10)  # press key 's'
        self.send_key("s", down_time=0.11)  # press key 's'
        self.sleep(0.16)  # wait for 0.16s
        self.send_key("a", down_time=0.11)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("a", down_time=0.07)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.send_key("a", down_time=0.09)  # press key 'a'
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.10)  # wait for 0.10s
        self.send_key("a", down_time=0.06)  # press key 'a'
        self.sleep(0.29)  # wait for 0.29s
        self.send_key("a", down_time=0.06)  # press key 'a'
        self.sleep(0.13)  # wait for 0.13s
        self.send_key("a", down_time=0.03)  # press key 'a'
        self.sleep(0.12)  # wait for 0.12s
        self.send_key("a", down_time=0.08)  # press key 'a'
        self.sleep(0.10)  # wait for 0.55s

    # 寻路到LG1层电梯
    def arb_bank_goto_lg1(self):
        self.custom_log("大厅负一层，寻路到LG1层电梯")
        self.send_key(f"{self.config.get(self.CONF_MINT, 3)}", down_time=0.15)  # 切换到薄荷
        self.sleep(0.10)
        self.send_key("a", down_time=0.15)
        self.sleep(0.10)
        self.send_key("s", down_time=0.15)
        self.sleep(0.10)
        self.send_key("d", down_time=1.28)
        self.sleep(0.10)
        self.send_key("w", down_time=5.27)
        self.sleep(0.10)
        self.send_key("d", down_time=0.45)
        self.sleep(0.10)
        self.send_key("w", down_time=2.25)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("w", down_time=1.60)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)

    # 寻路到藏品层电梯
    def arb_bank_goto_colle(self):
        self.custom_log("寻路到藏品层电梯")
        self.sleep(0.20)
        self.send_key("w", down_time=9.08)
        self.sleep(0.10)
        self.send_key("d", down_time=1.72)
        self.sleep(0.10)
        self.send_key("s", down_time=1.00)
        self.sleep(0.22)
        self.send_key("f", down_time=0.06)
        self.sleep(0.30)
        self.send_key("s", down_time=1.25)
        self.sleep(0.10)
        self.send_key_down("d")
        self.sleep(0.20)
        self.send_key("f", down_time=0.062)
        self.sleep(0.22)
        self.send_key("f", down_time=0.062)
        self.sleep(0.201)
        self.send_key("f", down_time=0.063)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.216)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.201)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.send_key_up("d")
        self.sleep(0.216)
        self.send_key_down("a")
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.201)
        self.send_key("f", down_time=0.062)
        self.sleep(0.216)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.202)
        self.send_key("f", down_time=0.061)
        self.sleep(0.217)
        self.send_key("f", down_time=0.061)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.203)
        self.send_key("f", down_time=0.062)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.202)
        self.send_key("f", down_time=0.062)
        self.sleep(0.201)
        self.send_key("f", down_time=0.061)
        self.sleep(0.215)
        self.send_key("f", down_time=0.062)
        self.sleep(0.215)
        self.send_key("f", down_time=0.061)
        self.sleep(0.201)
        self.send_key("f", down_time=0.062)
        self.send_key_up("a")
        self.sleep(0.308)
        self.send_key("d", down_time=0.403)
        self.sleep(0.109)
        self.send_key("w", down_time=2.01)
        self.sleep(0.108)
        self.send_key_down("d")
        self.sleep(0.051)
        self.send_key("f", down_time=0.057)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.142)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.063)
        self.send_key_up("d")
        self.sleep(0.108)
        self.send_key("w", down_time=2.024)
        self.sleep(0.109)
        self.send_key("d", down_time=3.205)
        self.sleep(0.109)
        self.send_key_down("d")
        self.sleep(0.159)
        self.send_key("f", down_time=0.058)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key_down("f")
        self.sleep(0.015)
        self.send_key_up("d")
        self.sleep(0.046)
        self.send_key_up("f")
        self.sleep(0.062)
        self.send_key("w", down_time=2.007)
        self.sleep(0.416)
        self.send_key("w", down_time=2.007)
        self.sleep(0.31)
        self.send_key("w", down_time=8.31)
        self.sleep(0.313)
        self.send_key_down("a")
        self.sleep(0.128)
        self.send_key("f", down_time=0.055)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key_up("a")
        self.sleep(0.51)
        self.send_key("s", down_time=1.315)
        self.sleep(0.109)
        self.send_key("w", down_time=0.201)
        self.sleep(0.309)
        self.send_key("a", down_time=1.514)
        self.sleep(0.109)
        self.send_key("d", down_time=0.201)
        self.sleep(0.108)
        self.send_key_down("w")
        self.sleep(0.176)
        self.send_key("f", down_time=0.057)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.059)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.14)
        self.send_key_down("a")
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.047)
        self.send_key_up("a")
        self.sleep(0.093)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.062)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key_down("f")
        self.sleep(0.015)
        self.send_key_up("w")
        self.sleep(0.047)
        self.send_key_up("f")
        self.sleep(0.061)
        self.send_key("s", down_time=0.155)
        self.sleep(0.109)
        self.send_key("d", down_time=2.507)
        self.sleep(0.108)
        self.send_key("a", down_time=0.403)
        self.sleep(0.108)
        self.send_key("w", down_time=5.303)
        self.sleep(0.111)
        self.send_key_down("d")
        self.sleep(0.106)
        self.send_key("s", down_time=3.311)
        self.sleep(0.112)
        self.send_key_up("d")
        self.sleep(0.104)
        self.send_key("a", down_time=0.308)
        self.sleep(0.108)
        self.send_key("w", down_time=1.514)
        self.sleep(0.108)
        self.send_key("a", down_time=0.108)
        self.sleep(0.109)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.249)
        self.send_key_down("w")
        self.sleep(0.068)
        self.send_key("f", down_time=0.054)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.062)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.062)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.sleep(0.141)
        self.send_key("f", down_time=0.06)
        self.sleep(0.217)
        self.send_key("d", down_time=2.615)
        self.sleep(0.107)
        self.send_key_up("w")
        self.sleep(0.108)
        self.send_key("a", down_time=0.31)
        self.sleep(0.312)
        self.send_key_down("w")
        self.sleep(0.216)
        self.send_key("space", down_time=0.061)
        self.sleep(0.309)
        self.send_key("space", down_time=0.061)
        self.sleep(1.903)
        self.send_key("d", down_time=1.609)
        self.sleep(0.108)
        self.send_key_up("w")
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.sleep(0.14)
        self.send_key("f", down_time=0.062)
        self.sleep(0.448)
        self.send_key_down("w")
        self.sleep(0.216)
        self.send_key_down("d")
        self.sleep(0.604)
        self.send_key("space", down_time=0.062)
        self.sleep(0.556)
        self.send_key("space", down_time=0.061)
        self.sleep(0.139)
        self.send_key_up("d")
        self.sleep(0.108)
        self.send_key_up("w")
        self.send_key("f", down_time=0.06)
        self.sleep(0.109)
        self.send_key("f", down_time=0.062)
        self.sleep(0.109)
        self.send_key_down("d")
        self.sleep(1.403)
        self.send_key("w", down_time=0.806)
        self.sleep(0.108)
        self.send_key_up("d")
        self.sleep(0.10)
        self.send_key("s", down_time=0.463)
        self.sleep(0.10)
        self.send_key("d", down_time=0.602)
        self.sleep(0.10)
        self.send_key_down("w")
        self.sleep(0.02)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.06)
        self.sleep(0.10)
        self.send_key_up("w")
        self.sleep(0.10)
        self.send_key("d", down_time=0.72)
        self.sleep(0.10)
        self.send_key("f", down_time=0.06)
        self.send_key("f", down_time=0.06)
        self.send_key("s", down_time=0.68)
        self.send_key("f", down_time=0.06)
        self.send_key("f", down_time=0.06)
        self.send_key("f", down_time=0.06)
        self.send_key("f", down_time=0.06)
        self.sleep(6.00)  # 这里最好加个检测是否有保险箱要翘的判断
        self.send_key("f", down_time=0.06)
        self.send_key("f", down_time=0.06)
        self.sleep(0.139)
        self.send_key("f", down_time=0.061)
        self.send_key("f", down_time=0.06)
        self.sleep(0.14)
        self.send_key("f", down_time=0.061)
        self.send_key("s", down_time=1.57)
        self.sleep(0.10)
        self.send_key("d", down_time=1.25)
        self.sleep(0.10)
        self.send_key_down("w")
        self.sleep(1.0)
        self.send_key(f"{self.config.get(self.CONF_DOGBRO, 2)}", down_time=0.1)  # 切狗哥潜行
        self.sleep(1.0)
        self.send_key("lshift", down_time=2.00)
        self.sleep(0.5)
        self.send_key("lshift", down_time=2.00)
        self.sleep(6.0)
        self.send_key_up("w")
        self.send_key(f"{self.config.get(self.CONF_MINT, 3)}", down_time=0.1)  # 切薄荷
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(9.00)
        self.send_key("w", down_time=1.00)
        self.sleep(0.20)
        self.send_key("f", down_time=0.10)
        self.sleep(0.10)
        self.send_key("f", down_time=0.10)
        self.sleep(2.20)

    # 藏品层一楼搜刮
    def arb_bank_colle_f1_earn(self):
        self.custom_log("在藏品层一楼进行搜刮")
        self.sleep(0.10)

    # 前往藏品层二楼
    def arb_bank_goto_colle_f2(self):
        self.custom_log("前往藏品层二楼")
        self.sleep(0.10)

    # 藏品层二楼搜刮
    def arb_bank_colle_f2_earn(self):
        self.custom_log("在藏品层二楼进行搜刮")
        self.sleep(0.10)

    # 前往安全撤离点
    def arb_bank_goto_safeexit(self):
        self.custom_log("前往安全撤离点")
        self.sleep(0.10)
