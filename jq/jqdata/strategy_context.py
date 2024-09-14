from collections import defaultdict

class Position:
    def __init__(self):
        self.security = None
        self.price = None
        self.avg_cost = None
        self.init_time = None
        self.transact_time = None
        self.total_amount = None
        self.closeable_amount = None
        self.value = None

    def __repr__(self):
        return f"UserPosition({self.security})"

class Params():
    def __init__(self):
        self.start_date = None
        self.end_date = None
        self.type = None
        self.frequency = None

class Portfolio():
    def __init__(self, start_cash):
        self.positions = defaultdict(lambda: Position())
        self.available_cash = None
        self.total_value = None
        self.returns = None
        self.starting_cash = start_cash
        self.positions_value = None

class StrategyContext():
    _context = None
    def __init__(self, start_cash):
        if StrategyContext._context is not None:
            raise RuntimeError("StrategyContext 只能初始化一次")
        StrategyContext._context = self
        self.previous_date = None
        self.current_dt = None
        self.portfolio = Portfolio(start_cash)
        self.run_params = Params()
        self.universe = None
        
    @classmethod
    def get_instance(cls):
        if cls._context is None:
            raise RuntimeError("StrategyContext 还未初始化")
        return cls._context