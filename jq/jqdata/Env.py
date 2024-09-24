# -*- coding: utf-8 -*-
from userStrategy import userconfig

import pandas as pd
import pickle
from functools import lru_cache
import datetime

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
    "password": "yourpassword",
}

def shift_str_date(date_str: str, days_delta: int):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    new_date_obj = date_obj + datetime.timedelta(days=days_delta)
    return new_date_obj.strftime("%Y-%m-%d")

# @lru_cache(maxsize=8192)
def transform_key(key):
    if key.endswith('XSHE'):
        return key[:-4] + 'sz'
    elif key.endswith('XSHG'):
        return key[:-4] + 'sh'
    return key

def trans_name(name):
    if name.endswith('sz'):
        return name[:-2] + 'XSHE'
    elif name.endswith('sh'):
        return name[:-2] + 'XSHG'
    return name

class KeyTransDict(dict):
    def __getitem__(self, key):
        print(key)
        key = transform_key(key)
        print(key)
        return super().__getitem__(key)
    
    def __contains__(self, key):
        print(key)
        key = transform_key(key)
        print(key)
        return super().__contains__(key)

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
        self.data = dict()#KeyTransDict()
        self.index_data = dict()#KeyTransDict()

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

    def load_data(self):
        env = Env.get_instance()
        db_gate = MySQL_gate(
                start_date=shift_str_date(env.usercfg['start'], -7), 
                end_date=env.usercfg['end'], 
                **db_config
            )
        if_load = env.usercfg['if_load_data']
        if if_load:
            with open('data.pkl', 'rb') as f:
                self.data = pickle.load(f)
        else:
            stock_ls = db_gate.get_tables(db='stock').iloc[:, 0]
            for stock in stock_ls:
                print(f"{stock} data loading...", end="\r")
                df = db_gate.read_df(stock, db='stock')
                if df.empty:
                    continue
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df['date'] = df['trade_date']
                df.set_index('trade_date', inplace=True)
                self.data[trans_name(stock)] = df
            self._dump_data()


        index_ls = db_gate.get_tables(db='index').iloc[:, 0]
        for index in index_ls:
            print(f"{index} data loading...", end="\r")
            df = db_gate.read_df(index, db='index')
            if df.empty:
                continue
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df['date'] = df['trade_date']
            df.set_index('trade_date', inplace=True)
            self.index_data[trans_name(index)] = df

            

    def _dump_data(self):
        with open('data.pkl', 'wb') as f:
            pickle.dump(self.data, f)
            
