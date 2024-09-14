# -*- coding: utf-8 -*-
import pandas as pd
import pickle
from userStrategy import userconfig
config = {
    "mod": {
        "stock": {
            "enabled": True,
        },
        "future": {
            "enabled": False,
        }
    }
}

from .events import EventBus
from .gate import MySQL_gate

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "137137a",
}

class Env(object):
    _env = None

    def __init__(self, config):
        Env._env = self
        self.config = config
        self.event_bus = EventBus()
        self.usercfg = userconfig
        self.global_vars = None
        self.current_dt = None
        self.event_source = None
        self.data = dict()

    @classmethod
    def get_instance(cls):
        """
        返回已经创建的 Environment 对象
        """
        if Env._env is None:
            raise RuntimeError("策略还未初始化")
        return Env._env

    def set_global_vars(self, global_vars):
        self.global_vars = global_vars

    def set_event_source(self, event_source):
        self.event_source = event_source

    def load_data(self, if_load=False):
        if if_load:
            with open('data.pkl', 'rb') as f:
                self.data = pickle.load(f)
        else:
            env = Env.get_instance()
            db_gate = MySQL_gate(
                start_date=env.usercfg['start'], 
                end_date=env.usercfg['end'], 
                **db_config
            )
            stock_ls = db_gate.get_tables(db='stock').iloc[:, 0]
            for stock in stock_ls:
                print(f"{stock} data loading...", end="\r")
                df = db_gate.read_df(stock)
                if df.empty:
                    continue
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df['date'] = df['trade_date']
                df.set_index('trade_date', inplace=True)
                self.data[stock] = df
            self._dump_data()

    def _dump_data(self):
        with open('data.pkl', 'wb') as f:
            pickle.dump(self.data, f)
            
