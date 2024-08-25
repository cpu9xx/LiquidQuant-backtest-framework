# -*- coding: utf-8 -*-
from userStrategy import userconfig
config = {
  "mod": {
    "stock": {
      "enabled": True,
    },
    "future": {
        "enabled": False,
    }
  }
}
from .events import EventBus
class Env(object):
    _env = None
    def __init__(self, config):
        Env._env = self
        self.config = config
        self.event_bus = EventBus()
        self.usercfg = userconfig
        self.global_vars = None
        self.current_dt = None
        self.event_source = None

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Environment 对象
        """
        if Env._env is None:
            raise RuntimeError("策略还未初始化")
        return Env._env

    def set_global_vars(self, global_vars):
        self.global_vars = global_vars

    def set_event_source(self, event_source):
        self.event_source = event_source
