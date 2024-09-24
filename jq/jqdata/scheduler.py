from .Env import Env
from .events import Event, EVENT
from .logger import log
import datetime
from collections import defaultdict
from enum import Enum

class TIME(Enum):
    BEFORE_OPEN = datetime.time(9, 0)
    OPEN = datetime.time(9, 30)
    CLOSE = datetime.time(15, 0)
    AFTER_CLOSE = datetime.time(15, 30)
    DAY_END = datetime.time(23, 59)

    @property
    def hour(self):
        return self.value.hour

    @property
    def minute(self):
        return self.value.minute

    def __str__(self):
        return self.value.strftime("%H:%M")
    

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
        self.event_src = defaultdict(lambda: defaultdict(list))
        # self._frequency = frequency
        env = Env.get_instance()
        self.start = datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
        self.end = datetime.datetime.strptime(env.usercfg['end'], "%Y-%m-%d")
        event_bus = env.event_bus
        event_bus.add_listener(EVENT.TIME, self._run_before_open)
        event_bus.add_listener(EVENT.TIME, self._run_open)
        event_bus.add_listener(EVENT.TIME, self._run_close)
        event_bus.add_listener(EVENT.TIME, self._run_after_close)
        # event_bus.add_listener(EVENT.BEFORE_TRADING, self.before_trading_)
        # event_bus.add_listener(EVENT.BAR, self.next_bar_)

    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _run_daily(self, func, time, reference_security):
        env = Env.get_instance()
        trade_dates = env.index_data[reference_security].index

        # 触发初始化
        first_tick_time = trade_dates[0] + datetime.timedelta(days=0, hours=TIME.OPEN.hour, minutes=TIME.OPEN.minute)
        self.event_src[trade_dates[0]][TIME.OPEN].append(Event(EVENT.FIRST_TICK, func=None, time=first_tick_time))

        for date in trade_dates:
            time_type = getattr(TIME, time.upper())
            t = date + datetime.timedelta(days=0, hours=time_type.hour, minutes=time_type.minute)
            self.event_src[date][time_type].append(Event(EVENT.TIME, func=func, time=t))

    def start_event_src(self, reference_security):
        env = Env.get_instance()
        event_bus = env.event_bus
        # for i in range((self.end - self.start).days + 1): 
        #     date = self.start + datetime.timedelta(days=i)

        for date in env.index_data[reference_security].index:
            events_dict = self.event_src.get(date, {})
            for time_type in TIME:
                events = events_dict.get(time_type, [])
                for event in events:
                    time = event.__dict__['time']
                    if self._ucontext.current_dt:
                        assert time >= self._ucontext.current_dt
                        self._ucontext.previous_date = self._ucontext.current_dt.date()
                    self._ucontext.current_dt = time
                    env.current_dt = time
                    event_bus.publish_event(event)

            #每个交易日最后执行
            aft_close_time = date + datetime.timedelta(days=0, hours=TIME.AFTER_CLOSE.hour, minutes=TIME.AFTER_CLOSE.minute)
            self._ucontext.current_dt = aft_close_time
            env.current_dt = aft_close_time

            event_bus.publish_event(Event(EVENT.MARKET_CLOSE))
            
    def _run_before_open(self, event):
        time = event.__dict__['time']
        if time == self._ucontext.current_dt:
            func = event.__dict__['func']
            func(self._ucontext)
            return True
        else:
            raise ValueError("Scheduler before_open time error")

    def _run_open(self, event):
        time = event.__dict__['time']
        if time == self._ucontext.current_dt:
            func = event.__dict__['func']
            func(self._ucontext)
            return True
        else:
            raise ValueError("Scheduler open time error")


    def _run_close(self, event):
        time = event.__dict__['time']
        if time == self._ucontext.current_dt:
            func = event.__dict__['func']
            func(self._ucontext)
            return True
        else:
            raise ValueError("Scheduler close time error")

    def _run_after_close(self, event):
        time = event.__dict__['time']
        if time == self._ucontext.current_dt:
            func = event.__dict__['func']
            func(self._ucontext)
            return True
        else:
            raise ValueError("Scheduler after_close time error")