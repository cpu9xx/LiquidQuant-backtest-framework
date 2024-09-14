# -*- coding: utf-8 -*-
from enum import Enum
from collections import defaultdict

class Event(object):
    def __init__(self, event_type, **kwargs):
        self.__dict__ = kwargs
        self.event_type = event_type

    # print(event) 
    def __repr__(self):
        return ' '.join('{}:{}'.format(k, v) for k, v in self.__dict__.items())


class EventBus(object):
    def __init__(self):
        self._listeners = defaultdict(list)
        print(self._listeners)

    def add_listener(self, event, listener):
        self._listeners[event].append(listener)

    def prepend_listener(self, event, listener):
        self._listeners[event].insert(0, listener)

    def publish_event(self, event):
        for l in self._listeners[event.event_type]:
            # listener 返回 True ，那么消息不再传递下去，否则继续传递
            if l(event):
                break

class EVENT(Enum):
    # 股票
    STOCK = 'stock'
    # 期货
    FUTURE = 'future'
    #事件
    TIME = 'time'

# print(parse_event('stock'))   # 输出: EVENT.STOCK
def parse_event(event_str):
    return EVENT.__members__.get(event_str.upper(), None)
