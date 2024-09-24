# -*- coding: utf-8 -*-
import pandas as pd
from .Env import Env
from .events import Event, EVENT
from .logger import log
from .setting import Setting, OrderCost

_scheduler = None # main.py中的scheduler
_data = None
_strategy = None
_broker = None
_strategy = None
setting = Setting()
test = 11


##################################### time ################################
def run_daily(func, time, reference_security='000300.XSHG'):
    _scheduler._run_daily(func, time, reference_security)

##################################### time ################################




##################################### data ################################
# 返回行数与count强相关
def get_bars(security, count, unit='1d', fields=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
    return _data._get_bars(security, count, unit, fields, include_now, end_dt, fq_ref_date, df)


# 返回行数与end_date强相关
def get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
    return _data._get_price(security, start_date, end_date, frequency, fields, skip_paused, fq, count, panel, fill_paused, df)

##################################### data ################################






##################################### strategy ################################
def order(security, amount, style=None, side='long', pindex=0, close_today=False):
    _strategy._order(security, amount)

def order_target(security, target, style=None, side='long', pindex=0, close_today=False):
    _strategy._order_target(security, target)

def order_value(security, value, style=None, side='long', pindex=0, close_today=False):    
    _strategy._order_value(security, value)
##################################### strategy ################################



##################################### broker ################################
def get_trades():
    return _broker._get_trades()
##################################### broker ################################





##################################### setting ################################
def set_order_cost(cost, type: str, ref=None):
    setting._set_order_cost(cost, type, ref)

def set_benchmark(security):
    setting._set_benchmark(security)

def set_option(option: str, value):
    setting._set_option(option, value)
##################################### setting ################################
    
class Data(object):
    def __init__(self):
        self._ucontext = None
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _get_price(self, security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='post', count=None, panel=False, fill_paused=True, df=True):
        end_date = pd.to_datetime(end_date) if end_date else pd.to_datetime(self._ucontext.current_dt)
        env = Env.get_instance()
        if start_date and count:
            log.error('start_date and count cannot be set at the same time')
        elif start_date:
            start_date = pd.to_datetime(start_date)
        elif count:
            start_date = end_date - pd.Timedelta(days=count)
        else:
            log.error('start_date or count must be set')

        def process_security(security, start_date, end_date, fields, df):
            if df:
                return env.data[security].loc[start_date:end_date, fields].reset_index(drop=True)
            else:
                return env.data[security].loc[start_date:end_date, fields].to_records(index=False)


        if isinstance(security, str):
            res = process_security(security, start_date, end_date, fields, df)
        else:
            res = {s: process_security(s, start_date, end_date, fields, df) for s in security}
        return res

    def _history(self, count, unit='1d', field=['close'], security_list=None, df=True, skip_paused=False, fq='post'):
        pass

    def _get_bars(self, security, count, unit='1d', fields=['close'], include_now=False, end_dt=None, fq_ref_date=None, df=False):
        end_dt = pd.to_datetime(end_dt) if end_dt else pd.to_datetime(self._ucontext.current_dt)
        env = Env.get_instance()

        if not include_now:
            end_dt -= pd.Timedelta(days=1)

        # 定义处理单个security的函数
        def process_security(security, end_dt, fields, count, df):
            if df:
                return env.data[security].loc[:end_dt, fields].tail(count).reset_index(drop=True)
            else:
                return env.data[security].loc[:end_dt, fields].tail(count).to_records(index=False)

        # 处理数据
        if isinstance(security, str):
            res = process_security(security, end_dt, fields, count, df)
        else:
            res = {s: process_security(s, end_dt, fields, count, df) for s in security}

        return res

