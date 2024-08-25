# -*- coding: utf-8 -*-
import random
from .events import EVENT
__all__ = [
]
def export_as_api(func):
    __all__.append(func)
    return func

@export_as_api
def startup(event_bus):
    event_bus.add_listener(EVENT.STOCK, handler)
    print('load and register stock mod')

def handler(event):
    rd = random.randint(0,9)
    if rd == 7:
        print('成交记录：UserTrade({''secu:000001.XHSG,''order_id'': 1522310538, ''trade_id'': 1522310538, ''price'': 10.52, ''amount'': 2300')
    if rd == 5:
        print('成交记录：UserTrade({''secu:000254.XHSG,''order_id'': 1522310538, ''trade_id'': 1522310538, ''price'': 23.52, ''amount'': 1700')
    if rd == 2:
        print('成交记录：UserTrade({''secu:600012.XHSG,''order_id'': 1522310538, ''trade_id'': 1522310538, ''price'': 13.52, ''amount'': 1700')
    
    return True
  
    