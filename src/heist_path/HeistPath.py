from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.tasks.AutoHeistTask import AutoHeistTask


class HeistPath:
    def __init__(self, task: AutoHeistTask):
        self.task = task

    @property
    def config(self) -> Any:
        """任务配置。"""
        return self.task.config

    @property
    def CONF_NANALLY(self) -> str:
        """娜娜莉位置配置键。"""
        return self.task.CONF_NANALLY

    @property
    def CONF_MINT(self) -> str:
        """薄荷位置配置键。"""
        return self.task.CONF_MINT

    @property
    def CONF_DOGBRO(self) -> str:
        """狗哥位置配置键。"""
        return self.task.CONF_DOGBRO

    @property
    def CONF_SAKIRI(self) -> str:
        """早雾位置配置键。"""
        return self.task.CONF_SAKIRI

    @property
    def custom_log(self):
        """记录路径日志 (代理到 task.custom_log)。"""
        return self.task.custom_log

    @property
    def sleep(self):
        """等待指定秒数 (代理到 task.sleep)。"""
        return self.task.sleep

    @property
    def send_key(self):
        """发送按键 (代理到 task.send_key)。"""
        return self.task.send_key

    @property
    def send_key_down(self):
        """按下按键 (代理到 task.send_key_down)。"""
        return self.task.send_key_down

    @property
    def send_key_up(self):
        """松开按键 (代理到 task.send_key_up)。"""
        return self.task.send_key_up

    @property
    def click(self):
        """点击屏幕坐标或 Box (代理到 task.click)。"""
        return self.task.click

    @property
    def operate_click(self):
        """操作式点击屏幕坐标或 Box (代理到 task.operate_click)。"""
        return self.task.operate_click

    @property
    def wait_ocr(self):
        """等待 OCR 匹配结果 (代理到 task.wait_ocr)。"""
        return self.task.wait_ocr
    
    @property
    def check_current_floor(self):
        return self.task.check_current_floor
