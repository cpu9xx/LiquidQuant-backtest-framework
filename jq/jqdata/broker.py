from .events import EVENT, Event
from .Env import Env
from .logger import log
from .api import setting
from .order import OrderStatus
from .scheduler import TIME
from collections import defaultdict
# class Executor(object):
#     def __init__(self, env):
#         self._env = env

#     KNOWN_EVENTS = {
#         EVENT.TICK,
#         EVENT.BAR,
#         EVENT.BEFORE_TRADING,
#         EVENT.AFTER_TRADING,
#         EVENT.POST_SETTLEMENT,
#     }

#     def run(self, bar_dict):

#         start = self._env.usercfg['start']
#         end = self._env.usercfg['end']
#         frequency = self._env.config.base.frequency
#         event_bus = self._env.event_bus

#         for event in self._env.event_source.events(start, end, frequency):
#             if event.event_type in self.KNOWN_EVENTS:
#                 self._env.calendar_dt = event.calendar_dt
#                 #self._env.trading_dt = event.trading_dt

#                 event_bus.publish_event(event)
class UserTrade(object):
    _trade_id = 0
    def __init__(self, order, time):
        self.time = time
        self.order = order
        self.trade_id = UserTrade._trade_id
        UserTrade._trade_id += 1

    def __repr__(self):
        return f"UserTrade(trder_id={self.trade_id}, order_id={self.order.order_id}, time={self.time}, price={self.order.price}, amount={self.order.amount}, commission={self.order.commission})"


class Broker(object):
    # _broker = None
    def __init__(self):
        # Broker._broker = self
        self._ucontext = None
        self._env = Env()
        self._order_recieved = defaultdict(list)
        self._trades = defaultdict(dict)
        # self.start = datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
        # self.end = datetime.datetime.strptime(env.usercfg['end'], "%Y-%m-%d")
        event_bus = self._env.event_bus
        event_bus.add_listener(EVENT.STOCK_ORDER, self._before_trading)
        event_bus.add_listener(EVENT.STOCK_ORDER, self._trading)
        event_bus.add_listener(EVENT.STOCK_ORDER, self._after_trading)
        event_bus.add_listener(EVENT.MARKET_CLOSE, self._market_close)
        # event_bus.add_listener(EVENT.GET_TRADES, self._get_trades)

    def set_user_context(self, ucontext):
        self._ucontext = ucontext
    # @classmethod
    # def get_instance(cls):
    #     """
    #     返回已经创建的 broker 对象
    #     """
    #     if Broker._broker is None:
    #         raise RuntimeError("Broker还未初始化")
    #     return Broker._broker    
    
    #check oreder
    def _before_trading(self, event):
        order = event.__dict__['order']
        self._order_recieved[self._env.current_dt.date()].append(order)
        if order.is_buy():
            log.info(f"订单已委托：{order}")
            # total_price = order.price * order.amount
            # if total_price < self.portfolio.available_cash:
            #     order.open()
            # else:
            #     order.reject()
            #     log.warning(f"可用资金不足：{order.security}")
            #     return True
        else:
            if order.security in self._ucontext.portfolio.positions and self._ucontext.portfolio.positions[order.security].closeable_amount >= order.amount:
                self._ucontext.portfolio.positions[order.security].closeable_amount -= order.amount
                order.open()
                log.info(f"订单已委托：{order}")
            else:
                order.reject()
                log.warning(f"可卖出股数不足：{order.security}")
                return True
        return False

    def _trading(self, event):
        order = event.__dict__['order']
        ordertime = order.add_time
        data_date = self._env.data[order.security][self._ucontext.current_dt, 'date'][0]
        if data_date is None:
            order.reject()
            log.warning(f"停牌无法成交：{order.security}")
            return True
        else:
            total_price = order.price * order.amount
            order_cost = setting.get_order_cost(type='stock')

            if order.is_buy():
                commission = (order_cost.open_tax + order_cost.open_commission) * total_price
                order.commission = commission if commission > order_cost.min_commission else order_cost.min_commission
                total_cost = total_price + order.commission
                if total_cost < self._ucontext.portfolio.available_cash:
                    self._ucontext.portfolio.available_cash -= total_cost
                    self._ucontext.portfolio.positions.create_key(order.security)
                    self._ucontext.portfolio.positions[order.security].init_position(order.security, total_cost/order.amount, ordertime, order.amount)
                    order.done()
                else:
                    log.warning(f"可用资金不足：{order}")
                    order.reject()
            else:
                commission = (order_cost.close_tax + order_cost.close_commission) * total_price
                order.commission = commission if commission > order_cost.min_commission else order_cost.min_commission
                if total_price > order.commission:
                    total_gain = total_price - order.commission
                    self._ucontext.portfolio.available_cash += total_gain
                    self._ucontext.portfolio.positions[order.security].close_position(order.amount, self._env.current_dt)
                    if self._ucontext.portfolio.positions[order.security].total_amount <= 0:
                        self._ucontext.portfolio.positions.remove_key(order.security)
                    order.done()
                else:
                    log.warning(f"收益小于手续费：{order}")
                    order.done()
            
            return False
        
    def _after_trading(self, event):
        order = event.__dict__['order']
        if order.status() == OrderStatus.done:
            trade = UserTrade(order, self._env.current_dt)
            self._trades[self._env.current_dt.date()][trade.trade_id] = trade
            log.info(f"订单完成：{order}")
        else:
            log.warning(f"订单未完成：{order}")
        return True

    def _get_trades(self):
        return self._trades[self._env.current_dt.date()]

    def _market_close(self, event):
        for order in self._order_recieved[self._env.current_dt.date()]:
            if order.status() == OrderStatus.done:
                continue
            order.expired()
        # T+1, orders expired
        for security in self._ucontext.portfolio.positions:
            self._ucontext.portfolio.positions[security].update_closeable_amount()
        return False
