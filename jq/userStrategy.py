import pandas as pd
import datetime

def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    #set_option('avoid_future_data', True)
    # 过滤掉order系列API产生的比error级别低的log
    log.set_level('order', 'error')
    
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
    
    g.MAX_HOLD = 20
    g.hold = g.MAX_HOLD

    stock_list=get_all_securities(types=['stock']).index.tolist()
    #print(stock_list)
    # stock_list = st_filter(stock_list)
    stock_list = filter_kcbj_stock(stock_list)
    #stock_list = price_filter(stock_list)
    g.security = stock_list
    
    g.buydict = {}
    g.selldict = {}
    g.flagdict = {}
    
    init_dict()
    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    #run_monthly(change_big_rate, 1, time='before_open', reference_security='000300.XSHG')
      # 开盘时或每分钟开始时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
      # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')

    
def get_after_trade_days(date, count):
    all_date = pd.Series(get_all_trade_days())
    if isinstance(date,str):
        all_date = all_date.astype(str)
    if isinstance(date, datetime.datetime):
        date = date.date()

    return all_date[all_date>date].head(count).values[-1]

def future_profit(days,stock,context):
    date = get_after_trade_days(context.current_dt,days)
    future_top_price = get_price(stock, start_date=context.current_dt,
                end_date=date,  
                frequency='daily',
                fields='close').max()[-1]
    future_low_price = get_price(stock, start_date=context.current_dt,
                end_date=date,  
                frequency='daily',
                fields='close').min()[-1]
                
    top_profit = 100*((future_top_price - context.portfolio.positions[stock].price)/context.portfolio.positions[stock].price)
    low_profit = 100*((future_low_price - context.portfolio.positions[stock].price)/context.portfolio.positions[stock].price)
    return top_profit,low_profit

def if_space_up_down(stock_list):
    last_open = history(count=3, unit='1d', field='open', security_list=stock_list)
    log.test("history 1 end")
    last_2_close = history(count=2, unit='1d', field='close', security_list=stock_list).head(1)
    log.test("history 2 end")
    last_2_open = history(count=2, unit='1d', field='open', security_list=stock_list).head(1)
    log.test("history end")
    for stock in stock_list:
        #跳空低开
        if 0.98*min(last_2_close[stock][-1],last_2_open[stock][-1]) > last_open[stock][-1]:
            g.flagdict[stock] = 0
        #跳空高开    
        elif min(last_2_close[stock][-1],last_2_open[stock][-1]) < last_open[stock][-1]:
            g.flagdict[stock] = 1
        else:
            g.flagdict[stock] = 2
    '''
    for stock in stock_list :
        #跳空低开
        if last_2_close[stock][-1] > last_open[stock][-1]:
            g.flagdict[stock] = 0
        #跳空高开    
        elif last_2_close[stock][-1] < last_open[stock][-1]:
            g.flagdict[stock] = 1
        else:
            g.flagdict[stock] = 2'''
    
    
def update_dict(context):
    for stock in g.security :
        flag = g.flagdict[stock]
        if flag == 0:
            g.selldict[stock] += 1
            g.buydict[stock]  = 0
            if g.selldict[stock] == 1 :
                sell_security(stock,context)
        elif flag == 1:
            g.buydict[stock] += 1
            g.selldict[stock] = 0
            if g.buydict[stock] == 7:
                buy_security(stock,context)
        elif flag == 2:
            g.selldict[stock] = 0
            g.buydict[stock]  = 0
        
def init_dict():
    for stock in g.security :
        g.selldict[stock] = 0
        g.buydict[stock]  = 0
        g.flagdict[stock] = 0
    print("初始化完成")
    

 
#过滤ST   
def st_filter(security_list):
    current_data = get_current_data()
    security_list = [stock for stock in security_list if not current_data[stock].is_st]
    return security_list 



def buy_security(stock,context):
    if not stock in list(context.portfolio.positions.keys()) and (g.hold > 0):
        cash_per_stock = context.portfolio.available_cash/g.hold
        order = order_value(stock, cash_per_stock)
        #如果买入成功
        if stock in list(context.portfolio.positions.keys()):
            g.hold -= 1
            # 记录这次买入
            log.info("%s 买入 %s, 剩余仓位 %s %%" % (context.portfolio.positions[stock].price, stock, 100*context.portfolio.available_cash/(context.portfolio.available_cash+context.portfolio.positions_value)))

def sell_security(stock,context):
    if stock in list(context.portfolio.positions.keys()):
        #计算收益率
        profit = 100*((context.portfolio.positions[stock].price - context.portfolio.positions[stock].avg_cost)/context.portfolio.positions[stock].avg_cost)
        time = context.portfolio.positions[stock].init_time

        top_profit,low_profit = future_profit(60,stock,context)
        if order_target(stock, 0) != None:
            g.hold += 1
            # 记录这次卖出
            log.info("%s 建仓，卖出 %s, 收益 %s %%, 卖出后最大涨幅%s %%, 最小涨幅%s %%" % (time, stock, profit, top_profit,low_profit))
    
## 开盘时运行函数
def market_open(context):
    if_space_up_down(g.security)
    log.test('if_space_up_down end')
    update_dict(context)
    log.test('update_dict end')
    print(g.hold)
    print("当前持仓：",set(context.portfolio.positions.keys()))
    if g.hold < g.MAX_HOLD:
        for security in list(context.portfolio.positions.keys()):
            #计算收益率
            profit = 100*((context.portfolio.positions[security].price - context.portfolio.positions[security].avg_cost)/context.portfolio.positions[security].avg_cost)
            print( "%s, 当前利润: %s" % (security,profit))

 
## 收盘后运行函数  
def after_market_close(context):
    log.info('一天结束')
    log.info('##############################################################')