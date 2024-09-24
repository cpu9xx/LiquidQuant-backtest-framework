from .Env import Env

from enum import Enum
import datetime

class OrderStatus(Enum):
    open = 0
    partly_filled = 1
    canceled = 2
    rejected = 3
    done = 4
    held = 6
    expired = 5
    new = 8
    pending_cancel = 9
    

class UserOrder(object):
    _order_id = 0
    def __init__(self, security, amount, add_time):
        self._status = OrderStatus.held
        self.add_time = add_time
        self._is_buy = True if amount > 0 else False
        self.amount = abs(amount)
        self.filled = None
        self.security = security
        self.order_id = UserOrder._order_id
        UserOrder._order_id += 1
        self._price = None
        self.avg_cost = None
        self.side = None
        self.action = None
        self.commission = None

    @property
    def price(self):
        # 访问 self.price 时会自动调用这个函数
        if self._price is None:
            env = Env.get_instance()
            dtime = env.current_dt
            if datetime.time(9, 30) <= dtime.time() < datetime.time(15, 0):
                field = 'open'
            else:
                field = 'close'

            if datetime.time(0, 0) <= dtime.time() < datetime.time(9, 30):
                dtime += datetime.timedelta(days=-1, hours=0, minutes=0)
            self._price =  env.data[self.security].loc[dtime.date():dtime.date(), [field]].iloc[-1][field]
        return self._price

    def is_buy(self):
        return self._is_buy
    
    def status(self):
        return self._status
    
    def reject(self):
        self._status = OrderStatus.rejected

    def open(self):
        self._status = OrderStatus.open

    def done(self):
        self._status = OrderStatus.done

    def expired(self):
        self._status = OrderStatus.expired

    def __repr__(self):
        return f"UserOrder(order_id={self.order_id}, security={self.security}, price={self.price}, amount={self.amount}, buy={self._is_buy}, status={self._status}, filled={self.filled}, add_time={self.add_time}, avg_cost={self.avg_cost}, commission={self.commission})"
