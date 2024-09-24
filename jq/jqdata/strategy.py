from .events import Event, EVENT
from .order import UserOrder
from .Env import Env
from .logger import log
from .api import setting

class Strategy(object):
    def __init__(self):
        self._ucontext = None
        
    def set_user_context(self, ucontext):
        self._ucontext = ucontext

    def _order(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        env = Env.get_instance()
        event_bus = env.event_bus
        order = UserOrder(security, amount, add_time=self._ucontext.current_dt)
        event_bus.publish_event(Event(EVENT.STOCK_ORDER, order=order))

    def _order_target(self, security, amount, style=None, side='long', pindex=0, close_today=False):
        current_amount = self._ucontext.portfolio.positions[security].total_amount
        amount = amount - current_amount
        self._order(security, amount, style, side, pindex, close_today)

    def _order_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        order_cost = setting.get_order_cost(type='stock')
        #买入时需要预留手续费
        if value > 0:
            commission= (order_cost.open_tax + order_cost.open_commission) * value
            commission = commission if commission > order_cost.min_commission else order_cost.min_commission
            value -= commission
            if value <= 0:
                return
        current_price = self._ucontext.portfolio.positions[security].price
        amount = value / current_price
        self._order(security, amount, style, side, pindex, close_today)

    def _order_target_value(self, security, value, style=None, side='long', pindex=0, close_today=False):
        pass