# -*- coding: utf-8 -*-
from .Env import Env
import datetime
from .events import Event, EVENT

_scheduler = None # main.py中的scheduler

def run_daily(func, time):
    _scheduler._run_daily(func, time)

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
                self._ucontext.current_dt = day
                env.current_dt = day
        pass
