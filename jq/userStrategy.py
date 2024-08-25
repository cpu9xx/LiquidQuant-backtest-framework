# print(globals())
print(globals()['__name__'])
userconfig = {
    "start":"2018-01-01",
    "end":"2018-03-29"
}

def initialize(context):
    context.current_dt = '2018-01-01'
    g.today = "2018-03-23"
    run_daily(market_open, time='open')

def market_open(context):
    print('context:',context.current_dt)
    pass

def handle_data(context, data):
    #print('HANDLE:',context.current_dt)
    pass
