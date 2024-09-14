# -*- coding: utf-8 -*-
import pandas as pd
from .Env import Env
import datetime
from .events import Event, EVENT
from enum import Enum
_scheduler = None # main.py中的scheduler
_data = None

def run_daily(func, time):
    _scheduler._run_daily(func, time)

def get_bars(security, count, unit='1d', field=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
    return _data._get_bars(security, count, unit, field, include_now, end_dt, fq_ref_date, df)

class Scheduler(object):
    def __init__(self):
        # self._registry = []
        # self._today = None
        # self._this_week = None
        # self._this_month = None
        # self._last_minute = 0
        # self._current_minute = 0
        # self._stage = None
        self._ucontext = None
        # self._frequency = frequency

        # event_bus = Environment.get_instance().event_bus
        # event_bus.add_listener(EVENT.PRE_BEFORE_TRADING, self.next_day_)
        # event_bus.add_listener(EVENT.BEFORE_TRADING, self.before_trading_)
        # event_bus.add_listener(EVENT.BAR, self.next_bar_)

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _run_daily(self, func, time):
        env = Env.get_instance()
        event_bus = env.event_bus
        eventSrc = []
        if time == 'open':
            start = datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
            end = datetime.datetime.strptime(env.usercfg['end'], "%Y-%m-%d")
            for i in range((end - start).days + 1):
                day = start + datetime.timedelta(days=i, hours=9, minutes=30)
                event = Event(EVENT.TIME)
                eventSrc.append(event)
                # print(day)
                event_bus.publish_event(Event(EVENT.STOCK))
                # for i in eventSrc:
                #    for k, v in i.__dict__.items():
                #        print(type(k))
                #        pass




                func(self._ucontext)
                self._ucontext.previous_date = self._ucontext.current_dt
                self._ucontext.current_dt = day
                env.current_dt = day
        pass

class OrderCost(object):
    def __init__(self, open_tax=0, close_tax=0.001, open_commission=0.0001, close_commission=0.0001, min_commission=0.1):
        self.open_tax = open_tax
        self.close_tax = close_tax
        self.open_commission = open_commission
        self.close_commission = close_commission
        self.min_commission = min_commission

class Setting(object):
    def __init__(self):
        self._ucontext = None

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _set_benchmark(self, security: str):
        return None
    
    def _set_order_cost(self, cost: OrderCost, type: str, ref=None):
        pass
    
    def _set_option(self):
        pass

    def _set_universe(self, security_list):
        self._ucontext.universe = security_list
    
class Data(object):
    def __init__(self):
        self._ucontext = None
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _get_price(self, security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True):
        if isinstance(security, str):
            security = [security]
        for s in security:
            pass

    def _history(self, count, unit='1d', field=['close'], security_list=None, df=True, skip_paused=False, fq='post'):
        pass

    def _get_bars(self, security, count, unit='1d', field=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
        end_dt = pd.to_datetime(end_dt) if end_dt else pd.to_datetime(self._ucontext.current_dt)
        env = Env.get_instance()

        if not include_now:
            end_dt -= pd.Timedelta(days=1)

        # 定义处理单个security的函数
        def process_security(security, end_dt, field, count, df):
            if df:
                return env.data[security].loc[:end_dt, field].tail(count).reset_index(drop=True)
            else:
                return env.data[security].loc[:end_dt, field].tail(count).to_records(index=False)

        # 处理数据
        if isinstance(security, str):
            res = process_security(security, end_dt, field, count, df)
        else:
            res = {s: process_security(s, end_dt, field, count, df) for s in security}

        return res

class OrderStatus(Enum):
    open = 0
    partly_filled = 1
    cancel = 2
    rejected = 3
    done = 4
    new = 8
    pending_cancel = 9
    # held = 'Held'

class Order(object):
    def __init__(self):
        self.status = OrderStatus()
        self.add_time = None
        self.is_buy = None
        self.amount = None
        self.filled = None
        self.security = None
        self.order_id = None
        self.price = None
        self.avg_cost = None
        self.side = None
        self.action = None
        self.commission = None

class Trade(object):
    def __init__(self):
        self._ucontext = None
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def order(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        pass

    def order_target(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        pass

    def order_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        pass

    def order_target_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        pass