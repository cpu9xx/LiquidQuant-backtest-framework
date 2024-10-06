from .Env import Env
from .events import EVENT
from .api import setting
from .logger import log

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

class Recorder(object):
    def __init__(self):
        self._ucontext = None
        self._env = Env()
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

    # def plot(self):
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(self._dt_ls, self._returns_ls, label="Returns", color="blue", linewidth=2)
    #     plt.plot(self._dt_ls, self._bm_returns_ls, label="Benchmark Returns", color="red", linewidth=2)  # 绘制曲线

    #     plt.fill_between(self._dt_ls, self._returns_ls, color="#B9CFE9", alpha=0.5)
        
    #     # 添加网格和标题
    #     plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    #     plt.title("PNL", fontsize=16)
    #     plt.xlabel("Date", fontsize=12)
    #     plt.ylabel("Returns (%)", fontsize=12)
        
    #     plt.gcf().autofmt_xdate()
    #     plt.legend()
    #     plt.show()  # 显示图形
    #     plt.savefig('pnl.png')  # 保存到文件中
    #     plt.close()

    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 6))

        # 绘制两条曲线
        line1, = ax.plot(self._dt_ls, self._returns_ls, label="Returns", color="blue", linewidth=2, picker=5)
        line2, = ax.plot(self._dt_ls, self._bm_returns_ls, label="Benchmark Returns", color="red", linewidth=2, picker=5)

        # 添加填充
        ax.fill_between(self._dt_ls, self._returns_ls, color="#B9CFE9", alpha=0.5)

        # 添加网格和标题
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title("PNL", fontsize=16)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Returns (%)", fontsize=12)

        # 自动格式化 x 轴标签
        fig.autofmt_xdate()
        ax.legend()

        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="black", lw=0.5),
                    arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=.1", color="gray"))

        annot.set_visible(False)

        def update_annot(line, ind):
            # 获取鼠标悬停点的索引
            pos = line.get_xydata()[ind["ind"][0]]
            annot.xy = pos
            date_str = mdates.num2date(pos[0]).strftime("%Y-%m-%d")
            padding_length = max(0, len(f"Date:  {date_str}") - len(f"Returns:  {pos[1]:.2f}%"))
            padding = ' ' * (padding_length+1)
            text = f"Date:  {date_str}\nReturns:  {padding}{pos[1]:.2f} %"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.9)  # 设置背景透明度，使其略显高亮

        def hover(event):
            # 如果鼠标在坐标轴范围内
            if event.inaxes == ax:
                # 检查鼠标是否在任一条曲线的范围内
                cont1, ind1 = line1.contains(event)
                cont2, ind2 = line2.contains(event)
                if cont1:
                    update_annot(line1, ind1)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                elif cont2:
                    update_annot(line2, ind2)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

        # 连接鼠标移动事件和 hover 函数
        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.show() 