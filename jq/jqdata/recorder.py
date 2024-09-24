from .Env import Env
from .events import EVENT
from .api import setting
from .logger import log

import matplotlib.pyplot as plt
import datetime

class Recorder(object):
    def __init__(self):
        self._ucontext = None
        self._env = Env.get_instance()
        self._returns_ls =[]
        self._bm_returns_ls = []
        self._dt_ls = []
        self._bm_start_price = None
        event_bus = self._env.event_bus
        event_bus.add_listener(EVENT.MARKET_CLOSE, self._pnl)
        event_bus.add_listener(EVENT.FIRST_TICK, self._set_bm_start_price)

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def get_index_price(self, security):
        dtime = self._env.current_dt
        if datetime.time(9, 30) <= dtime.time() < datetime.time(15, 0):
            field = 'open'
        else:
            field = 'close'
            if datetime.time(0, 0) <= dtime.time() < datetime.time(9, 30):
                dtime += datetime.timedelta(days=-1, hours=0, minutes=0)
        return self._env.index_data[security].loc[dtime.date():dtime.date(), [field]].iloc[-1][field]

    def _set_bm_start_price(self, event):
        if self._ucontext.current_dt:
            self._bm_start_price = self.get_index_price(setting.get_benchmark())
        return False

    def _pnl(self, event):
        if self._bm_start_price:
            bm_price = self.get_index_price(setting.get_benchmark())
            self._returns_ls.append(100 * self._ucontext.portfolio.returns)
            self._bm_returns_ls.append(100 * (bm_price/self._bm_start_price - 1))
            self._dt_ls.append(self._ucontext.current_dt.date())
        return False

    def plot(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self._dt_ls, self._returns_ls, label="Returns", color="blue", linewidth=2)
        plt.plot(self._dt_ls, self._bm_returns_ls, label="Benchmark Returns", color="red", linewidth=2)  # 绘制曲线

        plt.fill_between(self._dt_ls, self._returns_ls, color="lightblue", alpha=0.5)
        
        # 添加网格和标题
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.title("PNL", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Returns (%)", fontsize=12)
        
        # 美化日期显示
        plt.gcf().autofmt_xdate()
        
        # 显示图例
        plt.legend()

        # 显示图表
        plt.show()