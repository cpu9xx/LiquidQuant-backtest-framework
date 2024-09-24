# -*- coding: utf-8 -*-
# from Env import Env, config
# from Mod import ModHandler
# from events import EVENT, Event
# from globalVars import GlobalVars
# from CodeLoader import CodeLoader
# from strategy_context import StrategyContext
# import api
# from api import Scheduler
# import datetime
from . import logger
from .Env import Env, config
from .Mod import ModHandler
from .events import EVENT, Event
from .globalVars import GlobalVars
from .CodeLoader import CodeLoader
from .strategy_context import StrategyContext
from .recorder import Recorder
from .scheduler import Scheduler
from .broker import Broker
from .strategy import Strategy
from .setting import Setting
from . import api
import datetime

def run_file(strategy_file_path):
    #加载config到env
    env = Env(config)
    #启动加载模块
    mod = ModHandler()
    #加载模块中注入config
    mod.set_env(env)
    #启动加载
    mod.start_up()
    
    loader = CodeLoader(strategy_file_path)
    
    # scope = {}
    scope = {'__name__': 'userStrategy'}
    scope = loader.load(scope)
    context = StrategyContext(start_cash=env.usercfg['start_cash'])
    env.set_global_vars(GlobalVars())

    logger.log.set_env(env)

    scope.update({
        "g": env.global_vars,
        "log": logger.log,

    })
    
    env.current_dt =  datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
    context.current_dt = env.current_dt
    env.load_data()

    recorder = Recorder()
    strategy = Strategy()
    broker = Broker()
    scheduler = Scheduler()
    data = api.Data()

    recorder.set_user_context(context)
    api.setting.set_user_context(context)
    strategy.set_user_context(context)
    broker.set_user_context(context)
    scheduler.set_user_context(context)
    data.set_user_context(context)
    

    api._strategy = strategy
    api._broker = broker
    api._scheduler = scheduler
    api._data = data
    

    initialize = scope.get('initialize', None)
    initialize(context)

    scheduler.start_event_src(reference_security=api.setting.get_benchmark())

    recorder.plot()

