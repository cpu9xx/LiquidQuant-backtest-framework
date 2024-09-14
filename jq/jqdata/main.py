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
from .Env import Env, config
from .Mod import ModHandler
from .events import EVENT, Event
from .globalVars import GlobalVars
from .CodeLoader import CodeLoader
from .strategy_context import StrategyContext
from .api import Scheduler, Setting, Data
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

    env.set_global_vars(GlobalVars())
    scope.update({
        "g": env.global_vars

    })
    
    env.current_dt =  datetime.datetime.strptime(env.usercfg['start'], "%Y-%m-%d")
    env.load_data(if_load=True)
    # env.load_data(if_load=False)

    context = StrategyContext(start_cash=env.usercfg['start_cash'])

    scheduler = Scheduler()
    data = Data()
    setting = Setting()

    scheduler.set_user_context(context)
    data.set_user_context(context)
    setting.set_user_context(context)

    api._scheduler = scheduler
    api._data = data
    api._setting = setting

    initialize = scope.get('initialize', None)
    initialize(context)

    data = {}
    f1 = scope.get('handle_data', None)
    f1(context,data)




    #事件发布
    # event_bus = env.event_bus
    # event_bus.publish_event(Event(EVENT.STOCK))
    # event_bus.publish_event(Event(EVENT.FUTURE))
